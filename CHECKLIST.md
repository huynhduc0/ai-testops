# Чеклист перед защитой проекта

## ✅ Технические требования (60 баллов)

### 1. Микросервисы (10 баллов)

- [ ] **Минимум 3 микросервиса**
  - [ ] Django App - работает
  - [ ] Test Execute Consumer - работает
  - [ ] PostgreSQL - работает
  - [ ] Kafka - работает
  - [ ] Zookeeper - работает
  
**Проверка:**
```bash
kubectl get pods -n ai-testops
# Все pods должны быть Running
```

### 2. Kubernetes + Helm (10 баллов)

- [ ] **Helm Chart создан**
  - [ ] `Chart.yaml` существует
  - [ ] `values.yaml` корректно заполнен
  - [ ] Templates для всех сервисов
  
- [ ] **Развертывание работает**
  - [ ] `helm install` успешен
  - [ ] Все ресурсы созданы

**Проверка:**
```bash
helm list -n ai-testops
helm get values ai-testops -n ai-testops
kubectl get all -n ai-testops
```

### 3. GitOps с ArgoCD (10 баллов)

- [ ] **ArgoCD установлен**
  - [ ] ArgoCD UI доступен
  - [ ] `argocd/application.yaml` создан
  
- [ ] **Auto-sync настроен**
  - [ ] `automated.prune: true`
  - [ ] `automated.selfHeal: true`
  
- [ ] **Application synced**
  - [ ] Статус: Healthy
  - [ ] Статус: Synced

**Проверка:**
```bash
kubectl get application -n argocd ai-testops
argocd app get ai-testops
# Должно быть: Health Status: Healthy, Sync Status: Synced
```

### 4. CI/CD Pipeline (10 баллов)

- [ ] **GitHub Actions настроен**
  - [ ] `.github/workflows/ci.yaml` существует
  - [ ] Workflow запускается при push
  
- [ ] **Pipeline этапы**
  - [ ] Lint & Test
  - [ ] Build Docker images
  - [ ] Push to registry
  - [ ] Security scan

**Проверка:**
```bash
# Проверить последний workflow run на GitHub
# Actions tab → последний run → все jobs green
```

### 5. Secrets и безопасность (5 баллов)

- [ ] **Secrets настроены**
  - [ ] Database credentials в Secret
  - [ ] API keys в Secret
  - [ ] Secrets смонтированы в pods
  
- [ ] **RBAC настроен**
  - [ ] ServiceAccount создан
  - [ ] Role с минимальными правами
  - [ ] RoleBinding настроен
  
- [ ] **NetworkPolicy**
  - [ ] Ingress rules
  - [ ] Egress rules

**Проверка:**
```bash
kubectl get secrets -n ai-testops
kubectl get serviceaccount -n ai-testops
kubectl get role -n ai-testops
kubectl get rolebinding -n ai-testops
kubectl get networkpolicy -n ai-testops
```

### 6. Autoscaling (5 баллов)

- [ ] **HPA для Django**
  - [ ] minReplicas: 2
  - [ ] maxReplicas: 10
  - [ ] targetCPU: 70%
  
- [ ] **HPA для Consumer**
  - [ ] minReplicas: 2
  - [ ] maxReplicas: 8
  - [ ] targetCPU: 70%

**Проверка:**
```bash
kubectl get hpa -n ai-testops
# Должно показать current/target metrics
```

### 7. Health Probes (5 баллов)

- [ ] **Liveness probes**
  - [ ] Django app
  - [ ] Test consumer
  - [ ] PostgreSQL
  - [ ] Kafka
  - [ ] Zookeeper
  
- [ ] **Readiness probes**
  - [ ] Django app
  - [ ] Test consumer
  - [ ] PostgreSQL
  - [ ] Kafka
  - [ ] Zookeeper

**Проверка:**
```bash
kubectl describe deployment django-app -n ai-testops | grep -A 5 "Liveness\|Readiness"
```

### 8. Kafka/Pub-Sub (5 баллов)

- [ ] **Kafka работает**
  - [ ] Kafka pod Running
  - [ ] Zookeeper pod Running
  - [ ] Topics созданы
  
- [ ] **Producer работает**
  - [ ] Django отправляет сообщения
  
- [ ] **Consumer работает**
  - [ ] Test consumer получает сообщения
  - [ ] Сообщения обрабатываются

**Проверка:**
```bash
# Kafka UI
kubectl port-forward svc/kafka-ui -n ai-testops 8080:8080
# Открыть http://localhost:8080
# Проверить topics и messages
```

### 9. Circuit Breaker (5 баллов)

