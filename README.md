# 🛡️ Fraud Detection System — End-to-End Pipeline (XGBoost + Kafka + Airflow + MLflow)

This project is a **semi-production-ready pipeline** for **fraud detection**, integrating state-of-the-art tools and cloud-native features to simulate an industrial-grade data science workflow.

---

## 🚀 Overview

The pipeline is designed to:
- Ingest real-time and batch data using **Apache Kafka** (Confluent Cloud).
- Run DAGs with **Apache Airflow** to orchestrate tasks.
- Use **XGBoost** for high-performance fraud detection modeling.
- Log experiments and metrics with **MLflow**.
- Store artifacts in **MinIO** (S3-compatible object storage).
- Delegate task execution to distributed workers via **Celery**.
- Perform inference and scalable data processing using **Apache Spark** and **Hadoop**.
- Manage all services with **Docker**, and develop using **PyCharm** IDE.

---

## 🧠 Key Features

- 📡 **Data Ingestion**: Real-time data streaming from Kafka topics on Confluent Cloud.
- 🎯 **Model Training**: 
  - Temporal and behavioral **feature engineering**.
  - Model re-training until optimal performance is achieved.
  - Training/test data split handled dynamically via Kafka stream.
- 📊 **Model Management**:
  - Experiments tracked with **MLflow**.
  - Artifacts stored in **MinIO** (S3-compatible).
- 🧵 **Task Management**:
  - Scheduled and monitored using **Airflow**.
  - Execution distributed using **Celery** workers.
- 🔎 **Inference & Evaluation**:
  - Real-time and batch inference using **Spark** and **Hadoop**.
  - All key metrics and visualizations included for interpretability.
- 🐳 **Containerization**: Fully containerized stack using Docker.

---

## 🧰 Tech Stack

| Category          | Tools/Frameworks |
|------------------|------------------|
| Data Streaming    | Apache Kafka (Confluent Cloud) |
| Orchestration     | Apache Airflow |
| ML Model          | XGBoost |
| Experiment Tracking | MLflow |
| Artifact Storage  | MinIO (S3) |
| Distributed Workers | Celery |
| Inference & Scaling | Apache Spark, Hadoop |
| Containerization  | Docker |
| IDE               | PyCharm |

---

## 🧪 ML Pipeline Flow

1. **Kafka** streams incoming data.
2. **Airflow DAG** schedules and orchestrates:
   - Data preprocessing
   - Feature engineering (temporal & behavioral)
   - Training and evaluation
3. **XGBoost** trains and evaluates model.
4. **MLflow** logs:
   - Parameters
   - Metrics
   - Trained models
5. **Artifacts** (models, plots) are stored on **MinIO**.
6. **Celery** handles asynchronous tasks and job distribution.
7. **Spark/Hadoop** used for scalable inference and analysis.
8. New data continues to flow from Kafka for continuous improvement.

---

## 📈 Results & Metrics

All results include:
- ROC-AUC, Precision, Recall, F1-score
- Confusion matrix
- Feature importances
- Inference latency benchmarks
- Re-training comparisons

---

## 🛠️ Development & Deployment

- Developed using **PyCharm**
- Services managed using **Docker Compose**
- Compatible with **AWS integrations** for future deployment scaling

---

## 🤝 Contributions

Contributions, ideas, and improvements are welcome. Please open an issue or pull request!

---

## 📄 License

MIT License

---



