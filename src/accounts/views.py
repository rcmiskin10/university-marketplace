from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render_to_response, RequestContext, Http404, HttpResponseRedirect, render, HttpResponse
from rest_framework import viewsets
import json
from .serializers import MyUserSerializer
from .models import MyUser
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from .models import MyUser

for user in MyUser.objects.all():
	Token.objects.get_or_create(user=user)

class MyUserViewSet(viewsets.ModelViewSet):
	queryset = MyUser.objects.all()
	serializer_class = MyUserSerializer




@csrf_exempt
def login_android(request):
	if request.method == 'POST':        
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(email=email, password=password)
		if user is not None:
			response_data = {}


			response_data['success'] = True
			response_data['name'] = user.first_name + " " + user.last_name
			new_data = json.dumps(response_data)
			return HttpResponse(new_data, content_type='application/json')

		if user == None:
			response_data = {}


			response_data['success'] = False
			response_data['message'] = "Login failed. Try again!"
			new_data = json.dumps(response_data)
			return HttpResponse(new_data, content_type='application/json')
		
