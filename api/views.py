from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hola, tu API funciona 🚀"})



from rest_framework import viewsets, permissions
from .models import Device, UsageRecord, Challenge, Questionnaire, UserProfile
from .serializers import DeviceSerializer, UsageRecordSerializer, ChallengeSerializer, QuestionnaireSerializer

#Registro Usuario

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class UsageRecordViewSet(viewsets.ModelViewSet):
    queryset = UsageRecord.objects.all()
    serializer_class = UsageRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UsageRecord.objects.filter(device__user=self.request.user)

    def perform_create(self, serializer):
        # La lógica de creación se ha movido al serializador.
        # El serializador ahora requiere que se envíe 'device_id' en la petición.
        # Nos aseguramos de que el dispositivo pertenezca al usuario autenticado.
        device = serializer.validated_data.get('device')
        if device.user == self.request.user:
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Este dispositivo no pertenece al usuario.")

class ChallengeViewSet(viewsets.ModelViewSet):
    # Añadimos un queryset base. get_queryset() lo filtrará por usuario.
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    # Añadimos un queryset base. get_queryset() lo filtrará por usuario.
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # La lógica de cálculo de 'score' se ha movido al serializador.
        serializer.save(user=self.request.user)


from django.db.models import Sum, Count
from datetime import date
from django.db.models.functions import TruncDate

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_summary(request):
    """
    Devuelve el tiempo total de uso del usuario agrupado por día.
    """
    # Filtramos registros de uso del usuario actual
    records = UsageRecord.objects.filter(device__user=request.user)

    # Agrupamos por fecha de inicio y sumamos duración
    summary = (
        records.annotate(day=TruncDate("start_time"))
        .values("day")
        .annotate(total_seconds=Sum("duration_seconds"))
        .order_by("day")
    )

    # Convertimos a un dict legible
    data = {str(item["day"]): item["total_seconds"] for item in summary}
    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Devuelve un perfil consolidado del usuario autenticado, incluyendo
    estadísticas de uso y retos.
    """
    user = request.user

    # 1. Calcular puntos y retos completados
    challenge_stats = Challenge.objects.filter(
        user=user, status='completed'
    ).aggregate(
        total_points=Sum('awarded_points'),
        challenges_completed=Count('id')
    )

    # 2. Calcular el tiempo total de uso
    usage_stats = UsageRecord.objects.filter(
        device__user=user
    ).aggregate(
        total_usage_seconds=Sum('duration_seconds')
    )

    # 3. Construir la respuesta, asegurando que los valores nulos sean 0
    data = {
        'username': user.username,
        'email': user.email,
        'total_points': challenge_stats.get('total_points') or 0,
        'challenges_completed': challenge_stats.get('challenges_completed') or 0,
        'total_usage_seconds': usage_stats.get('total_usage_seconds') or 0,
    }

    return Response(data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notifications_view(request):
    """
    Genera y devuelve una lista de notificaciones dinámicas para el usuario
    autenticado basadas en su comportamiento reciente.
    """
    user = request.user
    notifications = []
    today = date.today()

    # Condición 1: Uso diario superior a 2 horas (7200 segundos)
    usage_today = UsageRecord.objects.filter(
        device__user=user, start_time__date=today
    ).aggregate(total_seconds=Sum('duration_seconds'))['total_seconds']

    if usage_today and usage_today > 7200:
        notifications.append("Has usado el móvil más de 2 horas hoy. Tómate un descanso.")

    # Condición 2: Ha completado 3 o más retos
    completed_challenges_count = Challenge.objects.filter(
        user=user, status='completed'
    ).count()

    if completed_challenges_count >= 3:
        notifications.append("¡Excelente! Has completado varios retos esta semana.")

    # Condición 3: No tiene retos en progreso
    if not Challenge.objects.filter(user=user, status='in_progress').exists():
        notifications.append("No tienes retos activos. Crea uno nuevo para seguir avanzando.")

    return Response({"notifications": notifications})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ranking_view(request):
    """
    Devuelve el top 10 de usuarios con más puntos.
    """
    # Usamos select_related('user') para optimizar la consulta y evitar
    # un hit a la base de datos por cada usuario en el bucle.
    top_profiles = UserProfile.objects.select_related('user').order_by('-total_points')[:10]

    # Construimos la respuesta con el formato deseado.
    ranking_data = [
        {
            "username": profile.user.username,
            "total_points": profile.total_points
        }
        for profile in top_profiles
    ]

    return Response(ranking_data)
