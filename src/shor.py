"""Shor's algorithm — quantum order finding to factor ``N = 15``.

This is the canonical "RSA-killer" demonstration. Factoring is the hard problem
RSA encryption relies on: it is easy to multiply two primes ``p * q = N`` but
classically infeasible to recover ``p`` and ``q`` from a large ``N``. Shor's
algorithm finds the *period* (order) of ``a^x mod N`` on a quantum computer,
and that period reveals the factors — collapsing RSA's security.

The modular-multiplication circuit here is hand-compiled for ``N = 15`` (the
standard textbook case). Compiling it for arbitrary ``N`` is the genuinely hard
engineering part, and is why real hardware can still only factor toy numbers.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from fractions import Fraction

from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qiskit.primitives import StatevectorSampler

#: The number we factor. ``15 = 3 x 5`` — a baby stand-in for an RSA modulus.
N = 15

#: Bases coprime to 15 that have a known, hand-compiled modular-mult circuit.
VALID_BASES = (2, 4, 7, 8, 11, 13)


@dataclass
class ShorResult:
    """Outcome of one factoring attempt."""

    n: int
    a: int
    success: bool
    factors: tuple[int, int] | None
    period: int | None
    phase: float | None
    method: str  # "quantum" or "classical-gcd"
    phase_counts: dict[float, int] = field(default_factory=dict)


def _controlled_amod15(a: int, power: int) -> Gate:
    """Return a controlled gate computing ``|y> -> |a^power * y mod 15>``.

    These swap/X sequences are the standard textbook compilation of modular
    multiplication by ``a`` on a 4-qubit register (enough to hold 0..15).
    """
    if a not in VALID_BASES:
        raise ValueError(f"'a' must be one of {VALID_BASES}, got {a}")
    u = QuantumCircuit(4)
    for _ in range(power):
        if a in (2, 13):
            u.swap(2, 3)
            u.swap(1, 2)
            u.swap(0, 1)
        if a in (7, 8):
            u.swap(0, 1)
            u.swap(1, 2)
            u.swap(2, 3)
        if a in (4, 11):
            u.swap(1, 3)
            u.swap(0, 2)
        if a in (7, 11, 13):
            for q in range(4):
                u.x(q)
    gate = u.to_gate()
    gate.name = f"{a}^{power} mod 15"
    return gate.control()


def _inverse_qft(n: int) -> QuantumCircuit:
    """Build an ``n``-qubit inverse Quantum Fourier Transform."""
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc


def order_finding_circuit(a: int, n_count: int = 8) -> QuantumCircuit:
    """Build the phase-estimation circuit that finds the order of ``a mod 15``.

    ``n_count`` counting qubits set the phase precision; 4 work qubits hold the
    register being multiplied. More counting qubits give sharper peaks.
    """
    qc = QuantumCircuit(n_count + 4, n_count)

    # Counting register into uniform superposition.
    for q in range(n_count):
        qc.h(q)

    # Work register initialised to |1> (the multiplicative identity).
    qc.x(n_count + 3)

    # Controlled modular exponentiation: a^(2^q) for each counting qubit.
    for q in range(n_count):
        qc.append(
            _controlled_amod15(a, 2**q),
            [q] + [n_count + i for i in range(4)],
        )

    # Inverse QFT turns the accumulated phase into a readable bitstring.
    qc.append(_inverse_qft(n_count), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc


def measure_phases(a: int, n_count: int = 8, shots: int = 1024) -> dict[float, int]:
    """Run order finding on the local simulator; return phase -> shot counts.

    Each measured bitstring ``k`` corresponds to a phase ``k / 2^n_count`` that
    approximates ``s / r`` for some integer ``s`` and the order ``r``.
    """
    qc = order_finding_circuit(a, n_count)
    sampler = StatevectorSampler()
    counts = sampler.run([qc], shots=shots).result()[0].data.c.get_counts()
    return phases_from_counts(counts, n_count)


def phases_from_counts(counts: dict[str, int], n_count: int) -> dict[float, int]:
    """Convert measured bitstring counts into a ``phase -> shot-count`` map.

    Works for counts from any backend (local simulator or real hardware), so
    the same classical post-processing applies to both.
    """
    phases: dict[float, int] = {}
    for bitstring, freq in counts.items():
        phase = int(bitstring, 2) / (2**n_count)
        phases[phase] = phases.get(phase, 0) + freq
    return phases


def factors_from_phases(
    a: int, phases: dict[float, int], n: int = N
) -> tuple[int | None, float | None, tuple[int, int] | None]:
    """Recover ``(period, phase, factors)`` from a phase map, best phase first.

    Returns ``(None, None, None)`` if no measured phase yields a usable period
    — common on noisy hardware, where the clean peaks get smeared.
    """
    for phase, _freq in sorted(phases.items(), key=lambda kv: -kv[1]):
        r = candidate_period(phase, n)
        factors = factors_from_period(a, r, n)
        if factors is not None:
            return r, phase, factors
    return None, None, None


def candidate_period(phase: float, n: int = N) -> int | None:
    """Recover a candidate order ``r`` from a phase via continued fractions."""
    if phase == 0:
        return None
    return Fraction(phase).limit_denominator(n).denominator


def factors_from_period(a: int, r: int | None, n: int = N) -> tuple[int, int] | None:
    """Turn a period ``r`` into non-trivial factors of ``n``, if possible.

    Requires ``r`` even and ``a^(r/2) != -1 (mod n)``; then a factor is
    ``gcd(a^(r/2) ± 1, n)``.
    """
    if not r or r % 2 != 0:
        return None
    x = pow(a, r // 2, n)
    if x == n - 1:  # a^(r/2) ≡ -1 (mod n): yields only trivial factors
        return None
    for candidate in (math.gcd(x - 1, n), math.gcd(x + 1, n)):
        if candidate not in (1, n):
            return candidate, n // candidate
    return None


def factor(
    a: int | None = None,
    *,
    n_count: int = 8,
    shots: int = 1024,
    max_attempts: int = 5,
    seed: int | None = None,
) -> ShorResult:
    """Attempt to factor ``N = 15`` with Shor's algorithm.

    If ``a`` is given, only that base is tried. Otherwise random coprime bases
    are tried (up to ``max_attempts``) until the quantum step yields factors.
    """
    rng = random.Random(seed)
    if a is not None:
        bases = [a]
    else:
        shuffled = rng.sample(VALID_BASES, k=len(VALID_BASES))
        bases = shuffled[:max_attempts]

    last_counts: dict[float, int] = {}
    for base in bases:
        # Lucky classical shortcut: the base already shares a factor with N.
        shared = math.gcd(base, N)
        if shared not in (1, N):
            return ShorResult(N, base, True, (shared, N // shared), None, None, "classical-gcd")

        counts = measure_phases(base, n_count, shots)
        last_counts = counts
        r, phase, factors = factors_from_phases(base, counts)
        if factors is not None:
            return ShorResult(N, base, True, factors, r, phase, "quantum", counts)

    return ShorResult(N, bases[0], False, None, None, None, "quantum", last_counts)
