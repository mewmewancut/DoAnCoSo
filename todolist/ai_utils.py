"""
AI utilities for TodoList application
Enhanced with better error handling and retry logic
"""
import os
import json
import time
from dotenv import load_dotenv
from ai_prompts import (
    improve_description_prompt,
    suggest_priority_prompt,
    generate_subtasks_prompt
)

# Load environment variables
load_dotenv()


def get_llm_client():
    """
    Get LLM client based on environment configuration
    Returns configured LLM instance with timeout and retry settings
    """
    provider = os.getenv('LLM_PROVIDER', 'gemini')
    
    if provider == 'openai':
        from langchain_openai import ChatOpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key,
            timeout=15,  # 15 seconds timeout
            max_retries=2  # Retry up to 2 times
        )
    
    elif provider == 'gemini':
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )
    
    elif provider == 'groq':
        from langchain_groq import ChatGroq
        api_key = os.getenv('GROQ_API_KEY')
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=api_key
        )
    
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


# ============================================
# AI FEATURES
# ============================================

def improve_task_description(title, description=""):
    """
    Use AI to improve task description with enhanced error handling
    
    Args:
        title (str): Task title
        description (str): Current task description (can be empty)
    
    Returns:
        str: Improved description
        
    Raises:
        Exception: If AI call fails after retries
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    try:
        llm = get_llm_client()
        
        # Format the prompt
        prompt = improve_description_prompt.format(
            title=title,
            description=description if description else "Chưa có mô tả"
        )
        
        # Call LLM
        response = llm.invoke(prompt)
        improved_description = response.content.strip()
        
        # Validate response
        if not improved_description:
            raise ValueError("AI returned empty response")
        
        if len(improved_description) < 10:
            raise ValueError("AI response too short")
        
        return improved_description
        
    except ValueError as e:
        raise e
    except Exception as e:
        # Provide user-friendly error message
        error_msg = str(e).lower()
        if 'api key' in error_msg or 'authentication' in error_msg:
            raise Exception("API key error. Please check OPENAI_API_KEY configuration.")
        elif 'rate limit' in error_msg:
            raise Exception("Rate limit exceeded. Please try again in a moment.")
        elif 'timeout' in error_msg:
            raise Exception("Request timeout. Please try again.")
        else:
            raise Exception(f"AI service error: {str(e)}")


def suggest_task_priority(title, description="", deadline=None):
    """
    Use AI to suggest task priority with enhanced error handling
    
    Args:
        title (str): Task title
        description (str): Task description
        deadline (datetime): Task deadline
    
    Returns:
        dict: {
            'priority': 'HIGH|MEDIUM|LOW',
            'reason': 'explanation'
        }
        
    Raises:
        Exception: If AI call fails after retries
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    try:
        llm = get_llm_client()
        
        # Format deadline
        deadline_str = deadline.strftime("%Y-%m-%d %H:%M") if deadline else "Không có deadline"
        
        # Format the prompt
        prompt = suggest_priority_prompt.format(
            title=title,
            description=description if description else "Chưa có mô tả",
            deadline=deadline_str
        )
        
        # Call LLM
        response = llm.invoke(prompt)
        
        # Parse JSON response
        result = json.loads(response.content.strip())
        
        # Validate response structure
        if 'priority' not in result or 'reason' not in result:
            raise ValueError("Invalid AI response format")
        
        if result['priority'] not in ['HIGH', 'MEDIUM', 'LOW']:
            # Default to MEDIUM if invalid
            result['priority'] = 'MEDIUM'
        
        return result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response. Please try again.")
    except ValueError as e:
        raise e
    except Exception as e:
        error_msg = str(e).lower()
        if 'api key' in error_msg or 'authentication' in error_msg:
            raise Exception("API key error. Please check OPENAI_API_KEY configuration.")
        elif 'rate limit' in error_msg:
            raise Exception("Rate limit exceeded. Please try again in a moment.")
        elif 'timeout' in error_msg:
            raise Exception("Request timeout. Please try again.")
        else:
            raise Exception(f"AI service error: {str(e)}")


def generate_task_subtasks(title, description=""):
    """
    Use AI to generate subtasks for a task with enhanced error handling
    
    Args:
        title (str): Task title
        description (str): Task description
    
    Returns:
        list: List of subtask titles
        
    Raises:
        Exception: If AI call fails after retries
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    try:
        llm = get_llm_client()
        
        # Format the prompt
        prompt = generate_subtasks_prompt.format(
            title=title,
            description=description if description else "Chưa có mô tả"
        )
        
        # Call LLM
        response = llm.invoke(prompt)
        
        # Parse JSON response
        result = json.loads(response.content.strip())
        
        # Validate and clean subtasks
        subtasks = result.get('subtasks', [])
        
        if not subtasks or not isinstance(subtasks, list):
            raise ValueError("No subtasks generated")
        
        # Clean and validate each subtask
        cleaned_subtasks = []
        for subtask in subtasks:
            if isinstance(subtask, str) and subtask.strip():
                # Remove numbering if present
                cleaned = subtask.strip()
                # Remove common prefixes
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '-', '•', '*']:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):].strip()
                if cleaned:
                    cleaned_subtasks.append(cleaned)
        
        if not cleaned_subtasks:
            raise ValueError("No valid subtasks after cleaning")
        
        # Limit to 7 subtasks maximum
        return cleaned_subtasks[:7]
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response. Please try again.")
    except ValueError as e:
        raise e
    except Exception as e:
        error_msg = str(e).lower()
        if 'api key' in error_msg or 'authentication' in error_msg:
            raise Exception("API key error. Please check OPENAI_API_KEY configuration.")
        elif 'rate limit' in error_msg:
            raise Exception("Rate limit exceeded. Please try again in a moment.")
        elif 'timeout' in error_msg:
            raise Exception("Request timeout. Please try again.")
        else:
            raise Exception(f"AI service error: {str(e)}")
