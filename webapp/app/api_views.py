from django.contrib.auth import authenticate, login, logout
from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema
from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from .models import Photo
from .serializers import (
    HealthResponseSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    MessageSerializer,
    PhotoSerializer,
    RegisterSerializer,
    TokenResponseSerializer,
)

@csrf_exempt
class PhotoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PhotoSerializer

    def get_queryset(self):
        sort = self.request.query_params.get('sort', 'name')
        if sort == 'date':
            return Photo.objects.all().order_by('uploaded_at')
        return Photo.objects.all().order_by('name')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@csrf_exempt
class PhotoDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def delete(self, request, *args, **kwargs):
        photo = self.get_object()
        if not request.user.is_staff and photo.owner != request.user:
            return Response({'detail': 'You can only delete your own photos.'}, status=status.HTTP_403_FORBIDDEN)
        photo.photo.delete(save=False)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: MessageSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)
        return Response({'detail': f'Welcome, {user.username}!'}, status=status.HTTP_201_CREATED)

@csrf_exempt
class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer, 400: MessageSerializer})
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'detail': f'Welcome back, {user.username}!', 'token': token.key}, status=status.HTTP_200_OK)

@csrf_exempt
class TokenLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: TokenResponseSerializer, 400: MessageSerializer})
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

@csrf_exempt
class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={200: MessageSerializer})
    def post(self, request):
        if isinstance(request.auth, Token):
            request.auth.delete()
        logout(request)
        return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)

@csrf_exempt
class HealthReadyAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: HealthResponseSerializer, 503: HealthResponseSerializer})
    def get(self, request):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        except OperationalError:
            return Response({'status': 'error', 'detail': 'database unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            return Response({'status': 'error', 'detail': 'readiness check failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
