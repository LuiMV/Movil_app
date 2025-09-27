from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, UsageRecordViewSet, ChallengeViewSet, QuestionnaireViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'usage', UsageRecordViewSet)
router.register(r'challenges', ChallengeViewSet)
router.register(r'questionnaires', QuestionnaireViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Endpoints de autenticación JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]



from .views import usage_summary

urlpatterns = [
    # ... tus rutas actuales
    path('usage/summary/', usage_summary, name='usage-summary'),
]
