from django.db import models
from django.conf import settings
<<<<<<< HEAD

=======
from django.db.models import Avg


>>>>>>> origin/main
class InterviewSession(models.Model):
    INTERVIEW_TYPES = [
        ('technical', 'Entrevista Técnica'),
        ('behavioral', 'Entrevista Conductual'),
        ('general', 'Entrevista General'),
<<<<<<< HEAD
        ('leadership', 'Liderazgo'),
        ('sales', 'Ventas'),
        ('customer_service', 'Atención al Cliente'),
    ]
    
    DURATION_CHOICES = [
        ('quick', 'Rápida (10 min)'),
        ('standard', 'Estándar (20 min)'),
        ('extended', 'Extendida (30 min)'),
        ('unlimited', 'Sin límite'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]
    
    FOCUS_AREAS = [
        ('communication', 'Comunicación'),
        ('problem_solving', 'Resolución de Problemas'),
        ('teamwork', 'Trabajo en Equipo'),
        ('adaptability', 'Adaptabilidad'),
        ('time_management', 'Gestión del Tiempo'),
        ('conflict_resolution', 'Resolución de Conflictos'),
=======
        ('custom', 'Personalizada'),
>>>>>>> origin/main
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES, default='general')
    title = models.CharField(max_length=200, default='Nueva Entrevista')
<<<<<<< HEAD
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='standard')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    focus_area = models.CharField(max_length=30, choices=FOCUS_AREAS, default='communication')
    position_level = models.CharField(max_length=100, blank=True, help_text='Ej: Junior Developer, Senior Manager')
    total_points = models.IntegerField(default=0)
    current_level = models.CharField(max_length=20, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def get_level_info(self):
        levels = [
            {'level': 1, 'name': 'Novato', 'min': 0, 'max': 30},
            {'level': 2, 'name': 'Aprendiz', 'min': 30, 'max': 70},
            {'level': 3, 'name': 'Practicante', 'min': 70, 'max': 120},
            {'level': 4, 'name': 'Competente', 'min': 120, 'max': 180},
            {'level': 5, 'name': 'Experimentado', 'min': 180, 'max': 250},
            {'level': 6, 'name': 'Profesional', 'min': 250, 'max': 330},
            {'level': 7, 'name': 'Experto', 'min': 330, 'max': 420},
            {'level': 8, 'name': 'Maestro', 'min': 420, 'max': 520},
            {'level': 9, 'name': 'Elite', 'min': 520, 'max': 630},
            {'level': 10, 'name': 'Leyenda', 'min': 630, 'max': None},
        ]
        
        for level_data in levels:
            if level_data['max'] is None:
                return {
                    'level': level_data['level'],
                    'name': level_data['name'],
                    'next': None,
                    'progress': 100
                }
            elif self.total_points < level_data['max']:
                progress = ((self.total_points - level_data['min']) / (level_data['max'] - level_data['min'])) * 100
                return {
                    'level': level_data['level'],
                    'name': level_data['name'],
                    'next': level_data['max'],
                    'progress': int(progress)
                }
        
        return {'level': 10, 'name': 'Leyenda', 'next': None, 'progress': 100}
    
    def add_points(self, points):
        self.total_points += points
        level_info = self.get_level_info()
        self.current_level = str(level_info['level'])
        self.save()
=======
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def get_average_response_time(self):
        """Promedio de tiempo de respuesta del usuario en segundos."""
        data = self.messages.filter(
            sender='user',
            response_time_seconds__isnull=False
        ).aggregate(Avg('response_time_seconds'))

        return data['response_time_seconds__avg']
>>>>>>> origin/main

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

<<<<<<< HEAD
=======
    # Tiempo que el usuario tardó en responder a la última pregunta del bot
    response_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Tiempo en segundos que el usuario tardó en responder esta pregunta."
    )

>>>>>>> origin/main
    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."
<<<<<<< HEAD

class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)
    practice_dates = models.JSONField(default=list)  # Lista de fechas en formato 'YYYY-MM-DD'
    
    def update_streak(self):
        from datetime import date, timedelta
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # Si ya practicó hoy, no hacer nada
        if self.last_practice_date == today:
            return False
        
        # Primera vez practicando
        if self.last_practice_date is None:
            self.current_streak = 1
        # Día consecutivo
        elif self.last_practice_date == today - timedelta(days=1):
            self.current_streak += 1
        # Rompió la racha
        elif self.last_practice_date < today - timedelta(days=1):
            self.current_streak = 1
        
        self.last_practice_date = today
        
        # Actualizar racha más larga
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        # Agregar fecha a la lista
        if today_str not in self.practice_dates:
            self.practice_dates.append(today_str)
        
        self.save()
        return True  # Indica que se actualizó
    
    def __str__(self):
        return f"{self.user.username} - Racha: {self.current_streak} días"
=======
>>>>>>> origin/main