- [ ] **Retry механизм**
  - [ ] В consumer есть retry logic
  - [ ] Exponential backoff
  
- [ ] **Fallback**
  - [ ] Обработка ошибок
  - [ ] Graceful degradation

**Проверка:**
```bash
# Проверить код consumer на наличие try/except и retry
cat test-execute-consumer/consumer.py | grep -A 5 "retry\|except"
```

### 10. Chaos Engineering (5 баллов)

- [ ] **Chaos Mesh установлен**
  - [ ] Chaos Mesh pods Running
  
- [ ] **Эксперименты созданы**
  - [ ] pod-failure.yaml
  - [ ] network-delay.yaml
  - [ ] cpu-stress.yaml
  - [ ] memory-stress.yaml
  - [ ] workflow-comprehensive.yaml
  
- [ ] **Эксперименты работают**
  - [ ] Можно применить
  - [ ] Система восстанавливается

**Проверка:**
```bash
kubectl get podchaos -n ai-testops
kubectl apply -f chaos-experiments/pod-failure.yaml
kubectl get pods -n ai-testops --watch
# Pods должны перезапуститься
```

---

## 🎯 Защита проекта (40 баллов)

### Подготовка презентации (10 минут)

- [ ] **Слайды/материалы готовы**
  - [ ] Архитектурная диаграмма
  - [ ] Список микросервисов
  - [ ] GitOps workflow diagram
  
- [ ] **Демо подготовлено**
  - [ ] ArgoCD UI работает
  - [ ] Приложение доступно
  - [ ] Kafka UI работает
  - [ ] Chaos эксперимент готов

### Демонстрация компонентов

- [ ] **CI/CD**
  - [ ] Показать GitHub Actions
  - [ ] Показать Docker Hub images
  
- [ ] **GitOps**
  - [ ] Показать ArgoCD UI
  - [ ] Показать auto-sync
  - [ ] Показать rollback
  
- [ ] **HPA**
  - [ ] Показать текущие metrics
  - [ ] Показать scaling event
  
- [ ] **Kafka**
  - [ ] Показать topics
  - [ ] Показать message flow
  
- [ ] **Chaos**
  - [ ] Запустить эксперимент
  - [ ] Показать восстановление

### Ответы на вопросы

#### Архитектурные решения

- [ ] **Почему микросервисы?**
  - Prepared answer ✓
  
- [ ] **Почему Kafka?**
  - Prepared answer ✓
  
- [ ] **Как обеспечена отказоустойчивость?**
  - Prepared answer ✓

#### GitOps

- [ ] **Что такое GitOps?**
  - Prepared answer ✓
  
- [ ] **Преимущества перед традиционным CI/CD?**
  - Prepared answer ✓
  
- [ ] **Что происходит при ручном изменении?**
  - Prepared answer ✓

#### Kubernetes

- [ ] **Как работает HPA?**
  - Prepared answer ✓
  
- [ ] **Liveness vs Readiness?**
  - Prepared answer ✓
  
- [ ] **Service Discovery?**
  - Prepared answer ✓

#### Безопасность

- [ ] **Как обеспечена безопасность?**
  - Prepared answer ✓
  
- [ ] **Где хранятся secrets?**
  - Prepared answer ✓

#### Chaos Engineering

- [ ] **Типы экспериментов?**
  - Prepared answer ✓
  
- [ ] **Реакция на pod failure?**
  - Prepared answer ✓

---

## 📋 Вклад команды

### Git коммиты

- [ ] **Проверить коммиты каждого участника**

```bash
# Для каждого участника
git log --author="Name" --oneline | wc -l
git shortlog -s -n --all
```

- [ ] **Задокументировать вклад**
  - [ ] В README.md
  - [ ] В DEFENSE.md

### Распределение работы

- [ ] **Четкое разделение**
  - [ ] CI/CD - Member 1
  - [ ] ArgoCD - Member 1
  - [ ] Django App - Member 2
  - [ ] Consumer - Member 2
  - [ ] Kubernetes - Member 3
  - [ ] Chaos - Member 4

---

## 🧪 Финальное тестирование

### 1. Полное развертывание с нуля

```bash
# Удалить все
argocd app delete ai-testops --cascade
kubectl delete namespace ai-testops

# Развернуть заново через ArgoCD
kubectl apply -f argocd/application.yaml

# Проверить
kubectl get all -n ai-testops
argocd app get ai-testops
```

- [ ] **Все pods Running**
- [ ] **ArgoCD Healthy & Synced**
- [ ] **Application работает**

### 2. Проверка auto-sync

