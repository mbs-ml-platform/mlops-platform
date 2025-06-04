## 🚀 Tổng quan cấu trúc Master Project (Polyrepo)

Thay vì một "siêu repo" duy nhất, tôi khuyến nghị sử dụng kiến trúc **polyrepo**, nơi mỗi thành phần chính hoặc nhóm chức năng logic của nền tảng MLOps sẽ nằm trong một repository Git riêng biệt. Cách tiếp cận này mang lại nhiều lợi ích:

- **Quản lý độc lập:** Mỗi đội (Data Engineering, ML Engineering, Data Science) có thể quản lý vòng đời, phiên bản, và quy trình CI/CD của riêng mình.
- **Kiểm soát truy cập chi tiết:** Dễ dàng cấp quyền truy cập khác nhau cho từng repo.
- **Build và deploy nhanh hơn:** Chỉ những thành phần thay đổi mới cần được build và deploy lại.
- **Giảm thiểu xung đột:** Ít khả năng xảy ra xung đột khi nhiều người làm việc trên các phần khác nhau.

Master Project của bạn sẽ là một **khái niệm tổ chức** bao gồm các repo sau:

1. **`feature-store-management`**: Quản lý định nghĩa features, pipelines xử lý dữ liệu cho Feature Store, và cấu hình Feast.
2. **`ml-model-development`**: Nơi Data Scientists phát triển, huấn luyện, và đánh giá các mô hình ML.
3. **`ml-model-services`**: Chứa mã nguồn để đóng gói mô hình thành các API services (Model Service Layer & Label Engine Layer).
4. **`mlops-orchestration-pipelines`**: Định nghĩa các DAGs cho Apache Airflow (data pipelines, training pipelines, batch serving).
5. **`mlops-platform-infrastructure`**: Mã nguồn Infrastructure as Code (IaC) và cấu hình cho các công cụ MLOps (MLFlow, Jenkins, Monitoring stack, cơ sở dữ liệu).
6. **`ml-reporting-and-monitoring-logic`**: Mã nguồn cho việc xây dựng báo cáo tùy chỉnh, dashboards, và các logic giám sát chuyên sâu.

Sơ đồ mối quan hệ giữa các Repo và Servers:

```
graph TD
    subgraph Developer Workstation
        Dev[Git Client]
    end

    subgraph Source Control (GitLab/GitHub)
        R1[Repo: feature-store-management]
        R2[Repo: ml-model-development]
        R3[Repo: ml-model-services]
        R4[Repo: mlops-orchestration-pipelines]
        R5[Repo: mlops-platform-infrastructure]
        R6[Repo: ml-reporting-and-monitoring-logic]
    end

    subgraph Server 1 (Data Processing & Feature Store Backend)
        S1_FS_Offline[PostgreSQL for Feast Offline]
        S1_MLFlow_Meta[PostgreSQL for MLFlow Metadata]
        S1_Spark[Apache Spark]
        S1_Kafka[Apache Kafka]
        S1_Feast_SDK[Feast SDK Consumers]
    end

    subgraph Server 2 (MLOps Orchestration & Management)
        S2_Airflow[Apache Airflow]
        S2_MLFlow_Server[MLFlow Server]
        S2_FS_Online[Redis for Feast Online]
        S2_Jenkins[Jenkins CI/CD]
        S2_Feast_Core[Feast Core Services]
    end

    subgraph Server 3 (Model Serving & Monitoring)
        S3_APIs[Model Serving APIs (FastAPI/Docker)]
        S3_Prometheus[Prometheus]
        S3_Grafana[Grafana]
        S3_ELK[ELK Stack]
    end

    Dev --> R1; Dev --> R2; Dev --> R3; Dev --> R4; Dev --> R5; Dev --> R6

    R1 --> S1_FS_Offline; R1 --> S2_FS_Online; R1 --> S2_Feast_Core
    R2 -- Training Data From --> S1_FS_Offline
    R2 -- Log Experiments/Models To --> S2_MLFlow_Server
    R3 -- Fetch Models From --> S2_MLFlow_Server
    R3 -- Fetch Online Features From --> S2_FS_Online
    R3 -- Deploy To --> S3_APIs
    R4 -- DAGs Deployed To --> S2_Airflow
    R5 -- IaC & Config For --> S1_FS_Offline; R5 -- IaC & Config For --> S1_MLFlow_Meta; R5 -- IaC & Config For --> S1_Spark; R5 -- IaC & Config For --> S1_Kafka
    R5 -- IaC & Config For --> S2_Airflow; R5 -- IaC & Config For --> S2_MLFlow_Server; R5 -- IaC & Config For --> S2_FS_Online; R5 -- IaC & Config For --> S2_Jenkins
    R5 -- IaC & Config For --> S3_APIs; R5 -- IaC & Config For --> S3_Prometheus; R5 -- IaC & Config For --> S3_Grafana; R5 -- IaC & Config For --> S3_ELK
    R6 -- Dashboards/Reports For --> S3_Grafana; R6 -- Dashboards/Reports For --> S3_ELK; R6 -- Consumes Data From --> S2_MLFlow_Server; R6 -- Consumes Data From --> S3_Prometheus

    S2_Jenkins -- Builds & Deploys --> R1; S2_Jenkins -- Builds & Deploys --> R2; S2_Jenkins -- Builds & Deploys --> R3; S2_Jenkins -- Builds & Deploys --> R4; S2_Jenkins -- Builds & Deploys --> R5; S2_Jenkins -- Builds & Deploys --> R6
    S2_Airflow -- Orchestrates Tasks Involving --> S1_Spark; S2_Airflow -- Orchestrates Tasks Involving --> S1_FS_Offline; S2_Airflow -- Orchestrates Tasks Involving --> S2_FS_Online; S2_Airflow -- Orchestrates Tasks Involving --> S2_MLFlow_Server
    S3_APIs -- Metrics To --> S3_Prometheus; S3_APIs -- Logs To --> S3_ELK
```

