from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from scripts.crypto_db import get_passphrase, open_encrypted_db


DB_PATH = Path("data/localdb.sqlite3")


def cmd_init(verbose: bool) -> int:
    passphrase = get_passphrase()
    if not passphrase:
        print("No passphrase provided. Set MINGDOM_DB_PASSPHRASE or run interactively to enter one.", file=sys.stderr)
        return 2
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    handle = open_encrypted_db(str(DB_PATH), passphrase)
    # touch DB and close
    handle.conn.close()
    if verbose:
        print(f"Initialized encrypted DB at {DB_PATH}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Local DB utilities")
    parser.add_argument("action", nargs="?", default="init", choices=["init"], help="Action to run (default: init)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.action == "init":
        raise SystemExit(cmd_init(args.verbose))


if __name__ == "__main__":
    main()

