"""End-to-end Shor's algorithm demo on the local simulator.

    python -m examples.run_shor_local

Factors ``N = 15`` (a baby "RSA modulus", 3 x 5) using quantum order finding,
then explains why this is the threat that post-quantum cryptography defends
against. No API key or quota required — it runs on the local simulator.
"""

from __future__ import annotations

from src.shor import N, factor


def main() -> None:
    a = 7  # classic choice: the order of 7^x mod 15 is 4

    print("=" * 64)
    print("SHOR'S ALGORITHM — factoring a baby RSA modulus")
    print("=" * 64)
    print(f"Public modulus N = {N}   (secretly 3 x 5)")
    print("RSA's security assumes nobody can recover those secret factors.")
    print("Classically, factoring a 2048-bit N is infeasible.")
    print(f"\nRunning quantum order finding with base a = {a} ...\n")

    result = factor(a=a)

    print("Measured phases (top 5 by frequency):")
    for phase, freq in sorted(result.phase_counts.items(), key=lambda kv: -kv[1])[:5]:
        print(f"  phase ~= {phase:.4f}   ({freq} shots)")

    if result.success and result.factors and result.period:
        p, q = result.factors
        print("\nClassical post-processing (continued fractions):")
        print(f"  recovered a working period r = {result.period}")
        print(f"  a^(r/2) mod N = {pow(a, result.period // 2, N)}")
        print(f"\n>>> FACTORS FOUND: {N} = {p} x {q}   (method: {result.method})")
        print(">>> An RSA key built on this modulus would now be recoverable.")
    else:
        print("\nNo factors this run (measurement landed on phase 0).")
        print("Order finding is probabilistic — just re-run the demo.")

    print("\n" + "-" * 64)
    print("Why this matters (the PQC tie-in):")
    print("  RSA/ECC are secure ONLY because factoring / discrete-log are")
    print("  classically hard. A large fault-tolerant quantum computer running")
    print("  THIS algorithm breaks them. Post-quantum cryptography (ML-KEM,")
    print("  ML-DSA) swaps in lattice/hash math that Shor cannot crack.")
    print("  Caveat: real hardware today can still only factor toy numbers.")
    print("-" * 64)


if __name__ == "__main__":
    main()
