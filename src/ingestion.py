import os
import time
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from src.search_engine import VisualSearchEngine
from src.config import Config
from langchain_core.documents import Document
import mlflow

# Define paths
DATA_DIR = Path("data")
PROCESSED_CATALOG_PATH = DATA_DIR / "processed_catalog.csv"

def ingest_catalog_item(row, engine: VisualSearchEngine):
    """
    Ingests a single product into the vector store.
    """
    try:
        image_path = row['image_path']
        product_id = row['product_id']
        
        # Check if image exists
        # Check if image exists
        if not os.path.exists(image_path):
            # Fallback: Try relative path in data/images
            filename = Path(image_path).name
            relative_path = DATA_DIR / "images" / filename
            if relative_path.exists():
                image_path = str(relative_path)
            else:
                print(f"Skipping {product_id}: Image not found at {image_path}")
                return

        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Generate description using GPT-4o
        description = engine.generate_image_description(image_bytes)
        
        if description == "[CONTENT BLOCKED]":
            print(f"Skipping {product_id}: Content blocked by governance.")
            return

        # Create Metadata dictionary from the row
        metadata = row.to_dict()
        metadata["original_image_path"] = str(image_path) # Ensure path is string
        
        # Create Document
        doc = Document(
            page_content=description,
            metadata=metadata
        )
        
        # Add to Vector Store
        engine.vector_store.add_documents([doc])
        print(f"Ingested {product_id}")

    except Exception as e:
        print(f"Failed to ingest {row.get('product_id', 'unknown')}: {e}")

def main():
    print("Starting ingestion process...")
    

    # 1. Load Catalog
    if not PROCESSED_CATALOG_PATH.exists():
        print("Processed catalog not found. Running data loader...")
        from src.data_loader import load_catalog
        df = load_catalog()
    else:
        print(f"Loading catalog from {PROCESSED_CATALOG_PATH}")
        df = pd.read_csv(PROCESSED_CATALOG_PATH)
    
    if df is None or df.empty:
        print("No data to ingest. Exiting.")
        return

    # 2. Initialize Engine
    try:
        engine = VisualSearchEngine()
    except Exception as e:
        print(f"Failed to initialize engine: {e}")
        return

    print(f"Found {len(df)} products. Starting ingestion...")
    
    # 3. Ingest Loop
    # Use INGESTION_LIMIT from environment (0 = no limit, processes all items)
    limit = Config.INGESTION_LIMIT
    
    if limit > 0:
        print(f"Processing first {limit} items (set via INGESTION_LIMIT env variable).")
        df_subset = df.head(limit)
    else:
        print(f"Processing all {len(df)} items (INGESTION_LIMIT=0 means no limit).")
        df_subset = df
    
    mlflow.set_experiment(Config.MLFLOW_EXPERIMENT_NAME)
    
    with mlflow.start_run(run_name="catalog_ingestion") as run:
        items_ingested = 0
        items_failed = 0
        
        for index, row in tqdm(df_subset.iterrows(), total=len(df_subset)):
            try:
                ingest_catalog_item(row, engine)
                items_ingested += 1
            except Exception as e:
                print(f"Failed to ingest item at index {index}: {e}")
                items_failed += 1
            
            # Sleep slightly to avoid strict rate limits if needed
            time.sleep(1)

        mlflow.log_metric("items_ingested", items_ingested)
        mlflow.log_metric("items_failed", items_failed)
        mlflow.log_metric("total_processed", len(df_subset))

    print("Ingestion complete.")

if __name__ == "__main__":
    main()