---

## 🏛️ Cấu trúc chi tiết các Repository

### 1. Repo: `feature-store-management`

Quản lý mọi thứ liên quan đến Feature Store.

```
feature-store-management/
├── feast_repository/              # Thư mục gốc cho `feast apply` và `feast materialize`
│   ├── entities.py                # Định nghĩa Entities (user, item, etc.)
│   ├── data_sources.py            # Định nghĩa Data Sources (trỏ đến DWH, Data Lake, Kafka topics)
│   ├── feature_views/             # Định nghĩa Feature Views
│   │   ├── user_profile_features.py
│   │   ├── transaction_agg_features.py
│   │   └── ...
│   ├── feature_services/          # (Tùy chọn) Định nghĩa Feature Services
│   │   └── credit_scoring_service_features.py
│   └── feature_store.yaml         # Cấu hình chính của Feast (registry, provider, online/offline stores)
├── data_transformation_pipelines/ # Scripts/dbt models để chuẩn bị dữ liệu cho Feast
│   ├── dbt_project_feast/         # Nếu dùng dbt để transform dữ liệu nguồn thành bảng cho Feast
│   │   ├── dbt_project.yml
│   │   ├── models/                # dbt models: staging, intermediate, marts (feature tables)
│   │   │   ├── staging/
│   │   │   │   └── stg_transactions.sql
│   │   │   └── marts/
│   │   │       └── fct_user_daily_spend.sql
│   │   └── profiles.yml.template
│   ├── spark_jobs_feast/          # Spark jobs nếu dùng Spark cho data transformation
│   │   └── process_market_stream.py
│   └── python_scripts_feast/      # Python scripts cho các tác vụ ETL nhỏ
│       └── clean_user_demographics.py
├── notebooks_feature_dev/         # Jupyter notebooks cho EDA, profiling, feature engineering
│   ├── 01_eda_raw_transactions.ipynb
│   ├── 02_profiling_market_data.ipynb
│   ├── 03_feature_engineering_user_behavior.ipynb
│   └── common_utils/              # Tiện ích cho notebooks
│       └── data_loading.py
├── data_source_connectors/        # Mã nguồn kết nối đến các hệ thống dữ liệu (DWH, Data Lake, API)
│   ├── database_connector.py
│   ├── kafka_consumer_utils.py
│   └── config/
│       └── connections.ini.template # Template, secrets quản lý riêng
├── tests/                         # Unit tests cho data transformations, feature definitions
│   ├── test_dbt_models.py
│   ├── test_feature_view_logic.py
│   └── common_test_utils.py
├── scripts/                       # Scripts tiện ích (deploy, materialize)
│   ├── run_feast_apply.sh
│   ├── run_feast_materialize_incremental.sh
│   └── run_dbt_for_feast.sh
├── Dockerfile.feast_cli           # (Tùy chọn) Dockerfile để chạy Feast CLI trong CI/CD
├── requirements.txt               # Python dependencies (feast, pandas, pyspark, dbt-postgres, etc.)
└── README.md
```

