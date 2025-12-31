"""
Test script for AI utilities
Run this to test AI functions before integrating into views

Usage:
    python test_ai.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todolist.settings')
django.setup()

from ai_utils import (
    test_connection,
    improve_task_description,
    suggest_task_priority,
    generate_task_subtasks
)
from datetime import datetime, timedelta


def test_ai_connection():
    """Test 1: Check API connection"""
    print("\n" + "="*60)
    print("TEST 1: API Connection")
    print("="*60)
    
    result = test_connection()
    if result:
        print("✓ API connection test PASSED")
    else:
        print("✗ API connection test FAILED")
        print("Please check your .env file and API key")
        return False
    return True


def test_improve_description():
    """Test 2: Improve task description"""
    print("\n" + "="*60)
    print("TEST 2: Improve Task Description")
    print("="*60)
    
    # Test case 1: Simple task
    print("\n--- Test Case 1: Simple task ---")
    title = "Học Python"
    description = "Học cơ bản"
    
    print(f"Original Title: {title}")
    print(f"Original Description: {description}")
    
    try:
        improved = improve_task_description(title, description)
        print(f"\nImproved Description:\n{improved}")
        print("\n✓ Test PASSED")
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        return False
    
    # Test case 2: Empty description
    print("\n--- Test Case 2: Empty description ---")
    title = "Viết báo cáo đồ án"
    description = ""
    
    print(f"Original Title: {title}")
    print(f"Original Description: {description}")
    
    try:
        improved = improve_task_description(title, description)
        print(f"\nImproved Description:\n{improved}")
        print("\n✓ Test PASSED")
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        return False
    
    return True


def test_suggest_priority():
    """Test 3: Suggest task priority"""
    print("\n" + "="*60)
    print("TEST 3: Suggest Task Priority")
    print("="*60)
    
    # Test case 1: Urgent task
    print("\n--- Test Case 1: Urgent task with close deadline ---")
    title = "Nộp báo cáo cuối kỳ"
    description = "Hoàn thành báo cáo đồ án môn Cơ sở dữ liệu"
    deadline = datetime.now() + timedelta(days=2)
    
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}")
    
    try:
        result = suggest_task_priority(title, description, deadline)
        print(f"\nSuggested Priority: {result['priority']}")
        print(f"Reason: {result['reason']}")
        print("\n✓ Test PASSED")
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        return False
    
    # Test case 2: No deadline
    print("\n--- Test Case 2: Task without deadline ---")
    title = "Đọc sách về Django"
    description = "Đọc documentation Django để nâng cao kiến thức"
    deadline = None
    
    print(f"Title: {title}")
    print(f"Description: {description}")
    print(f"Deadline: None")
    
    try:
        result = suggest_task_priority(title, description, deadline)
        print(f"\nSuggested Priority: {result['priority']}")
        print(f"Reason: {result['reason']}")
        print("\n✓ Test PASSED")
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        return False
    
    return True


def test_generate_subtasks():
    """Test 4: Generate subtasks"""
    print("\n" + "="*60)
    print("TEST 4: Generate Subtasks")
    print("="*60)
    
    # Test case: Complex task
    print("\n--- Test Case: Complex project task ---")
    title = "Xây dựng website bán hàng"
    description = "Tạo một trang web bán hàng online với Django, có giỏ hàng và thanh toán"
    
    print(f"Title: {title}")
    print(f"Description: {description}")
    
    try:
        subtasks = generate_task_subtasks(title, description)
        print(f"\nGenerated Subtasks ({len(subtasks)} items):")
        for i, subtask in enumerate(subtasks, 1):
            print(f"{i}. {subtask}")
        print("\n✓ Test PASSED")
    except Exception as e:
        print(f"\n✗ Test FAILED: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI UTILITIES TEST SUITE")
    print("="*60)
    print("Testing AI functions for TodoList application")
    print("Make sure you have .env file with OPENAI_API_KEY set")
    
    # Run tests
    tests = [
        ("API Connection", test_ai_connection),
        ("Improve Description", test_improve_description),
        ("Suggest Priority", test_suggest_priority),
        ("Generate Subtasks", test_generate_subtasks),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AI utilities are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
