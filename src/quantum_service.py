"""Connection helpers for the IBM Quantum Platform.

Wraps ``QiskitRuntimeService`` so the rest of the project does not need to
know how credentials are stored. Two ways to authenticate are supported:

1. Save the account once to disk (``save_account``) and then call
   ``get_service()`` with no arguments in every script.
2. Authenticate directly from the ``.env`` values on each run.
"""

from __future__ import annotations

from qiskit_ibm_runtime import QiskitRuntimeService

from .config import (
    IBM_QUANTUM_CHANNEL,
    IBM_QUANTUM_INSTANCE,
    IBM_QUANTUM_TOKEN,
    has_valid_token,
)


def _credentials() -> dict[str, str]:
    """Build the keyword arguments used to authenticate with IBM Quantum."""
    if not has_valid_token():
        raise ValueError(
            "IBM_QUANTUM_TOKEN is missing or still a placeholder. "
            "Edit your .env file and add your IBM Quantum API key."
        )
    creds: dict[str, str] = {
        "channel": IBM_QUANTUM_CHANNEL,
        "token": IBM_QUANTUM_TOKEN,  # type: ignore[dict-item]
    }
    if IBM_QUANTUM_INSTANCE:
        creds["instance"] = IBM_QUANTUM_INSTANCE
    return creds


def save_account(overwrite: bool = True) -> None:
    """Persist credentials to ``~/.qiskit`` so future runs need no token."""
    QiskitRuntimeService.save_account(
        set_as_default=True,
        overwrite=overwrite,
        **_credentials(),
    )


def get_service() -> QiskitRuntimeService:
    """Return an authenticated service.

    Prefers a previously saved account; falls back to the ``.env`` token.
    """
    try:
        return QiskitRuntimeService()
    except Exception:
        # No saved account found — authenticate from environment values.
        return QiskitRuntimeService(**_credentials())
