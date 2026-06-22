"""Run the Bell-state circuit on real IBM Quantum hardware.

    python -m examples.run_hardware

Requires a valid API key in .env (and ideally running save_account first).
This consumes your IBM Quantum runtime quota, so test with run_local first.
"""

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler

from src.circuits import bell_state
from src.quantum_service import get_service


def main() -> None:
    service = get_service()

    # Pick the least busy real (non-simulator) device that is online.
    backend = service.least_busy(operational=True, simulator=False)
    print(f"Using backend: {backend.name}")

    # Transpile the circuit to the backend's native gates and qubit layout.
    qc = bell_state()
    pass_manager = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pass_manager.run(qc)

    # Submit the job using the V2 Sampler primitive.
    sampler = Sampler(mode=backend)
    job = sampler.run([isa_circuit], shots=1024)
    print(f"Submitted job: {job.job_id()} — waiting for results...")

    counts = job.result()[0].data.c.get_counts()
    print("Bell state counts (hardware):")
    for bitstring, count in sorted(counts.items()):
        print(f"  {bitstring}: {count}")


if __name__ == "__main__":
    main()
