"""Node model for EdgePilot AI."""

from typing import List, Optional


class Node:

    def __init__(
        self,
        id: str,
        name: str,
        tier: Optional[str] = None,
        node_type: Optional[str] = None,

        # Current API
        cpu_capacity: Optional[float] = None,
        memory_capacity: Optional[float] = None,

        # Legacy API used by tests
        cpu_total: Optional[float] = None,
        ram_total: Optional[float] = None,

        bandwidth_mbps: float = 0.0,
        latency_ms: float = 0.0,
        reliability: float = 1.0,

        # Current GPU API
        gpu: Optional[bool] = None,

        # Legacy GPU API
        has_gpu: Optional[bool] = None,

        healthy: bool = True,

        cpu_used: float = 0.0,

        # Current memory API
        memory_used: Optional[float] = None,

        # Legacy RAM API
        ram_used: Optional[float] = None,

        packet_loss: float = 0.0,
        workloads: Optional[List[str]] = None,
    ):

        self.id = id
        self.name = name

        # =================================================
        # NODE TYPE
        # =================================================

        self.tier = tier or node_type or "edge"
        self.node_type = node_type or self.tier

        # =================================================
        # CPU
        # =================================================

        if cpu_capacity is None:
            cpu_capacity = cpu_total

        if cpu_capacity is None:
            cpu_capacity = 0.0

        self.cpu_capacity = float(cpu_capacity)

        # Legacy alias
        self.cpu_total = self.cpu_capacity

        self.cpu_used = float(cpu_used)

        # =================================================
        # MEMORY / RAM
        # =================================================

        if memory_capacity is None:
            memory_capacity = ram_total

        if memory_capacity is None:
            memory_capacity = 0.0

        self.memory_capacity = float(memory_capacity)

        # Legacy alias
        self.ram_total = self.memory_capacity

        if memory_used is None:
            memory_used = ram_used

        if memory_used is None:
            memory_used = 0.0

        self.memory_used = float(memory_used)

        # Legacy alias
        self.ram_used = self.memory_used

        # =================================================
        # NETWORK
        # =================================================

        self.bandwidth_mbps = float(bandwidth_mbps)
        self.latency_ms = float(latency_ms)
        self.packet_loss = float(packet_loss)

        # =================================================
        # RELIABILITY
        # =================================================

        self.reliability = float(reliability)

        # =================================================
        # GPU
        # =================================================

        if gpu is None:
            gpu = has_gpu

        if gpu is None:
            gpu = False

        self.gpu = bool(gpu)

        # Legacy alias
        self.has_gpu = self.gpu

        # =================================================
        # HEALTH
        # =================================================

        self.healthy = bool(healthy)

        # =================================================
        # WORKLOADS
        # =================================================

        self.workloads = (
            list(workloads)
            if workloads is not None
            else []
        )

    # =====================================================
    # CPU AVAILABLE
    # =====================================================

    @property
    def cpu_available(self) -> float:
        """Return remaining CPU capacity."""

        return max(
            0.0,
            self.cpu_capacity - self.cpu_used
        )

    # =====================================================
    # MEMORY AVAILABLE
    # =====================================================

    @property
    def memory_available(self) -> float:
        """Return remaining memory."""

        return max(
            0.0,
            self.memory_capacity - self.memory_used
        )

    # =====================================================
    # RAM AVAILABLE
    # =====================================================

    @property
    def ram_available(self) -> float:
        """Legacy alias for memory_available."""

        return self.memory_available

    # =====================================================
    # CPU UTILIZATION
    # =====================================================

    @property
    def cpu_utilization(self) -> float:

        if self.cpu_capacity <= 0:
            return 0.0

        return (
            self.cpu_used /
            self.cpu_capacity
        ) * 100.0

    # =====================================================
    # MEMORY UTILIZATION
    # =====================================================

    @property
    def memory_utilization(self) -> float:

        if self.memory_capacity <= 0:
            return 0.0

        return (
            self.memory_used /
            self.memory_capacity
        ) * 100.0

    # =====================================================
    # RAM UTILIZATION
    # =====================================================

    @property
    def ram_utilization(self) -> float:
        """Legacy alias."""

        return self.memory_utilization

    # =====================================================
    # CAN HOST
    # =====================================================

    def can_host(
        self,
        cpu_required: float,
        memory_required: float = 0.0,
        gpu_required: bool = False,
        ram_required: Optional[float] = None,
    ) -> bool:

        if not self.healthy:
            return False

        if ram_required is not None:
            memory_required = ram_required

        if gpu_required and not self.gpu:
            return False

        if self.cpu_available < cpu_required:
            return False

        if self.memory_available < memory_required:
            return False

        return True

    # =====================================================
    # ADD WORKLOAD
    # =====================================================

    def add_workload(
        self,
        workload_id: str,
        cpu_required: float,
        memory_required: float = 0.0,
        ram_required: Optional[float] = None,
    ) -> bool:

        if workload_id in self.workloads:
            return True

        if ram_required is not None:
            memory_required = ram_required

        if not self.can_host(
            cpu_required,
            memory_required,
        ):
            return False

        self.workloads.append(workload_id)

        self.cpu_used += cpu_required
        self.memory_used += memory_required

        # Keep legacy values synchronized
        self.cpu_total = self.cpu_capacity
        self.ram_total = self.memory_capacity
        self.ram_used = self.memory_used

        return True

    # =====================================================
    # REMOVE WORKLOAD
    # =====================================================

    def remove_workload(
        self,
        workload_id: str,
        cpu_required: float = 0.0,
        memory_required: float = 0.0,
        ram_required: Optional[float] = None,
    ) -> bool:

        if workload_id not in self.workloads:
            return False

        if ram_required is not None:
            memory_required = ram_required

        self.workloads.remove(workload_id)

        self.cpu_used = max(
            0.0,
            self.cpu_used - cpu_required,
        )

        self.memory_used = max(
            0.0,
            self.memory_used - memory_required,
        )

        self.ram_used = self.memory_used

        return True

    # =====================================================
    # DICTIONARY
    # =====================================================

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,

            "tier": self.tier,
            "node_type": self.node_type,

            "cpu_capacity": self.cpu_capacity,
            "cpu_total": self.cpu_total,
            "cpu_used": self.cpu_used,
            "cpu_available": self.cpu_available,
            "cpu_utilization": self.cpu_utilization,

            "memory_capacity": self.memory_capacity,
            "ram_total": self.ram_total,
            "memory_used": self.memory_used,
            "ram_used": self.ram_used,
            "memory_available": self.memory_available,
            "ram_available": self.ram_available,
            "memory_utilization": self.memory_utilization,
            "ram_utilization": self.ram_utilization,

            "bandwidth_mbps": self.bandwidth_mbps,
            "latency_ms": self.latency_ms,
            "packet_loss": self.packet_loss,

            "reliability": self.reliability,

            "gpu": self.gpu,
            "has_gpu": self.has_gpu,

            "healthy": self.healthy,

            "workloads": self.workloads,
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:

        return (
            f"Node("
            f"id={self.id!r}, "
            f"name={self.name!r}, "
            f"cpu={self.cpu_used}/{self.cpu_capacity}, "
            f"ram={self.memory_used}/{self.memory_capacity}, "
            f"healthy={self.healthy}"
            f")"
        )