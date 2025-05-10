import pandas as pd
from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer("all-MiniLM-L6-v2")

def format_test_type(test_types):
    """Format test type for embedding."""
    if isinstance(test_types, list):
        return ', '.join(test_types)
    if isinstance(test_types, str) and test_types.startswith('['):
        try:
            return ', '.join(eval(test_types))
        except:
            pass
    return str(test_types)

def get_relevant_passages(query, df, top_k=20):
    """Find most relevant assessments using semantic search."""
    # Create a copy to avoid modifying the original dataframe
    df_copy = df.copy()
    
    if df_copy.empty:
        print("Warning: Empty dataframe passed to get_relevant_passages")
        return df_copy
    
    # Display dataframe info for debugging
    print(f"Dataframe columns: {df_copy.columns}")
    print(f"Dataframe sample: {df_copy.head(1).to_dict('records')}")
    
    # Ensure test_type is properly formatted
    if 'test_type' in df_copy.columns:
        # Convert test_type to proper format if it's a string representation of a list
        df_copy['test_type'] = df_copy['test_type'].apply(
            lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else 
                    ([x] if not isinstance(x, list) else x)
        )
    
    # Concatenate all fields into a single string per row for embedding
    corpus = []
    for _, row in df_copy.iterrows():
        try:
            description = row['description'] if pd.notna(row['description']) else ""
            test_types = format_test_type(row['test_type']) if 'test_type' in row else ""
            adaptive = row['adaptive_support'] if 'adaptive_support' in row else "Unknown"
            remote = row['remote_support'] if 'remote_support' in row else "Unknown"
            duration = f"{row['duration']} minutes" if pd.notna(row.get('duration')) else "Unknown duration"
            
            text = (f"{description} "
                   f"Test types: {test_types}. "
                   f"Adaptive support: {adaptive}. "
                   f"Remote support: {remote}. "
                   f"Duration: {duration}.")
            corpus.append(text)
        except Exception as e:
            print(f"Error processing row: {e}")
            corpus.append("Error processing assessment")
    
    print(f"Created corpus with {len(corpus)} items")
    
    # Generate embeddings
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Find most similar
    hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=min(top_k, len(corpus)))[0]
    
    # Get top matches
    result = df_copy.iloc[[hit['corpus_id'] for hit in hits]].copy()
    print(f"Found {len(result)} relevant passages")
    
    # Add score for debugging
    result['score'] = [hit['score'] for hit in hits]
    
    return result