### 2. Repo: `ml-model-development`

Nơi Data Scientists phát triển, huấn luyện và đánh giá mô hình.

```
ml-model-development/
├── models/                        # Mỗi sub-folder là một dự án/loại mô hình
│   ├── fraud_detection_xgboost/
│   │   ├── notebooks/             # Notebooks cho EDA, thử nghiệm, model building
│   │   │   ├── 01_data_exploration.ipynb
│   │   │   ├── 02_feature_selection_and_preprocessing.ipynb
│   │   │   └── 03_xgboost_training_and_evaluation.ipynb
│   │   ├── src/                   # Mã nguồn chính thức cho mô hình
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Cấu hình (Pydantic model): hyperparameters, feature list
│   │   │   ├── data_loader.py     # Tải data từ Feature Store, xử lý label
│   │   │   ├── preprocessor.py    # Tiền xử lý feature đặc thù (sau khi lấy từ Feature Store)
│   │   │   ├── train.py           # Script huấn luyện, log vào MLFlow
│   │   │   ├── evaluate.py        # Script đánh giá, so sánh model
│   │   │   └── predict_batch.py   # (Tùy chọn) Script cho dự đoán batch
│   │   ├── tests/                 # Unit tests cho src/
│   │   │   ├── test_preprocessor.py
│   │   │   └── test_data_loader.py
│   │   ├── requirements.txt       # Dependencies riêng cho model này
│   │   └── Dockerfile.train       # (Tùy chọn) Nếu cần môi trường huấn luyện đặc biệt
│   ├── customer_churn_lightgbm/
│   │   ├── notebooks/
│   │   ├── src/                   # Tương tự như trên
│   │   │   └── ...
│   │   ├── tests/
│   │   └── requirements.txt
│   └── ...
├── common_ml_utils/               # Các hàm, lớp tiện ích dùng chung cho nhiều mô hình
│   ├── __init__.py
│   ├── base_model_trainer.py      # Abstract Base Class cho trainer (kế thừa)
│   ├── data_schemas/              # Pydantic models cho cấu trúc dữ liệu dùng chung
│   │   └── training_data_contract.py
│   ├── evaluation_utils.py        # Các hàm đánh giá tùy chỉnh
│   ├── feature_store_client.py    # Helper để tương tác với Feature Store
│   └── mlflow_utils.py            # Helper để tương tác với MLFlow
├── research_and_poc/              # Cho các thử nghiệm, PoC chưa chính thức
│   └── new_nlp_approach.ipynb
├── requirements_common.txt        # Dependencies chung (ít khi dùng, ưu tiên trong từng model)
└── README.md
```

### 3. Repo: `ml-model-services`

Đóng gói mô hình thành API services.

