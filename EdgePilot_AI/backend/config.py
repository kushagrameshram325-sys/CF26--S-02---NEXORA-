"""Central configuration for the EdgePilot AI simulation."""

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HOST = "0.0.0.0"
PORT = 8000
TICK_SECONDS = 1.0

# Scheduler weights. They sum to 1.0.
WEIGHT_CPU = 0.25
WEIGHT_MEMORY = 0.20
WEIGHT_LATENCY = 0.20
WEIGHT_BANDWIDTH = 0.15
WEIGHT_RELIABILITY = 0.15
WEIGHT_GPU = 0.05

# System thresholds
CPU_OVERLOAD_THRESHOLD = 85.0
MEMORY_OVERLOAD_THRESHOLD = 90.0
PACKET_LOSS_THRESHOLD = 15.0
LATENCY_DEGRADATION_THRESHOLD = 120.0

# Migration and recovery configuration
MIGRATION_DOWNTIME_MS = 20.0
CHECKPOINT_SIZE_MB = 50.0
REPLICATION_THRESHOLD = 0.85
RECOVERY_TIMEOUT_MS = 500.0