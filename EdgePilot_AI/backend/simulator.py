"""FastAPI application and simulation controller for EdgePilot AI."""

import json
import random

from typing import Dict

from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from backend.ai_engine import AIEngine

from backend.config import (
    DATA_DIR,
    TICK_SECONDS
)

from backend.metrics import MetricsCollector

from backend.migration import MigrationManager

from backend.recovery import RecoveryManager

from backend.scheduler import Scheduler

from models.node import Node

from models.workload import Workload


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(

    title="EdgePilot AI",

    description=(
        "Autonomous cloud-edge "
        "workload placement simulation API"
    ),

    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# SIMULATION CLASS
# =========================================================

class Simulation:

    def __init__(self):

        self.nodes: Dict[
            str,
            Node
        ] = {}

        self.workloads: Dict[
            str,
            Workload
        ] = {}

        self.scheduler = Scheduler()

        self.ai = AIEngine()

        self.migration = MigrationManager()

        self.recovery = RecoveryManager()

        self.metrics = MetricsCollector()

        self.running = False

        self.auto_mode = False

        self.tick = 0

        self.events = []

        self.reset()

    # =====================================================
    # RESET SIMULATION
    # =====================================================

    def reset(self):

        self.nodes.clear()

        self.workloads.clear()

        self.scheduler = Scheduler()

        self.ai = AIEngine()

        self.migration = MigrationManager()

        self.recovery = RecoveryManager()

        self.metrics = MetricsCollector()

        self.events = []

        self.tick = 0

        self.running = True

        self.auto_mode = False

        self._load_nodes()

        self._load_workloads()

        self._place_initial_workloads()

        self.metrics.record(
            self.nodes,
            self.workloads
        )

    # =====================================================
    # LOAD JSON FILE
    # =====================================================

    def _load_json(
        self,
        filename,
        fallback
    ):

        path = DATA_DIR / filename

        if not path.exists():

            return fallback

        try:

            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            OSError,
            json.JSONDecodeError
        ):

            return fallback

    # =====================================================
    # LOAD NODES
    # =====================================================

    def _load_nodes(self):

        default_nodes = [

            {
                "id": "edge-01",
                "name": "EDGE-01",
                "tier": "edge",
                "cpu_capacity": 8,
                "memory_capacity": 16,
                "bandwidth_mbps": 300,
                "latency_ms": 15,
                "reliability": 0.97,
                "gpu": False
            },

            {
                "id": "edge-02",
                "name": "EDGE-02",
                "tier": "edge",
                "cpu_capacity": 8,
                "memory_capacity": 16,
                "bandwidth_mbps": 250,
                "latency_ms": 20,
                "reliability": 0.96,
                "gpu": True
            },

            {
                "id": "regional-01",
                "name": "REGIONAL-01",
                "tier": "regional",
                "cpu_capacity": 24,
                "memory_capacity": 64,
                "bandwidth_mbps": 700,
                "latency_ms": 35,
                "reliability": 0.985,
                "gpu": True
            },

            {
                "id": "regional-02",
                "name": "REGIONAL-02",
                "tier": "regional",
                "cpu_capacity": 32,
                "memory_capacity": 96,
                "bandwidth_mbps": 800,
                "latency_ms": 45,
                "reliability": 0.99,
                "gpu": False
            },

            {
                "id": "cloud-01",
                "name": "CLOUD-01",
                "tier": "cloud",
                "cpu_capacity": 64,
                "memory_capacity": 256,
                "bandwidth_mbps": 1500,
                "latency_ms": 90,
                "reliability": 0.999,
                "gpu": True
            }
        ]

        for data in self._load_json(
            "nodes.json",
            default_nodes
        ):

            self.nodes[
                data["id"]
            ] = Node(**data)

    # =====================================================
    # LOAD WORKLOADS
    # =====================================================

    def _load_workloads(self):

        default_workloads = [

            {
                "id": "traffic-controller",
                "name": "Traffic Controller",
                "priority": 5,
                "cpu_required": 2,
                "memory_required": 3,
                "gpu_required": False,
                "demand": 65
            },

            {
                "id": "camera-analytics",
                "name": "Camera Analytics",
                "priority": 4,
                "cpu_required": 3,
                "memory_required": 4,
                "gpu_required": True,
                "demand": 55
            },

            {
                "id": "parking-service",
                "name": "Smart Parking",
                "priority": 3,
                "cpu_required": 1.5,
                "memory_required": 2,
                "gpu_required": False,
                "demand": 45
            },

            {
                "id": "emergency-alert",
                "name": "Emergency Alert",
                "priority": 5,
                "cpu_required": 2,
                "memory_required": 2,
                "gpu_required": False,
                "demand": 30
            }
        ]

        for data in self._load_json(
            "workloads.json",
            default_workloads
        ):

            data["state"] = {

                "processed_events":
                    random.randint(
                        100,
                        500
                    )
            }

            self.workloads[
                data["id"]
            ] = Workload(**data)

    # =====================================================
    # INITIAL WORKLOAD PLACEMENT
    # =====================================================

    def _place_initial_workloads(self):

        ordered = list(
            self.nodes.values()
        )

        for index, workload in enumerate(
            self.workloads.values()
        ):

            node = ordered[
                index % len(ordered)
            ]

            if not node.can_host(

                workload.cpu_required,

                workload.memory_required,

                workload.gpu_required
            ):

                candidates = (
                    self.scheduler.eligible_nodes(
                        workload,
                        self.nodes
                    )
                )

                if not candidates:

                    workload.status = "failed"

                    continue

                node = candidates[0]

            node.add_workload(

                workload.id,

                workload.cpu_required,

                workload.memory_required
            )

            workload.node_id = node.id

    # =====================================================
    # CREATE COMPLETE SNAPSHOT
    # =====================================================

    def snapshot(self):

        return {

            "running":
                self.running,

            "auto_mode":
                self.auto_mode,

            "tick":
                self.tick,

            "nodes":
                [
                    self.node_dict(n)
                    for n in self.nodes.values()
                ],

            "workloads":
                [
                    self.workload_dict(w)
                    for w in self.workloads.values()
                ],

            "ai":
                self.ai.analyze(
                    self.nodes,
                    self.workloads
                ),

            "metrics":
                self.metrics.current(),

            "decisions":
                self.scheduler.decisions()[-10:],

            "events":
                self.events[-20:]
        }

    # =====================================================
    # NODE → JSON
    # =====================================================

    @staticmethod
    def node_dict(node: Node):

        return {

            "id":
                node.id,

            "name":
                node.name,

            "tier":
                node.tier,

            "cpu_capacity":
                node.cpu_capacity,

            "memory_capacity":
                node.memory_capacity,

            "cpu_used":
                round(
                    node.cpu_used,
                    2
                ),

            "memory_used":
                round(
                    node.memory_used,
                    2
                ),

            "cpu_utilization":
                round(
                    node.cpu_utilization,
                    2
                ),

            "memory_utilization":
                round(
                    node.memory_utilization,
                    2
                ),

            "bandwidth_mbps":
                node.bandwidth_mbps,

            "latency_ms":
                round(
                    node.latency_ms,
                    2
                ),

            "packet_loss":
                round(
                    node.packet_loss,
                    2
                ),

            "reliability":
                node.reliability,

            "gpu":
                node.gpu,

            "healthy":
                node.healthy,

            "workloads":
                node.workloads
        }

    # =====================================================
    # WORKLOAD → JSON
    # =====================================================

    @staticmethod
    def workload_dict(
        workload: Workload
    ):

        return {

            "id":
                workload.id,

            "name":
                workload.name,

            "priority":
                workload.priority,

            "cpu_required":
                workload.cpu_required,

            "memory_required":
                workload.memory_required,

            "gpu_required":
                workload.gpu_required,

            "demand":
                round(
                    workload.demand,
                    2
                ),

            "node_id":
                workload.node_id,

            "status":
                workload.status,

            "replicas":
                workload.replicas,

            "state":
                workload.state
        }

    # =====================================================
    # SIMULATION STEP
    # =====================================================

    def step(self):

        if not self.running:

            return self.snapshot()

        self.tick += 1

        # -------------------------------------------------
        # Simulate changing node conditions
        # -------------------------------------------------

        for node in self.nodes.values():

            if node.healthy:

                node.cpu_used = max(

                    0.0,

                    min(

                        node.cpu_capacity,

                        node.cpu_used
                        +
                        random.uniform(
                            -0.5,
                            0.8
                        )
                    )
                )

                node.memory_used = max(

                    0.0,

                    min(

                        node.memory_capacity,

                        node.memory_used
                        +
                        random.uniform(
                            -0.4,
                            0.5
                        )
                    )
                )

                node.latency_ms = max(

                    5.0,

                    node.latency_ms
                    +
                    random.uniform(
                        -3,
                        4
                    )
                )

                node.packet_loss = max(

                    0.0,

                    min(

                        100.0,

                        node.packet_loss
                        +
                        random.uniform(
                            -1,
                            1
                        )
                    )
                )

        # -------------------------------------------------
        # Simulate workload demand
        # -------------------------------------------------

        for workload in self.workloads.values():

            if workload.status == "running":

                workload.demand = min(

                    100.0,

                    max(

                        0.0,

                        workload.demand
                        +
                        random.uniform(
                            -3,
                            5
                        )
                    )
                )

                workload.state[
                    "processed_events"
                ] = (

                    workload.state.get(
                        "processed_events",
                        0
                    )

                    +

                    random.randint(
                        1,
                        10
                    )
                )

        # -------------------------------------------------
        # Autonomous mode
        # -------------------------------------------------

        if self.auto_mode:

            for workload in self.workloads.values():

                if workload.status != "running":

                    continue

                decision = (
                    self.scheduler.decide(
                        workload,
                        self.nodes
                    )
                )

                self.apply_decision(
                    workload,
                    decision
                )

        # -------------------------------------------------
        # Record metrics
        # -------------------------------------------------

        self.metrics.record(

            self.nodes,

            self.workloads
        )

        return self.snapshot()

    # =====================================================
    # APPLY SCHEDULER DECISION
    # =====================================================

    def apply_decision(
        self,
        workload: Workload,
        decision: Dict
    ):

        action = decision["action"]

        # Stay
        if action == "stay":

            return decision

        target_id = decision.get(
            "to_node"
        )

        # -------------------------------------------------
        # Migration
        # -------------------------------------------------

        if (
            action == "move"
            and workload.node_id
            and target_id
        ):

            result = self.migration.migrate(

                workload,

                self.nodes[
                    workload.node_id
                ],

                self.nodes[
                    target_id
                ]
            )

            if result["success"]:

                self.events.append(
                    result["event"]
                )

                self.metrics.record_event(
                    result["event"]
                )

        # -------------------------------------------------
        # Recovery
        # -------------------------------------------------

        elif action == "recover":

            result = self.recovery.recover(

                workload,

                self.nodes
            )

            if result["success"]:

                self.events.append(
                    result["event"]
                )

                self.metrics.record_event(
                    result["event"]
                )

        return decision

    # =====================================================
    # TRIGGER DEMO SCENARIOS
    # =====================================================

    def trigger(
        self,
        scenario: str
    ):

        # -------------------------------------------------
        # Traffic Surge
        # -------------------------------------------------

        if scenario == "traffic_surge":

            for workload in self.workloads.values():

                workload.demand = min(

                    100.0,

                    workload.demand + 30
                )

            self.events.append({

                "type":
                    "scenario",

                "scenario":
                    scenario
            })

        # -------------------------------------------------
        # Network Failure
        # -------------------------------------------------

        elif scenario == "network_failure":

            node = self.nodes.get(
                "edge-01"
            )

            if node:

                node.latency_ms = 250

                node.packet_loss = 25

            self.events.append({

                "type":
                    "scenario",

                "scenario":
                    scenario,

                "node":
                    "edge-01"
            })

        # -------------------------------------------------
        # Kill Node
        # -------------------------------------------------

        elif scenario == "kill_node":

            node = self.nodes.get(
                "edge-01"
            )

            if node:

                node.healthy = False

            self.events.append({

                "type":
                    "scenario",

                "scenario":
                    scenario,

                "node":
                    "edge-01"
            })

        # -------------------------------------------------
        # Manual Migration
        # -------------------------------------------------

        elif scenario == "migrate":

            workload = self.workloads.get(
                "traffic-controller"
            )

            if (
                not workload
                or not workload.node_id
            ):

                raise HTTPException(

                    404,

                    "Traffic controller workload not found."
                )

            decision = (
                self.scheduler.decide(
                    workload,
                    self.nodes
                )
            )

            if decision["action"] == "stay":

                ranked = (
                    decision[
                        "ranked_candidates"
                    ]
                )

                alternatives = [

                    r

                    for r in ranked

                    if r["node_id"]
                    != workload.node_id
                ]

                if not alternatives:

                    return self.snapshot()

                decision["action"] = "move"

                decision["to_node"] = (
                    alternatives[0]["node_id"]
                )

            self.apply_decision(
                workload,
                decision
            )

        # -------------------------------------------------
        # AI Prediction
        # -------------------------------------------------

        elif scenario == "ai_predict":

            self.ai.observe(
                self.nodes
            )

            self.events.append({

                "type":
                    "scenario",

                "scenario":
                    scenario
            })

        # -------------------------------------------------
        # Auto Mode
        # -------------------------------------------------

        elif scenario == "auto_mode":

            self.auto_mode = (
                not self.auto_mode
            )

            self.events.append({

                "type":
                    "mode",

                "auto_mode":
                    self.auto_mode
            })

        else:

            raise HTTPException(

                400,

                f"Unknown scenario: {scenario}"
            )

        return self.step()


