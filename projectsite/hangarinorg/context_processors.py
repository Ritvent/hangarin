from .models import Category


def categories(request):
    """Provide categories to all templates for dynamic sidebar rendering."""
    return {
        'categories': Category.objects.all()
    }


from .models import Task

def parent_tasks(request):
    """Provide a short list of tasks (parents) for the Subtasks sidebar submenu."""
    try:
        tasks = Task.objects.order_by('-updated_at')[:12]
    except Exception:
        tasks = []
    return {'parent_tasks': tasks}
