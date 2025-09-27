from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def hello(request):
    return Response({"message": "Hola, tu API funciona 🚀"})



from rest_framework import viewsets, permissions
from .models import Device, UsageRecord, Challenge, Questionnaire
from .serializers import DeviceSerializer, UsageRecordSerializer, ChallengeSerializer, QuestionnaireSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class UsageRecordViewSet(viewsets.ModelViewSet):
    serializer_class = UsageRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UsageRecord.objects.filter(device__user=self.request.user)

    def perform_create(self, serializer):
        start = self.request.data.get("start_time")
        end = self.request.data.get("end_time")

        # Calculamos duración en segundos
        from datetime import datetime
        fmt = "%Y-%m-%dT%H:%M:%S"  # formato esperado
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
        duration = int((end_dt - start_dt).total_seconds())

        serializer.save(device=Device.objects.filter(user=self.request.user).first(),
                        duration_seconds=duration)


class ChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Challenge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionnaireSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        answers = self.request.data.get("answers")
        # Simple: sumar valores (ajusta según cuestionario real)
        score = sum(answers.values())
        serializer.save(user=self.request.user, score=score)



from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
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

