from django.urls import path
from .views import SignupView, CustomLoginView ,SendOTPView, VerifyOTPView, SetNewPasswordView,ResendOTPView,MakeSuperUserView,UserListView, RevokeSuperUserView,OTPRequestHistoryView,ProductImageUploadView,CartListView, CartAddView, CartUpdateView, CartDeleteView,ProductCreateView,ProductListView,ProductUpdateView,ProductDeleteView
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
    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('product/list/', ProductListView.as_view(), name='product-list'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('upload-product-image/', ProductImageUploadView.as_view()),
    path('cart/', CartListView.as_view()),         # GET: list cart
    path('cart/add/', CartAddView.as_view()),      # POST: add item
    path('cart/update/<int:pk>/', CartUpdateView.as_view()),  # PUT: update qty
    path('cart/delete/<int:pk>/', CartDeleteView.as_view()),  # DELETE
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
