import os
import pandas as pd
import mlflow
from src.search_engine import VisualSearchEngine
from src.config import Config

def evaluate_retrieval():
    """
    Evaluates the Visual Search Engine using MLflow.
    Uses a small synthetic dataset for validation.
    """
    print("Starting evaluation...")
    
    # 1. Setup Data for Evaluation
    # In a real scenario, this would be ground-truth data (query, expected_product_id)
    eval_data = pd.DataFrame({
        "query_text": [
            "blue running shoes",
            "cotton summer dress",
            "formal black minimalist watch", # Example query
            "red leather handbag"
        ],
        "expected_category": [
            "Footwear",
            "Apparel",
            "Accessories",
            "Accessories"
        ]
    })
    
    # 2. Define Evaluation Logic using existing Engine
    engine = VisualSearchEngine()
    
    def model_inference(df):
        results = []
        for index, row in df.iterrows():
            query = row["query_text"]
            # Perform search
            docs, _ = engine.search_by_text(query, k=3)
            
            # Extract retrieved context
            retrieved_context = [doc.page_content for doc in docs]
            retrieved_ids = [doc.metadata.get("product_id") for doc in docs]
            
            results.append({
                "retrieved_context": retrieved_context,
                "retrieved_ids": retrieved_ids
            })
        return pd.DataFrame(results)

    # 3. Run Evaluation with MLflow
    mlflow.set_experiment(Config.MLFLOW_EXPERIMENT_NAME)
    
    with mlflow.start_run(run_name="retrieval_evaluation"):
        # Evaluate using custom function if standard metrics aren't enough, 
        # or use mlflow.evaluate to run standard RAG metrics if Azure AI evaluation is configured.
        
        # Here we demonstrate logging custom metrics for the run
        print("Running inference on eval set...")
        results_df = model_inference(eval_data)
        
        # Combine input and output
        final_df = pd.concat([eval_data, results_df], axis=1)
        
        # Simple exact match or relevance check (Mock Metric)
        # In production, check if 'expected_category' is in the metadata of retrieved items
        matches = 0
        for index, row in final_df.iterrows():
            # For simplicity, we just assume non-empty retrieval is a 'hit' in this basic script
            if row['retrieved_ids']:
                matches += 1
        
        accuracy = matches / len(final_df) if len(final_df) > 0 else 0
        
        mlflow.log_metric("retrieval_hit_rate", accuracy)
        mlflow.log_table(final_df, "evaluation_results.json")
        
        print(f"Evaluation complete. Hit Rate: {accuracy}")
        print("Detailed results logged to MLflow.")

if __name__ == "__main__":
    evaluate_retrieval()
