# GitOps Workflow - AI TestOps

## 📊 Визуализация полного процесса

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DEVELOPER WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────┘

1. Developer makes changes
   │
   ├─── Edit code (Django, Consumer, etc.)
   ├─── Edit Kubernetes manifests
   └─── Edit Helm values
   │
   ▼
2. Git Push to GitHub
   │
   git add .
   git commit -m "Update replicas"
   git push origin main
   │
   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                      CI/CD PIPELINE (GitHub Actions)                 │
└─────────────────────────────────────────────────────────────────────┘

3. GitHub Actions Triggered
   │
   ├─── Checkout code
   │
   ▼
   ├─── Lint & Test
   │    ├─── Python linting (flake8)
   │    ├─── Run Django tests
   │    └─── Code coverage check
   │
   ▼
   ├─── Build Docker Images
   │    ├─── Build Django image
   │    └─── Build Consumer image
   │
   ▼
   ├─── Security Scan
   │    └─── Trivy vulnerability scan
   │
   ▼
   ├─── Push to Docker Hub
   │    ├─── huynhduc0/ai-testops-django:latest
   │    └─── huynhduc0/ai-testops-consumer:latest
   │
   ▼
   └─── Update Helm Chart (if image tag changed)
        └─── Update values.yaml with new image tag
   │
   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                      GITOPS DEPLOYMENT (ArgoCD)                      │
└─────────────────────────────────────────────────────────────────────┘

4. ArgoCD detects Git changes (polling every 3 min)
   │
   ▼
5. ArgoCD compares Git state vs Kubernetes state
   │
   ├─── IF OutOfSync:
   │    │
   │    ▼
   │    Auto-Sync enabled → Proceed to deploy
   │    │
   │    ▼
   │    ├─── Generate Kubernetes manifests from Helm
   │    ├─── Validate manifests
   │    └─── Apply changes to cluster
   │
   └─── IF Synced:
        └─── No action needed
   │
   ▼
6. Kubernetes applies changes
   │
   ├─── Update Deployments
   │    ├─── Rolling update strategy
   │    └─── Respect PodDisruptionBudget
   │
   ├─── Update ConfigMaps/Secrets
   │    └─── Trigger pod restart if needed
   │
   ├─── Update Services
   │
   ├─── Update HPA
   │    └─── Adjust min/max replicas
   │
   └─── Update Ingress
   │
   ▼
7. Health checks
   │
   ├─── Readiness probes check
   │    └─── Wait until all pods ready
   │
   └─── Liveness probes monitoring
        └─── Auto-restart unhealthy pods
   │
   ▼
8. ArgoCD reports status
   │
   ├─── Health Status: Healthy ✅
   └─── Sync Status: Synced ✅

┌─────────────────────────────────────────────────────────────────────┐
│                      SELF-HEALING                                    │
└─────────────────────────────────────────────────────────────────────┘

9. Manual change detected (e.g., kubectl scale)
   │
   ▼
10. ArgoCD detects drift
    │
    OutOfSync status
    │
    ▼
11. Self-Heal enabled → Auto-revert to Git state
    │
    ├─── Rollback manual changes
    └─── Restore desired state from Git
    │
    ▼
12. System back to Synced ✅

┌─────────────────────────────────────────────────────────────────────┐
│                      ROLLBACK SCENARIO                               │
└─────────────────────────────────────────────────────────────────────┘

13. Bad deployment detected
    │
    ├─── Application errors
    ├─── Failed health checks
    └─── User reports issues
    │
    ▼
14. Rollback options
    │
    ├─── Option A: Git revert
    │    │
    │    git revert <commit-hash>
    │    git push
    │    │
    │    → ArgoCD auto-sync to previous version
    │
    └─── Option B: ArgoCD rollback
         │
         argocd app rollback ai-testops <revision-id>
         │
         → Instant rollback to specific revision
    │
    ▼
15. System restored ✅
```

## 🔄 Детальный поток данных

### Application Update Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│Developer │────▶│   Git    │────▶│  GitHub  │────▶│  Docker  │
│          │     │ (main)   │     │ Actions  │     │   Hub    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                        │                                 │
                        │                                 │
                        ▼                                 ▼
                 ┌──────────┐                      ┌──────────┐
                 │  ArgoCD  │◀─────────────────────│New Image │
                 │          │  Update values.yaml  │   Tag    │
                 └──────────┘                      └──────────┘
                        │
                        │ Sync
                        ▼
                 ┌──────────┐
                 │Kubernetes│
                 │ Cluster  │
                 └──────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ Django  │   │Consumer │   │  Kafka  │
    │  Pods   │   │  Pods   │   │  Pods   │
    └─────────┘   └─────────┘   └─────────┘
```

### Configuration Update Flow

```
values.yaml change
        │
        ▼
    Git Push
        │
        ▼
   ArgoCD Sync
        │
        ├──▶ ConfigMap updated
        │         │
        │         ▼
        │    Pods restart (if needed)
        │
        ├──▶ HPA updated
        │         │
        │         ▼
        │    Replicas adjusted
        │
        └──▶ Resources updated
                  │
                  ▼
             Pods rescheduled
```

