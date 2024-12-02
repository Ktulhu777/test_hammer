import time

from django.contrib.auth import get_user_model, login
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.core.cache import cache

from .serializers import CreateCodeSerializer, LoginSerializer, ProfileSerializer
from .utils import generate_code
from drf_yasg.utils import swagger_auto_schema


class CreateCodeView(APIView):

    @swagger_auto_schema(request_body=CreateCodeSerializer)
    def post(self, requests):
        serializer = CreateCodeSerializer(data=requests.data)

        if serializer.is_valid():
            code = generate_code()
            phone = serializer.data['phone']
            cache.set(code, phone, timeout=60 * 5)

            time.sleep(2)  # имитация отправки смс

            return Response(
                data={'success': f'Your authorization code {code!r} '},
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, requests):
        serializer = LoginSerializer(data=requests.data)

        if serializer.is_valid():
            code = serializer.data['code']
            phone = cache.get(code)
            if phone:
                user, create = get_user_model().objects.get_or_create(phone=phone)
                login(requests, user)

                return Response(
                    data={'success': f'Congratulations! You have successfully logged in.'},
                    status=status.HTTP_200_OK
                )
        return Response(
            data={'error': 'Something went wrong'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invited_by_code': openapi.Schema(type=openapi.TYPE_STRING, description='Invitation code'),
            },
            required=['invited_by_code']
        )
    )
    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
