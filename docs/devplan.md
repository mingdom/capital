# Import Pipeline Dev Plan (Local, Encrypted, Simple)

This document captures the design and decisions for a simple, local-only import pipeline that consumes raw files you drop into `data/import/`, updates the canonical app inputs, and archives source files. It favors minimal dependencies and ease of iteration.

## Goals

- Single drop folder: `data/import/` for raw inputs (CSV and JSON mixed).
- Auto-detect latest of each type on demand:
  - `.json` => SavvyTrader valuations dump
  - `.csv` => Fidelity performance export
- Keep canonical app inputs stable so existing code continues to work:
  - `data/valuations.json` (SavvyTrader daily changes)
  - `data/private/fidelity-performance.csv` (Fidelity)
- Maintain a local, file-based DB for provenance and history.
- Encrypt sensitive data at rest in the DB with a passphrase.
- Archive processed raw files indefinitely under `data/import/archive/`.

## Non-Goals (for now)

- No production-grade key management or full-database encryption. We use app-layer encryption for sensitive columns.
- No background watchers. Import is run manually via a CLI.
- No schema for advanced analytics in the DB; we store raw payloads (encrypted) and file metadata.

## Storage Design

- SQLite database at `data/localdb.sqlite3` (created on first run).
- Tables:
  - `meta(key TEXT PRIMARY KEY, value TEXT)` — stores KDF salt and schema version.
  - `files(id INTEGER PRIMARY KEY, source TEXT, original_name TEXT, path TEXT, sha256 TEXT UNIQUE, size INTEGER, mtime REAL, imported_at TEXT, status TEXT, archive_path TEXT, notes TEXT, content_cipher BLOB, content_nonce BLOB)`
  - `valuations(id INTEGER PRIMARY KEY, as_of_date TEXT, source TEXT, file_id INTEGER, payload_cipher BLOB, payload_nonce BLOB, ingested_at TEXT)`

Notes:
- We encrypt and store the entire SavvyTrader JSON payload in `valuations`.
- For Fidelity CSV, we encrypt and store the file content in `files.content_*` only (no separate normalized table yet).

## Encryption

- Algorithm: AES-256-GCM (`cryptography` package) with a random 12-byte nonce per row.
- Key derivation: PBKDF2-HMAC-SHA256 from a passphrase provided at runtime.
- Salt: randomly generated on first DB initialization; stored in `meta` as hex.
- Passphrase sources (in order):
  1. `MINGDOM_DB_PASSPHRASE` env var
  2. Interactive prompt (TTY only)
- Behavior if passphrase is absent and not interactive: skip DB encryption/ingest; still update canonical outputs and archive (safety + convenience for local use). A warning is printed.
- We never log or persist the passphrase.

## File Discovery and Selection

- Scan `data/import/` (files only; direct children).
- Ignore: hidden files, zero-byte files, and partial extensions: `.crdownload`, `.download`, `.part`, `.partial`, `.tmp`.
- Latest-of-each selection:
  - JSON (SavvyTrader): try to parse and use the maximum `summaryDate` in the payload; fallback to file modification time (mtime).
  - CSV (Fidelity): pick the newest by mtime.
- Deterministic tie-breaker: if equal, use lexicographically last filename.

## Import Flow

1. Discover latest JSON and CSV as above.
2. For each selected file:
   - Compute SHA256 and basic metadata.
   - Copy to canonical destination atomically:
     - JSON → `data/valuations.json`
     - CSV → `data/private/fidelity-performance.csv`
   - If a passphrase is available:
     - Initialize DB (create tables, derive key).
     - Insert a `files` row with encrypted file content (`content_cipher`, `content_nonce`).
     - For JSON, also insert a `valuations` row with the encrypted payload and detected `as_of_date`.
   - Move original file to `data/import/archive/YYYY-MM-DD/<original_name>`.

Atomic writes: write to a `*.tmp` file in the target directory then `os.replace`.

Idempotency: the `files.sha256` column is unique. Re-importing the same file will be a no-op for DB inserts; canonical outputs will still be refreshed.

## CLI Usage

Command: `python scripts/import_latest.py`

Options:
- `--dry-run` — print actions without modifying files/DB.
- `--verbose` — extra logging.

Environment:
- `MINGDOM_DB_PASSPHRASE` — optional; enables DB encryption. If not set, the script prompts (if interactive) or proceeds without DB ingestion.

## Git Hygiene

Ignored paths (see `.gitignore` updates):
- `data/import/**` and `data/import/archive/**`
- `data/localdb*`
- any temp or encrypted artifacts `data/*.tmp`, `data/*.enc`
- optional `.env.local` for local env vars

We keep `data/valuations.json` under version control (as before). `data/private/` remains ignored.

## Testing Strategy (initial)

- Unit: file discovery, latest-of-each selection (mtime and JSON max `summaryDate`), checksum dedupe, encrypt/decrypt round-trip.
- Integration: run importer in a temp dir with sample CSV/JSON to verify canonical outputs are updated and files archived.

## Future Enhancements (optional)

- Add a normalized `fidelity_monthly` table with parsed monthly returns.
- Add a `watch_imports.py` to process on file drops.
- Export `data/valuations.parquet` for faster analysis (optional).
- Key rotation and encrypted backup utility.

## Rationale Summary

- Prioritizes simplicity and local convenience; DB encryption is best-effort and optional per-run.
- Avoids committing sensitive data by default; archives retained locally and out of Git.
- Keeps existing analysis code unchanged by writing to existing canonical inputs.

