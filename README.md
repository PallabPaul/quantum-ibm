# IBM Quantum Project

A clean starter for running quantum circuits on the **IBM Quantum Platform**
with [Qiskit](https://www.ibm.com/quantum/qiskit). Credentials are kept out of
source code using a `.env` file.

> ⚠️ **SECURITY — read first.** An API key was shared in plain text while
> creating this project. Treat it as compromised: go to
> <https://quantum.ibm.com/> → **Account settings** and **delete / regenerate**
> the API key immediately, then paste the **new** key into `.env`.
> Never paste API keys into chats, screenshots, or commits.

## Project structure

```
quantum-ibm/
├── .env                 # your real credentials (git-ignored, edit this)
├── .env.example         # template to copy from
├── .gitignore           # keeps secrets & junk out of git
├── requirements.txt     # Python dependencies
├── README.md
├── docs/
│   └── shor-rsa-demo.md   # detailed walkthrough of the Shor/RSA demos
├── src/
│   ├── config.py          # loads credentials from .env
│   ├── quantum_service.py # connect to IBM Quantum
│   ├── circuits.py        # reusable quantum circuits
│   ├── shor.py            # Shor's algorithm: quantum order finding for N=15
│   └── rsa_break.py       # toy RSA broken using Shor's factors
└── examples/
    ├── save_account.py    # one-time: save credentials to disk
    ├── run_local.py       # run on local simulator (no key needed)
    ├── run_hardware.py    # run on real IBM quantum hardware
    ├── run_shor_local.py  # factor 15 with Shor (simulator)
    ├── run_rsa_break.py   # encrypt → break → decrypt end to end
    └── run_shor_hardware.py # Shor on real hardware vs. simulator
```

## Setup

From the project folder (`quantum-ibm/`):

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your NEW api key to .env
#    Open .env and replace paste_your_new_api_key_here
```

## Usage

Run the scripts as modules from the project root so imports resolve correctly.

```bash
# Test locally first — no credentials or quota used
python -m examples.run_local

# Save your IBM account once (after editing .env)
python -m examples.save_account

# Run on real quantum hardware
python -m examples.run_hardware
```

`run_local.py` should print roughly equal counts of `00` and `11` — the
signature of an entangled Bell state.

## Shor's algorithm & breaking RSA (demo)

Three scripts demonstrate, end to end, how a quantum computer factors a number
and why that breaks RSA encryption — plus an honest look at why today's hardware
is nowhere near doing it for real:

```bash
# 1. Factor 15 with Shor on the local simulator (the "weapon")
python -m examples.run_shor_local

# 2. Encrypt a message, break the key with Shor, decrypt it (the "crime")
python -m examples.run_rsa_break

# 3. Same circuit on simulator vs. real IBM hardware (the "reality check")
python -m examples.run_shor_hardware
```

The number `15` is a toy stand-in for a real ~617-digit RSA modulus; the math is
identical, just shrunk to something current hardware can attempt. For the full
explanation — the number 15, what a "period" is, each file's findings, and the
simulator-vs-hardware comparison — see
**[docs/shor-rsa-demo.md](docs/shor-rsa-demo.md)**.

## Notes

- The current IBM Quantum Platform uses the `ibm_quantum_platform` channel.
  The legacy `ibm_quantum` channel was retired in 2025.
- Hardware jobs consume your monthly runtime quota — develop with the local
  simulator, then submit to hardware when the circuit is ready.
- Add new circuits in `src/circuits.py` and reuse them across both runners.
