"""Loads IBM Quantum credentials from environment variables / .env file.

Credentials are read from a local ``.env`` file (see ``.env.example``) so that
secrets never live in source code. Import the values from here instead of
calling ``os.getenv`` throughout the project.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

# Load variables from a local .env file if present. Real environment
# variables always take precedence over values in the file.
load_dotenv()

IBM_QUANTUM_TOKEN: str | None = os.getenv("IBM_QUANTUM_TOKEN")
IBM_QUANTUM_CHANNEL: str = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum_platform")
IBM_QUANTUM_INSTANCE: str | None = os.getenv("IBM_QUANTUM_INSTANCE")

_PLACEHOLDERS = {"", "paste_your_new_api_key_here", "your_api_key_here"}


def has_valid_token() -> bool:
    """Return True if a non-placeholder API token has been configured."""
    return IBM_QUANTUM_TOKEN is not None and IBM_QUANTUM_TOKEN not in _PLACEHOLDERS