```
ml-model-services/
├── services/                       # Mỗi sub-folder là một microservice cho một mô hình
│   ├── fraud_detection_api/
│   │   ├── app/                    # Mã nguồn FastAPI/Flask
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # FastAPI app, API endpoints
│   │   │   ├── schemas.py          # Pydantic schemas cho request/response
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py       # Cấu hình service (MLFlow URI, model name/stage)
│   │   │   │   └── model_handler.py # Tải model từ MLFlow, gọi Feature Store online
│   │   │   ├── business_logic/     # Model Service Layer & Label Engine Layer
│   │   │   │   ├── __init__.py
│   │   │   │   └── fraud_processing.py # Tiền xử lý, gọi model, hậu xử lý, áp dụng rules
│   │   │   └── dependencies.py     # (Tùy chọn) FastAPI dependencies
│   │   ├── tests/                  # Unit/Integration tests cho API
│   │   │   ├── test_api_endpoints.py
│   │   │   └── test_fraud_processing.py
│   │   ├── Dockerfile              # Dockerfile để đóng gói service
│   │   ├── requirements.txt        # Dependencies (fastapi, uvicorn, mlflow-skinny, feast)
│   │   └── deployment_configs/     # (Tùy chọn) Kubernetes manifests, docker-compose.yml
│   │       └── kubernetes_deployment.yaml
│   ├── customer_churn_api/
│   │   ├── app/
│   │   │   └── ...                 # Tương tự
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── ...
├── common_service_libs/            # Thư viện dùng chung cho các model services
│   ├── __init__.py
│   ├── base_api_config.py        # Pydantic BaseSettings cho cấu hình chung
│   ├── error_handlers.py         # Xử lý lỗi chung
│   ├── monitoring_middleware.py  # Middleware để expose Prometheus metrics
│   └── auth_utils.py             # (Tùy chọn) Logic xác thực API
├── Dockerfile.base_service         # (Tùy chọn) Base Docker image nếu nhiều service dùng chung libs nặng
└── README.md
```

### 4. Repo: `mlops-orchestration-pipelines`

Định nghĩa các DAGs cho Apache Airflow.

```
mlops-orchestration-pipelines/
├── dags/
│   ├── data_ingestion_and_feature_store/ # DAGs cho Feature Store
│   │   ├── run_dbt_feast_models_dag.py
│   │   ├── materialize_feast_online_store_dag.py
│   │   └── stream_market_data_to_feast_dag.py # Nếu có streaming
│   ├── model_training_pipelines/           # DAGs cho huấn luyện mô hình
│   │   ├── train_fraud_detection_xgboost_dag.py
│   │   └── train_customer_churn_lightgbm_dag.py
│   ├── batch_inference_pipelines/          # DAGs cho dự đoán batch
│   │   └── score_daily_transactions_fraud_dag.py
│   ├── model_monitoring_pipelines/         # DAGs cho giám sát (drift detection, retraining trigger)
│   │   └── check_fraud_model_drift_dag.py
│   └── utility_dags/
│       └── backup_mlflow_db_dag.py
├── plugins/                                # Custom Airflow plugins (operators, hooks, sensors)
│   ├── operators/
│   │   └── feast_materialize_operator.py   # Ví dụ
│   └── hooks/
│       └── internal_api_hook.py
├── config/                                 # Cấu hình có thể được load bởi DAGs (ít dùng)
│   └── pipeline_variables.json
├── tests/                                  # Tests cho DAGs (DAG integrity, task dependencies)
│   ├── test_dag_definitions.py
│   └── test_training_pipeline_flow.py
├── Dockerfile.airflow_custom_worker        # Dockerfile cho custom Airflow worker image (nếu cần)
├── requirements_airflow.txt                # Python dependencies cho môi trường Airflow worker
└── README.md
```

### 5. Repo: `mlops-platform-infrastructure`

Mã nguồn IaC và cấu hình cho các công cụ nền tảng.