```bash
# Изменить replicas в values.yaml
vim helm/ai-testops/values.yaml
# django.replicas: 3

# Push в Git
git add .
git commit -m "Test auto-sync"
git push

# Подождать 3 минуты
# Проверить
kubectl get pods -n ai-testops -l app=django-app
```

- [ ] **ArgoCD обнаружил изменения**
- [ ] **Replicas обновились**

### 3. Проверка self-heal

```bash
# Ручное изменение
kubectl scale deployment django-app --replicas=5 -n ai-testops

# Подождать ~30 секунд
kubectl get pods -n ai-testops -l app=django-app
```

- [ ] **ArgoCD вернул replicas из Git**

### 4. Chaos test

```bash
# Запустить pod failure
kubectl apply -f chaos-experiments/pod-failure.yaml

# Мониторинг
kubectl get pods -n ai-testops --watch
```

- [ ] **Pods перезапустились**
- [ ] **HPA создал новые replicas**
- [ ] **Application продолжает работать**

### 5. End-to-end тест

```bash
# Создать тест через UI
# Проверить Kafka message
# Проверить выполнение в consumer
# Проверить результат в DB
```

- [ ] **Полный workflow работает**

---

## 📄 Документация

### Обязательные файлы

- [ ] **README.md**
  - [ ] Описание проекта
  - [ ] Архитектура
  - [ ] Quick start
  - [ ] Команда
  
- [ ] **DEPLOYMENT.md**
  - [ ] Полная инструкция развертывания
  - [ ] Требования курса
  - [ ] Troubleshooting
  
- [ ] **argocd/README.md**
  - [ ] GitOps workflow
  - [ ] ArgoCD setup
  - [ ] Best practices
  
- [ ] **chaos-experiments/README.md**
  - [ ] Chaos testing guide
  - [ ] Примеры экспериментов
  
- [ ] **DEFENSE.md**
  - [ ] Презентация для защиты
  - [ ] Вопросы и ответы
  - [ ] Метрики проекта

### Code quality

- [ ] **Requirements.txt актуален**
- [ ] **Docker images собираются**
- [ ] **Helm chart валиден**

```bash
helm lint ./helm/ai-testops
```

---

## 🎓 День защиты

### За день до защиты

- [ ] **Проверить доступ к ArgoCD**
- [ ] **Проверить GitHub Actions**
- [ ] **Проверить Docker Hub images**
- [ ] **Обновить презентацию**

### В день защиты

- [ ] **Приехать заранее**
- [ ] **Проверить интернет**
- [ ] **Открыть все нужные вкладки:**
  - [ ] ArgoCD UI
  - [ ] GitHub repository
  - [ ] GitHub Actions
  - [ ] Docker Hub
  - [ ] Kafka UI
  - [ ] Chaos Mesh
  
- [ ] **Terminal готов с командами:**

```bash
# Быстрый доступ
kubectl get all -n ai-testops
argocd app get ai-testops
kubectl get hpa -n ai-testops
kubectl apply -f chaos-experiments/pod-failure.yaml
```

### Во время защиты

- [ ] **Говорить уверенно**
- [ ] **Показывать код при необходимости**
- [ ] **Отвечать на вопросы честно**
- [ ] **Если не знаете - скажите "Не уверен, но думаю..."**

---

## 📊 Ожидаемая оценка

### Расчет баллов

**Технические требования:** ___/60
- Микросервисы: ___/10
- Kubernetes + Helm: ___/10
- GitOps: ___/10
- CI/CD: ___/10
- Безопасность: ___/5
- Autoscaling: ___/5
- Probes: ___/5
- Kafka: ___/5
- Circuit Breaker: ___/5
- Chaos: ___/5

**Защита:** ___/40
- Архитектурные решения: ___/15
- Демонстрация: ___/15
- Презентация: ___/10

**ИТОГО:** ___/100

### Конвертация в оценку

- 85-100: **5 (отлично)** ✅
- 70-84: **4 (хорошо)**
- 55-69: **3 (удовлетворительно)**
- <55: **2 (неудовлетворительно)**

---

## ✅ Финальный чек

```bash
# Запустить все проверки
./scripts/final-check.sh
```

**ВСЕ ЗЕЛЕНОЕ?** 🎉

**ГОТОВЫ К ЗАЩИТЕ!** 🚀

---

## 📞 Контакты для помощи

- **ArgoCD issues:** [ArgoCD Slack](https://argoproj.github.io/community/join-slack/)
- **Kubernetes help:** [Kubernetes Slack](https://slack.k8s.io/)
- **Chaos Mesh:** [Chaos Mesh Docs](https://chaos-mesh.org/docs/)

**Удачи на защите! 🍀**
