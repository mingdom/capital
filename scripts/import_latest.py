from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # only for static type checkers; avoids hard dependency at runtime
    from scripts.crypto_db import DBHandle


IMPORT_DIR = Path("data/import")
ARCHIVE_DIR = IMPORT_DIR / "archive"
LOCAL_DB_PATH = Path("data/localdb.sqlite3")
CANONICAL_JSON = Path("data/valuations.json")
CANONICAL_FIDELITY = Path("data/private/fidelity-performance.csv")


PARTIAL_SUFFIXES = (".crdownload", ".download", ".part", ".partial", ".tmp")


@dataclass
class Candidate:
    path: Path
    mtime: float


def is_valid_file(p: Path) -> bool:
    if not p.is_file():
        return False
    if p.name.startswith("."):
        return False
    if p.suffix.lower() not in (".json", ".csv"):
        return False
    if any(p.name.endswith(sfx) for sfx in PARTIAL_SUFFIXES):
        return False
    try:
        if p.stat().st_size == 0:
            return False
    except FileNotFoundError:
        return False
    return True


def list_candidates(root: Path, ext: str) -> list[Candidate]:
    files: list[Candidate] = []
    for child in root.iterdir():
        if child.is_file() and child.suffix.lower() == ext and is_valid_file(child):
            try:
                mtime = child.stat().st_mtime
            except FileNotFoundError:
                continue
            files.append(Candidate(path=child, mtime=mtime))
    return files


def _max_summary_date(file: Path) -> Optional[datetime]:
    try:
        with file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            return None
        max_dt: Optional[datetime] = None
        for item in data:
            if not isinstance(item, dict):
                continue
            v = item.get("summaryDate")
            if not v:
                continue
            try:
                dt = datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                continue
            if max_dt is None or dt > max_dt:
                max_dt = dt
        return max_dt
    except Exception:
        return None


def pick_latest_json(cands: Iterable[Candidate]) -> Optional[Candidate]:
    if not cands:
        return None
    scored: list[tuple[datetime, float, str, Candidate]] = []
    for c in cands:
        as_of = _max_summary_date(c.path)
        key_dt = as_of or datetime.fromtimestamp(c.mtime)
        scored.append((key_dt, c.mtime, c.path.name, c))
    # Sort by (date desc, mtime desc, name desc)
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    return scored[-1][3]


def pick_latest_csv(cands: Iterable[Candidate]) -> Optional[Candidate]:
    if not cands:
        return None
    # Sort by (mtime desc, name desc)
    scored = sorted(((c.mtime, c.path.name, c) for c in cands), key=lambda t: (t[0], t[1]))
    return scored[-1][2]


def sha256_hex(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_copy(src: Path, dst: Path, dry_run: bool = False) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return
    import tempfile

    with src.open("rb") as fh:
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(dst.parent)) as tmp:
            shutil.copyfileobj(fh, tmp)
            tmp_path = Path(tmp.name)
    os.replace(tmp_path, dst)


def archive_move(src: Path, archive_root: Path, dry_run: bool = False) -> Path:
    day = datetime.utcnow().strftime("%Y-%m-%d")
    dest_dir = archive_root / day
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if not dry_run:
        # Avoid overwrite by adding numeric suffix
        final = dest
        idx = 1
        while final.exists():
            final = dest_dir / f"{src.stem}-{idx}{src.suffix}"
            idx += 1
        shutil.move(str(src), str(final))
        return final
    else:
        return dest