## 🔒 Security Flow

```
Secrets in Git (encrypted)
        │
        ▼
ArgoCD reads secrets
        │
        ▼
Create Kubernetes Secrets
        │
        ▼
Mount to Pods
        │
        ├──▶ Environment variables
        └──▶ Volume mounts
```

## 📈 Scaling Flow

```
Load increase
        │
        ▼
HPA monitors metrics
        │
   ┌────┴────┐
   │ CPU >70%│
   └────┬────┘
        │
        ▼
  Scale up pods
        │
        ▼
ArgoCD ignores replica count
(ignoreDifferences configured)
        │
        ▼
System handles load ✅
```

## 🔥 Chaos Engineering Flow

```
Apply Chaos Experiment
        │
        ▼
Chaos Mesh kills pods
        │
        ▼
Kubernetes detects failure
        │
        ├──▶ Restart pods (liveness)
        ├──▶ Remove from service (readiness)
        └──▶ HPA scales up
        │
        ▼
System recovers
        │
        ▼
ArgoCD maintains desired state
        │
        ▼
Health Status: Healthy ✅
```

## 🎯 Full Lifecycle

```
Day 1: Initial Deploy
┌─────────────────────────────────────┐
│ kubectl apply -f argocd/app.yaml   │
│ → ArgoCD creates all resources      │
│ → Application running               │
└─────────────────────────────────────┘

Day 2-N: Continuous Updates
┌─────────────────────────────────────┐
│ Developer pushes code               │
│ → CI builds & tests                 │
│ → New image pushed                  │
│ → Git updated                       │
│ → ArgoCD auto-syncs                 │
│ → Rolling update                    │
│ → Zero downtime                     │
└─────────────────────────────────────┘

Incident: Bad Deploy
┌─────────────────────────────────────┐
│ Health checks fail                  │
│ → Alert triggered                   │
│ → git revert + push                 │
│ → ArgoCD auto-syncs                 │
│ → Rollback to previous version      │
│ → System recovered                  │
└─────────────────────────────────────┘

Chaos Day: Testing Resilience
┌─────────────────────────────────────┐
│ Apply pod-failure experiment        │
│ → Pods killed randomly              │
│ → K8s restarts pods                 │
│ → HPA scales up                     │
│ → Traffic routes to healthy pods    │
│ → Zero user impact                  │
│ → ArgoCD maintains state            │
└─────────────────────────────────────┘
```

## 🔍 Monitoring Flow

```
Application Metrics
        │
        ├──▶ Prometheus scrapes
        │         │
        │         ▼
        │    Store metrics
        │         │
        │         ▼
        │    Grafana visualizes
        │
        ├──▶ ArgoCD monitors health
        │         │
        │         ▼
        │    Report to UI
        │
        └──▶ HPA monitors CPU/Memory
                  │
                  ▼
             Scale decisions
```

## 📊 Decision Tree

```
Change detected in Git
        │
        ▼
    Is it code?
        │
   ┌────┴────┐
  YES        NO
   │          │
   ▼          ▼
CI/CD    Is it config?
   │          │
   │     ┌────┴────┐
   │    YES       NO
   │     │         │
   │     ▼         ▼
   │  ArgoCD   Is it manifest?
   │  Sync         │
   │     │    ┌────┴────┐
   │     │   YES       NO
   │     │    │         │
   │     │    ▼         ▼
   │     │ ArgoCD    Ignore
   │     │ Sync
   │     │    │
   └─────┴────┴──▶ Deploy to K8s
                        │
                        ▼
                   Success?
                        │
                   ┌────┴────┐
                  YES       NO
                   │         │
                   ▼         ▼
                Synced   Rollback
```

## 🚀 Quick Reference

### Проверка статуса на каждом этапе

```bash
# 1. Git changes
git log --oneline -5

# 2. CI/CD status
gh run list --limit 5

# 3. Docker images
docker pull huynhduc0/ai-testops-django:latest

# 4. ArgoCD sync status
argocd app get ai-testops

# 5. Kubernetes resources
kubectl get all -n ai-testops

# 6. Pod health
kubectl get pods -n ai-testops -o wide

# 7. HPA metrics
kubectl get hpa -n ai-testops

# 8. Application endpoint
curl http://ai-testops.example.com/health
```

### Ручное управление workflow

```bash
# Trigger manual sync
argocd app sync ai-testops

# Force sync (ignore differences)
argocd app sync ai-testops --force

# Rollback to previous
argocd app rollback ai-testops

# View sync history
argocd app history ai-testops

# Pause auto-sync
argocd app set ai-testops --sync-policy none

# Resume auto-sync
argocd app set ai-testops --sync-policy automated
```

## 📝 Notes

- **Auto-sync interval**: 3 minutes (configurable)
- **Self-heal delay**: ~5 seconds after drift detection
- **Rollback time**: < 1 minute for typical deployment
- **Zero downtime**: Achieved via rolling updates + readiness probes
- **Git as single source of truth**: All changes must go through Git
