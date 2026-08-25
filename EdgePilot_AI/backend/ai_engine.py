"""Lightweight AI-assisted prediction and anomaly detection.

This prototype intentionally uses transparent statistical heuristics rather than
an external trained model. That keeps the hackathon demo deterministic, fast,
and easy to explain.
"""

from collections import defaultdict, deque
from statistics import mean, pstdev
from typing import Dict, List

from backend.config import (
    CPU_OVERLOAD_THRESHOLD,
    LATENCY_DEGRADATION_THRESHOLD,
    MEMORY_OVERLOAD_THRESHOLD,
    PACKET_LOSS_THRESHOLD,
)


class AIEngine:

    def __init__(self, history_size: int = 12):
        self.history_size = history_size

        self.metric_history = defaultdict(
            lambda: deque(maxlen=history_size)
        )

    def observe(self, nodes: Dict):

        for node_id, node in nodes.items():

            self.metric_history[node_id].append({
                "cpu": node.cpu_utilization,
                "memory": node.memory_utilization,
                "latency": node.latency_ms,
                "packet_loss": node.packet_loss,
                "health": 1.0 if node.healthy else 0.0,
            })

    def predict_demand(self, workload) -> Dict:

        # Simple transparent trend-based prediction

        current = workload.demand

        predicted = min(
            100.0,
            max(0.0, current * 1.12)
        )

        trend = predicted - current

        return {
            "workload_id": workload.id,
            "current_demand": round(current, 2),
            "predicted_demand": round(predicted, 2),
            "trend": round(trend, 2),

            "risk":
                "high"
                if predicted >= 80
                else
                "medium"
                if predicted >= 60
                else
                "low",
        }

    def detect_anomalies(self, nodes: Dict) -> List[Dict]:

        anomalies = []

        for node_id, node in nodes.items():

            reasons = []

            # Node failure
            if not node.healthy:
                reasons.append("node_failure")

            # CPU overload
            if node.cpu_utilization >= CPU_OVERLOAD_THRESHOLD:
                reasons.append("cpu_overload")

            # Memory overload
            if node.memory_utilization >= MEMORY_OVERLOAD_THRESHOLD:
                reasons.append("memory_overload")

            # Packet loss
            if node.packet_loss >= PACKET_LOSS_THRESHOLD:
                reasons.append("packet_loss")

            # High network latency
            if node.latency_ms >= LATENCY_DEGRADATION_THRESHOLD:
                reasons.append("network_latency")

            # Historical CPU spike detection
            history = list(
                self.metric_history[node_id]
            )

            if len(history) >= 4:

                cpu_values = [
                    h["cpu"]
                    for h in history
                ]

                if (
                    pstdev(cpu_values) > 20
                    and node.cpu_utilization > mean(cpu_values)
                ):
                    reasons.append("cpu_spike")

            if reasons:

                anomalies.append({
                    "node_id": node_id,

                    "severity":
                        "critical"
                        if not node.healthy
                        else "warning",

                    "reasons": reasons,
                })

        return anomalies

    def analyze(
        self,
        nodes: Dict,
        workloads: Dict
    ) -> Dict:

        self.observe(nodes)

        return {
            "predictions": [
                self.predict_demand(workload)
                for workload in workloads.values()
            ],

            "anomalies": self.detect_anomalies(nodes),
        }
