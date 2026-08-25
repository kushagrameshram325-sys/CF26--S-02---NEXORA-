
---

# `README.md`

This is the **first file a judge/developer should read**.

```markdown
# EdgePilot AI

## Autonomous Cloud-Edge Computing Fabric

EdgePilot AI is a software-only prototype for autonomous workload
placement across cloud, regional, and edge compute resources.

The system continuously observes simulated infrastructure conditions,
uses AI-assisted prediction and anomaly detection, and dynamically
decides whether workloads should remain where they are, migrate,
replicate, or recover.

---

## Problem

Distributed workloads can run across:

- Centralized cloud resources
- Regional compute clusters
- Software edge nodes

Static workload placement can become inefficient when:

- Application demand changes
- Network latency changes
- Resource availability changes
- Network quality degrades
- Compute nodes fail

EdgePilot AI addresses these conditions through autonomous,
condition-aware workload scheduling.

---

## Key Features

### Dynamic Scheduling

Selects suitable compute nodes using:

- CPU availability
- RAM availability
- Latency
- Bandwidth
- Node health
- GPU availability
- Workload requirements

### AI Demand Prediction

Predicts changes in workload demand.

### Anomaly Detection

Detects unusual infrastructure conditions.

### Workload Migration

Moves workloads when another node provides a significantly better
execution environment.

### Workload Replication

Creates additional workload instances when required.

### Failure Recovery

Automatically restores workloads after node failure.

### State Preservation

Uses checkpoints to preserve workload state during migration and recovery.

### Evaluation

Compares dynamic scheduling against a static-placement baseline.

---

## Architecture

```text
Frontend
   │
   ▼
Backend
   │
   ├── Simulator
   ├── AI Engine
   ├── Scheduler
   ├── Migration
   ├── Recovery
   └── Metrics