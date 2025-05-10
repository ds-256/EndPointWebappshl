import pandas as pd
import gradio as gr
from retriever import get_relevant_passages
from reranker import rerank

# Load and clean CSV
def clean_df(df):
    df = df.copy()
    
    # Get column names for reference
    print(f"Original columns: {df.columns}")
    
    # Ensure clean URLs from the second column
    second_col = df.iloc[:, 2].astype(str)  # Pre-packaged Job Solutions column
    
    if second_col.str.contains('http').any() or second_col.str.contains('www').any():
        df["url"] = second_col  # Already has full URLs
    else:
        # Create full URLs from IDs
        df["url"] = "https://www.shl.com" + second_col.str.replace(r'^(?!/)', '/', regex=True)
    
    # Map T/F to Yes/No for remote testing and adaptive support
    df["remote_support"] = df.iloc[:, 3].map(lambda x: "Yes" if x == "T" else "No")
    df["adaptive_support"] = df.iloc[:, 4].map(lambda x: "Yes" if x == "T" else "No")
    
    # Handle test_type properly - convert string representation of list to actual list
    df["test_type"] = df.iloc[:, 5].apply(lambda x: eval(x) if isinstance(x, str) else x)
    
    # Get description from column 7
    df["description"] = df.iloc[:, 6]
    
    # Extract duration with error handling from column 10
    df["duration"] = pd.to_numeric(
        df.iloc[:, 9].astype(str).str.extract(r'(\d+)')[0], 
        errors='coerce'
    )
    
    # Print sample of cleaned data for debugging
    print(f"Sample of cleaned data: {df[['url', 'adaptive_support', 'remote_support', 'description', 'duration', 'test_type']].head(2)}")
    
    return df[["url", "adaptive_support", "remote_support", "description", "duration", "test_type"]]

try:
    # Load CSV with explicit encoding
    df = pd.read_csv("assesments.csv", encoding='utf-8')
    print(f"CSV loaded successfully with {len(df)} rows")
    df_clean = clean_df(df)
except Exception as e:
    print(f"Error loading or cleaning data: {e}")
    # Create an empty DataFrame with required columns as fallback
    df_clean = pd.DataFrame(columns=["url", "adaptive_support", "remote_support", 
                                     "description", "duration", "test_type"])

def validate_and_fix_urls(candidates):
    """Validates and fixes URLs in candidate assessments."""
    for candidate in candidates:
        # Skip if candidate is not a dictionary
        if not isinstance(candidate, dict):
            continue
            
        # Ensure URL exists
        if 'url' not in candidate or not candidate['url']:
            candidate['url'] = 'https://www.shl.com/missing-url'
            continue
            
        url = str(candidate['url'])
        
        # Fix URLs that are just numbers
        if url.isdigit():
            candidate['url'] = f"https://www.shl.com/{url}"
            continue
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            candidate['url'] = f"https://www.shl.com{url}" if url.startswith('/') else f"https://www.shl.com/{url}"
            
    return candidates

def recommend(query):
    if not query.strip():
        return {"error": "Please enter a job description"}
    
    try:
        # Print some debug info
        print(f"Processing query: {query[:50]}...")
        
        # Get relevant passages
        top_k_df = get_relevant_passages(query, df_clean, top_k=20)
        
        # Debug: Check if we got any results
        print(f"Retrieved {len(top_k_df)} assessments")
        
        if top_k_df.empty:
            return {"error": "No matching assessments found"}
            
        # Convert test_type to list if it's not already
        top_k_df['test_type'] = top_k_df['test_type'].apply(
            lambda x: x if isinstance(x, list) else 
                     (eval(x) if isinstance(x, str) and x.startswith('[') else [str(x)])
        )
        
        # Handle nan values for duration
        top_k_df['duration'] = top_k_df['duration'].fillna(-1).astype(int)
        top_k_df.loc[top_k_df['duration'] == -1, 'duration'] = None
        
        # Convert DataFrame to list of dictionaries
        candidates = top_k_df.to_dict(orient="records")
        
        # Additional URL validation
        candidates = validate_and_fix_urls(candidates)
        
        # Print sample of data being sent to reranker
        if candidates:
            print(f"Sample candidate being sent to reranker: {candidates[0]}")
        
        # Get recommendations
        result = rerank(query, candidates)
        
        # Post-process result
        if 'recommended_assessments' in result:
            result['recommended_assessments'] = validate_and_fix_urls(result['recommended_assessments'])
            print(f"Returning {len(result['recommended_assessments'])} recommended assessments")
            
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error: {str(e)}\n{error_details}")
        return {"error": f"Error processing request: {str(e)}"}

iface = gr.Interface(
    fn=recommend,
    inputs=gr.Textbox(label="Enter Job Description", lines=4),
    outputs="json",
    title="SHL Assessment Recommender",
    description="Paste a job description to get the most relevant SHL assessments."
)

if __name__ == "__main__":
    iface.launch()
