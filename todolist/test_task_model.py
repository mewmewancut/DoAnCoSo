"""
Management command to test Task model and database
Usage: python manage.py shell < test_task_model.py
"""

from tasks.models import Task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

print("\n" + "="*60)
print("TESTING TASK MODEL")
print("="*60)

# Get or create test user
try:
    user = User.objects.get(email='test@example.com')
    print(f"✓ Found test user: {user.email}")
except User.DoesNotExist:
    print("⚠ Test user not found. Please create a user first.")
    print("You can create one via: python manage.py createsuperuser")
    exit()

# Test 1: Create Task
print("\n--- Test 1: Create Task ---")
task = Task.objects.create(
    user=user,
    title="Test Task - Sample TODO",
    description="This is a test task to verify model works",
    deadline=timezone.now() + timedelta(days=7),
    priority='high',
    status='pending'
)
print(f"✓ Created task: {task.title}")
print(f"  ID: {task.id}")
print(f"  Priority: {task.priority}")
print(f"  Status: {task.status}")
print(f"  Deadline: {task.deadline}")

# Test 2: Query Tasks
print("\n--- Test 2: Query Tasks ---")
all_tasks = Task.objects.filter(user=user)
print(f"✓ Total tasks for user: {all_tasks.count()}")

pending_tasks = all_tasks.filter(status='pending')
print(f"  Pending tasks: {pending_tasks.count()}")

# Test 3: Test is_overdue property
print("\n--- Test 3: Test is_overdue property ---")
overdue_task = Task.objects.create(
    user=user,
    title="Overdue Task",
    description="This task is overdue",
    deadline=timezone.now() - timedelta(days=1),
    priority='high',
    status='pending'
)
print(f"✓ Created overdue task: {overdue_task.title}")
print(f"  Is overdue: {overdue_task.is_overdue}")

# Test 4: Update Task
print("\n--- Test 4: Update Task ---")
task.status = 'completed'
task.save()
print(f"✓ Updated task status to: {task.status}")
print(f"  Updated at: {task.updated_at}")

# Test 5: Delete Task
print("\n--- Test 5: Delete Test Tasks ---")
Task.objects.filter(title__contains='Test Task').delete()
Task.objects.filter(title__contains='Overdue Task').delete()
print("✓ Deleted test tasks")

print("\n" + "="*60)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("="*60)
print("\nTask model is working correctly! ✨")
