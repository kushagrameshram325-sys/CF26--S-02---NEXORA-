from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Checkpoint:
    """
    Represents a saved workload state.
    """

    workload_id: str

    checkpoint_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    source_node_id: Optional[str] = None

    state_data: dict = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    valid: bool = True

    def invalidate(self) -> None:
        self.valid = False

    def to_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workload_id": self.workload_id,
            "source_node_id": self.source_node_id,
            "state_data": self.state_data,
            "created_at": self.created_at.isoformat(),
            "valid": self.valid,
        }


@dataclass
class Replica:
    """
    Represents a replicated workload instance.
    """

    workload_id: str
    node_id: str

    replica_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    active: bool = True

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    synchronized: bool = True

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True

    def mark_out_of_sync(self) -> None:
        self.synchronized = False

    def mark_synced(self) -> None:
        self.synchronized = True

    def to_dict(self) -> dict:
        return {
            "replica_id": self.replica_id,
            "workload_id": self.workload_id,
            "node_id": self.node_id,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "synchronized": self.synchronized,
        }


@dataclass
class WorkloadState:
    """
    Central state record for a workload.

    Used by migration and recovery modules.
    """

    workload_id: str

    current_node_id: Optional[str] = None

    previous_node_id: Optional[str] = None

    status: str = "pending"
    # pending / running / migrating / failed / recovering / recovered

    checkpoint: Optional[Checkpoint] = None

    replicas: list[Replica] = field(default_factory=list)

    migration_count: int = 0

    recovery_count: int = 0

    last_event: Optional[str] = None

    def create_checkpoint(
        self,
        source_node_id: str,
        state_data: dict,
    ) -> Checkpoint:
        """
        Create a new checkpoint before migration/recovery.
        """

        self.checkpoint = Checkpoint(
            workload_id=self.workload_id,
            source_node_id=source_node_id,
            state_data=state_data.copy(),
        )

        self.last_event = "checkpoint_created"

        return self.checkpoint

    def restore_checkpoint(self) -> Optional[dict]:
        """
        Restore the latest valid checkpoint.
        """

        if self.checkpoint is None:
            return None

        if not self.checkpoint.valid:
            return None

        self.last_event = "checkpoint_restored"

        return self.checkpoint.state_data.copy()

    def start_migration(
        self,
        source_node_id: str,
        destination_node_id: str,
    ) -> None:
        """
        Start workload migration.
        """

        self.previous_node_id = source_node_id
        self.current_node_id = destination_node_id
        self.status = "migrating"

        self.last_event = (
            f"migration_started:"
            f"{source_node_id}->{destination_node_id}"
        )

    def complete_migration(self) -> None:
        """
        Complete workload migration.
        """

        self.status = "running"
        self.migration_count += 1
        self.last_event = "migration_completed"

    def mark_failed(self) -> None:
        """
        Mark workload as failed.
        """

        self.status = "failed"
        self.last_event = "workload_failed"

    def start_recovery(self) -> None:
        """
        Start recovery process.
        """

        self.status = "recovering"
        self.last_event = "recovery_started"

    def complete_recovery(
        self,
        node_id: str,
    ) -> None:
        """
        Complete workload recovery.
        """

        self.current_node_id = node_id
        self.status = "recovered"
        self.recovery_count += 1

        self.last_event = "recovery_completed"

    def add_replica(self, node_id: str) -> Replica:
        """
        Create a replica on another node.
        """

        replica = Replica(
            workload_id=self.workload_id,
            node_id=node_id,
        )

        self.replicas.append(replica)

        self.last_event = f"replica_created:{node_id}"

        return replica

    def get_active_replica(self) -> Optional[Replica]:
        """
        Return the first active replica.
        """

        for replica in self.replicas:
            if replica.active:
                return replica

        return None

    def to_dict(self) -> dict:
        return {
            "workload_id": self.workload_id,
            "current_node_id": self.current_node_id,
            "previous_node_id": self.previous_node_id,
            "status": self.status,
            "checkpoint": (
                self.checkpoint.to_dict()
                if self.checkpoint
                else None
            ),
            "replicas": [
                replica.to_dict()
                for replica in self.replicas
            ],
            "migration_count": self.migration_count,
            "recovery_count": self.recovery_count,
            "last_event": self.last_event,
        }