```
mlops-platform-infrastructure/
├── terraform/                            # Hoặc Ansible, Pulumi
│   ├── environments/                     # Cấu hình cho từng môi trường (dev, staging, prod)
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   └── prod/
│   │       └── ...
│   ├── modules/                          # Terraform modules tái sử dụng (server, postgres, redis, airflow)
│   │   ├── compute_instance/
│   │   ├── postgresql_server/
│   │   ├── redis_cluster/
│   │   └── airflow_on_docker/
│   └── backend_config.tf                 # Cấu hình remote state
├── docker_compose_setups/                # Docker Compose files cho dev/local hoặc non-Kubernetes setups
│   ├── airflow/
│   │   └── docker-compose.yml
│   ├── mlflow_server/
│   │   └── docker-compose.yml
│   ├── feature_store_backend/            # Postgres & Redis cho Feast
│   │   └── docker-compose.yml
│   └── monitoring_stack/                 # Prometheus, Grafana, ELK
│       └── docker-compose.yml
├── jenkins_config/                       # Cấu hình Jenkins
│   ├── Jenkinsfile_feature_store         # Pipeline as Code cho repo feature-store-management
│   ├── Jenkinsfile_ml_model_development
│   ├── Jenkinsfile_ml_model_services
│   ├── Jenkinsfile_mlops_orchestration
│   ├── Jenkinsfile_platform_infra        # CI/CD cho chính repo này
│   ├── Jenkinsfile_reporting_monitoring
│   ├── jobs_dsl/                         # (Tùy chọn) Nếu dùng Job DSL plugin
│   └── initial_config/
│       └── plugins.txt                   # Danh sách plugin cần cài
├── kubernetes_deployments/               # (Nếu dùng Kubernetes) Manifests cho các thành phần
│   ├── airflow_cluster/
│   ├── mlflow_on_k8s/
│   ├── model_service_templates/
│   └── monitoring_on_k8s/
├── server_provisioning_scripts/          # Scripts để bootstrap server vật lý/VM (nếu không dùng IaC hoàn toàn)
│   ├── setup_server1_dataproc.sh
│   ├── setup_server2_orchestration.sh
│   └── setup_server3_serving.sh
├── platform_config_templates/            # File cấu hình template cho các dịch vụ
│   ├── airflow/airflow.cfg.j2
│   ├── prometheus/prometheus.yml.j2
│   └── grafana/provisioning_templates/
│       ├── dashboards.yml.j2
│       └── datasources.yml.j2
└── README.md
```

### 6. Repo: `ml-reporting-and-monitoring-logic`

Mã nguồn cho báo cáo, dashboards tùy chỉnh, và logic giám sát chuyên sâu.

```
ml-reporting-and-monitoring-logic/
├── dashboards_as_code/                # Định nghĩa dashboards (JSON cho Grafana, NDJSON cho Kibana)
│   ├── grafana_dashboards/
│   │   ├── overview_model_performance.json
│   │   ├── feature_drift_analysis.json
│   │   └── system_health_overview.json
│   └── kibana_dashboards/
│       └── api_error_and_latency_analysis.ndjson
├── custom_reports/                    # Scripts/notebooks để tạo báo cáo định kỳ, ad-hoc
│   ├── generate_monthly_model_retraining_report.py
│   ├── adhoc_customer_segment_prediction_analysis.ipynb
│   └── utils/
│       └── db_query_for_reports.py
├── alerting_configurations/           # (Tùy chọn) Định nghĩa alert rules cho Prometheus Alertmanager
│   ├── model_specific_alerts.yml
│   └── system_critical_alerts.yml
├── advanced_monitoring_scripts/       # Scripts cho các tác vụ giám sát phức tạp
│   ├── calculate_concept_drift_scores.py
│   └── analyze_prediction_bias.py
├── requirements.txt                   # Dependencies (pandas, matplotlib, grafana_api, elasticsearch-dsl)
└── README.md
```

---

## 🔄 Workflow chi tiết và vị trí thực hiện

### 1. Khi có nguồn dữ liệu mới hoặc thêm feature trong Feature Store, EDA, Feature Engineering

- **Người thực hiện**: Data Engineer, Data Scientist.
- **Repo chính**: `feature-store-management`.
- **Các bước và vị trí:**
    1. **Kết nối nguồn dữ liệu mới**:
        - Nếu cần code connector mới: `feature-store-management/data_source_connectors/`.
        - Cấu hình connection (không commit secret): `feature-store-management/data_source_connectors/config/`.
    2. **EDA và Profiling dữ liệu nguồn**:
        - Thực hiện trong: `feature-store-management/notebooks_feature_dev/`. Sử dụng connector ở trên.
    3. **Thử nghiệm Feature Engineering**:
        - Tiếp tục trong: `feature-store-management/notebooks_feature_dev/`.
    4. **Triển khai Data Transformation Pipelines**:
        - Viết dbt models: `feature-store-management/data_transformation_pipelines/dbt_project_feast/models/`.
        - Hoặc Spark jobs: `feature-store-management/data_transformation_pipelines/spark_jobs_feast/`.
        - Hoặc Python scripts: `feature-store-management/data_transformation_pipelines/python_scripts_feast/`.
    5. **Định nghĩa Features trong Feast**:
        - Cập nhật/tạo file trong: `feature-store-management/feast_repository/feature_views/`, `entities.py`, `data_sources.py`.
        - Cập nhật `feature_store.yaml` nếu cần.
    6. **Viết Tests**:
        - `feature-store-management/tests/`.
    7. **Commit & Push**: Lên repo `feature-store-management`.
    8. **CI/CD (Jenkins)**:
        - Trigger `Jenkinsfile_feature_store` (từ `mlops-platform-infrastructure/jenkins_config/`).
        - Chạy tests.
        - Chạy `dbt run` (nếu có).
        - Chạy `feast apply` (sử dụng `feature-store-management/scripts/run_feast_apply.sh`).
    9. **Orchestration (Airflow)**:
        - DAGs trong `mlops-orchestration-pipelines/dags/data_ingestion_and_feature_store/` sẽ được trigger (theo lịch hoặc sự kiện) để chạy các data transformation pipelines và `feast materialize` (sử dụng `mlops-orchestration-pipelines/plugins/operators/feast_materialize_operator.py` nếu bạn tạo custom operator, hoặc PythonOperator với Feast SDK).