def insert_file_row(db, *, source: str, original: Path, archive_path: Optional[Path], content_bytes: bytes) -> int:
    from scripts.crypto_db import encrypt_bytes, now_iso  # lazy import

    cipher, nonce = encrypt_bytes(db, content_bytes)
    cur = db.conn.cursor()
    meta = original.stat()
    cur.execute(
        """
        INSERT OR IGNORE INTO files(source, original_name, path, sha256, size, mtime, imported_at, status, archive_path, notes, content_cipher, content_nonce)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            source,
            original.name,
            str(original),
            sha256_hex(original),
            meta.st_size,
            meta.st_mtime,
            now_iso(),
            "archived" if archive_path else "imported",
            str(archive_path) if archive_path else None,
            None,
            cipher,
            nonce,
        ),
    )
    db.conn.commit()
    # Retrieve row id (on duplicate ignore, fetch existing id)
    cur.execute("SELECT id FROM files WHERE sha256 = ?", (sha256_hex(original),))
    row = cur.fetchone()
    return int(row[0])


def insert_valuations_row(db, *, as_of_date: Optional[datetime], source: str, file_id: int, payload_bytes: bytes) -> int:
    from scripts.crypto_db import encrypt_bytes  # lazy import

    cipher, nonce = encrypt_bytes(db, payload_bytes)
    cur = db.conn.cursor()
    cur.execute(
        """
        INSERT INTO valuations(as_of_date, source, file_id, payload_cipher, payload_nonce, ingested_at)
        VALUES(?,?,?,?,?,?)
        """,
        (
            (as_of_date or datetime.utcnow()).date().isoformat(),
            source,
            file_id,
            cipher,
            nonce,
            __import__("scripts.crypto_db", fromlist=["now_iso"]).now_iso(),
        ),
    )
    db.conn.commit()
    return int(cur.lastrowid)


def run(args: argparse.Namespace) -> int:
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    json_cands = list_candidates(IMPORT_DIR, ".json")
    csv_cands = list_candidates(IMPORT_DIR, ".csv")

    latest_json = pick_latest_json(json_cands)
    latest_csv = pick_latest_csv(csv_cands)

    if args.verbose:
        print(f"Found JSON candidates: {[c.path.name for c in json_cands]}")
        print(f"Found CSV candidates: {[c.path.name for c in csv_cands]}")
        print(f"Selected JSON: {latest_json.path.name if latest_json else None}")
        print(f"Selected CSV: {latest_csv.path.name if latest_csv else None}")

    # Prepare DB if passphrase available
    db_handle = None
    # Lazily import crypto only if needed
    try:
        from scripts.crypto_db import get_passphrase, open_encrypted_db
    except Exception:  # pragma: no cover - cryptography not installed yet
        get_passphrase = None  # type: ignore
        open_encrypted_db = None  # type: ignore

    passphrase = None
    if get_passphrase is not None:
        passphrase = get_passphrase()
    if passphrase:
        if args.verbose:
            print("DB encryption enabled (passphrase provided).")
        if not args.dry_run and open_encrypted_db is not None:
            db_handle = open_encrypted_db(str(LOCAL_DB_PATH), passphrase)
    else:
        if args.verbose:
            print("No passphrase provided; skipping DB ingestion.")

    # Process JSON → valuations.json
    if latest_json:
        if args.verbose:
            print(f"Copying {latest_json.path} -> {CANONICAL_JSON}")
        atomic_copy(latest_json.path, CANONICAL_JSON, dry_run=args.dry_run)

        archive_path = archive_move(latest_json.path, ARCHIVE_DIR, dry_run=args.dry_run)

        if db_handle is not None:
            # Use the archive path after move; in dry-run the original still exists.
            file_for_db = archive_path if not args.dry_run else latest_json.path
            # Payload for valuations row should reflect canonical file unless dry-run.
            payload = CANONICAL_JSON.read_bytes() if not args.dry_run else latest_json.path.read_bytes()
            as_of = _max_summary_date(file_for_db)
            file_bytes = file_for_db.read_bytes()
            file_id = insert_file_row(
                db_handle,
                source="savvytrader",
                original=file_for_db,
                archive_path=archive_path if not args.dry_run else None,
                content_bytes=file_bytes,
            )
            insert_valuations_row(
                db_handle,
                as_of_date=as_of,
                source="savvytrader",
                file_id=file_id,
                payload_bytes=payload,
            )

    # Process CSV → fidelity-performance.csv
    if latest_csv:
        if args.verbose:
            print(f"Copying {latest_csv.path} -> {CANONICAL_FIDELITY}")
        atomic_copy(latest_csv.path, CANONICAL_FIDELITY, dry_run=args.dry_run)

        archive_path = archive_move(latest_csv.path, ARCHIVE_DIR, dry_run=args.dry_run)

        if db_handle is not None:
            file_for_db = archive_path if not args.dry_run else latest_csv.path
            file_bytes = file_for_db.read_bytes()
            insert_file_row(
                db_handle,
                source="fidelity",
                original=file_for_db,
                archive_path=archive_path if not args.dry_run else None,
                content_bytes=file_bytes,
            )

    if not latest_json and not latest_csv:
        print("No valid .json or .csv files found in data/import/.")
    else:
        if args.dry_run:
            print("Dry-run complete (no files modified).")
        else:
            print("Import complete.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Import latest JSON and CSV from data/import/ and update canonical inputs.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files or DB")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
