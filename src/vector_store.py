import os
from src.config import Config
from langchain_community.vectorstores import AzureSearch, Chroma

def get_vector_store(embedding_function):
    """
    Returns a LangChain VectorStore based on the configuration.
    
    Args:
        embedding_function: The LangChain embedding function to use.
    """
    store_type = Config.VECTOR_STORE_TYPE.lower()
    
    if store_type == "chroma":
        # ChromaDB implementation
        try:
            # Use a local persistent directory for Chroma
            persist_directory = os.path.join(os.getcwd(), "chroma_db")
            
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embedding_function,
                collection_name="product-catalog"
            )
            print(f"Initialized ChromaDB (LangChain) at {persist_directory}")
            return vector_store
            
        except ImportError:
            raise ImportError("chromadb is not installed. Please install it with 'pip install chromadb'.")
            
    elif store_type == "azure_search":
        # Azure AI Search implementation
        endpoint = Config.AZURE_SEARCH_ENDPOINT
        key = Config.AZURE_SEARCH_KEY
        index_name = Config.AZURE_SEARCH_INDEX_NAME
        
        if not endpoint or not key:
            raise ValueError("AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY must be set for Azure Search.")
            
        vector_store = AzureSearch(
            azure_search_endpoint=endpoint,
            azure_search_key=key,
            index_name=index_name,
            embedding_function=embedding_function.embed_query
        )
        print(f"Initialized Azure AI Search (LangChain) for index '{index_name}'")
        return vector_store
        
    else:
        raise ValueError(f"Unsupported VECTOR_STORE_TYPE: {store_type}")

