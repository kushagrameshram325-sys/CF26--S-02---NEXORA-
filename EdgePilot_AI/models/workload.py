from dataclasses import dataclass
from typing import Optional


@dataclass(init=False)
class Workload:
    """
    Represents an application workload running on the
    EdgePilot cloud-edge computing fabric.

    Supports both:
    - memory_required
    - legacy ram_required
    """

    # =====================================================
    # IDENTITY
    # =====================================================

    id: str
    name: str

    # =====================================================
    # SCHEDULING
    # =====================================================

    priority: int

    # =====================================================
    # RESOURCES
    # =====================================================

    cpu_required: float
    memory_required: float

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    max_latency_ms: float
    gpu_required: bool

    # =====================================================
    # RUNTIME
    # =====================================================

    demand: float
    node_id: Optional[str]
    status: str
    replicas: int
    state: dict

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        id: str,
        name: str,
        cpu_required: float,
        memory_required: Optional[float] = None,
        ram_required: Optional[float] = None,
        max_latency_ms: float = float("inf"),
        gpu_required: bool = False,
        priority: int = 0,
        demand: float = 0.0,
        node_id: Optional[str] = None,
        status: str = "pending",
        replicas: int = 1,
        state=None,
    ):
        self.id = id
        self.name = name

        # -------------------------------------------------
        # Scheduling
        # -------------------------------------------------

        self.priority = int(priority)

        # -------------------------------------------------
        # Memory compatibility
        # -------------------------------------------------

        # If memory_required is not provided,
        # use the legacy ram_required field.
        if memory_required is None:
            memory_required = ram_required

        if memory_required is None:
            raise ValueError(
                "memory_required or ram_required must be provided"
            )

        # -------------------------------------------------
        # Resources
        # -------------------------------------------------

        self.cpu_required = float(cpu_required)
        self.memory_required = float(memory_required)

        # -------------------------------------------------
        # Constraints
        # -------------------------------------------------

        self.max_latency_ms = float(max_latency_ms)
        self.gpu_required = bool(gpu_required)

        # -------------------------------------------------
        # Runtime
        # -------------------------------------------------

        self.demand = float(demand)
        self.node_id = node_id
        self.status = status
        self.replicas = int(replicas)

        self.state = dict(state or {})

    # =====================================================
    # RAM ALIAS
    # =====================================================

    @property
    def ram_required(self) -> float:
        """
        Backward-compatible alias for memory_required.
        """
        return self.memory_required

    # =====================================================
    # STATUS HELPERS
    # =====================================================

    @property
    def is_running(self) -> bool:
        """Return True if workload is currently running."""
        return self.status == "running"

    @property
    def is_failed(self) -> bool:
        """Return True if workload has failed."""
        return self.status == "failed"

    # =====================================================
    # CAN RUN ON NODE
    # =====================================================

    def can_run_on(self, node) -> bool:
        """
        Check whether this workload can run on a node.

        Conditions:
        1. Node must be healthy.
        2. Node must have enough CPU.
        3. Node must have enough RAM.
        4. Node latency must satisfy SLA.
        5. Node must have GPU if required.
        """

        # -------------------------------------------------
        # 1. Node health
        # -------------------------------------------------

        if not node.healthy:
            return False

        # -------------------------------------------------
        # 2. CPU availability
        # -------------------------------------------------

        if node.cpu_available < self.cpu_required:
            return False

        # -------------------------------------------------
        # 3. RAM availability
        # -------------------------------------------------

        if node.memory_available < self.memory_required:
            return False

        # -------------------------------------------------
        # 4. Latency requirement
        # -------------------------------------------------

        if node.latency_ms > self.max_latency_ms:
            return False

        # -------------------------------------------------
        # 5. GPU requirement
        # -------------------------------------------------

        if self.gpu_required and not node.gpu:
            return False

        return True

    # =====================================================
    # ASSIGN NODE
    # =====================================================

    def assign_node(self, node_id: str) -> None:
        """
        Assign this workload to a node.
        """

        self.node_id = node_id
        self.status = "running"

    # =====================================================
    # UNASSIGN NODE
    # =====================================================

    def unassign_node(self) -> None:
        """
        Remove workload from its current node.
        """

        self.node_id = None
        self.status = "pending"

    # =====================================================
    # CHECKPOINT
    # =====================================================

    def checkpoint(self) -> dict:
        """
        Create a checkpoint of the workload state.
        """

        return dict(self.state)

    # =====================================================
    # RESTORE CHECKPOINT
    # =====================================================

    def restore_checkpoint(self, checkpoint: dict) -> None:
        """
        Restore workload state from a checkpoint.
        """

        self.state = dict(checkpoint or {})

    # =====================================================
    # UPDATE STATE
    # =====================================================

    def update_state(self, key: str, value) -> None:
        """
        Update a value inside the workload state.
        """

        self.state[key] = value

    # =====================================================
    # TO DICTIONARY
    # =====================================================

    def to_dict(self) -> dict:
        """
        Convert workload into a dictionary for
        API responses and dashboard display.
        """

        return {
            "id": self.id,
            "name": self.name,

            "priority": self.priority,

            "cpu_required": self.cpu_required,

            "memory_required": self.memory_required,
            "ram_required": self.ram_required,

            "max_latency_ms": self.max_latency_ms,

            "gpu_required": self.gpu_required,

            "demand": self.demand,

            "node_id": self.node_id,

            "status": self.status,

            "replicas": self.replicas,

            "state": self.state,
        }

    # =====================================================
    # STRING REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:
        return (
            f"Workload("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"cpu_required={self.cpu_required}, "
            f"memory_required={self.memory_required}, "
            f"max_latency_ms={self.max_latency_ms}, "
            f"gpu_required={self.gpu_required}, "
            f"node_id={self.node_id!r}, "
            f"status={self.status!r}"
            f")"
        )