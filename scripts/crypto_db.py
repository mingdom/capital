from __future__ import annotations

import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


KDF_ITERATIONS = 200_000
SALT_META_KEY = "kdf_salt"
SCHEMA_VERSION = "1"


@dataclass
class DBHandle:
    conn: sqlite3.Connection
    aesgcm: AESGCM
    salt: bytes


def _ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            source TEXT,
            original_name TEXT,
            path TEXT,
            sha256 TEXT UNIQUE,
            size INTEGER,
            mtime REAL,
            imported_at TEXT,
            status TEXT,
            archive_path TEXT,
            notes TEXT,
            content_cipher BLOB,
            content_nonce BLOB
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS valuations (
            id INTEGER PRIMARY KEY,
            as_of_date TEXT,
            source TEXT,
            file_id INTEGER,
            payload_cipher BLOB,
            payload_nonce BLOB,
            ingested_at TEXT,
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
        """
    )
    # Track schema version
    cur.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)",
        ("schema_version", SCHEMA_VERSION),
    )
    conn.commit()


def _get_or_create_salt(conn: sqlite3.Connection) -> bytes:
    cur = conn.cursor()
    cur.execute("SELECT value FROM meta WHERE key = ?", (SALT_META_KEY,))
    row = cur.fetchone()
    if row and row[0]:
        return bytes.fromhex(row[0])
    salt = os.urandom(16)
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES(?, ?)", (SALT_META_KEY, salt.hex()))
    conn.commit()
    return salt


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(passphrase.encode("utf-8"))


def get_passphrase() -> Optional[str]:
    env = os.getenv("MINGDOM_DB_PASSPHRASE")
    if env:
        return env
    # Interactive prompt fallback
    if sys.stdin.isatty():
        try:
            import getpass

            return getpass.getpass("Enter local DB passphrase (leave blank to skip DB): ") or None
        except Exception:
            return None
    return None


def open_encrypted_db(db_path: str, passphrase: str) -> DBHandle:
    conn = sqlite3.connect(db_path)
    _ensure_schema(conn)
    salt = _get_or_create_salt(conn)
    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    # Pragmas for better durability/perf at our scale
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    conn.commit()
    return DBHandle(conn=conn, aesgcm=aesgcm, salt=salt)


def encrypt_bytes(handle: DBHandle, data: bytes) -> Tuple[bytes, bytes]:
    nonce = os.urandom(12)
    cipher = handle.aesgcm.encrypt(nonce, data, associated_data=None)
    return cipher, nonce


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

