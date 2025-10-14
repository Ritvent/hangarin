from .models import Category


def categories(request):
    """Provide categories to all templates for dynamic sidebar rendering."""
    return {
        'categories': Category.objects.all()
    }
