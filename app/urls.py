from django.urls import path
from .views import SignupView, CustomLoginView ,SendOTPView, VerifyOTPView, SetNewPasswordView,ResendOTPView,MakeSuperUserView,UserListView, RevokeSuperUserView,OTPRequestHistoryView,ProductView,CartView,ProductImageUploadView
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    #-------------------Auth-------------------------
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('set-password/', SetNewPasswordView.as_view(), name='set-password'),
    path("resend-otp/",ResendOTPView.as_view(),name='resend-password'),
    path('make-superuser/', MakeSuperUserView.as_view()),
    path('revokesuperuser/', RevokeSuperUserView.as_view()),
    path('users/', UserListView.as_view(), name='user-list'),
    path('loginhistory/',OTPRequestHistoryView.as_view()),
    path('otphistory/',OTPRequestHistoryView.as_view()),

    #----------------------------product---------------
    path("product/",ProductView.as_view()),
    path("Cart/",CartView.as_view()),
    path('upload-product-image/', ProductImageUploadView.as_view()),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
