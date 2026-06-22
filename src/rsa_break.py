"""Toy RSA on ``N = 15`` to show how Shor's factoring breaks encryption.

EDUCATIONAL ONLY. ``N = 15`` is a 4-bit modulus — this is a teaching toy, not
real cryptography. Never use any of this to protect real data. Its only purpose
is to demonstrate the chain:

    period r  ->  factors p, q  ->  phi(N)  ->  private key d  ->  decrypt

The quantum factoring step lives in :mod:`src.shor`; this module is the purely
classical RSA scaffolding that turns "factors found" into "message decrypted".
"""

from __future__ import annotations

from dataclasses import dataclass
from math import gcd

from .shor import N as SHOR_N
from .shor import ShorResult, factor


@dataclass
class RSAKeypair:
    """A toy RSA keypair. ``d`` (and the primes) are the secret half."""

    n: int  # public modulus
    e: int  # public exponent
    d: int  # PRIVATE exponent
    p: int  # PRIVATE prime
    q: int  # PRIVATE prime

    @property
    def public_key(self) -> tuple[int, int]:
        """The half an attacker legitimately sees: ``(N, e)``."""
        return (self.n, self.e)


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclid: return ``(g, x, y)`` with ``a*x + b*y == g``."""
    if b == 0:
        return (a, 1, 0)
    g, x, y = _egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def modinv(a: int, m: int) -> int:
    """Modular inverse of ``a`` mod ``m`` (raises if none exists)."""
    g, x, _ = _egcd(a % m, m)
    if g != 1:
        raise ValueError(f"no modular inverse for {a} mod {m}")
    return x % m


def totient(p: int, q: int) -> int:
    """Euler totient for a product of two primes: ``phi = (p-1)(q-1)``."""
    return (p - 1) * (q - 1)


def build_keypair(p: int, q: int, e: int = 7) -> RSAKeypair:
    """Construct a keypair from two primes and a public exponent ``e``."""
    n = p * q
    phi = totient(p, q)
    if gcd(e, phi) != 1:
        raise ValueError(f"e={e} is not coprime with phi(N)={phi}")
    d = modinv(e, phi)
    return RSAKeypair(n=n, e=e, d=d, p=p, q=q)


def encrypt(m: int, public_key: tuple[int, int]) -> int:
    """RSA encrypt a single number: ``c = m^e mod N``."""
    n, e = public_key
    if not 0 <= m < n:
        raise ValueError(f"message {m} must satisfy 0 <= m < N={n}")
    return pow(m, e, n)


def decrypt(c: int, d: int, n: int) -> int:
    """RSA decrypt a single number: ``m = c^d mod N``."""
    return pow(c, d, n)


@dataclass
class BreakResult:
    """Everything an attacker reconstructs from only the public key."""

    public_key: tuple[int, int]
    factors: tuple[int, int]
    phi: int
    recovered_d: int
    shor: ShorResult


def break_public_key(public_key: tuple[int, int], *, seed: int | None = None) -> BreakResult:
    """Recover the private exponent ``d`` from a public key alone.

    Uses Shor's algorithm (quantum order finding on the local simulator) to
    factor ``N``, then derives ``phi(N)`` and ``d`` with classical arithmetic.
    """
    n, e = public_key
    if n != SHOR_N:
        raise ValueError(
            f"the hand-compiled Shor circuit only factors N={SHOR_N}, got N={n}"
        )

    shor = factor(seed=seed)
    if not shor.success or shor.factors is None:
        raise RuntimeError("Shor step failed to find factors; re-run the demo")

    p, q = shor.factors
    phi = totient(p, q)
    recovered_d = modinv(e, phi)
    return BreakResult((n, e), (p, q), phi, recovered_d, shor)
