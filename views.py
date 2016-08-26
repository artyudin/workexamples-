
from django.contrib.auth import get_user_model
User = get_user_model()


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group, Permission

from user.serializers import (
	UserSerializer, 
	GroupSerializer, 
	EmployeeSerializer,
	TeamCreateSerializer,
	TeamSerializer, 
	AddTeamMemberSerializer,
	UserRegisterSerializer,
	UserLoginSerializer,
	UpdateTeamNameSerializer,
	MemberCreateSerializer,
	)



from user.models import Team
from django.views.generic import View
from rest_framework import generics
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.http import Http404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView

from datetime import datetime
# from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.db.models import Q
from rest_framework.filters import (
		SearchFilter,
		OrderingFilter,
	)

from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.generics import (
	CreateAPIView,
	DestroyAPIView,
	ListAPIView, 
	UpdateAPIView,
	RetrieveAPIView,
	RetrieveUpdateAPIView,
	RetrieveDestroyAPIView
	)
from rest_framework.permissions import (
	AllowAny,
	IsAuthenticated,
	IsAdminUser,
	IsAuthenticatedOrReadOnly,

	)

# from posts.api.permissions import IsOwnerOrReadOnly
# from posts.api.pagination import PostLimitOffsetPagination, PostPageNumberPagination


class UserLoginTemplate(APIView):
	# Renders User Login Template
	renderer_classes = (TemplateHTMLRenderer,)
	template_name = "user/user_login.html"

	def get(self, request):
		
		return Response(template_name = "user/user_login.html")

# class E(APIView):
# 	# Regestering new User not creating Member
# 	permission_classes = [AllowAny]
# 	serializer_class = EmployeeSerializer
# 	renderer_classes = (JSONRenderer,)
# 	parser_classes = (FormParser,)
# 	template_name = "user/user_login.html"

# 	def get(self, request):
# 		serializer = EmployeeSerializer()
# 		serializer = serializer.data
# 		print(serializer)
		
# 		return Response({'serializer':serializer})

class UserRegisterAPIView(APIView):
	# Regestering new User not creating Member
	permission_classes = [AllowAny]
	serializer_class = UserRegisterSerializer
	renderer_classes = (JSONRenderer,)
	parser_classes = (FormParser,)
	template_name = "user/user_login.html"

	def get(self, request):
		serializer = UserRegisterSerializer()
		serializer = serializer.data
		
		return Response({'serializer':serializer})

	def post(self,	request):
		serializer = UserRegisterSerializer(data=request.data)
		if not serializer.is_valid():
			return Response({'serializer':serializer})

		serializer.save()
		
		return redirect('user:welcome')

class UserLoginAPIView(APIView):
	# Login verification
	permission_classes = [AllowAny]
	renderer_classes = (JSONRenderer,)
	parser_classes = (FormParser,)
	template_name = "user/user_login.html"

	def post(self, request, *args, **kwargs):
		data = request.data
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			new_data =serializer.data
			return Response(new_data, status=HTTP_200_OK)
		return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

'''
Inside User app authenticated users only 
'''

class UserWelcomeView(APIView):
	# Rendering the first User app Welcome template
	renderer_classes = (TemplateHTMLRenderer,)
	def get(self, request):
		
		return Response(template_name = "user/user.html")

class MemberCreateView(APIView):
	#Creating a new member by an authenticated users
	serializer_class = MemberCreateSerializer
	renderer_classes = (JSONRenderer,)
	parser_classes = (FormParser,)
	template_name = "user/user.html"

	def get(self, request):
		serializer = MemberCreateSerializer()
		serializer = serializer.data
		print(serializer)
	
		return Response({'serializer':serializer})

	def post(self,	request):
		serializer = MemberCreateSerializer(data=request.data)
		print('Req', request.data)
		if not serializer.is_valid():
			print('PIZDA')
			return Response({'serializer':serializer})

		serializer.save()
		print(serializer)
		return redirect('user:list_all')






class UserDetailsAPIView(APIView):
	# User Datails view 
	renderer_classes = (JSONRenderer,)
	template_name = "user/user.html"

	def get(self, request, id):
		user = get_object_or_404(User, id=id)
		serializer = UserSerializer(user)
		user = serializer.data
		
			
		return Response({'user':user})




