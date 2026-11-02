from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import *
r=DefaultRouter();r.register('workshops',WorkshopViewSet,basename='workshop');r.register('enrollments',EnrollmentViewSet,basename='enrollment');r.register('products',ProductViewSet,basename='product');r.register('orders',OrderViewSet,basename='order');r.register('events',EventViewSet,basename='event');r.register('tickets',TicketViewSet,basename='ticket');r.register('certificates',CertificateViewSet,basename='certificate')
urlpatterns=[path('health/',health),path('auth/register/',RegisterView.as_view()),path('auth/token/',TokenObtainPairView.as_view()),path('auth/token/refresh/',TokenRefreshView.as_view()),path('auth/me/',MeView.as_view()),path('translation/demo/',translation_demo),path('recommendations/',recommendations),path('certificates/verify/<uuid:code>/',verify_certificate),path('',include(r.urls))]
