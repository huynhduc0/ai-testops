# AI TestOps Project

## Description (English)

The AI TestOps project is designed to streamline and automate the testing operations for AI models. This project aims to provide a comprehensive framework for testing, validating, and deploying AI models efficiently. It includes tools and scripts for various testing methodologies, continuous integration, and continuous deployment (CI/CD) pipelines.

## Features

- Automated testing for AI models
- Continuous integration and deployment
- Comprehensive test coverage
- Easy-to-use framework
- Scalable and flexible architecture

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker
- Git

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/ai-testops.git
    ```
2. Navigate to the project directory:
    ```bash
    cd ai-testops
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Setting Up Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```
POSTGRES_DB=canvas_db
POSTGRES_USER=canvas_user
POSTGRES_PASSWORD=canvas_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=your_secret_key
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_oauth2_key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_oauth2_secret
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/auth/complete/google/

GRAFANA_CLOUD_API_KEY=your_grafana_cloud_api_key
GRAFANA_CLOUD_PROMETHEUS_URL=https://prometheus-us-central2.grafana.net/api/prom/push
```

### Usage

1. Run the tests:
    ```bash
    pytest
    ```
2. Build and run the Docker container:
    ```bash
    docker-compose up --build
    ```

## How It Works

The AI TestOps project consists of several services that work together to provide a comprehensive testing and deployment framework for AI models:

- **Zookeeper**: Manages and coordinates the Kafka brokers.
- **Kafka**: A distributed streaming platform used for building real-time data pipelines and streaming applications.
- **Kafka UI**: A web-based user interface for managing and monitoring Kafka clusters.
- **PostgreSQL Database**: Stores application data.
- **Application Service**: The main application that runs the AI model and handles requests.
- **Test Execute Consumer**: A service that consumes test execution messages from Kafka and processes them.
- **Grafana Agent**: Collects and sends metrics to Grafana Cloud for monitoring and visualization.

Each service is defined in the `docker-compose.yml` file and can be started using Docker Compose. The services communicate with each other through defined ports and environment variables.

## Screenshots and Functionalities

### Home Screen

![Home Screen](screenshots/home_screen.png)

- **Description**: The home screen provides an overview of the project and quick access to various functionalities.
- **Functionalities**:
  - Navigation to different sections of the application.
  - Overview of recent activities and statistics.

### Test Execution Screen

![Test Execution Screen](screenshots/test_execution_screen.png)

- **Description**: This screen allows users to execute tests and view the results.
- **Functionalities**:
  - Execute individual test cases or a suite of tests.
  - View detailed results of each test execution.
  - Filter and search test executions.

### Test Case Management Screen

![Test Case Management Screen](screenshots/test_case_management_screen.png)

- **Description**: This screen is used for managing test cases.
- **Functionalities**:
  - Create, update, and delete test cases.
  - Generate test case content automatically.
  - Save and view test case details.

### Kafka UI Screen

![Kafka UI Screen](screenshots/kafka_ui_screen.png)

- **Description**: The Kafka UI screen provides a web-based interface for managing and monitoring Kafka clusters.
- **Functionalities**:
  - View and manage Kafka topics.
  - Monitor Kafka brokers and their health status.
  - View real-time metrics and logs.

## watch.py File

The `watch.py` file is responsible for listening to Kafka messages, executing test cases, and collecting metrics.

### How It Works

1. **Listening to Kafka Messages**: The `listen_for_kafka_messages` function sets up a Kafka consumer that listens to the `test_run_queue` topic. When a message is received, it processes the message and executes the test case.

2. **Executing Test Cases**: The `run_test_case` function writes the test script to a temporary file and runs it using `pytest`. The result of the test execution is captured and returned.

3. **Saving Test Results**: The `save_test_result_to_db` function sends the test result to the application service to be saved in the database.

4. **Collecting Metrics**: The `TEST_CASES_STATUS` counter from the Prometheus client library is used to collect metrics on the status of test cases. The metrics are exposed on port 8001 for Grafana to scrape.

### Prometheus Metrics

The following Prometheus metrics are collected:

- `test_cases_status`: A counter that tracks the status of test cases (passed, failed, error) with labels for `test_case_id` and `status`.

## Meeting the Seven Criteria

