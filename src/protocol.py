"""Utilities for working with MultispeQ protocol definitions and pulse timing."""

from __future__ import annotations

import itertools
import json
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd
    from numpy.typing import NDArray

try:
    from pyspark.sql.connect.session import SparkSession

    _IN_DATABRICKS = SparkSession.getActiveSession() is not None
except Exception:
    _IN_DATABRICKS = False

CATALOG = "open_jii_data_hackathon.default"


def load_protocols(data: Path) -> pd.DataFrame:
    """Load the protocol definitions table.

    Args:
        data: Path to the local data directory.

    Returns:
        DataFrame with columns: project_id, dataset, protocol_id,
        protocol_name, protocol_json (as JSON string).
    """
    if _IN_DATABRICKS:
        from pyspark.sql.connect.session import SparkSession
        from typing import cast

        spark = cast(SparkSession, SparkSession.getActiveSession())
        return spark.sql(
            f"SELECT * EXCEPT(protocol_json) FROM {CATALOG}.photosynq_protocols"
        ).toPandas()

    import pandas as pd

    return pd.read_parquet(data / "protocols.parquet")


def get_protocol(data: Path, protocol_id: str) -> dict[str, Any]:
    """Get a single protocol definition by ID.

    Args:
        data: Path to the local data directory.
        protocol_id: The protocol ID (e.g. "3517").

    Returns:
        Parsed protocol JSON dict.
    """
    import pandas as pd

    df = pd.read_parquet(
        data / "protocols.parquet",
        columns=["protocol_id", "protocol_json"],
    )
    row = df[df["protocol_id"] == str(protocol_id)].iloc[0]
    return json.loads(row["protocol_json"])


def _resolve_ref(ref: Any, v_arrays: list) -> int:
    """Resolve a ``@nN:M`` v_arrays reference to its integer value."""
    if isinstance(ref, str) and ref.startswith("@n"):
        parts = ref[2:].split(":")
        return int(v_arrays[int(parts[0])][int(parts[1])])
    return int(ref)


def generate_protocol_timing(
    protocol: dict[str, Any],
    verbose: bool = False,
) -> dict[str, Any]:
    """Generate a protocol object with timing information.

    MultispeQ does not output trace timing directly, so we calculate it
    from the protocol definition.  Per the PhotosynQ docs, ``pulse_distance``
    is the time **between each sub-pulse** (in microseconds).  When multiple
    detectors are used (``len(pulse_length[i]) > 1``), each detector fires
    in sequence within one measurement pulse, and each sub-pulse is separated
    by ``pulse_distance``.

    Args:
        protocol: Protocol dict (the ``protocol_json`` value).
        verbose: Print debug information.

    Returns:
        Dict keyed by sub-protocol label.  Each entry contains:
        - ``time_ms``: cumulative pulse times in milliseconds (one per sample).
        - ``segments``: list of segment dicts with ``n_pulses``, ``n_samples``,
          ``start_ms``, and ``duration_ms``.
        - ``n_detectors``: number of interleaved detectors per pulse.
        - ``pulse_distance_us``: pulse distance in microseconds (per segment).
    """
    v_arrays = protocol.get("v_arrays", [])
    result: dict[str, Any] = {}

    if "_protocol_set_" not in protocol:
        return result

    for step in protocol["_protocol_set_"]:
        pulses_refs = step.get("pulses")
        pulse_distances = step.get("pulse_distance")
        if not pulses_refs or not pulse_distances:
            continue

        label = step.get("label", "")
        n_detectors = max(len(pl) for pl in step.get("pulse_length", [[1]]))

        segments: list[dict[str, Any]] = []
        pulse_times: list[float] = []
        cumulative_us = 0.0

        for ref, pd_us in zip(pulses_refs, pulse_distances):
            n_pulses = _resolve_ref(ref, v_arrays)
            n_samples = n_pulses * n_detectors
            seg_start_us = cumulative_us

            for j in range(n_samples):
                pulse_times.append(cumulative_us + j * pd_us)

            duration_us = n_samples * pd_us
            cumulative_us += duration_us

            segments.append(
                {
                    "n_pulses": n_pulses,
                    "n_samples": n_samples,
                    "start_ms": seg_start_us / 1000,
                    "duration_ms": duration_us / 1000,
                    "pulse_distance_us": pd_us,
                }
            )

        time_ms = np.array(pulse_times) / 1000

        entry = {
            "time_ms": time_ms,
            "segments": segments,
            "n_detectors": n_detectors,
            "total_samples": len(time_ms),
            "total_duration_ms": time_ms[-1] if len(time_ms) > 0 else 0.0,
        }
        result[label] = entry

        if verbose:
            print(
                f"{label:15s}  {len(time_ms):>5} samples "
                f"({n_detectors} det),  {entry['total_duration_ms']:.0f} ms"
            )

    return result


def segment_boundaries(timing_entry: dict[str, Any]) -> NDArray[np.float64]:
    """Return segment boundary times in ms for vertical line markers.

    Args:
        timing_entry: One entry from ``generate_protocol_timing()`` output.

    Returns:
        Array of segment start times (excluding the first at t=0).
    """
    return np.array([s["start_ms"] for s in timing_entry["segments"][1:]])


def deinterleave(
    trace: NDArray[np.float64],
    n_detectors: int = 2,
) -> list[NDArray[np.float64]]:
    """Split an interleaved trace into per-detector channels.

    MultispeQ interleaves detector readings: [det0, det1, det0, det1, ...].

    Args:
        trace: Raw interleaved trace array.
        n_detectors: Number of interleaved detectors (default: 2).

    Returns:
        List of arrays, one per detector channel.
    """
    return [trace[i::n_detectors] for i in range(n_detectors)]
