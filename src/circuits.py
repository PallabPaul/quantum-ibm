"""Reusable quantum circuits.

Keep circuit definitions here so the same circuit can run on both the local
simulator and real IBM hardware without duplicating code.
"""

from __future__ import annotations

from qiskit import QuantumCircuit


def bell_state() -> QuantumCircuit:
    """Create a 2-qubit Bell state (entangled pair) with measurement.

    The classical register is named ``c`` (the default for an integer-sized
    register), so results are read with ``result[0].data.c.get_counts()``.
    """
    qc = QuantumCircuit(2, 2)
    qc.h(0)          # put qubit 0 in superposition
    qc.cx(0, 1)      # entangle qubit 0 with qubit 1
    qc.measure([0, 1], [0, 1])
    return qc
