# EdgePilot AI — System Architecture

> Autonomous Cloud-Edge Workload Scheduling, Migration & Recovery

---

## 1. Overview

EdgePilot AI is a software-only prototype for intelligent workload
orchestration across a simulated cloud-edge computing fabric.

The system continuously monitors:

- Compute resources
- Memory utilization
- Network latency
- Bandwidth
- Packet loss
- Node health
- GPU availability
- Workload requirements

It combines rule-based scheduling with AI-assisted prediction and
anomaly detection to determine where workloads should execute.

The system can dynamically:

- Keep workloads on their current node
- Migrate workloads to a better node
- Replicate critical workloads
- Recover workloads after node failure
- Preserve workload state using checkpoints
- Measure system performance
- Compare dynamic scheduling against static placement

The prototype uses simulated infrastructure, allowing the complete
system to be demonstrated without requiring physical edge devices.

---

# 2. Design Goals

The architecture is designed around the following goals.

### 2.1 Dynamic Placement

Workloads should be placed according to current infrastructure
conditions rather than using fixed placement.

### 2.2 Low Latency

Latency-sensitive workloads should preferably run closer to users
and data sources.

### 2.3 Resource Awareness

The scheduler must consider available CPU, RAM, GPU and network
resources before selecting a node.

### 2.4 Fault Tolerance

Workloads should be recoverable when a node fails.

### 2.5 State Preservation

Workload state should survive migration and recovery through
checkpoints and replicas.

### 2.6 AI-Assisted Decisions

AI should provide prediction and anomaly information to improve
scheduling decisions.

AI must not bypass hard infrastructure constraints.

### 2.7 Explainability

Every scheduling action should have an understandable reason.

For example:

```text
MIGRATE Traffic Controller

Reason:
- Edge-01 latency exceeded SLA
- Edge-02 has sufficient CPU
- Edge-02 satisfies latency requirement
- Edge-02 provides better overall score