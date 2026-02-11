# 🩺 Visual Search RAG System with GenAIOps

A comprehensive **GenAIOps (LLMOps)** solution for an e-commerce Visual Search system. This project allows users to upload an image of a product and find similar items in a catalog using a "Caption-then-Embed" strategy powered by GPT-4o and Azure AI Search.

It features a robust **Governance & Guardrails** layer and a unified **Monitoring** system.

## 🌟 Key Features

*   **Multimodal Search**: Uses GPT-4o to generate detailed visual descriptions of images, enabling semantic search using text embeddings.
*   **Vector Store Agnostic**: Switch between **Azure AI Search** (Production) and **ChromaDB** (Local/Dev) via configuration.
*   **Governance & Guardrails**:
    *   **Safety Validator**: Detects prompt injection, jailbreaks, and unsafe content (using Azure Content Safety).
    *   **Compliance Checker**: Detects and redacts PII (GDPR/HIPAA compliance).
    *   **Hallucination Detection**: Checks responses for uncertain language.
*   **Observability**: Integrated **MLflow** and **Azure Monitor** (Application Insights) for full tracing and metrics.
*   **Evaluation**: Pipeline using **Azure AI Evaluation SDK** to measure Relevance and Coherence.

---

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **Azure Subscription** with:
    *   **Azure OpenAI Service** (Deployments: `gpt-4o`, `text-embedding-3-small`)
    *   **Azure AI Search** (Optional if using ChromaDB)
    *   **Azure Content Safety** (Optional but recommended)
    *   **Azure Monitor** (Optional)
*   **Docker** (for containerization)

---

## 🚀 Setup & Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd week_14_llmops
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    *   Copy the sample configuration file:
        ```bash
        cp .env.sample .env
        ```
    *   Open `.env` and configure:
        *   `VECTOR_STORE_TYPE`: Set to `chroma` (local) or `azure_search` (cloud).
        *   `AZURE_OPENAI_*`: Add your keys and endpoints.
        *   `MLFLOW_TRACKING_URI`: Set tracking URI (default `http://localhost:5000` for local).

---


## 🏃‍♂️ Usage Guide - The LLMOps Pipeline

### 1. Start Monitoring (MLflow)
Start the local MLflow server to track all experiments and traces.

```bash
./start_mlflow.sh
```
*   View the dashboard at `http://localhost:5000`.

### 2. Data Ingestion
Populate the vector index (Chroma or Azure) with your product catalog.

```bash
python src/data_loader.py  # Load data from Kaggle/Local
# Ingest data into Vector Store
python -m src.ingestion
```

### 3. Running the Application
Launch the Streamlit interface. This handles the **RAG flow** with **Governance** checks.

```bash
streamlit run src/app.py
```
*   **Governance in Action**: Try uploading an unsafe image or simulating a prompt injection to see the `GovernanceGate` block it.
*   **Monitoring**: Check MLflow traces for every search request.



---

## 🛡️ Governance & Guardrails

The system uses a layered safety approach located in `governance/` and `guardrails/`.

*   **Governance Gate** (`governance.governance_gate`): Orchestrates checks.
*   **Safety Validator**: Blocks harmful content.
*   **Compliance Checker**: Redacts PII.

---

## 📊 Monitoring

Unified monitoring via `monitoring/`.

*   **Logger**: Structured JSON logging.
*   **Metrics**: Token usage, latency, cost.
*   **Traces**: Distributed tracing via OpenTelemetry.