### 2. Khi xây 1 mô hình mới: Lấy feature, đánh giá, build model, train, build train pipeline, báo cáo, đóng gói

- **Người thực hiện**: Data Scientist, ML Engineer.
- **Repo chính**: `ml-model-development`, `mlops-orchestration-pipelines`.
- **Các bước và vị trí:**
    1. **Tạo thư mục dự án model mới**:
        - Trong `ml-model-development/models/your_new_model_project/`.
    2. **EDA, Feature Selection, Model Prototyping**:
        - Trong `ml-model-development/models/your_new_model_project/notebooks/`.
        - Sử dụng `ml-model-development/common_ml_utils/feature_store_client.py` để lấy data từ Feast.
        - Log các thử nghiệm ban đầu lên MLFlow Tracking Server (Server 2) bằng `mlflow.start_run()`.
    3. **Viết mã nguồn huấn luyện chính thức**:
        - Trong `ml-model-development/models/your_new_model_project/src/`.
        - `config.py`: Dùng Pydantic, kế thừa từ `BaseSettings` để load params từ env, file.
        - `train.py`: Script chính, sử dụng MLFlow để log metrics, params, model artifact (`mlflow.log_model`).
        - Kế thừa base model từ `ml-model-development/common_ml_utils/base_model_trainer.py`.
    4. **Viết Tests**:
        - `ml-model-development/models/your_new_model_project/tests/`.
    5. **Commit & Push**: Lên repo `ml-model-development`.
    6. **CI (Jenkins)**:
        - Trigger `Jenkinsfile_ml_model_development`.
        - Chạy tests, linting. (Không train ở đây, chỉ build/test code).
    7. **Xây dựng Training Pipeline (Airflow DAG)**:
        - **ML Engineer/Data Scientist** tạo DAG mới trong `mlops-orchestration-pipelines/dags/model_training_pipelines/`.
        - DAG sẽ:
            - Checkout code từ repo `ml-model-development` (phiên bản cụ thể).
            - Chuẩn bị môi trường huấn luyện (có thể dùng KubernetesPodOperator, DockerOperator).
            - Chạy script `train.py` từ repo `ml-model-development`. Script này sẽ tự log model lên MLFlow Model Registry (Server 2).
            - (Tùy chọn) Chạy `evaluate.py`, gửi thông báo.
    8. **Commit & Push DAG**: Lên repo `mlops-orchestration-pipelines`.
    9. **CI/CD cho DAGs (Jenkins)**:
        - Trigger `Jenkinsfile_mlops_orchestration`.
        - Test DAG, deploy lên Airflow (Server 2).
    10. **Xuất báo cáo phát triển**:
        - Notebooks đã dùng có thể được dọn dẹp, xuất ra HTML/PDF.
        - Hoặc tạo script báo cáo trong `ml-reporting-and-monitoring-logic/custom_reports/` để query MLFlow.
    11. **Đóng gói lưu trữ mô hình**:
        - MLFlow Model Registry (Server 2) đã tự động làm việc này khi `train.py` chạy `mlflow.log_model(..., registered_model_name="your_model_name")`.

### 3. Triển khai mô hình (production, service, batch, online)

