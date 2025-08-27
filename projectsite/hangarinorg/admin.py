from django.contrib import admin
from .models import Category, Priority, Task, SubTask, Note

admin.site.register(Category)
admin.site.register(Priority)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Note)
