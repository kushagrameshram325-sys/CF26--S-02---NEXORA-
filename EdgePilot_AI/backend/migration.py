"""Checkpoint, state transfer and workload migration."""

from time import perf_counter
from typing import Dict, List

from backend.config import (
    CHECKPOINT_SIZE_MB,
    MIGRATION_DOWNTIME_MS
)

from models.node import Node
from models.state import Checkpoint
from models.workload import Workload


class MigrationManager:

    def __init__(self):

        self.checkpoints: Dict[
            str,
            Checkpoint
        ] = {}

        self.events: List[Dict] = []

    # ---------------------------------------------------------
    # Create checkpoint
    # ---------------------------------------------------------

    def checkpoint(
        self,
        workload: Workload
    ) -> Checkpoint:

        previous = self.checkpoints.get(
            workload.id
        )

        sequence = (
            previous.sequence + 1
            if previous
            else 1
        )

        checkpoint = Checkpoint(

            workload_id=workload.id,

            sequence=sequence,

            state=workload.state.copy(),

            size_mb=CHECKPOINT_SIZE_MB
        )

        self.checkpoints[
            workload.id
        ] = checkpoint

        return checkpoint

    # ---------------------------------------------------------
    # Migrate workload
    # ---------------------------------------------------------

    def migrate(
        self,
        workload: Workload,
        source: Node,
        target: Node
    ) -> Dict:

        # Same source and destination
        if source.id == target.id:

            return {
                "success": False,
                "reason":
                    "Source and target are identical."
            }

        # Check target capacity
        if not target.can_host(

            workload.cpu_required,

            workload.memory_required,

            workload.gpu_required
        ):

            return {
                "success": False,
                "reason":
                    "Target node cannot host workload."
            }

        start = perf_counter()

        # Save state
        checkpoint = self.checkpoint(
            workload
        )

        # Simulated state transfer time
        transfer_time_ms = (

            checkpoint.size_mb /

            max(
                target.bandwidth_mbps,
                1.0
            )

            * 1000.0
        )

        # Remove workload from source
        source.remove_workload(

            workload.id,

            workload.cpu_required,

            workload.memory_required
        )

        # Add workload to target
        target.add_workload(

            workload.id,

            workload.cpu_required,

            workload.memory_required
        )

        # Update workload location
        workload.node_id = target.id

        # Restore previous state
        workload.restore(

            checkpoint.state
            |
            {
                "status": "running",
                "node_id": target.id
            }
        )

        elapsed_ms = (
            perf_counter() - start
        ) * 1000.0

        event = {

            "type": "migration",

            "workload_id":
                workload.id,

            "source":
                source.id,

            "target":
                target.id,

            "checkpoint_sequence":
                checkpoint.sequence,

            "transfer_time_ms":
                round(
                    transfer_time_ms,
                    2
                ),

            "downtime_ms":
                MIGRATION_DOWNTIME_MS,

            "execution_overhead_ms":
                round(
                    elapsed_ms,
                    2
                ),

            "state_preserved":
                True,
        }

        self.events.append(
            event
        )

        return {
            "success": True,
            "event": event
        }

    # ---------------------------------------------------------
    # Replicate workload
    # ---------------------------------------------------------

    def replicate(
        self,
        workload: Workload,
        target: Node
    ) -> Dict:

        if not target.can_host(

            workload.cpu_required,

            workload.memory_required,

            workload.gpu_required
        ):

            return {
                "success": False,
                "reason":
                    "Target cannot host replica."
            }

        target.add_workload(

            f"{workload.id}-replica",

            workload.cpu_required,

            workload.memory_required
        )

        workload.replicas += 1

        event = {

            "type": "replication",

            "workload_id":
                workload.id,

            "target":
                target.id,

            "replicas":
                workload.replicas,

            "state_preserved":
                True,
        }

        self.events.append(
            event
        )

        return {
            "success": True,
            "event": event
        }