import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.state import WorkloadState


def test_migration_state():

    state = WorkloadState(
        workload_id="WL-001",
        current_node_id="EDGE-01",
        status="running",
    )

    state.create_checkpoint(
        source_node_id="EDGE-01",
        state_data={
            "vehicle_count": 120,
            "signal_state": "GREEN",
        },
    )

    state.start_migration(
        source_node_id="EDGE-01",
        destination_node_id="EDGE-02",
    )

    assert state.status == "migrating"
    assert state.current_node_id == "EDGE-02"

    state.complete_migration()

    assert state.status == "running"
    assert state.migration_count == 1


def test_checkpoint_restore():

    state = WorkloadState(
        workload_id="WL-001",
        current_node_id="EDGE-01",
    )

    original_data = {
        "vehicle_count": 150,
        "signal_state": "RED",
    }

    state.create_checkpoint(
        source_node_id="EDGE-01",
        state_data=original_data,
    )

    restored = state.restore_checkpoint()

    assert restored == original_data