from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, CustomLoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import SendOTPSerializer, OTPVerifySerializer,SetNewPasswordSerializer
from .models import PasswordResetOTP,CustomUser
from django.utils import timezone
from datetime import timedelta


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(APIView):
    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get('otp')

        try:
            otp_obj = PasswordResetOTP.objects.filter(otp=otp).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # 10 min expiry
        if timezone.now() - otp_obj.created_at > timedelta(minutes=10):
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

        # OTP verified, store email in session/context if needed
        request.session['reset_email'] = otp_obj.email  # optional
        return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
    
class SetNewPasswordView(APIView):
    def post(self, request):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        email = request.session.get('reset_email')  # same email from previous step

        if not email:
            return Response({'error': 'Session expired. Please verify OTP again.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Delete OTP after use
            PasswordResetOTP.objects.filter(email=email).delete()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
