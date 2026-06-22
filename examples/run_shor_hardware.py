"""Run Shor's order-finding on REAL IBM hardware and compare to the simulator.

    python -m examples.run_shor_hardware

Submits the SAME order-finding circuit to (1) the local simulator and (2) the
least-busy real IBM quantum computer, then prints both phase distributions side
by side. The point is to SEE what today's hardware is really like: noise smears
the clean ``k/4`` peaks, so factoring from hardware results often fails and
needs several runs. That honest contrast is the lesson.

Requires a valid IBM Quantum token (see README). Consumes your runtime quota and
may sit in a queue before running.
"""

from __future__ import annotations

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler

from src.shor import (
    N,
    factors_from_phases,
    measure_phases,
    order_finding_circuit,
    phases_from_counts,
)
from src.quantum_service import get_service

# Fewer counting qubits => a much shallower circuit that survives noise better.
# 3 bits still resolves the quarters (0, 1/4, 1/2, 3/4) needed for a = 7.
A = 7
N_COUNT = 3
SHOTS = 1024


def _print_phases(title: str, phases: dict[float, int]) -> None:
    total = sum(phases.values()) or 1
    print(f"\n{title}")
    for phase, freq in sorted(phases.items()):
        bar = "#" * round(40 * freq / total)
        print(f"  phase {phase:.3f} | {freq:4d} {bar}")


def main() -> None:
    print("=" * 64)
    print("SHOR ORDER-FINDING: local simulator vs. real IBM hardware")
    print("=" * 64)
    print(f"Factoring N = {N}, base a = {A}, counting qubits = {N_COUNT}")

    # --- 1. Ideal reference run on the local simulator. ------------------
    sim_phases = measure_phases(A, n_count=N_COUNT, shots=SHOTS)
    _print_phases("Local simulator (ideal):", sim_phases)

    # --- 2. Real hardware run. ------------------------------------------
    service = get_service()
    backend = service.least_busy(operational=True, simulator=False)
    print(f"\nUsing real backend: {backend.name}")

    qc = order_finding_circuit(A, n_count=N_COUNT)
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pass_manager.run(qc)
    print(f"Transpiled circuit depth: {isa_circuit.depth()} (sim depth: {qc.depth()})")

    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=SHOTS)
    print(f"Submitted job {job.job_id()} — may queue; waiting for results...")

    hw_counts = job.result()[0].data.c.get_counts()
    hw_phases = phases_from_counts(hw_counts, N_COUNT)
    _print_phases(f"Real hardware ({backend.name}, noisy):", hw_phases)

    # --- 3. Try to factor from the (noisy) hardware result. -------------
    r, phase, factors = factors_from_phases(A, hw_phases)
    print("\n" + "-" * 64)
    if factors is not None:
        p, q = factors
        print(f">>> Hardware result SUCCEEDED: period r = {r} -> {N} = {p} x {q}")
        print("    The signal survived the noise this time.")
    else:
        print(">>> Hardware result did NOT yield factors this run.")
        print("    Noise smeared the peaks so continued fractions failed.")
        print("    This is normal for NISQ-era hardware — just run it again.")
    print("-" * 64)
    print("Takeaway: the simulator shows the clean ideal; the real chip shows")
    print("today's noise. Reliable factoring still needs error correction.")


if __name__ == "__main__":
    main()
