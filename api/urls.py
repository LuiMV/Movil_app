from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, UsageRecordViewSet, ChallengeViewSet, QuestionnaireViewSet, user_profile, notifications_view, ranking_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# --- Configuración de drf-yasg para documentación ---
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="API - Control de Uso del Móvil (MVP)",
      default_version='1.0.0',
      description="Documentación de endpoints de usuario, retos, cuestionarios y estadísticas.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'usage', UsageRecordViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)

urlpatterns = [
    # Endpoints de documentación
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Endpoints de autenticación JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint de perfil de usuario
    path('profile/', user_profile, name='user-profile'),

    # Endpoint de notificaciones dinámicas
    path('notifications/', notifications_view, name='notifications'),

    # Endpoint de ranking de usuarios
    path('ranking/', ranking_view, name='user-ranking'),

    path('', include(router.urls)),
]
