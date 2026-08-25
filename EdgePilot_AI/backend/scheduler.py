"""Dynamic workload eligibility, scoring and decision engine."""

from typing import Dict, List

from backend.config import (
    CPU_OVERLOAD_THRESHOLD,
    LATENCY_DEGRADATION_THRESHOLD,
    WEIGHT_BANDWIDTH,
    WEIGHT_CPU,
    WEIGHT_GPU,
    WEIGHT_LATENCY,
    WEIGHT_MEMORY,
    WEIGHT_RELIABILITY,
)

from models.node import Node
from models.workload import Workload


class Scheduler:

    def __init__(self):

        self.decision_log: List[Dict] = []

    # ---------------------------------------------------------
    # Find nodes capable of hosting the workload
    # ---------------------------------------------------------

    def eligible_nodes(
        self,
        workload: Workload,
        nodes: Dict[str, Node]
    ) -> List[Node]:

        return [
            node
            for node in nodes.values()

            if node.can_host(
                workload.cpu_required,
                workload.memory_required,
                workload.gpu_required
            )
        ]

    # ---------------------------------------------------------
    # Calculate score for a node
    # ---------------------------------------------------------

    def score_node(
        self,
        workload: Workload,
        node: Node
    ) -> float:

        # CPU availability score
        cpu_score = (
            node.cpu_available /
            node.cpu_capacity
        )

        # Memory availability score
        memory_score = (
            node.memory_available /
            node.memory_capacity
        )

        # Lower latency = better score
        latency_score = (
            1.0 /
            (1.0 + node.latency_ms / 100.0)
        )

        # Higher bandwidth = better
        bandwidth_score = min(
            1.0,
            node.bandwidth_mbps / 1000.0
        )

        # Reliability
        reliability_score = max(
            0.0,
            min(1.0, node.reliability)
        )

        # GPU capability
        gpu_score = (
            1.0
            if (
                not workload.gpu_required
                or node.gpu
            )
            else 0.0
        )

        # Weighted score
        score = (

            WEIGHT_CPU *
            cpu_score

            +

            WEIGHT_MEMORY *
            memory_score

            +

            WEIGHT_LATENCY *
            latency_score

            +

            WEIGHT_BANDWIDTH *
            bandwidth_score

            +

            WEIGHT_RELIABILITY *
            reliability_score

            +

            WEIGHT_GPU *
            gpu_score
        )

        return round(
            score * 100.0,
            2
        )

    # ---------------------------------------------------------
    # Rank eligible nodes
    # ---------------------------------------------------------

    def rank_nodes(
        self,
        workload: Workload,
        nodes: Dict[str, Node]
    ) -> List[Dict]:

        eligible = self.eligible_nodes(
            workload,
            nodes
        )

        ranked = [

            {
                "node_id": node.id,

                "node_name": node.name,

                "tier": node.tier,

                "score":
                    self.score_node(
                        workload,
                        node
                    ),
            }

            for node in eligible
        ]

        return sorted(
            ranked,
            key=lambda x: x["score"],
            reverse=True
        )

    # ---------------------------------------------------------
    # Main scheduling decision
    # ---------------------------------------------------------

    def decide(
        self,
        workload: Workload,
        nodes: Dict[str, Node]
    ) -> Dict:

        ranked = self.rank_nodes(
            workload,
            nodes
        )

        current = (
            nodes.get(workload.node_id)
            if workload.node_id
            else None
        )

        # No eligible nodes
        if not ranked:

            decision = {

                "action": "recover",

                "reason":
                    "No healthy eligible node is available.",

                "workload_id":
                    workload.id,

                "from_node":
                    workload.node_id,

                "to_node":
                    None,

                "ranked_candidates":
                    [],
            }

            self.decision_log.append(
                decision
            )

            return decision

        # Best node
        best = ranked[0]

        # No current placement
        if current is None:

            action = "move"

            reason = (
                "Workload has no current placement."
            )

        # Current node failed
        elif not current.healthy:

            action = "recover"

            reason = (
                "Current node is unhealthy."
            )

        # Better node exists
        elif (
            best["node_id"] != current.id

            and

            best["score"]
            >=
            self.score_node(
                workload,
                current
            ) + 8
        ):

            action = "move"

            reason = (
                "A materially better eligible "
                "node is available."
            )

        # Current node overloaded
        elif (
            current.cpu_utilization
            >= CPU_OVERLOAD_THRESHOLD

            or

            current.latency_ms
            >= LATENCY_DEGRADATION_THRESHOLD
        ):

            action = "move"

            reason = (
                "Current node is overloaded "
                "or experiencing network degradation."
            )

        # Everything is fine
        else:

            action = "stay"

            reason = (
                "Current placement remains suitable."
            )

        decision = {

            "action": action,

            "reason": reason,

            "workload_id":
                workload.id,

            "from_node":
                workload.node_id,

            "to_node":
                (
                    best["node_id"]
                    if action != "stay"
                    else workload.node_id
                ),

            "current_score":
                (
                    self.score_node(
                        workload,
                        current
                    )
                    if current
                    else None
                ),

            "best_score":
                best["score"],

            "ranked_candidates":
                ranked,
        }

        self.decision_log.append(
            decision
        )

        return decision

    # ---------------------------------------------------------
    # Return decision history
    # ---------------------------------------------------------

    def decisions(self) -> List[Dict]:

        return list(
            self.decision_log
        )