1. **The project must have a server**: The project includes an application service that runs the AI model and handles requests. This is defined in the `docker-compose.yml` file under the `app` service.

2. **The project must have a consumer**: The `watch.py` file acts as a Kafka consumer that listens for test execution messages, processes them, and collects metrics. This is defined in the `docker-compose.yml` file under the `test-execute-consumer` service.

3. **The service must work with a real DB**: The project uses PostgreSQL as the database to store application data. This is defined in the `docker-compose.yml` file under the `db` service.

4. **Everything should be wrapped in Docker**: The entire system, including custom services, the database, the broker, and monitoring, is wrapped in Docker. The system can be launched locally with one `docker-compose up` command.

5. **Metrics should be collected from the server**: Metrics are collected using the Prometheus client library and exposed on port 8001 for Grafana to scrape. The `grafana-agent` service in the `docker-compose.yml` file handles the collection and sending of metrics to Grafana Cloud.

6. **All code should be covered by tests**: The project includes tests for all code, ensuring 100% coverage. The tests can be run using the `pytest` command.

7. **Test checking is automated via CI**: The project includes a CI pipeline that automates the checking of tests. This ensures that all code changes are tested before being merged.

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# Проект AI TestOps

## Описание (Russian)

Проект AI TestOps предназначен для упрощения и автоматизации тестовых операций для моделей ИИ. Этот проект направлен на предоставление комплексной структуры для тестирования, валидации и развертывания моделей ИИ. Он включает инструменты и скрипты для различных методологий тестирования, непрерывной интеграции и непрерывного развертывания (CI/CD).

## Особенности

- Автоматизированное тестирование моделей ИИ
- Непрерывная интеграция и развертывание
- Полное покрытие тестами
- Удобная структура
- Масштабируемая и гибкая архитектура

## Начало работы

### Предварительные требования

- Python 3.8 или выше
- Docker
- Git

### Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/yourusername/ai-testops.git
    ```
2. Перейдите в каталог проекта:
    ```bash
    cd ai-testops
    ```
3. Установите необходимые зависимости:
    ```bash
    pip install -r requirements.txt
    ```

### Настройка переменных окружения

Создайте файл `.env` в корневом каталоге проекта и добавьте следующие переменные окружения:

```
POSTGRES_DB=canvas_db
POSTGRES_USER=canvas_user
POSTGRES_PASSWORD=canvas_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=your_secret_key
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_oauth2_key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_oauth2_secret
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/auth/complete/google/

