from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken  
from .models import PasswordResetOTP , Product ,Cart
from django.core.mail import send_mail
from django.utils import timezone
import random
from .models import CustomUser, PasswordResetOTP, OTPRequestHistory, LoginHistory
from datetime import timedelta



# ------------------- Signup Serializer -------------------
class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'name', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Don't save confirm_password
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'is_superuser']


# ------------------- Custom Login Serializer -------------------
User = get_user_model()

class CustomLoginSerializer(serializers.Serializer):
    email= serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or phone")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password")

        if not user.is_active:
            raise serializers.ValidationError("User is inactive")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
            }
        }
    
class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Check if user exists
        from .models import CustomUser
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        otp = str(random.randint(100000, 999999))

        # Save to DB
        otp_instance=PasswordResetOTP.objects.create(email=email, otp=otp)
        

        # Send email
        send_mail(
            subject="Your OTP for Password Reset",
            message=f"Your OTP is: {otp}",
            from_email="yourprojectemail@gmail.com",  # same as EMAIL_HOST_USER
            recipient_list=[email],
        )
        #return {"message": "OTP sent to your email."}
        return otp_instance
    


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email']
        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.filter(email=email).delete()
        PasswordResetOTP.objects.create(email=email, otp=otp)

        # OTP Email bhejna
        send_mail(
            subject="Your New OTP",
            message=f"Your OTP is: {otp}",
            from_email="yourprojectemail@gmail.com",
            recipient_list=[email]
        )

        return {"message": "OTP resent successfully."}    

class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.IntegerField()

    def validate(self, attrs):
        otp = attrs.get("otp")
        email = self.context.get("email")  # context se email mila

        if not email:
            raise serializers.ValidationError("Email not provided")

        try:
            otp_obj = PasswordResetOTP.objects.filter(email=email, otp=otp).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        if timezone.now() - otp_obj.created_at > timedelta(minutes=10):
            raise serializers.ValidationError("OTP expired")

        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        email = self.context.get("email")
        if not email:
            raise serializers.ValidationError("Email not provided")

        user = CustomUser.objects.get(email=email)
        user.set_password(validated_data['new_password'])
        user.save()

        PasswordResetOTP.objects.filter(email=email).delete()
        return user

# Reusable for both make and revoke
class SuperUserActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        request_user = self.context['request'].user
        if not request_user.is_authenticated or not request_user.is_superuser_custom:
            raise serializers.ValidationError("Only superusers can perform this action.")
        return data
    
    def create(self, validated_data):
        user_id = validated_data['user_id']
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_superuser_custom = True
            user.save()
            return user
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        
class OTPRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequestHistory
        fields = ['id', 'user', 'requested_at']

class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ['id', 'user', 'login_time', 'ip_address', 'user_agent']


#-------------------ProductSerializer------------------------------
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'image',
            'brand_name',
            'product_name',
            'product_id',
            'price',
            'quantity',
            'description',
            'specification'
        ]

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'added_at']

    def validate(self, attrs):
        user = attrs.get('user')
        product = attrs.get('product')
        if Cart.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Product already in cart for this user.")
        return attrs
                                             