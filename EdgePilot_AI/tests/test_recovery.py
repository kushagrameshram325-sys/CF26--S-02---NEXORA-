import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.state import WorkloadState


def test_workload_failure():

    state = WorkloadState(
        workload_id="WL-001",
        current_node_id="EDGE-01",
        status="running",
    )

    state.mark_failed()

    assert state.status == "failed"


def test_workload_recovery():

    state = WorkloadState(
        workload_id="WL-001",
        current_node_id="EDGE-01",
        status="running",
    )

    state.create_checkpoint(
        source_node_id="EDGE-01",
        state_data={
            "vehicle_count": 200,
            "signal_state": "GREEN",
        },
    )

    state.mark_failed()

    assert state.status == "failed"

    state.start_recovery()

    assert state.status == "recovering"

    state.complete_recovery("REG-01")

    assert state.status == "recovered"
    assert state.current_node_id == "REG-01"
    assert state.recovery_count == 1