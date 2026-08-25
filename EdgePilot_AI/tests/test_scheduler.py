import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from models.node import Node
from models.workload import Workload


def test_node_can_host_workload():
    node = Node(
        id="EDGE-01",
        name="Edge-01",
        node_type="edge",
        cpu_total=100,
        cpu_used=20,
        ram_total=8192,
        ram_used=2000,
        latency_ms=20,
        bandwidth_mbps=200,
        has_gpu=False,
    )

    workload = Workload(
        id="WL-001",
        name="Traffic Controller",
        cpu_required=20,
        ram_required=1024,
        max_latency_ms=30,
    )

    assert workload.can_run_on(node) is True


def test_failed_node_cannot_host_workload():
    node = Node(
        id="EDGE-01",
        name="Edge-01",
        node_type="edge",
        cpu_total=100,
        cpu_used=20,
        ram_total=8192,
        ram_used=2000,
        latency_ms=20,
        bandwidth_mbps=200,
        healthy=False,
    )

    workload = Workload(
        id="WL-001",
        name="Traffic Controller",
        cpu_required=20,
        ram_required=1024,
        max_latency_ms=30,
    )

    assert workload.can_run_on(node) is False


def test_gpu_requirement():
    node = Node(
        id="EDGE-01",
        name="Edge-01",
        node_type="edge",
        cpu_total=100,
        ram_total=8192,
        has_gpu=False,
    )

    workload = Workload(
        id="WL-002",
        name="CCTV AI",
        cpu_required=20,
        ram_required=1024,
        max_latency_ms=50,
        gpu_required=True,
    )

    assert workload.can_run_on(node) is False