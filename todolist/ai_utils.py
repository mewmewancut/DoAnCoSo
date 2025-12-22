"""
AI utilities for TodoList application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_llm_client():
    """
    Get LLM client based on environment configuration
    Returns configured LLM instance
    """
    provider = os.getenv('LLM_PROVIDER', 'openai')
    
    if provider == 'openai':
        from langchain_openai import ChatOpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key
        )
    
    # TODO: Add support for other providers (Gemini, Groq)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def test_connection():
    """
    Test LLM API connection
    """
    try:
        llm = get_llm_client()
        response = llm.invoke("Hello, are you working?")
        print("✓ LLM connection successful!")
        print(f"Response: {response.content}")
        return True
    except Exception as e:
        print(f"✗ LLM connection failed: {str(e)}")
        return False
