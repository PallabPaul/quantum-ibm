"""End-to-end RSA break: encrypt a secret, factor with Shor, decrypt it.

    python -m examples.run_rsa_break

Shows the full attack chain on a toy RSA key built on ``N = 15``:

    1. A keypair is created; only the PUBLIC key (N, e) is exposed.
    2. A secret message is encrypted with the public key.
    3. The attacker, holding ONLY the public key + ciphertext, runs Shor's
       algorithm to factor N, derives phi(N), and recovers the private key d.
    4. The stolen d decrypts the message — and every other message too.

Runs entirely on the local simulator. EDUCATIONAL ONLY — N=15 is not secure.
"""

from __future__ import annotations

from src.rsa_break import build_keypair, break_public_key, decrypt, encrypt

SECRET_MESSAGE = 2  # any integer in 0..14 (N = 15 only holds one small number)


def main() -> None:
    print("=" * 64)
    print("BREAKING RSA WITH SHOR — encrypt, factor, decrypt")
    print("=" * 64)

    # --- 1. Legitimate party builds a keypair; d stays secret. -----------
    key = build_keypair(p=3, q=5, e=7)
    print("\n[owner] builds a keypair on N = p*q = 3*5 = 15")
    print(f"[owner] PUBLISHES public key (N, e) = {key.public_key}")
    print(f"[owner] KEEPS SECRET private key d = {key.d}  (and primes 3, 5)")

    # --- 2. Someone encrypts a secret message with the public key. --------
    ciphertext = encrypt(SECRET_MESSAGE, key.public_key)
    print(f"\n[sender] secret message m = {SECRET_MESSAGE}")
    print(f"[sender] encrypts: c = m^e mod N = {ciphertext}")
    print(f"[sender] sends only c = {ciphertext} over the wire")

    # --- 3. Attacker sees ONLY (N, e) and c. Runs Shor to factor N. -------
    print(f"\n[attacker] intercepts c = {ciphertext}, knows public (N, e) = {key.public_key}")
    print("[attacker] runs Shor's algorithm on N = 15 (local simulator)...")
    brk = break_public_key(key.public_key, seed=1)
    p, q = brk.factors
    print(f"[attacker] Shor found period r = {brk.shor.period} (base a = {brk.shor.a})")
    print(f"[attacker] factors: N = {p} x {q}")
    print(f"[attacker] phi(N) = ({p}-1)*({q}-1) = {brk.phi}")
    print(f"[attacker] derives private key d = e^-1 mod phi = {brk.recovered_d}")

    # --- 4. Attacker decrypts the message with the stolen key. -----------
    cracked = decrypt(ciphertext, brk.recovered_d, brk.public_key[0])
    print(f"\n[attacker] decrypts: m = c^d mod N = {cracked}")
    verdict = "MATCH — message stolen!" if cracked == SECRET_MESSAGE else "mismatch"
    print(f">>> recovered message = {cracked}   (original was {SECRET_MESSAGE}) -> {verdict}")

    # --- It's a master key: every message in the space round-trips. -------
    n = brk.public_key[0]
    all_ok = all(
        decrypt(encrypt(m, key.public_key), brk.recovered_d, n) == m for m in range(n)
    )
    print(f">>> stolen d decrypts EVERY message 0..{n - 1}: {all_ok}")

    print("\n" + "-" * 64)
    print("Honest footnotes:")
    print("  * For N=15 the math forces d == e (a quirk of this tiny modulus);")
    print("    at real key sizes d != e. What matters is that d was DERIVED")
    print("    from the secret factors — unobtainable without Shor.")
    print("  * Real RSA uses 2048+ bit N. Breaking that needs millions of")
    print("    error-corrected qubits that do not exist yet. This is the")
    print("    *mechanism*, shown at toy scale. PQC (ML-KEM/ML-DSA) is the fix.")
    print("-" * 64)


if __name__ == "__main__":
    main()
