from django.db import models
from django.contrib.auth.models import User

class InterviewSession(models.Model):
    INTERVIEW_TYPES = [
        ('technical', 'Entrevista Técnica'),
        ('behavioral', 'Entrevista Conductual'),
        ('general', 'Entrevista General'),
        ('custom', 'Personalizada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES, default='general')
    title = models.CharField(max_length=200, default='Nueva Entrevista')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_interview_type_display()})"

class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'Usuario'),
        ('bot', 'JoBot'),
    ]

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."
