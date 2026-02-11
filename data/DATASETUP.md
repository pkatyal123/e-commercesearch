# Data Setup & Testing Guide

## 1. Dataset Setup
This project uses the [Fashion Product Images (Small)](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small) dataset.

### Option A: Automatic Download (Requires Kaggle API)
1.  Ensure you have your `kaggle.json` in `~/.kaggle/` or set `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables.
2.  Run the data loader:
    ```bash
    python src/data_loader.py
    ```

### Option B: Manual Download
1.  Download the dataset from Kaggle.
2.  Extract the contents into the `data/` folder in this project root.
3.  Ensure you have:
    *   `data/styles.csv`
    *   `data/images/*.jpg`