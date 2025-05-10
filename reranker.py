import os
import re
import json
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("models/gemini-2.0-flash")

def rerank(query, candidates):
    """
    Rerank the candidate assessments using Gemini.
    
    Args:
        query: The job description
        candidates: List of assessment dictionaries
    
    Returns:
        Dictionary containing the recommended assessments
    """
    # Ensure we have candidates
    if not candidates:
        return {"error": "No candidate assessments to rerank"}
    
    # Print debugging info
    print(f"Reranking {len(candidates)} candidates")
    print(f"Sample candidate: {json.dumps(candidates[0], indent=2)}")
    
    # Clean up candidates data for API
    cleaned_candidates = []
    for candidate in candidates:
        # Create a clean copy
        clean_candidate = {}
        
        # Copy required fields
        for field in ["url", "adaptive_support", "remote_support", "description", "duration", "test_type"]:
            if field in candidate:
                # Special handling for test_type
                if field == "test_type" and isinstance(candidate[field], list):
                    clean_candidate[field] = candidate[field]
                else:
                    clean_candidate[field] = candidate[field]
            else:
                # Default values for missing fields
                if field == "test_type":
                    clean_candidate[field] = ["Unknown"]
                elif field == "duration":
                    clean_candidate[field] = None
                else:
                    clean_candidate[field] = "Unknown"
        
        cleaned_candidates.append(clean_candidate)
    
    # Create the prompt for Gemini
    prompt = f"""
    Given a job description, rank the most relevant SHL assessments based on how well they match the job requirements.
    
    Job description: "{query}"
    
    Candidate SHL assessments: {json.dumps(cleaned_candidates, indent=2)}
    
    Rank the most relevant assessments and return a JSON list in this format:
    {{
        "recommended_assessments": [
            {{
                "url": "...",
                "adaptive_support": "Yes/No",
                "remote_support": "Yes/No",
                "description": "...",
                "duration": integer or null,
                "test_type": ["type1", "type2", ...]
            }}
        ]
    }}
    
    CRITICAL INSTRUCTIONS:
    1. Return ONLY valid JSON without any markdown code blocks or extra text
    2. Preserve the exact URL values from the input - do not modify them
    3. Include all fields from the original assessment data
    4. Limit to the top 10 most relevant assessments
    5. Ensure the JSON is properly formatted with all fields
    6. Keep all test_type values as arrays/lists, even if there's only one type
    """
    
    # Generate response
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Try to extract JSON from possible markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1).strip()
        
        # Parse the JSON
        result = json.loads(response_text)
        
        # Validate the response structure
        if "recommended_assessments" not in result:
            return {"error": "Invalid response format: missing recommended_assessments key"}
        
        # Ensure each assessment has the required fields
        for assessment in result["recommended_assessments"]:
            if "url" not in assessment:
                assessment["url"] = "https://www.shl.com/missing-url"
            if "test_type" not in assessment:
                assessment["test_type"] = ["Unknown"]
            if not isinstance(assessment["test_type"], list):
                assessment["test_type"] = [assessment["test_type"]]
                
        return result
        
    except Exception as e:
        error_msg = f"Error in reranking: {str(e)}"
        print(error_msg)
        return {"error": error_msg}