class UserListView(APIView):
	# User List view 
	renderer_classes = (JSONRenderer,)
	template_name = "user/user.html"

	def get(self, request):
		user = User.objects.all()
		serializer = UserSerializer(user, context={'request': request}, many=True)
		users = serializer.data
		
			
		return Response({'users':users})

class ListAllTeams(APIView):
	# List all teams on the team
	renderer_classes = (JSONRenderer,)
	template_name = "user/user.html"

	def get(self, request):
		teams = Team.objects.all()
		serializer = TeamSerializer(teams, context={'request': request}, many=True)
		teams = serializer.data

		return Response({'teams':teams})

	



class AddGroup(APIView):
	# Add user to a Group - permissions
	renderer_classes = [TemplateHTMLRenderer]
	template_name = "user/group.html"

	def get(self, request, id):
		user = get_object_or_404(User, id=id)
		print(user)
		serializer = GroupSerializer(user)

		return Response({'serializer':serializer,'user':user})

	def post(self, request, id):
		user = get_object_or_404(User, id=id)
		serializer = GroupSerializer(user, data=request.data)
		if not serializer.is_valid():
			return Response({'serializer': serializer, 'user':user})
		serializer.save()
		return redirect('user:list_all')
		

class CreateTeam(APIView):
	# Create a new team 
	renderer_classes = (JSONRenderer,)
	parser_classes = (FormParser,)
	template_name = "user/user.html"
	
	def get(self, request):
		serializer = TeamCreateSerializer()
		serializer = serializer.data
	
		return Response({'serializer':serializer})

	def post(self, request):
		serializer = TeamCreateSerializer(data=request.data)
		if not serializer.is_valid():
			return Response({'serializer':serializer})

		serializer.save()
		
		return redirect('user:welcome')

# class DeleteTeam(APIView):

# 	def get_object(self, pk):
# 		try:
# 			print('R',Team.objects.get(pk=pk))
# 			return Team.objects.get(pk=pk)
# 		except Team.DoesNotExist:
# 			raise Http404

	

# 	def delete(self, request, pk, format=None):
# 		team = self.get_object(pk)
# 		# team.delete()
# 		return team.delete()

class DeleteTeam(DestroyAPIView):
	# Deletes the Team
	queryset = Team.objects.all()
	serializer_class = TeamSerializer
	lookup_field = 'pk'


class TeamUpdateAPIView(RetrieveUpdateAPIView):
	# Updates name of the Team
    queryset = Team.objects.all()
    serializer_class = UpdateTeamNameSerializer
    



class AddTeamMember(UpdateAPIView):
	# Add users to the team
	# queryset = Team.objects.all()
	serializer_class = AddTeamMemberSerializer
	lookup_field = 'pk'
	renderer_classes = (JSONRenderer,)
	parser_classes = (FormParser,)
	template_name = "user/user.html"

	def get(self, request, pk):
		team = get_object_or_404(Team, id=pk)
		serializer = AddTeamMemberSerializer(team, context={'request': request})
		serializer = serializer.data
		return Response({'serializer':serializer})

	def post(self, request, pk):
		print('HUY')
		team = get_object_or_404(Team, id=pk)
		# team = TeamSerializer(team)
		serializer = AddTeamMemberSerializer(team, data=request.data)
		print('Pizda',serializer)
		if not serializer.is_valid():
			return Response({'serializer': serializer})
		
		return serializer.save()


	# def get_object(self, pk):
	# 	try:
	# 		return Team.objects.get(pk=pk)
	# 	except Team.DoesNotExist:
	# 		raise Http404

	# def put(self, request, pk, format=None):
	# 	team = self.get_object(pk)
	# 	serializer = AddTeamMemberSerializer(team, data=request.data)
	# 	if serializer.is_valid():
	# 		serializer.save()
	# 		return Response(serializer.data)
	# 	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







class AllTeamMembers(APIView):
	# List all user on the team
	renderer_classes = [TemplateHTMLRenderer]
	template_name = "user/allteam.html"

	def get(self, request, id):
		team = Team.objects.get(id=id)
		print(team)
		users = team.user.all()
		

		return Response({'users':users})







