import sys
import os
# Add project root to sys.path so we can import from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from src.search_engine import VisualSearchEngine
from src.config import Config
import src.monitoring # Enable MLflow/Azure Monitor
import time
import os

st.set_page_config(page_title="Visual Search RAG", layout="wide")

st.title("🛍️ Visual Product Search")
st.markdown("Upload an image to find similar products in the catalog.")

# Initialize Engine
@st.cache_resource
def get_engine():
    # Only init if secrets are present, else show warning
    try:
        return VisualSearchEngine()
    except Exception as e:
        st.error(f"Failed to initialize search engine: {e}")
        return None

def display_results(results, generated_desc):
    st.success(f"Found {len(results)} matches.")
    
    with st.expander("See Query Understanding"):
        st.write(generated_desc)
    
    st.subheader("Top Matches")
    if results:
        for i, doc in enumerate(results):
            with st.container():
                col_img, col_txt = st.columns([1, 2])
                
                with col_img:
                    # Try to get image path from metadata
                    img_path = doc.metadata.get("original_image_path") or doc.metadata.get("image_path")
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, caption=f"Product {doc.metadata.get('product_id')}", width="stretch")
                    else:
                        st.warning("Image not available")
                        
                with col_txt:
                    st.markdown(f"**{i+1}. {doc.metadata.get('product_id', 'Unknown Product')}**")
                    st.write(doc.page_content)
                    with st.expander("Metadata"):
                        st.json(doc.metadata)
                st.divider()
        
        # Synthesis
        st.subheader("AI Recommendation")
        with st.spinner("Synthesizing recommendation..."):
            recommendation = engine.synthesize_response(results, generated_desc)
            st.write(recommendation)
    else:
        st.warning("No matches found.")

engine = get_engine()

# Cache clear option (for debugging)
if st.sidebar.button("🔄 Clear Cache & Reload"):
    st.cache_resource.clear()
    st.rerun()

# Main Search Interface
st.markdown("### 🔍 Search Products")
st.markdown("Enter a description **or** upload an image to find similar products.")

# Unified Search Area
col_search, col_upload = st.columns([3, 1])

with col_search:
    query_text = st.text_input(
        "Describe the product you're looking for",
        placeholder="e.g., 'blue denim jacket' or 'red running shoes'",
        label_visibility="collapsed"
    )

with col_upload:
    uploaded_file = st.file_uploader(
        "Or upload image",
        type=["jpg", "png", "jpeg"],
        label_visibility="collapsed"
    )

search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Search Logic
if search_button and engine:
    if uploaded_file is not None:
        # Image Search
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(uploaded_file, caption='Your Image', width="stretch")
        with col2:
            with st.spinner("🔍 Analyzing image and searching catalog..."):
                image_bytes = uploaded_file.getvalue()
                start_time = time.time()
                results, generated_desc = engine.search_similar_products(image_bytes)
                latency = time.time() - start_time
                st.info(f"✅ Search completed in {latency:.2f}s")
                display_results(results, generated_desc)
                
    elif query_text:
        # Text Search
        st.markdown("---")
        with st.spinner("🔍 Searching catalog..."):
            start_time = time.time()
            results, generated_desc = engine.search_by_text(query_text)
            latency = time.time() - start_time
            st.info(f"✅ Search completed in {latency:.2f}s")
            display_results(results, generated_desc)
    else:
        st.warning("⚠️ Please enter a search query or upload an image.")