# =========================================================
# GLOBAL SIMULATION INSTANCE
# =========================================================

simulation = Simulation()


# =========================================================
# API ROUTES
# =========================================================

@app.get("/")
def root():

    return {

        "name":
            "EdgePilot AI",

        "status":
            "online",

        "message":
            "Autonomous cloud-edge computing simulation API"
    }


# ---------------------------------------------------------
# Complete state
# ---------------------------------------------------------

@app.get("/api/state")
def get_state():

    return simulation.snapshot()
# ---------------------------------------------------------
# Nodes
# ---------------------------------------------------------

@app.get("/api/nodes")
def get_nodes():
    return [
        simulation.node_dict(node)
        for node in simulation.nodes.values()
    ]


# ---------------------------------------------------------
# Start simulation
# ---------------------------------------------------------

@app.post("/api/simulation/start")
def start_simulation():

    simulation.running = True

    return {
        "success": True,
        "running": simulation.running,
        "state": simulation.snapshot()
    }


# ---------------------------------------------------------
# Stop simulation
# ---------------------------------------------------------

@app.post("/api/simulation/stop")
def stop_simulation():

    simulation.running = False

    return {
        "success": True,
        "running": simulation.running,
        "state": simulation.snapshot()
    }


# ---------------------------------------------------------
# Simulation reset
# ---------------------------------------------------------

