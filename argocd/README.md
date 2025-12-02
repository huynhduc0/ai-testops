# ArgoCD GitOps Deployment

## Что такое GitOps?

GitOps - это методология непрерывной доставки, где Git является единственным источником правды для декларативной инфраструктуры и приложений.

### Принципы GitOps

1. **Декларативность**: Вся система описана в виде кода
2. **Версионирование**: Все изменения в Git
3. **Автоматизация**: Автоматическое применение изменений
4. **Непрерывная синхронизация**: Система всегда соответствует Git

## Установка ArgoCD

```bash
# 1. Создание namespace
kubectl create namespace argocd

# 2. Установка ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. Ожидание готовности компонентов
kubectl wait --for=condition=available --timeout=300s \
  deployment/argocd-server -n argocd

# 4. Установка ArgoCD CLI (опционально)
brew install argocd  # macOS
# или
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd
```

## Первый доступ к ArgoCD

```bash
# 1. Port-forward для доступа к UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 2. Получение начального пароля
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo

# 3. Вход в CLI
argocd login localhost:8080

# 4. Смена пароля (рекомендуется)
argocd account update-password
```

**UI доступен на**: https://localhost:8080
- Username: `admin`
- Password: (из команды выше)

## Развертывание AI TestOps

### Метод 1: Через kubectl

```bash
# Применение ArgoCD Application
kubectl apply -f argocd/application.yaml

# Проверка статуса
kubectl get application -n argocd ai-testops
```

### Метод 2: Через ArgoCD CLI

```bash
argocd app create ai-testops \
  --repo https://github.com/huynhduc0/ai-testops.git \
  --path helm/ai-testops \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace ai-testops \
  --sync-policy automated \
  --auto-prune \
  --self-heal
```

### Метод 3: Через UI

1. Откройте ArgoCD UI
2. Нажмите "+ NEW APP"
3. Заполните параметры:
   - **Application Name**: `ai-testops`
   - **Project**: `default`
   - **Sync Policy**: `Automatic`
   - **Repository URL**: `https://github.com/huynhduc0/ai-testops.git`
   - **Path**: `helm/ai-testops`
   - **Cluster**: `https://kubernetes.default.svc`
   - **Namespace**: `ai-testops`
4. Нажмите "CREATE"

## GitOps Workflow

### 1. Разработка и изменения

```bash
# Клонирование репозитория
git clone https://github.com/huynhduc0/ai-testops.git
cd ai-testops

# Создание ветки для изменений
git checkout -b feature/update-replicas

# Внесение изменений (например, в values.yaml)
vim helm/ai-testops/values.yaml

# Коммит изменений
git add .
git commit -m "Increase Django replicas to 3"

# Push в репозиторий
git push origin feature/update-replicas
```

### 2. Pull Request и Review

```bash
# Создайте PR на GitHub
# Дождитесь прохождения CI/CD pipeline
# Получите code review от команды
```

### 3. Merge и автоматический деплой

```bash
# После merge в main ветку
# ArgoCD автоматически:
# 1. Обнаружит изменения (sync каждые 3 мин)
# 2. Применит новую конфигурацию
# 3. Обновит ресурсы в Kubernetes
```

## Управление приложением

### Просмотр статуса

```bash
# CLI
argocd app get ai-testops

# kubectl
kubectl get application -n argocd ai-testops -o yaml

# UI
# Откройте https://localhost:8080 и выберите приложение
```

### Ручная синхронизация

```bash
# CLI
argocd app sync ai-testops

# Синхронизация конкретного ресурса
argocd app sync ai-testops --resource Deployment:ai-testops:django-app
```

### Rollback к предыдущей версии

```bash
# Просмотр истории
argocd app history ai-testops

# Откат к конкретной ревизии
argocd app rollback ai-testops <REVISION_ID>
```

### Просмотр различий

```bash
# Сравнение Git и кластера
argocd app diff ai-testops
```

### Удаление приложения

```bash
# Удаление с каскадным удалением всех ресурсов
argocd app delete ai-testops --cascade

# Удаление только из ArgoCD (ресурсы останутся)
argocd app delete ai-testops --cascade=false
```

## Мониторинг ArgoCD

### Health Status

ArgoCD отслеживает health status всех ресурсов:
- **Healthy**: Ресурс работает корректно
- **Progressing**: Ресурс в процессе обновления
- **Degraded**: Ресурс неисправен
- **Suspended**: Ресурс приостановлен

### Sync Status

- **Synced**: Git и кластер совпадают
- **OutOfSync**: Есть различия между Git и кластером
- **Unknown**: Статус неизвестен

### Уведомления

Настройка уведомлений в Slack/Teams/Email:

```bash
# Настройка через ConfigMap
kubectl edit configmap argocd-notifications-cm -n argocd
```

## Auto-Sync и Self-Healing

### Auto-Sync

Автоматическое применение изменений из Git:

```yaml
syncPolicy:
  automated:
    prune: true      # Удалять ресурсы, отсутствующие в Git
    selfHeal: true   # Откатывать ручные изменения
    allowEmpty: false # Не разрешать пустые приложения
```

### Self-Healing

ArgoCD автоматически откатывает любые ручные изменения в кластере:

```bash
# Пример: если вручную изменить replicas
kubectl scale deployment django-app --replicas=5 -n ai-testops

# ArgoCD через несколько секунд вернет значение из Git
# (согласно values.yaml)
```

## Troubleshooting

### Проблема: Application не синхронизируется

```bash
# Проверка логов ArgoCD
kubectl logs -n argocd deployment/argocd-application-controller

# Проверка статуса
argocd app get ai-testops

# Ручная синхронизация с подробным выводом
argocd app sync ai-testops --prune --force
```

### Проблема: Resources OutOfSync

```bash
# Просмотр различий
argocd app diff ai-testops

# Принудительная синхронизация
argocd app sync ai-testops --force
```

### Проблема: Health check failed

```bash
# Проверка событий
kubectl get events -n ai-testops --sort-by='.lastTimestamp'

# Проверка подов
kubectl get pods -n ai-testops
kubectl describe pod <pod-name> -n ai-testops
```

## Best Practices

### 1. Структура репозитория

```
├── helm/
│   └── ai-testops/        # Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── argocd/
│   └── application.yaml   # ArgoCD Application
└── .github/
    └── workflows/         # CI pipeline
```

### 2. Разделение окружений

```yaml
# argocd/application-dev.yaml
spec:
  source:
    helm:
      valueFiles:
        - values.yaml
        - values-dev.yaml

# argocd/application-prod.yaml
spec:
  source:
    helm:
      valueFiles:
        - values.yaml
        - values-prod.yaml
```

### 3. Использование Projects

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: ai-testops-project
  namespace: argocd
spec:
  destinations:
    - namespace: 'ai-testops-*'
      server: https://kubernetes.default.svc
  sourceRepos:
    - https://github.com/huynhduc0/ai-testops.git
```

### 4. RBAC для команды

```bash
# Настройка прав для разработчиков
argocd proj role create ai-testops-project developer
argocd proj role add-policy ai-testops-project developer \
  --action get --permission allow --object 'applications/*'
```

## Полезные команды

```bash
# Список всех приложений
argocd app list

# Просмотр логов синхронизации
argocd app logs ai-testops

# Просмотр манифестов
argocd app manifests ai-testops

# Терминал в поде через ArgoCD
argocd app pods ai-testops
argocd app exec ai-testops <pod-name> -- /bin/bash

# Просмотр ресурсов приложения
argocd app resources ai-testops
```

## Дополнительная информация

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [GitOps Guide](https://www.gitops.tech/)
- [Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
