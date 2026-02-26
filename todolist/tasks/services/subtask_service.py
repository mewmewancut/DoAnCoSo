"""
Subtask Service - Business logic for SubTask operations
"""
from django.db.models import Max
from django.utils import timezone
from ..models import SubTask


class SubtaskService:
    """
    Service class for SubTask business logic
    """
    
    @staticmethod
    def get_subtasks_for_task(task):
        """Get all subtasks for a specific task"""
        return task.subtasks.all()
    
    @staticmethod
    def get_subtask_by_id(subtask_id, user):
        """Get a specific subtask ensuring it belongs to the user's task"""
        return SubTask.objects.filter(
            id=subtask_id, 
            task__user=user
        ).select_related('task').first()
    
    @staticmethod
    def create_subtask(task, title, description=''):
        """
        Create a new subtask for a task
        
        Args:
            task: Parent Task instance
            title: Subtask title (required)
            description: Subtask description
        
        Returns:
            Created SubTask instance
        """
        # Get max order for this task to add new subtask at the end
        max_order = task.subtasks.aggregate(Max('order'))['order__max'] or 0
        
        return SubTask.objects.create(
            task=task,
            title=title,
            description=description,
            order=max_order + 1
        )
    
    @staticmethod
    def create_bulk_subtasks(task, subtask_titles):
        """
        Create multiple subtasks at once
        
        Args:
            task: Parent Task instance
            subtask_titles: List of subtask titles
        
        Returns:
            List of created SubTask instances
        """
        max_order = task.subtasks.aggregate(Max('order'))['order__max'] or 0
        
        subtasks = []
        for i, title in enumerate(subtask_titles, start=1):
            subtask = SubTask.objects.create(
                task=task,
                title=title.strip(),
                order=max_order + i
            )
            subtasks.append(subtask)
        
        return subtasks
    
    @staticmethod
    def update_subtask(subtask, title=None, description=None, status=None, order=None):
        """
        Update a subtask with provided fields
        
        Args:
            subtask: SubTask instance to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            order: New order (optional)
        
        Returns:
            Updated SubTask instance
        """
        if title is not None:
            subtask.title = title.strip()
        if description is not None:
            subtask.description = description.strip()
        if status is not None:
            subtask.status = status
        if order is not None:
            subtask.order = order
        
        subtask.save()
        return subtask
    
    @staticmethod
    def toggle_subtask(subtask):
        """
        Toggle subtask completion status and check for cascade completion.

        If all sibling subtasks (including this one) are now completed,
        the parent task is automatically marked as completed too.

        Args:
            subtask: SubTask instance

        Returns:
            Tuple of (updated SubTask, parent_completed: bool)
        """
        if subtask.status == 'completed':
            subtask.status = 'pending'
        else:
            subtask.status = 'completed'

        subtask.save()

        # Check cascade: are ALL subtasks of the parent task now completed?
        parent_completed = False
        task = subtask.task
        all_subtasks = task.subtasks.all()
        total = all_subtasks.count()

        if total > 0 and all(s.status == 'completed' for s in all_subtasks):
            if task.status != 'completed':
                task.status = 'completed'
                task.save()
                parent_completed = True

        return subtask, parent_completed
    
    @staticmethod
    def delete_subtask(subtask):
        """Delete a subtask"""
        subtask.delete()
    
    @staticmethod
    def reorder_subtasks(task, orders):
        """
        Reorder subtasks for a task (used for drag & drop)
        
        Args:
            task: Parent Task instance
            orders: List of dicts with 'id' and 'order' keys
        """
        for item in orders:
            subtask_id = item.get('id')
            new_order = item.get('order')
            
            if subtask_id and new_order is not None:
                SubTask.objects.filter(
                    id=subtask_id,
                    task=task
                ).update(order=new_order)
    
    @staticmethod
    def get_subtask_stats(task):
        """
        Get statistics about subtasks for a task
        
        Returns:
            Dict with total, completed, pending, in_progress counts
        """
        subtasks = task.subtasks.all()
        total = subtasks.count()
        completed = subtasks.filter(status='completed').count()
        pending = subtasks.filter(status='pending').count()
        in_progress = subtasks.filter(status='in_progress').count()
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': round((completed / total * 100), 1) if total > 0 else 0
        }
    
    @staticmethod
    def subtask_to_dict(subtask, include_timestamps=True):
        """
        Convert a subtask to dictionary for JSON response
        
        Args:
            subtask: SubTask instance
            include_timestamps: Whether to include timestamp fields
        
        Returns:
            Dict representation of subtask
        """
        data = {
            'id': str(subtask.id),
            'title': subtask.title,
            'description': subtask.description,
            'status': subtask.status,
            'order': subtask.order,
            'is_completed': subtask.is_completed,
        }
        
        if include_timestamps:
            data['created_at'] = subtask.created_at.strftime('%Y-%m-%d %H:%M:%S')
            data['completed_at'] = (
                subtask.completed_at.strftime('%Y-%m-%d %H:%M:%S') 
                if subtask.completed_at else None
            )
        
        return data
