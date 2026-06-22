# Breaking RSA with Shor's Algorithm — A Detailed Walkthrough

This document explains, in depth, what the three demo scripts in this project do,
why the number **15** is used, what a **period** is, and what the **simulator vs.
real IBM hardware** comparison actually proves.

The whole project tells **one story in three chapters**:

> Quantum computers *can* break the encryption that protects the internet — but
> **not yet** — so the rational response is to migrate to quantum-proof
> ("post-quantum") cryptography *now*, before the hardware catches up.

---

## Table of contents

1. [Background: why factoring breaks RSA](#1-background-why-factoring-breaks-rsa)
2. [Why the number 15?](#2-why-the-number-15)
3. [What is a "period"?](#3-what-is-a-period)
4. [From period to broken key — the full chain](#4-from-period-to-broken-key--the-full-chain)
5. [File 1 — `run_shor_local.py` (the weapon)](#5-file-1--run_shor_localpy-the-weapon)
6. [File 2 — `run_rsa_break.py` (the crime)](#6-file-2--run_rsa_breakpy-the-crime)
7. [File 3 — `run_shor_hardware.py` (the reality check)](#7-file-3--run_shor_hardwarepy-the-reality-check)
8. [Simulator vs. real hardware](#8-simulator-vs-real-hardware)
9. [The conclusion: why this argues for PQC](#9-the-conclusion-why-this-argues-for-pqc)
10. [How to run everything](#10-how-to-run-everything)

---

## 1. Background: why factoring breaks RSA

RSA encryption — the math protecting most of the internet — is locked by a single
public number `N` that is secretly the product of two large prime numbers:

```
N = p × q
```

It is *easy* to multiply `p` and `q` together, but *classically infeasible* to go
backwards and recover `p` and `q` from a large `N`. That one-way difficulty is the
entire foundation of RSA's security. Everything secret in an RSA key can be
reconstructed the moment you know `p` and `q`.

**Shor's algorithm** is a quantum algorithm that factors `N` efficiently. It does
not break RSA by brute force; instead it finds the **period** (also called the
**order**) of a related repeating sequence, and that period hands you the factors.

---

## 2. Why the number 15?

`15` is the "Hello World" of quantum factoring: the smallest number that is a
product of two distinct odd primes (`3 × 5`), so it actually exercises the full
algorithm.

It is also *deliberately* tiny because **today's real quantum hardware can barely
factor it**. The size gap between this demo and real encryption is staggering:

| | Bits | Decimal digits | Example |
|---|---|---|---|
| **This demo** | 4 bits | 2 digits | `15` |
| **Real RSA today** | 2048 bits | ~617 digits | a 617-digit number |
| **High-security RSA** | 4096 bits | ~1,234 digits | twice as long again |

A real RSA modulus is **~617 digits long** — it would fill a paragraph. Ours is two
characters. The *algorithm is identical* at both scales; only the number of qubits
changes. That is the point: the mechanism you see here is the real one, just shrunk
to something current hardware can attempt.

**Hardware reality:** factoring `15` needs ~8 working qubits. Factoring a real
2048-bit key is estimated to need on the order of **~20 million** noisy physical
qubits (or several thousand *perfect*, error-corrected ones). Today's best machines
have ~1,000 noisy qubits — roughly a **20,000× gap**.

---

## 3. What is a "period"?

Pick a base `a` that shares no factors with `N`. For the demos we use `a = 7` and
`N = 15`. Now keep multiplying by `a`, taking the remainder mod `15` each time:

| `x` | `7^x` | `7^x mod 15` |
|----|-------|--------------|
| 0  | 1     | **1** |
| 1  | 7     | 7 |
| 2  | 49    | 4 |
| 3  | 343   | 13 |
| 4  | 2401  | **1** ← back to 1! |
| 5  | 16807 | 7 |
| 6  | …     | 4 |
| 7  | …     | 13 |
| 8  | …     | **1** ← again |

The remainders cycle: `1 → 7 → 4 → 13 → 1 → 7 → 4 → 13 → …`

It returns to `1` every **4 steps**. That repeat length is the **period**:

```
r = 4
```

Formally, `r` is the smallest positive power where `a^r ≡ 1 (mod N)`. Here
`7^4 = 2401 = 160 × 15 + 1`, so `7^4 mod 15 = 1`. ✓

**Finding `r` is the hard part.** For `N = 15` you can read it off a tiny table, but
for a 617-digit number this cycle is astronomically long and classically infeasible
to find. The quantum computer finds it *without walking the cycle* — see
[Section 8](#8-simulator-vs-real-hardware).

---

## 4. From period to broken key — the full chain

Once you know `r = 4`, everything else is easy gradeschool arithmetic:

```
r = 4  →  factors 3, 5  →  φ(N) = 8  →  private key d  →  decrypt anything
```

### Step 1 — Period → factors

`r` is even, so compute `a^(r/2) = 7^2 = 49`:

- `gcd(49 − 1, 15) = gcd(48, 15) = 3`
- `gcd(49 + 1, 15) = gcd(50, 15) = 5`

**Factors recovered: 3 and 5.** This is the step quantum makes possible.

### Step 2 — Factors → φ(N) (the secret "trapdoor")

RSA has a secret quantity `φ(N)` (Euler's totient) that *only* someone who knows the
factors can compute:

```
φ(N) = (p − 1)(q − 1) = (3 − 1)(5 − 1) = 2 × 4 = 8
```

From the public `N = 15` alone, you cannot get `φ`. From the factors, it is instant.
**This is the whole game.**

### Step 3 — φ(N) → private key d

With a public exponent `e = 7`, the private key `d` is defined as the modular
inverse of `e`:

```
d = e⁻¹ mod φ(N) = 7⁻¹ mod 8 = 7
```

(because `7 × 7 = 49 = 48 + 1 ≡ 1 (mod 8)`)

### Step 4 — d → decrypt anything

- **Encrypt** a secret message `m = 2` with the public key: `c = m^e mod N = 2^7 mod 15 = 8`
- **Decrypt** with the stolen `d`: `m = c^d mod N = 8^7 mod 15 = 2` ✓

The attacker started with **only public data** (`N`, `e`, ciphertext `c`) and
recovered the secret — because quantum handed them the one number, `r`, that
unlocks the entire chain.

> **Note on this toy:** for `N = 15` the math happens to force `d == e`. That is a
> quirk of this tiny modulus; at real key sizes `d ≠ e`. What matters is that `d`
> was *derived from the secret factors*, which are unobtainable without Shor.

---

## 5. File 1 — `run_shor_local.py` (the weapon)

**Command:** `python -m examples.run_shor_local`
**Code:** [`examples/run_shor_local.py`](../examples/run_shor_local.py) using
[`src/shor.py`](../src/shor.py)

**What it does:** Runs Shor's quantum order-finding on a *local simulator* to factor
`15`, then prints the factors and the PQC tie-in.

**What it proves:** A quantum algorithm can find the period `r = 4`, which yields the
secret factors `3 × 5`. This is the core "RSA lock-pick."

**Representative output (simulator, ideal):**

```
Measured phases (top 5 by frequency):
  phase ~= 0.7500   (265 shots)
  phase ~= 0.5000   (264 shots)
  phase ~= 0.2500   (257 shots)
  phase ~= 0.0000   (238 shots)

recovered a working period r = 4
>>> FACTORS FOUND: 15 = 3 x 5   (method: quantum)
```

The four phases `0.00, 0.25, 0.50, 0.75` are the multiples of `1/4` — the quantum
computer announcing "the period is 4."

---

## 6. File 2 — `run_rsa_break.py` (the crime)

**Command:** `python -m examples.run_rsa_break`
**Code:** [`examples/run_rsa_break.py`](../examples/run_rsa_break.py) using
[`src/rsa_break.py`](../src/rsa_break.py) + `src/shor.py`

**What it does:** Plays out the complete attack end to end:

1. An owner builds a keypair on `N = 15` and publishes only the public key `(15, 7)`.
2. A sender encrypts a secret message `m = 2` → ciphertext `c = 8`.
3. An attacker, holding **only** the public key and `c`, runs Shor to factor `N`,
   derives `φ(N)`, and reconstructs the private key `d`.
4. The stolen `d` decrypts the message — and every other message too.

**What it proves:** The factors from File 1 actually let you **decrypt a real secret
from public information alone**. It connects "found the primes" to "read your data."

**Representative output:**

```
[owner]    PUBLISHES public key (N, e) = (15, 7)
[sender]   secret message m = 2  →  c = 8
[attacker] runs Shor → factors: N = 3 x 5
[attacker] phi(N) = 8  →  private key d = 7
[attacker] decrypts: m = c^d mod N = 2
>>> recovered message = 2   (original was 2) -> MATCH — message stolen!
>>> stolen d decrypts EVERY message 0..14: True
```

Recovering the factors yields a **master key** for the entire message space, not a
one-off lucky guess.

---

## 7. File 3 — `run_shor_hardware.py` (the reality check)

**Command:** `python -m examples.run_shor_hardware`
**Code:** [`examples/run_shor_hardware.py`](../examples/run_shor_hardware.py)

**What it does:** Runs the *exact same* order-finding circuit from File 1 on a **real
IBM quantum computer**, side by side with the simulator, then tries to factor from
the (noisy) hardware result.

**What it proves:** Today's real hardware is so error-prone it can *barely* factor
`15`. The threat is **not here yet**.

**Representative output (real `ibm_fez` run):**

```
Local simulator (ideal):
  phase 0.000 |  272 ###########
  phase 0.250 |  259 ##########
  phase 0.500 |  223 #########
  phase 0.750 |  270 ###########

Transpiled circuit depth: 2236 (sim depth: 6)
Using real backend: ibm_fez

Real hardware (ibm_fez, noisy):
  phase 0.000 |  137 #####
  phase 0.125 |  125 #####
  phase 0.250 |  139 #####
  phase 0.375 |  152 ######   ← noise (tallest bar, but invalid period!)
  phase 0.500 |  128 #####
  phase 0.625 |  104 ####
  phase 0.750 |  106 ####
  phase 0.875 |  133 #####
```

Read the hardware numbers honestly:

- The four "correct" phases (`0.00, 0.25, 0.50, 0.75`) hold **~510 shots (49.8%)**.
- The four pure-noise phases hold **~514 shots (50.2%)**.
- That is essentially a **coin flip** — the quantum signal was almost entirely
  washed out.

It still printed "factors found" only because the **classical post-processing is
robust**: it tries candidate phases in order, rejects the noise bin `0.375` (`3/8`,
which gives trivial factors), and lands on `0.25` (`1/4 → r = 4`). The *classical
scaffolding* did the heavy lifting; the quantum hardware barely peeked above the
noise floor for a number as tiny as 15.

---

## 8. Simulator vs. real hardware

The single most important number in the hardware run is the **circuit depth**:

```
Transpiled circuit depth: 2236   (simulator depth: 6)
```

Your abstract circuit is **6 layers** of gates. But a real chip cannot run it
directly — it must be **transpiled** to fit the hardware, which exploded it to
**2,236 layers**. Two reasons:

1. **Limited connectivity.** The algorithm wants distant qubits to interact, but on a
   real chip they are not physically adjacent. The compiler inserts long chains of
   **SWAP gates** (3 two-qubit gates each) to shuffle states across the chip.
2. **Native gate set.** Friendly high-level gates get rewritten into the chip's
   actual basis gates, multiplying the count.

**Why depth is fatal — errors compound.** Each two-qubit gate has roughly a ~1% error
rate, and errors *multiply*:

```
fidelity ≈ 0.99^(number of 2-qubit gates)
0.99^300 ≈ 0.05      0.99^500 ≈ 0.007
```

By the end of a circuit this deep, essentially none of the original quantum signal
survives. A fully decohered quantum state collapses to the **maximally mixed state**:
every outcome equally likely. That is exactly why the hardware histogram is nearly
**flat** — the chip was effectively returning coin flips.

| Aspect | Local simulator | Real IBM hardware |
|---|---|---|
| Qubits | Perfect, simulated | Real atoms, noisy |
| Circuit depth | 6 | ~2,240 (after transpile) |
| Histogram | 4 clean peaks | Near-flat, smeared |
| Signal vs. noise | 100% signal | ~50% signal / ~50% noise |
| Factoring | Always succeeds | Sometimes; rescued by classical math |
| Error correction | N/A (ideal) | None (NISQ era) |

This is not the hardware being "broken" — it is exactly what **NISQ-era** (Noisy
Intermediate-Scale Quantum) hardware does: no error correction, so noise accumulates
unchecked. For a number as trivial as 15, noise already swamps signal.

### How the quantum step finds `r` at all

1. It puts *all* values of `x` into superposition at once.
2. It computes `a^x mod N` for all of them simultaneously (quantum parallelism).
3. The **inverse Quantum Fourier Transform** acts like a prism that detects the
   *repeat frequency* of the cycle — analogous to how a Fourier transform finds the
   pitch in a sound wave.
4. Measuring yields phases at multiples of `1/r`. Continued fractions read `r` back
   out (e.g. `0.25 → 1/4 → r = 4`).

---

## 9. The conclusion: why this argues for PQC

| File | Proves | One word |
|---|---|---|
| `run_shor_local` | A quantum computer can find the secret factors | **Weapon** |
| `run_rsa_break` | Those factors decrypt a real secret message | **Crime** |
| `run_shor_hardware` | Real hardware is still far too weak to do this for real | **Reality** |

- Files 1 + 2 (simulator): the attack **absolutely works in principle**.
- File 3 (real chip): today's hardware **cannot pull it off** beyond toy numbers.
- **Therefore:** the danger is *coming, not here* — which is the entire reason to
  migrate to **post-quantum cryptography** *before* the machines get good enough.

This is the "harvest-now, decrypt-later" urgency: an attacker can record encrypted
traffic *today* and decrypt it *years later* once a large fault-tolerant quantum
computer exists. Long-lived secrets are exposed now even though the computer does not
exist yet. The NIST-standardized PQC algorithms — **ML-KEM** (key exchange),
**ML-DSA** and **SLH-DSA** (signatures) — use lattice/hash math that Shor's algorithm
cannot crack, and run on ordinary classical computers.

---

## 10. How to run everything

From the project root, with the virtual environment activated:

```bash
source .venv/bin/activate

# 1. Factor 15 with Shor on the local simulator (instant, offline)
python -m examples.run_shor_local

# 2. Full attack: encrypt a message, break the key, decrypt it (instant, offline)
python -m examples.run_rsa_break

# 3. Same circuit on simulator vs. real IBM hardware (uses quota, may queue)
python -m examples.run_shor_hardware
```

Files 1 and 2 need no credentials. File 3 requires a valid IBM Quantum token in
`.env` and consumes your runtime quota; it may sit in a queue before running.

> **Honest caveat throughout:** these demos show the *mechanism* at toy scale. The
> modular-multiplication circuit is hand-compiled for `N = 15`. Breaking real
> RSA-2048 needs millions of error-corrected qubits that do not exist yet.