@app.post("/api/simulation/reset")
def simulation_reset():

    simulation.reset()

    return {
        "success": True,
        "running": simulation.running,
        "state": simulation.snapshot()
    }

# ---------------------------------------------------------
# Reset
# ---------------------------------------------------------

@app.post("/api/reset")
def reset():

    simulation.reset()

    return simulation.snapshot()


# ---------------------------------------------------------
# Simulation step
# ---------------------------------------------------------

@app.post("/api/step")
def step():

    return simulation.step()


# ---------------------------------------------------------
# Scenario
# ---------------------------------------------------------

@app.post("/api/scenario/{scenario}")
def scenario(
    scenario: str
):

    return simulation.trigger(
        scenario
    )


# ---------------------------------------------------------
# Individual workload decision
# ---------------------------------------------------------

@app.post("/api/decision/{workload_id}")
def make_decision(
    workload_id: str
):

    workload = simulation.workloads.get(
        workload_id
    )

    if not workload:

        raise HTTPException(
            404,
            "Workload not found."
        )

    decision = (
        simulation.scheduler.decide(
            workload,
            simulation.nodes
        )
    )

    simulation.apply_decision(
        workload,
        decision
    )

    simulation.metrics.record(

        simulation.nodes,

        simulation.workloads,

        decision
    )

    return decision


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

@app.get("/api/metrics")
def metrics():

    return {

        "current":
            simulation.metrics.current(),

        "evaluation":
            simulation.metrics.evaluation()
    }


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

@app.get("/api/evaluation")
def evaluation():

    return simulation.metrics.evaluation()


# ---------------------------------------------------------
# Scheduling decisions
# ---------------------------------------------------------

@app.get("/api/decisions")
def decisions():

    return simulation.scheduler.decisions()


# ---------------------------------------------------------
# Events
# ---------------------------------------------------------

@app.get("/api/events")
def events():
    return simulation.events[-100:]