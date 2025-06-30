from django.urls import path
from .views import SignupView, CustomLoginView ,ResetPasswordWithOTPView ,SendOTPView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
     path('reset-password/', ResetPasswordWithOTPView.as_view(), name='reset-password'),
]
