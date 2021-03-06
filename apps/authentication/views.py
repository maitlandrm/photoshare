from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login, logout

from rest_framework import permissions, viewsets, status, views
from rest_framework.response import Response
from rest_framework.request import Request

from models import Account
from permissions import IsAccountOwner
from serializers import AccountSerializer

import json

class IndexView(TemplateView):
	template_name = 'index.html'


class AccountViewSet(viewsets.ModelViewSet):
	lookup_field = 'email'
	queryset = Account.objects.all()
	serializer_class = AccountSerializer

	def list(self, request):
		return render(request, 'templates/index.html')

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return (permissions.AllowAny(),)

		if self.request.method == 'POST':
			return (permissions.AllowAny(),)

		return (permissions.IsAuthenticated(), IsAccountOwner(),)

	def create(self, request):
		serializer = self.serializer_class(data=request.data)

		if serializer.is_valid():
			Account.objects.create_user(**serializer.validated_data)
			print("Account successfully created")
			return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

		print("Account could not be created")
		return Response({
			'status': 'Bad request',
			'message': 'Account could not be created with received data'
		}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
	def post(self, request, format=None):
		data = request.data

		email = data.get('email', None)
		password = data.get('password', None)

		account = authenticate(email=email, password=password)

		if account is not None:
			if account.is_active:
				login(request, account)

				serialized = AccountSerializer(account)

				return Response(serialized.data)
			else:
				return Response({
					'status': 'Unauthorized',
					'message': 'This account has been disabled.'
				}, status=status.HTTP_401_UNAUTHORIZED)
		else:
			return Response({
				'status': 'Unauthorized',
				'message': 'Username/password combination invalid.'
			}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, format=None):
		logout(request)

		return Response({}, status=status.HTTP_204_NO_CONTENT)
