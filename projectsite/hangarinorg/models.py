from django.db import models
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Priority(BaseModel):
    priority_name = models.CharField(max_length=100)

    def __str__(self):
        return self.priority_name

class Category(BaseModel):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name
    
class Task(BaseModel):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    deadline = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    status = models.CharField(
    max_length=50,
    choices=[("Pending", "Pending"),
             ("In Progress", "In Progress"),
             ("Completed", "Completed"),
             ],
             default="Pending"
             )

    def __str__(self):
        return self.title

class Note(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.content

class SubTask(BaseModel):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    status = models.CharField(
    max_length=50,
    choices=[("Pending", "Pending"),
             ("In Progress", "In Progress"),
             ("Completed", "Completed"),
             ],
             default="Pending"
             )
    def __str__(self):
        return self.title



