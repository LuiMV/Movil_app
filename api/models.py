from django.db import models
from django.contrib.auth.models import User

# Dispositivos vinculados
class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_type = models.CharField(max_length=50)  # ej: Android, iOS
    os_version = models.CharField(max_length=50, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_type}"

# Registros de uso del dispositivo
class UsageRecord(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="usage_records")
    app_package = models.CharField(max_length=255)  # nombre/paquete de la app
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.app_package} - {self.duration_seconds}s"

# Retos y gamificación
class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challenges")
    title = models.CharField(max_length=255)
    target_seconds = models.PositiveIntegerField(help_text="Tiempo objetivo sin usar el móvil")
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pendiente"),
        ("in_progress", "En progreso"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    ], default="pending")
    awarded_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reto {self.title} - {self.user.username}"

#  Cuestionarios / Tests psicológicos
class Questionnaire(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questionnaires")
    type = models.CharField(max_length=50)  # ej: SAS, Nomofobia
    answers = models.JSONField()  # guarda respuestas en JSON
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.user.username}"

# Logs de auditoría (opcional pero útil)
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

