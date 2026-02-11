import os
import pandas as pd
from pathlib import Path
import json

# Dataset: https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small
# Expected Structure:
# data/
#   styles.csv
#   images/
#     1163.jpg
#     ...

DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"
STYLES_PATH = DATA_DIR / "styles.csv"

def download_kaggle_dataset():
    """
    Attempts to download the dataset using the Kaggle API.
    Requires ~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY env vars.
    """
    try:
        import kaggle
        print("Authenticating with Kaggle...")
        kaggle.api.authenticate()
        
        print("Downloading dataset paramaggarwal/fashion-product-images-small...")
        kaggle.api.dataset_download_files(
            "paramaggarwal/fashion-product-images-small",
            path=DATA_DIR,
            unzip=True
        )
        print("Download complete.")
        
    except ImportError:
        print("Kaggle library not installed or not configured.")
        print("Please run: pip install kaggle")
        print("And ensure you have kaggle.json in ~/.kaggle/")
    except Exception as e:
        print(f"Failed to download dataset: {e}")
        print("Please download manually from https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small")
        print("And extract to the 'data' folder.")

def load_catalog():
    """
    Loads the styles.csv and prepares the catalog dataframe.
    """
    if STYLES_PATH.exists():
        print(f"styles.csv found at {STYLES_PATH}. Using local data.")
    else:
        print("styles.csv not found. Attempting download...")
        download_kaggle_dataset()
    
    if not STYLES_PATH.exists():
        print("Error: Dataset not found. Please ensure 'styles.csv' represents the catalog.")
        return None

    # Load styles.csv
    # Some lines might have bad formatting, utilizing on_bad_lines='skip'
    try:
        df = pd.read_csv(STYLES_PATH, on_bad_lines='skip')
        
        # Filter for valid images
        valid_rows = []
        for index, row in df.iterrows():
            image_path = IMAGES_DIR / f"{row['id']}.jpg"
            if image_path.exists():
                valid_rows.append({
                    "product_id": row['id'],
                    "category": row['masterCategory'],
                    "sub_category": row['subCategory'],
                    "article_type": row['articleType'],
                    "gender": row['gender'],
                    "base_colour": row['baseColour'],
                    "season": row['season'],
                    "usage": row['usage'],
                    "display_name": row['productDisplayName'],
                    "image_path": str(image_path.absolute())
                })
        
        catalog_df = pd.DataFrame(valid_rows)
        print(f"Loaded {len(catalog_df)} valid products from catalog.")
        
        # Save processed catalog for easier loading next time
        catalog_df.to_csv(DATA_DIR / "processed_catalog.csv", index=False)
        return catalog_df

    except Exception as e:
        print(f"Error processing styles.csv: {e}")
        return None

if __name__ == "__main__":
    load_catalog()
