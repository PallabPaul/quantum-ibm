"""One-time setup: save your IBM Quantum account to disk.

Run this once after putting your API key in .env:

    python -m examples.save_account

Afterwards, every other script can call ``get_service()`` with no token.
"""

from src.quantum_service import save_account


def main() -> None:
    save_account()
    print("IBM Quantum account saved. You can now run examples/run_hardware.py")


if __name__ == "__main__":
    main()
