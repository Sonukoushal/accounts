from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, CustomLoginSerializer, ResendOTPSerializer,ProductSerializer,CartSerializer,ProductImageSerializer
from .serializers import SendOTPSerializer,UserListSerializer,SuperUserActionSerializer,SetNewPasswordSerializer, OTPVerifySerializer, OTPRequestHistorySerializer, LoginHistorySerializer
from .models import PasswordResetOTP,CustomUser,OTPRequestHistory, LoginHistory,Product,Cart
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsSuperUserOnly
from .utils import get_client_ip 
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUserOnly




class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                "message": "User created successfully",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Save OTP request history (if user exists)
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                OTPRequestHistory.objects.create(user=user)
            except CustomUser.DoesNotExist:
                pass  # just skip if not found

            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class CustomLoginView(APIView):
    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data
            user_id = validated["user"]["id"]
            user = CustomUser.objects.get(id=user_id)

            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )

            return Response(validated, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        email = request.data.get("email")  # Email bhi bhejna padega client se

        serializer = OTPVerifySerializer(data={"otp": otp}, context={"email": email})
        if serializer.is_valid():
            # OTP verified, store email in session
            request.session['reset_email'] = email
            return Response({"message": "OTP verified successfully"}, status=200)
        return Response(serializer.errors, status=400)  
    
class SetNewPasswordView(APIView):
    def post(self, request):
        email = request.session.get("reset_email")  # OTP step se mila

        if not email:
            return Response({'error': 'Session expired. Please verify OTP again.'}, status=400)

        serializer = SetNewPasswordSerializer(data=request.data, context={"email": email})
        if serializer.is_valid():
            serializer.save()  # Password set ho jayega
            return Response({"message": "Password reset successful"}, status=200)
        return Response(serializer.errors, status=400)



class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP resent successfully."}, status=200)
        return Response(serializer.errors, status=400)
    
class UserListView(APIView):
    permission_classes = [IsSuperUserOnly]  # 🔐 Only logged-in users can access

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    
class MakeSuperUserView(APIView):
    permission_classes = [IsSuperUserOnly]  

    def post(self, request):
        serializer = SuperUserActionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User promoted to superuser successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
class RevokeSuperUserView(APIView):
    permission_classes = [IsSuperUserOnly]  

    def post(self, request):
        serializer = SuperUserActionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user = CustomUser.objects.get(id=user_id)
            user.is_superuser_custom = False
            user.save()
            return Response({"message": f"{user.email} is no longer a superuser."})
        return Response(serializer.errors, status=400)
    
class OTPRequestHistoryView(APIView):
    permission_classes = [IsSuperUserOnly]

    def get(self, request):
        history = OTPRequestHistory.objects.all()
        serializer = OTPRequestHistorySerializer(history, many=True)
        return Response(serializer.data)
    
class LoginHistoryView(APIView):
    permission_classes = [IsSuperUserOnly]  # 🔐 Superuser only

    def get(self, request):
        logs = LoginHistory.objects.all().order_by('-login_time')
        serializer = LoginHistorySerializer(logs, many=True)
        return Response(serializer.data)
    
#--------------product-----------------

class ProductView(APIView):
    permission_classes = [IsAuthenticated]  # Har user ke liye auth required

    def get_permissions(self):
        # GET ke liye normal user, POST ke liye superuser
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsSuperUserOnly()]
        return [IsAuthenticated()]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductImageUploadView(APIView):
    permission_classes = [IsAuthenticated]  # Optional: Only allow admin

    def post(self, request):
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Image uploaded successfully'}, status=201)
        return Response(serializer.errors, status=400)
    
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id  # Automatically add user
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product added to cart"}, status=201)
        return Response(serializer.errors, status=400)
    
class CartDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        try:
            cart_item = Cart.objects.get(id=cart_id)

            if cart_item.user != request.user:
                return Response({"error": "You can only delete your own cart items."}, status=403)

            cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=200)

        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carts = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=200)
              
            
         
             