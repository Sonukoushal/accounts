from django.urls import path
from .views import SignupView, CustomLoginView ,SendOTPView, VerifyOTPView, SetNewPasswordView,ResendOTPView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('set-password/', SetNewPasswordView.as_view(), name='set-password'),
    path("resend-otp/",ResendOTPView.as_view(),name='resend-password')
]
