# Chaos Engineering Experiments

This directory contains Chaos Mesh experiments to test the resilience of the AI TestOps system.

## Prerequisites

Install Chaos Mesh in your Kubernetes cluster:

```bash
curl -sSL https://mirrors.chaos-mesh.org/v2.6.0/install.sh | bash
```

Or using Helm:

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh -n=chaos-mesh --version 2.6.0 --create-namespace
```

## Running Experiments

### 1. Pod Failure Experiment
Tests system resilience when pods randomly fail:

```bash
kubectl apply -f chaos-experiments/pod-failure.yaml
```

### 2. Network Delay Experiment
Simulates network latency between services:

```bash
kubectl apply -f chaos-experiments/network-delay.yaml
```

### 3. CPU Stress Experiment
Tests system behavior under high CPU load:

```bash
kubectl apply -f chaos-experiments/cpu-stress.yaml
```

### 4. Memory Stress Experiment
Tests memory pressure handling:

```bash
kubectl apply -f chaos-experiments/memory-stress.yaml
```

### 5. Kafka Partition Experiment
Tests Kafka failure scenarios:

```bash
kubectl apply -f chaos-experiments/kafka-partition.yaml
```

## Monitoring During Experiments

Monitor the system during chaos experiments:

```bash
# Watch pod status
kubectl get pods -n ai-testops -w

# Check HPA status
kubectl get hpa -n ai-testops -w

# View logs
kubectl logs -n ai-testops -l app=django-app --tail=100 -f
```

## Stopping Experiments

To stop a running experiment:

```bash
kubectl delete -f chaos-experiments/<experiment-file>.yaml
```

## Expected Outcomes

- **Pod Failure**: System should automatically recover with new pods
- **Network Delay**: Application should handle increased latency gracefully
- **CPU Stress**: HPA should scale up pods automatically
- **Memory Stress**: Pods should not OOM, or should restart gracefully
- **Kafka Partition**: Consumers should reconnect automatically
