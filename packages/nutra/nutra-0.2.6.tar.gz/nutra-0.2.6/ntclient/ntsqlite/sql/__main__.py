"""Call this with python -m sql"""
# pylint: disable=import-error
from . import build_ntsqlite

if __name__ == "__main__":
    build_ntsqlite(verbose=True)
