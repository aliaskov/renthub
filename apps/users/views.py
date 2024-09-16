from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import views, viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

from apps.users.serializers import (
    SignupSerializer,
    SigninSerializer,
    EmailTokenObtainPairSerializer,
    UserSerializer
)
from apps.users.permissions import IsOwnerOrReadOnly


def token_to_response(response, user):
    refresh_token = RefreshToken.for_user(user)
    refresh_token_str = str(refresh_token)
    refresh_token_exp = refresh_token['exp']
    refresh_token_exp = timezone.datetime.fromtimestamp(
        refresh_token_exp,
        tz=timezone.get_current_timezone()
    )
    access_token = refresh_token.access_token
    access_token_str = str(access_token)
    access_token_exp = access_token['exp']
    access_token_exp = timezone.datetime.fromtimestamp(
        access_token_exp,
        tz=timezone.get_current_timezone()
    )
    response.set_cookie(
        'refresh_token',
        refresh_token_str,
        expires=refresh_token_exp,
        httponly=True
    )
    response.set_cookie(
        'access_token',
        access_token_str,
        expires=access_token_exp,
        httponly=True
    )
    response.data = {
        'username': user.username,
        'email': user.email,
        'description': user.profile.description,
        'refresh_token': refresh_token_str,
        'access_token': access_token_str
    }
    return response


class SignupView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return token_to_response(
                Response(status=status.HTTP_201_CREATED),
                user
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class SigninView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SigninSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(
            request,
            username=user.username,
            password=password
        )
        if user is not None:
            return token_to_response(
                Response(status=status.HTTP_201_CREATED),
                user
            )
        else:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SignoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response({'msg': 'Bye!'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class ProtectedView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Ваша логика для GET-запроса
        return Response({'message': 'GET запрос выполнен'})

    def post(self, request, *args, **kwargs):
        # Ваша логика для POST-запроса
        return Response({'message': 'POST запрос выполнен'})


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @action(
        methods=['get'],
        detail=False,
        url_path='my-profile',
        permission_classes=[permissions.IsAuthenticated]
    )
    def my_profile(self, request):
        queryset = User.objects.get(pk=request.user.pk)
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)
