"""
AI utilities for TodoList application
"""
import os
import json
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


# ============================================
# AI FEATURES
# ============================================

def improve_task_description(title, description=""):
    """
    Use AI to improve task description
    
    Args:
        title (str): Task title
        description (str): Current task description (can be empty)
    
    Returns:
        str: Improved description
        
    Raises:
        Exception: If AI call fails
    """
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
        
        return improved_description
        
    except Exception as e:
        raise Exception(f"Failed to improve description: {str(e)}")


def suggest_task_priority(title, description="", deadline=None):
    """
    Use AI to suggest task priority
    
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
        Exception: If AI call fails
    """
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
        
        return result
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to suggest priority: {str(e)}")


def generate_task_subtasks(title, description=""):
    """
    Use AI to generate subtasks from a complex task
    
    Args:
        title (str): Task title
        description (str): Task description
    
    Returns:
        list: List of subtask titles
        
    Raises:
        Exception: If AI call fails
    """
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
        
        return result.get('subtasks', [])
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate subtasks: {str(e)}")
