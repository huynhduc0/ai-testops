# Защита проекта - AI TestOps

## 📊 Презентация (10 минут)

### 1. Обзор проекта (2 минуты)

**AI TestOps** - распределенная система для автоматизации тестирования API с использованием AI.

**Ключевые цифры:**
- 5 микросервисов (Django App, Test Consumer, PostgreSQL, Kafka, Zookeeper)
- 100% покрытие требований курса
- GitOps deployment через ArgoCD
- Автомасштабирование от 2 до 10 реплик
- Chaos Engineering: 5 типов экспериментов

### 2. Архитектурные решения (3 минуты)

#### Микросервисная архитектура

```
User → Ingress → Django App → Kafka → Test Consumer → PostgreSQL
                                ↓
                           Zookeeper
```

**Обоснование:**
1. **Django App** - Web интерфейс и API
   - Почему Django? Быстрая разработка, встроенный ORM, admin panel
   - REST API для управления тестами
   - Продюсер сообщений в Kafka

2. **Test Consumer** - Асинхронный воркер
   - Почему отдельный сервис? Изоляция выполнения тестов от Web-слоя
   - Независимое масштабирование (HPA 2-8 реплик)
   - Консьюмер Kafka для получения задач

3. **Kafka + Zookeeper** - Message Broker
   - Почему Kafka? Гарантированная доставка, масштабируемость, fault tolerance
   - Асинхронная обработка тестов
   - Decoupling между сервисами

4. **PostgreSQL** - Реляционная БД
   - Почему PostgreSQL? ACID, reliability, Django ORM support
   - Персистентное хранилище (PVC 5Gi)

#### GitOps с ArgoCD

**Преимущества:**
- ✅ Декларативность: вся инфраструктура в Git
- ✅ Версионирование: rollback одной командой
- ✅ Автоматизация: auto-sync, self-heal
- ✅ Аудит: все изменения tracked

**Workflow:**
```
Git Push → GitHub Actions (CI) → Update Image Tag → ArgoCD Sync → K8s Deploy
```

### 3. Демонстрация компонентов (4 минуты)

#### 3.1 CI/CD Pipeline

```bash
# GitHub Actions
- Lint & Test (Python)
- Build Docker images
- Push to registry
- Security scan (Trivy)
- Update Helm values
```

**Показать:**
- Открыть `.github/workflows/ci.yaml`
- Показать последний successful run
- Показать Docker Hub images

#### 3.2 GitOps Deploy

```bash
# ArgoCD Application
kubectl get application -n argocd ai-testops

# Sync status
argocd app get ai-testops
```

**Показать:**
- ArgoCD UI (health status, sync status)
- Auto-sync в действии
- Rollback example

#### 3.3 HPA Autoscaling

```bash
# Horizontal Pod Autoscaler
kubectl get hpa -n ai-testops

# Текущее состояние
kubectl get pods -n ai-testops
```

**Показать:**
- HPA metrics (CPU, Memory)
- Scaling в действии при нагрузке

#### 3.4 Kafka Pub/Sub

```bash
# Kafka UI
kubectl port-forward svc/kafka-ui -n ai-testops 8080:8080
```

**Показать:**
- Topics
- Messages flow
- Consumer groups

#### 3.5 Chaos Engineering

```bash
# Pod failure experiment
kubectl apply -f chaos-experiments/pod-failure.yaml

# Наблюдение
kubectl get podchaos -n ai-testops
```

**Показать:**
- Chaos Mesh эксперимент
- Восстановление системы
- HPA реакция

### 4. Безопасность и отказоустойчивость (1 минута)

**Реализовано:**
- ✅ RBAC: ServiceAccounts, Roles, RoleBindings
- ✅ Secrets для чувствительных данных
- ✅ NetworkPolicy: изоляция трафика
- ✅ Probes: liveness, readiness для всех сервисов
- ✅ Circuit Breaker: retry/fallback механизмы
- ✅ PodDisruptionBudget

---

## 🎯 Соответствие требованиям (60 баллов)

| Требование | Баллы | Статус | Доказательство |
|-----------|-------|---------|----------------|
| 3+ микросервиса | 10/10 | ✅ | 5 сервисов в `helm/ai-testops/templates/` |
| Kubernetes + Helm | 10/10 | ✅ | Helm chart с templates, values.yaml |
| GitOps (ArgoCD) | 10/10 | ✅ | `argocd/application.yaml`, auto-sync |
| CI/CD Pipeline | 10/10 | ✅ | `.github/workflows/ci.yaml` |
| Secrets/RBAC | 5/5 | ✅ | `templates/rbac.yaml`, `templates/secrets.yaml` |
| Autoscaling | 5/5 | ✅ | HPA для Django и Consumer |
| Probes | 5/5 | ✅ | Readiness/Liveness в Deployments |
| Kafka/Pub-Sub | 5/5 | ✅ | Kafka + Producer + Consumer |
| Circuit Breaker | 5/5 | ✅ | Retry logic в consumer |
| Chaos Engineering | 5/5 | ✅ | 5 экспериментов в `chaos-experiments/` |

