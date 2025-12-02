# AI TestOps - Distributed Systems Project

> Проект по курсу "Проектирование и разработка распределенных программных систем"

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Архитектура системы](#архитектура-системы)
- [Технический стек](#технический-стек)
- [Соответствие требованиям курса](#соответствие-требованиям-курса)
- [Быстрый старт](#быстрый-старт)
- [Развертывание](#развертывание)
- [CI/CD и GitOps](#cicd-и-gitops)
- [Мониторинг и логирование](#мониторинг-и-логирование)
- [Chaos Engineering](#chaos-engineering)
- [Команда разработки](#команда-разработки)

---

## Описание проекта

AI TestOps - это распределенная система для автоматизации тестирования API с использованием искусственного интеллекта. Проект реализует микросервисную архитектуру, развернутую в Kubernetes с полным соблюдением требований курса.

### Основные функции

- 🤖 Автоматическая генерация тестовых скриптов для API на основе Swagger
- ⚡ Асинхронное выполнение тестов через Kafka
- 📊 Визуализация результатов тестирования
- 🔄 Интеграция с LLM (Gemini) для генерации тестов
- 📈 Мониторинг и метрики через Grafana

---

## Архитектура системы

### Диаграмма компонентов

```
┌─────────────────────────────────────────────────────────────────┐
│                        Ingress (NGINX)                          │
│                     SSL/TLS (cert-manager)                      │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌────────────────────────────┐
│   Django App Service      │   │   Kafka UI Service         │
│   (ClusterIP)             │   │   (ClusterIP)              │
└───────────┬───────────────┘   └────────────┬───────────────┘
            │                                 │
            ▼                                 ▼
┌───────────────────────────┐   ┌────────────────────────────┐
│  Django App Deployment    │   │   Kafka UI Deployment      │
│  • Replicas: 2-10 (HPA)   │   │   • Replicas: 1            │
│  • Probes: Ready/Live     │   │   • Monitoring UI          │
│  • Resources: CPU/Mem     │   └────────────────────────────┘
└───────┬──────────┬────────┘
        │          │
        │          └──────────────┐
        ▼                         ▼
┌──────────────────┐   ┌────────────────────────────┐
│  PostgreSQL      │   │   Kafka Cluster            │
│  • PVC: 5Gi      │   │   • PVC: 10Gi              │
│  • Probes        │   │   • Replication: 1         │
└──────────────────┘   └───────────┬────────────────┘
                                   │
                                   ▼
                       ┌────────────────────────────┐
                       │   Zookeeper                │
                       │   • PVC: 2Gi               │
                       │   • Client Port: 2181      │
                       └────────────────────────────┘
                                   ▲
                                   │
                       ┌────────────────────────────┐
                       │  Test Execute Consumer     │
                       │  • Replicas: 2-8 (HPA)     │
                       │  • Kafka Consumer          │
                       └────────────────────────────┘
```

### Микросервисы

1. **Django App** - Основное веб-приложение
   - REST API для управления тестами
   - Интеграция с Swagger
   - Продюсер сообщений в Kafka

2. **Test Execute Consumer** - Сервис выполнения тестов
   - Консьюмер сообщений из Kafka
   - Асинхронное выполнение тестовых скриптов
   - Запись результатов в БД

3. **PostgreSQL** - База данных
   - Хранение тестов и результатов
   - Персистентное хранилище

4. **Kafka + Zookeeper** - Брокер сообщений
   - Асинхронная коммуникация между сервисами
   - Гарантия доставки сообщений

5. **Kafka UI** - Веб-интерфейс для мониторинга Kafka
   - Визуализация топиков и сообщений
   - Метрики производительности

---

## Технический стек

### Backend & Infrastructure
- **Python 3.11** - Язык программирования
- **Django 5.1** - Web framework
- **PostgreSQL 13** - СУБД
- **Kafka** - Message broker
- **Docker** - Контейнеризация

### Kubernetes & Orchestration
- **Kubernetes** - Оркестрация контейнеров
- **Helm 3** - Управление пакетами
- **ArgoCD** - GitOps деплоймент
- **NGINX Ingress** - Ingress controller

### CI/CD & DevOps
- **GitHub Actions** - CI/CD пайплайн
- **Docker Hub** - Container registry
- **Trivy** - Security scanning

### Monitoring & Observability
- **Grafana Agent** - Метрики и логи
- **Prometheus** - Сбор метрик
- **Chaos Mesh** - Chaos engineering

---

## Соответствие требованиям курса

### ✅ Технические требования (60 баллов)

#### 1. Микросервисная архитектура (✅)
- **5 микросервисов**: Django App, Test Consumer, PostgreSQL, Kafka, Zookeeper
- **Взаимодействие**: REST API + Pub/Sub через Kafka
- **Service Discovery**: DNS в Kubernetes (`service.namespace.svc.cluster.local`)

#### 2. Развертывание в Kubernetes (✅)
- **Helm Charts**: Полная структура в `helm/ai-testops/`
- **Deployments**: Все сервисы развернуты через Deployment/StatefulSet
- **Services**: ClusterIP для внутренней коммуникации
- **Ingress**: NGINX Ingress с TLS

#### 3. GitOps и CI/CD (✅)
- **ArgoCD**: Автоматическая синхронизация из Git
- **GitHub Actions**: Автоматическая сборка и публикация образов
- **Автотесты**: Запуск тестов при каждом коммите
- **Security scanning**: Trivy для проверки уязвимостей

#### 4. Секреты и конфигурация (✅)
- **Secrets**: Для БД, API ключей
- **ConfigMaps**: Для настроек приложения
- **Environment variables**: Из Secrets и ConfigMaps

#### 5. Безопасность (✅)
- **RBAC**: ServiceAccounts, Roles, RoleBindings
- **NetworkPolicy**: Ограничение сетевого трафика
- **TLS/HTTPS**: Через Ingress с cert-manager
- **Least privilege**: Минимальные права для сервисов

#### 6. Autoscaling и отказоустойчивость (✅)
- **HPA**: Автомасштабирование по CPU и Memory
  - Django App: 2-10 реплик
  - Consumer: 2-8 реплик
- **Resource limits**: Requests и Limits для всех подов
- **Probes**: Readiness и Liveness для всех сервисов
- **PodDisruptionBudget**: Гарантия доступности

#### 7. Взаимодействие через Kafka (✅)
- **Pub/Sub модель**: Асинхронная обработка
- **Топики**: test-execution, test-results
- **Консьюмер группы**: Масштабируемая обработка

#### 8. Chaos Engineering (✅)
- **Chaos Mesh**: Установлен и настроен
- **Эксперименты**:
  - Pod failure (случайное удаление подов)
  - Network delay (задержка сети)
  - CPU stress (нагрузка на CPU)
  - Memory stress (нагрузка на память)
  - Kafka partition (разделение сети)

---

## Быстрый старт

### Предварительные требования

- Kubernetes cluster (minikube, kind, или облачный)
- Helm 3.x
- kubectl
- Docker
- ArgoCD (опционально)

### 1. Клонирование репозитория

```bash
git clone https://github.com/huynhduc0/ai-testops.git
cd ai-testops
```

### 2. Установка через Helm

```bash
# Создание namespace
kubectl create namespace ai-testops

# Установка Helm chart
helm install ai-testops ./helm/ai-testops -n ai-testops

# Проверка статуса
kubectl get pods -n ai-testops
```

### 3. Настройка Secrets

```bash
# Создание секретов для API ключей
kubectl create secret generic api-keys-secret \
  --from-literal=GEMINI_API_KEY=your-gemini-key \
  --from-literal=GRAFANA_CLOUD_API_KEY=your-grafana-key \
  -n ai-testops

# Для production используйте Sealed Secrets
```

### 4. Доступ к приложению

```bash
# Port-forward для локального доступа
kubectl port-forward -n ai-testops svc/django-app 8000:8000

# Открыть в браузере
open http://localhost:8000
```

---

## Развертывание

### GitOps с ArgoCD (Основной метод)

#### 1. Установка ArgoCD (Однократно)

```bash
# Установка ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Ожидание готовности
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd
```

#### 2. Доступ к ArgoCD UI

```bash
# Port-forward для доступа
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Получение пароля администратора
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Откройте браузер: `https://localhost:8080`
- **Username**: `admin`
- **Password**: (из команды выше)

#### 3. Развертывание приложения

```bash
# Применение ArgoCD Application
kubectl apply -f argocd/application.yaml

# Проверка статуса
kubectl get application -n argocd
```

**Готово!** ArgoCD автоматически:
- ✅ Синхронизирует код из Git
- ✅ Развертывает все микросервисы
- ✅ Отслеживает изменения
- ✅ Выполняет auto-sync (каждые 3 минуты)
- ✅ Self-healing при ручных изменениях

#### 4. Обновление приложения

Для обновления просто пушьте изменения в Git:

```bash
# Внесите изменения в values.yaml или templates
git add .
git commit -m "Update configuration"
git push origin main
```

ArgoCD автоматически обнаружит и применит изменения.

#### 5. Ручная синхронизация (Опционально)

```bash
# Через ArgoCD CLI
argocd app sync ai-testops

# Через UI
# Нажмите кнопку "Sync" в ArgoCD UI
```

### Альтернативный метод: Прямой Helm

> ⚠️ Не рекомендуется для production (нарушает принцип GitOps)

```bash
# Только для локальной разработки
helm upgrade --install ai-testops ./helm/ai-testops \
  --namespace ai-testops \
  --create-namespace \
  --values helm/ai-testops/values.yaml
```

---

## CI/CD и GitOps

### GitHub Actions Pipeline

Пайплайн автоматически:

1. **Test** - Запускает тесты
2. **Lint** - Проверяет код
3. **Build** - Собирает Docker образы
4. **Push** - Публикует в Docker Hub
5. **Security Scan** - Сканирует на уязвимости
6. **Update Helm** - Обновляет версию образа

### Настройка секретов GitHub

```bash
# Необходимые секреты в GitHub:
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
GEMINI_API_KEY=your-gemini-api-key
```

### ArgoCD GitOps

- **Auto-sync**: Автоматическая синхронизация из Git
- **Self-heal**: Автоматическое восстановление при изменениях
- **Prune**: Удаление ресурсов, отсутствующих в Git
- **Rollback**: Откат к предыдущей версии

---

## Мониторинг и логирование

### Метрики Prometheus

```yaml
# Основные метрики
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- http_requests_total
- kafka_consumer_lag
```

### Grafana Dashboards

- **Kubernetes Cluster**: Общее состояние кластера
- **Application Metrics**: Метрики приложения
- **Kafka Monitoring**: Состояние Kafka
- **HPA Status**: Автомасштабирование

### Логи

```bash
# Просмотр логов
kubectl logs -n ai-testops -l app=django-app --tail=100 -f

# Логи Kafka consumer
kubectl logs -n ai-testops -l app=test-execute-consumer -f

# Поиск ошибок
kubectl logs -n ai-testops --all-containers | grep ERROR
```

---

## Chaos Engineering

### Установка Chaos Mesh

```bash
curl -sSL https://mirrors.chaos-mesh.org/v2.6.0/install.sh | bash
```


### Запуск экспериментов

```bash
# 1. Pod Failure - Имитация падения пода
kubectl apply -f chaos-experiments/pod-failure.yaml

# 2. Network Delay - Задержка сети
kubectl apply -f chaos-experiments/network-delay.yaml

# 3. CPU Stress - Нагрузка на CPU
kubectl apply -f chaos-experiments/cpu-stress.yaml

# 4. Memory Stress - Нагрузка на память
kubectl apply -f chaos-experiments/memory-stress.yaml

# 5. Комплексный тест
kubectl apply -f chaos-experiments/workflow-comprehensive.yaml

# Просмотр статуса эксперимента
kubectl get podchaos -n ai-testops
kubectl describe podchaos django-pod-failure -n ai-testops

# Остановка эксперимента
kubectl delete -f chaos-experiments/pod-failure.yaml
```

### Наблюдение за результатами

```bash
# Мониторинг HPA во время chaos
kubectl get hpa -n ai-testops --watch

# Проверка восстановления
kubectl get pods -n ai-testops --watch

# Просмотр событий
kubectl get events -n ai-testops --sort-by='.lastTimestamp'
```

```bash
# Pod failure
kubectl apply -f chaos-experiments/pod-failure.yaml

# Network delay
kubectl apply -f chaos-experiments/network-delay.yaml

# CPU stress
kubectl apply -f chaos-experiments/cpu-stress.yaml

# Comprehensive workflow
kubectl apply -f chaos-experiments/workflow-comprehensive.yaml
```

### Мониторинг во время экспериментов

```bash
# Наблюдение за подами
kubectl get pods -n ai-testops -w

# Проверка HPA
kubectl get hpa -n ai-testops -w

# Метрики
kubectl top pods -n ai-testops
```

### Ожидаемые результаты

- ✅ Система автоматически восстанавливается после сбоев
- ✅ HPA масштабирует поды при нагрузке
- ✅ Network policies изолируют трафик
- ✅ Приложение остается доступным

---

## Команда разработки

### Участники проекта

| Имя | Роль | Вклад | GitHub |
|-----|------|-------|--------|
| **Member 1** | Team Lead, Backend | Django App, API, Database | [@member1](https://github.com/member1) |
| **Member 2** | DevOps Engineer | Kubernetes, Helm, CI/CD, ArgoCD | [@member2](https://github.com/member2) |
| **Member 3** | Backend Developer | Kafka Consumer, Tests, Chaos Engineering | [@member3](https://github.com/member3) |
| **Member 4** | Infrastructure | Monitoring, Security, NetworkPolicies | [@member4](https://github.com/member4) |

### Распределение задач

- **Member 1**: Django приложение, REST API, интеграция с БД
- **Member 2**: Kubernetes манифесты, Helm charts, CI/CD, ArgoCD
- **Member 3**: Kafka интеграция, Consumer, тестирование, Chaos experiments
- **Member 4**: Мониторинг, метрики, RBAC, NetworkPolicies, безопасность

---

## Структура проекта

```
ai-testops/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # CI/CD pipeline
├── argocd/
│   ├── application.yaml           # ArgoCD application
│   └── argocd-config.yaml         # ArgoCD конфигурация
├── chaos-experiments/
│   ├── README.md
│   ├── pod-failure.yaml
│   ├── network-delay.yaml
│   ├── cpu-stress.yaml
│   ├── memory-stress.yaml
│   ├── kafka-partition.yaml
│   └── workflow-comprehensive.yaml
├── helm/
│   └── ai-testops/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── namespace.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           ├── postgres.yaml
│           ├── kafka.yaml
│           ├── zookeeper.yaml
│           ├── django-app.yaml
│           ├── consumer.yaml
│           ├── kafka-ui.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           ├── rbac.yaml
│           └── networkpolicy.yaml
├── k8s/
│   ├── namespace.yaml
│   ├── postgres-deployment.yaml
│   ├── kafka-deployment.yaml
│   ├── zookeeper-deployment.yaml
│   ├── app-deployment.yaml
│   ├── consumer-deployment.yaml
│   ├── kafka-ui-deployment.yaml
│   └── ingress.yaml
├── api_tests/                     # Django приложение
├── canvas/                        # Django настройки
├── test-execute-consumer/         # Kafka consumer
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README-DEPLOYMENT.md           # Эта документация
```

---

## Полезные команды

### Kubernetes

```bash
# Просмотр всех ресурсов
kubectl get all -n ai-testops

# Описание пода
kubectl describe pod <pod-name> -n ai-testops

# Exec в контейнер
kubectl exec -it <pod-name> -n ai-testops -- /bin/bash

# Просмотр событий
kubectl get events -n ai-testops --sort-by='.lastTimestamp'

# Масштабирование
kubectl scale deployment django-app --replicas=5 -n ai-testops
```

### Helm

```bash
# Список релизов
helm list -n ai-testops

# История релиза
helm history ai-testops -n ai-testops

# Откат
helm rollback ai-testops 1 -n ai-testops

# Удаление
helm uninstall ai-testops -n ai-testops
```

### ArgoCD

```bash
# Статус приложения
argocd app get ai-testops

# Синхронизация
argocd app sync ai-testops

# История
argocd app history ai-testops

# Откат
argocd app rollback ai-testops 1
```

---

## Troubleshooting

### Проблема: Поды не запускаются

```bash
# Проверить события
kubectl get events -n ai-testops

# Проверить логи
kubectl logs <pod-name> -n ai-testops

# Проверить описание
kubectl describe pod <pod-name> -n ai-testops
```

### Проблема: Нет доступа к приложению

```bash
# Проверить ingress
kubectl get ingress -n ai-testops

# Проверить services
kubectl get svc -n ai-testops

# Проверить endpoints
kubectl get endpoints -n ai-testops
```

### Проблема: HPA не масштабируется

```bash
# Проверить metrics-server
kubectl get deployment metrics-server -n kube-system

# Проверить метрики
kubectl top pods -n ai-testops

# Проверить HPA
kubectl describe hpa -n ai-testops
```

---

## Лицензия

MIT License

---

## Контакты

- **Email**: team@ai-testops.example.com
- **GitHub**: [huynhduc0/ai-testops](https://github.com/huynhduc0/ai-testops)
- **Issues**: [GitHub Issues](https://github.com/huynhduc0/ai-testops/issues)

---

**Дата последнего обновления**: Декабрь 2024

**Версия документации**: 1.0.0