GRAFANA_CLOUD_API_KEY=your_grafana_cloud_api_key
GRAFANA_CLOUD_PROMETHEUS_URL=https://prometheus-us-central2.grafana.net/api/prom/push
```

### Использование

1. Запустите тесты:
    ```bash
    pytest
    ```
2. Соберите и запустите Docker-контейнер:
    ```bash
    docker-compose up --build
    ```

## Как это работает

Проект AI TestOps состоит из нескольких сервисов, которые работают вместе, чтобы предоставить комплексную структуру для тестирования и развертывания моделей ИИ:

- **Zookeeper**: Управляет и координирует брокеры Kafka.
- **Kafka**: Распределенная платформа потоковой передачи данных, используемая для создания конвейеров данных в реальном времени и потоковых приложений.
- **Kafka UI**: Веб-интерфейс для управления и мониторинга кластеров Kafka.
- **База данных PostgreSQL**: Хранит данные приложения.
- **Сервис приложения**: Основное приложение, которое запускает модель ИИ и обрабатывает запросы.
- **Test Execute Consumer**: Сервис, который потребляет сообщения о выполнении тестов из Kafka и обрабатывает их.
- **Grafana Agent**: Сбор и отправка метрик в Grafana Cloud для мониторинга и визуализации.

Каждый сервис определен в файле `docker-compose.yml` и может быть запущен с помощью Docker Compose. Сервисы взаимодействуют друг с другом через определенные порты и переменные окружения.

## Скриншоты и функциональные возможности

### Главный экран

![Главный экран](screenshots/home_screen.png)

- **Описание**: Главный экран предоставляет обзор проекта и быстрый доступ к различным функциям.
- **Функциональные возможности**:
  - Навигация по различным разделам приложения.
  - Обзор последних действий и статистики.

### Экран выполнения тестов

![Экран выполнения тестов](screenshots/test_execution_screen.png)

- **Описание**: Этот экран позволяет пользователям выполнять тесты и просматривать результаты.
- **Функциональные возможности**:
  - Выполнение отдельных тестовых случаев или набора тестов.
  - Просмотр подробных результатов каждого выполнения теста.
  - Фильтрация и поиск выполнений тестов.

### Экран управления тестовыми случаями

![Экран управления тестовыми случаями](screenshots/test_case_management_screen.png)

- **Описание**: Этот экран используется для управления тестовыми случаями.
- **Функциональные возможности**:
  - Создание, обновление и удаление тестовых случаев.
  - Автоматическая генерация содержимого тестового случая.
  - Сохранение и просмотр деталей тестового случая.

### Экран Kafka UI

![Экран Kafka UI](screenshots/kafka_ui_screen.png)

- **Описание**: Экран Kafka UI предоставляет веб-интерфейс для управления и мониторинга кластеров Kafka.
- **Функциональные возможности**:
  - Просмотр и управление темами Kafka.
  - Мониторинг брокеров Kafka и их состояния.
  - Просмотр метрик и логов в реальном времени.

## watch.py файл

Файл `watch.py` отвечает за прослушивание сообщений Kafka, выполнение тестовых случаев и сбор метрик.

### Как это работает

1. **Прослушивание сообщений Kafka**: Функция `listen_for_kafka_messages` настраивает потребителя Kafka, который прослушивает тему `test_run_queue`. Когда сообщение получено, оно обрабатывается и выполняется тестовый случай.

2. **Выполнение тестовых случаев**: Функция `run_test_case` записывает тестовый скрипт во временный файл и запускает его с помощью `pytest`. Результат выполнения теста захватывается и возвращается.

3. **Сохранение результатов тестов**: Функция `save_test_result_to_db` отправляет результат теста в сервис приложения для сохранения в базе данных.

4. **Сбор метрик**: Счетчик `TEST_CASES_STATUS` из библиотеки Prometheus используется для сбора метрик о статусе тестовых случаев. Метрики доступны на порту 8001 для сбора Grafana.

### Метрики Prometheus

Собираются следующие метрики Prometheus:

- `test_cases_status`: Счетчик, отслеживающий статус тестовых случаев (пройдено, не пройдено, ошибка) с метками для `test_case_id` и `status`.

## Соответствие семи критериям

1. **Проект должен иметь сервер**: Проект включает сервис приложения, который запускает модель ИИ и обрабатывает запросы. Это определено в файле `docker-compose.yml` в разделе `app`.

2. **Проект должен иметь потребителя**: Файл `watch.py` действует как потребитель Kafka, который прослушивает сообщения о выполнении тестов, обрабатывает их и собирает метрики. Это определено в файле `docker-compose.yml` в разделе `test-execute-consumer`.

3. **Сервис должен работать с реальной базой данных**: Проект использует PostgreSQL в качестве базы данных для хранения данных приложения. Это определено в файле `docker-compose.yml` в разделе `db`.

4. **Все должно быть обернуто в Docker**: Вся система, включая пользовательские сервисы, базу данных, брокер и мониторинг, обернута в Docker. Систему можно запустить локально с помощью одной команды `docker-compose up`.

5. **Метрики должны собираться с сервера**: Метрики собираются с использованием библиотеки Prometheus и доступны на порту 8001 для сбора Grafana. Сервис `grafana-agent` в файле `docker-compose.yml` обрабатывает сбор и отправку метрик в Grafana Cloud.

6. **Весь код должен быть покрыт тестами**: Проект включает тесты для всего кода, обеспечивая 100% покрытие. Тесты можно запустить с помощью команды `pytest`.

7. **Проверка тестов автоматизирована через CI**: Проект включает CI-пайплайн, который автоматизирует проверку тестов. Это гарантирует, что все изменения кода тестируются перед слиянием.

## Вклад

Мы приветствуем вклад! Пожалуйста, прочитайте наши [Руководства по вкладу](CONTRIBUTING.md) для получения дополнительной информации.

## Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](LICENSE) для получения подробной информации.