**Итого: 60/60 баллов**

---

## 💡 Вопросы для защиты

### Архитектура

**Q: Почему выбрана микросервисная архитектура?**
A: Для независимого масштабирования компонентов (web ≠ worker), fault isolation, technology flexibility.

**Q: Почему Kafka, а не RabbitMQ или Redis?**
A: Kafka обеспечивает гарантированную доставку, высокую пропускную способность, persistence сообщений и better scalability для event streaming.

**Q: Как обеспечивается отказоустойчивость?**
A: 
- HPA для автомасштабирования
- Liveness/Readiness probes для health checks
- PodDisruptionBudget для graceful updates
- Kafka replication для message persistence
- PVC для database persistence

### GitOps

**Q: В чем преимущество GitOps перед традиционным CI/CD?**
A:
- Git как single source of truth
- Декларативность vs императивность
- Easy rollback (git revert)
- Better auditability
- Self-healing capabilities

**Q: Что произойдет если вручную изменить replicas в кластере?**
A: ArgoCD обнаружит drift и выполнит self-heal - вернет значение из Git согласно values.yaml.

### Kubernetes

**Q: Как работает HPA?**
A: HPA мониторит metrics (CPU/Memory), сравнивает с target utilization и scale up/down replicas в пределах min/max.

**Q: Разница между liveness и readiness probe?**
A:
- Liveness: контролирует живость пода (restart при failure)
- Readiness: контролирует готовность получать трафик (remove from Service endpoints при failure)

**Q: Как настроен Service Discovery?**
A: Через Kubernetes DNS (CoreDNS) - сервисы доступны по имени `<service>.<namespace>.svc.cluster.local`.

### Безопасность

**Q: Как обеспечена безопасность?**
A:
- RBAC для разграничения доступа
- Secrets для чувствительных данных
- NetworkPolicy для изоляции трафика
- ServiceAccounts для подов
- TLS/HTTPS через Ingress

**Q: Где хранятся API ключи?**
A: В Kubernetes Secrets, смонтированных как environment variables или volumes в подах.

### Chaos Engineering

**Q: Какие типы chaos экспериментов реализованы?**
A:
1. Pod Failure - убийство подов
2. Network Delay - задержка сети
3. CPU Stress - нагрузка на CPU
4. Memory Stress - нагрузка на память
5. Kafka Partition - сбой Kafka partition

**Q: Как система реагирует на pod failure?**
A:
- Kubernetes автоматически рестартует pod
- HPA создает новые replicas если нужно
- Service продолжает работать с оставшимися healthy pods
- Kafka гарантирует доставку сообщений

### CI/CD

**Q: Что происходит при git push?**
A:
1. GitHub Actions trigger
2. Запуск тестов
3. Build Docker images
4. Push в registry
5. Update image tag в values.yaml
6. ArgoCD detect changes
7. Auto-sync to K8s

---

## 👥 Команда разработки

| Имя | Роль | Вклад | Коммиты |
|-----|------|-------|---------|
| [Имя 1] | Team Lead | ArgoCD, CI/CD, Helm | X коммитов |
| [Имя 2] | Backend Dev | Django App, Consumer | X коммитов |
| [Имя 3] | DevOps | Kubernetes, Monitoring | X коммитов |
| [Имя 4] | QA/SRE | Chaos Engineering, Tests | X коммитов |

**Проверка вклада:**
```bash
git log --author="Name" --oneline | wc -l
git log --author="Name" --pretty=format:"%h %s" --shortstat
```

---

## 📈 Метрики проекта

```bash
# Количество файлов
find . -type f -name "*.yaml" -o -name "*.py" | wc -l

# Строки кода
cloc .

# Kubernetes ресурсы
kubectl get all -n ai-testops
```

**Статистика:**
- Python файлов: ~50
- YAML манифестов: ~30
- Docker images: 2
- Helm templates: 12
- Chaos experiments: 5
- CI/CD workflows: 1

---

## 🎓 Выводы

**Полученные навыки:**
1. ✅ Проектирование микросервисной архитектуры
2. ✅ Работа с Kubernetes и Helm
3. ✅ Реализация GitOps с ArgoCD
4. ✅ Настройка CI/CD pipeline
5. ✅ Обеспечение безопасности (RBAC, Secrets)
6. ✅ Автомасштабирование и отказоустойчивость
7. ✅ Chaos Engineering тестирование
8. ✅ Pub/Sub паттерн с Kafka

**Технологии:**
- Kubernetes, Helm, ArgoCD
- Docker, GitHub Actions
- Python, Django
- Kafka, PostgreSQL
- Chaos Mesh, Prometheus

---

## 📚 Ресурсы

- [GitHub Repository](https://github.com/huynhduc0/ai-testops)
- [Полная документация](DEPLOYMENT.md)
- [ArgoCD Guide](argocd/README.md)
- [Chaos Experiments](chaos-experiments/README.md)
- [YouTube Demo](https://www.youtube.com/watch?v=tNE39IoXOoc)