- **Người thực hiện**: ML Engineer, DevOps Engineer.
    
- **Repo chính**: `ml-model-services`, `mlops-orchestration-pipelines` (cho batch).
    
- **Các bước và vị trí:**
    
    **A. Triển khai Online Service (API):**
    
    1. **Phát triển Model Service API**:
        - Trong `ml-model-services/services/your_model_api/`.
        - `app/core/model_handler.py`: Load model từ MLFlow Model Registry (phiên bản đã được duyệt, ví dụ: "Production" stage).
        - `app/business_logic/your_processing.py`: Implement Model Service Layer (tiền xử lý input API, gọi Feature Store online qua Feast SDK, gọi model) và Label Engine Layer (áp dụng business rules).
        - `Dockerfile` để đóng gói.
    2. **Commit & Push**: Lên repo `ml-model-services`.
    3. **CI/CD (Jenkins)**:
        - Trigger `Jenkinsfile_ml_model_services`.
        - Chạy tests.
        - Build Docker image.
        - Push image lên Container Registry (nếu có) hoặc Server 3.
        - Deploy lên Staging (nếu có), chạy smoke tests.
        - Deploy lên Production (Server 3) dùng Docker Compose (từ `mlops-platform-infrastructure/docker_compose_setups/`) hoặc Kubernetes manifests (từ `mlops-platform-infrastructure/kubernetes_deployments/` hoặc `ml-model-services/services/your_model_api/deployment_configs/`).
    
    **B. Triển khai Batch Serving:**
    
    4. **Xây dựng Batch Inference Pipeline (Airflow DAG)**:
        - Trong `mlops-orchestration-pipelines/dags/batch_inference_pipelines/`.
        - DAG sẽ: Lấy dữ liệu batch, lấy features từ Feast Offline Store, tải model từ MLFlow Model Registry, chạy dự đoán, áp dụng Label Engine, lưu kết quả.
    5. **Commit & Push DAG**: Lên repo `mlops-orchestration-pipelines`.
    6. **CI/CD cho DAGs**: Deploy lên Airflow (Server 2).

### 4. Điều phối Airflow

- **Repo**: `mlops-orchestration-pipelines` (định nghĩa DAGs), `mlops-platform-infrastructure` (cấu hình Airflow).
- **Airflow của Feature Store**: Các DAGs trong `mlops-orchestration-pipelines/dags/data_ingestion_and_feature_store/` sẽ điều phối các pipeline dữ liệu cho Feast. Chúng sử dụng Feast SDK (cài trong môi trường worker của Airflow) để trigger `materialize`.
- **Airflow Worker Environment**: `mlops-orchestration-pipelines/Dockerfile.airflow_custom_worker` và `requirements_airflow.txt` định nghĩa môi trường cho worker (bao gồm Feast SDK, MLFlow client, các thư viện DB,...).

### 5. Phát triển thử nghiệm 1 service mới

- **Repo**: `ml-model-services` (nếu là model API) hoặc tạo repo mới nếu là service độc lập.
- **Local Development**: Dùng Docker Compose từ `mlops-platform-infrastructure/docker_compose_setups/`để dựng các dependencies (DB giả lập, MLFlow local).

### 6. Trigger các luồng CI/CD

- **Công cụ**: Jenkins (Server 2).
- **Trigger**: Webhooks từ Git (push, merge), manual trigger, scheduled.
- **Định nghĩa Pipelines**: Các `Jenkinsfile_*` trong `mlops-platform-infrastructure/jenkins_config/`.

### 7. Xây dựng các báo cáo mới, monitoring model mới

- **Repo**: `ml-reporting-and-monitoring-logic`.
- **Dashboards**: Tạo/cập nhật JSON/NDJSON trong `dashboards_as_code/`. CI/CD của repo này sẽ dùng Grafana/Kibana API để deploy.
- **Custom Reports**: Viết scripts/notebooks trong `custom_reports/`. Có thể được trigger bởi Airflow DAGs trong `mlops-orchestration-pipelines/dags/utility_dags/`.
- **Model Service Metrics**: Logic expose metrics nằm trong code của từng service (`ml-model-services/.../monitoring_middleware.py`). Prometheus (Server 3) cào các endpoint này. Alert rules có thể định nghĩa trong `ml-reporting-and-monitoring-logic/alerting_configurations/` và được apply vào Prometheus/Alertmanager.

