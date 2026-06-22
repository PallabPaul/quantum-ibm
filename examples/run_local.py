"""Run the Bell-state circuit on the local simulator (no API key needed).

    python -m examples.run_local

Uses Qiskit's built-in StatevectorSampler, so it works offline without any
IBM Quantum credentials. Great for developing and testing circuits before
spending real quantum hardware time.
"""

from qiskit.primitives import StatevectorSampler

from src.circuits import bell_state


def main() -> None:
    qc = bell_state()

    sampler = StatevectorSampler()
    job = sampler.run([qc], shots=1024)
    counts = job.result()[0].data.c.get_counts()

    print("Bell state counts (local simulator):")
    for bitstring, count in sorted(counts.items()):
        print(f"  {bitstring}: {count}")

    # Save a histogram image (optional, needs matplotlib).
    try:
        from qiskit.visualization import plot_histogram

        plot_histogram(counts).savefig("bell_histogram.png")
        print("Saved histogram to bell_histogram.png")
    except Exception as exc:  # pragma: no cover - plotting is optional
        print(f"(Skipped histogram: {exc})")


if __name__ == "__main__":
    main()
