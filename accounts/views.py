from django.shortcuts import render
from django.contrib.auth import authenticate

from rest_framework import (views,
                            status)
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import CustomUserSerializer

class Register(views.APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
                {
                    "error": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class Login(views.APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username is None or password is None:
            return Response("Input data is invalid, try again",
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is None:
            return Response("Input data is invalid, try again",
                            status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                },
                status=status.HTTP_201_CREATED
            )

class Logout(views.APIView):
    def post(self, request):
        refresh = request.data.get('refresh')

        if refresh is None:
            return Response({"error": "refresh token is required, try again"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response({'error': 'invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'you have successfully logged out'}, status=status.HTTP_200_OK)