---

## 📌 Làm rõ các điểm khác

1. **Feature Store Profiling/EDA và Feature Engineering**:
    
    - Đúng như bạn muốn, việc này nằm trong **`feature-store-management`**.
    - **Profiling/EDA**: `notebooks_feature_dev/` sử dụng Pandas, PySpark, các thư viện profiling.
    - **Feature Engineering**: Ý tưởng từ notebooks sẽ được hiện thực hóa trong `data_transformation_pipelines/` (dbt, Spark).
    - **Feast**: Chỉ lưu trữ features đã được tính toán.
    - **Clean/Aggregate nhẹ theo thời gian**: Có thể làm trong dbt/Spark trước khi ingest vào Feast, hoặc dùng on-demand transformations của Feast nếu phù hợp.
    - **Category preprocessing**: Để trong `ml-model-development/models/.../src/preprocessor.py` là hợp lý để tránh phình dữ liệu Feature Store.
2. **Viết data connection mới, profiling, EDA rồi mới quyết định feature engineering**:
    
    - Chính xác, quy trình này diễn ra trong **`feature-store-management`**.
        1. Thêm/cập nhật connector trong `data_source_connectors/`.
        2. Dùng connector đó trong `notebooks_feature_dev/` để profiling, EDA.
        3. Dựa trên kết quả, quyết định logic feature engineering và implement trong `data_transformation_pipelines/`, sau đó định nghĩa feature views trong `feast_repository/`.
3. **Thiết kế base model, kế thừa, data model (Pydantic), `settings.py`**:
    
    - **Base Model (cho logic huấn luyện)**: `ml-model-development/common_ml_utils/base_model_trainer.py`. Các model cụ thể sẽ kế thừa từ đây.
    - **Data Model (Pydantic)**:
        - Cho cấu trúc dữ liệu chung (ví dụ: training data contract): `ml-model-development/common_ml_utils/data_schemas/`.
        - Cho request/response API: Trong từng service API, ví dụ `ml-model-services/services/fraud_detection_api/app/schemas.py`.
        - Cho cấu hình: Dùng Pydantic `BaseSettings` trong các file `config.py`.
    - **`settings.py` (khai báo tham số mô hình)**:
        - Mỗi model project trong `ml-model-development/models/` sẽ có file `src/config.py`. File này sử dụng Pydantic `BaseSettings` để load cấu hình từ biến môi trường, file `.env`, hoặc các nguồn khác.
            
            Python
            
            ```
            # Ví dụ: ml-model-development/models/fraud_detection_xgboost/src/config.py
            from pydantic_settings import BaseSettings
            from typing import List, Optional
            
            class FraudModelHyperparameters(BaseSettings):
                n_estimators: int = 100
                learning_rate: float = 0.1
                max_depth: int = 3
                # ... các HPs khác
            
            class TrainingConfig(BaseSettings):
                mlflow_tracking_uri: str
                mlflow_experiment_name: str = "fraud_detection"
                feature_view_name: str = "fraud_transaction_features" # Tên FeatureView trong Feast
                label_column: str = "is_fraudulent"
                test_split_ratio: float = 0.2
                random_seed: int = 42
                hyperparameters: FraudModelHyperparameters = FraudModelHyperparameters()
            
                class Config:
                    env_prefix = "TRAINING_" # Ví dụ: TRAINING_MLFLOW_TRACKING_URI
                    env_file = ".env" # Load từ file .env
                    # Cho phép load nested Pydantic models từ biến môi trường
                    # Ví dụ: TRAINING_HYPERPARAMETERS__N_ESTIMATORS=200
                    # Chú ý dấu "__" cho nested.
                    # Hoặc có thể parse từ JSON string nếu phức tạp hơn.
            
            # Sử dụng:
            # from .config import TrainingConfig
            # training_cfg = TrainingConfig()
            # print(training_cfg.hyperparameters.n_estimators)
            ```
            

Cấu trúc này rất chi tiết và sẵn sàng cho việc triển khai một hệ thống MLOps phức tạp.
