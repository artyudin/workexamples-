from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from user.models import Team, Employee, Organization
from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q



from rest_framework.serializers import (
	HyperlinkedIdentityField,
	ModelSerializer,
	SerializerMethodField,
	ValidationError
	)

User = get_user_model()

'''
Outside User app registration and login
'''

class UserRegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(label= 'Email address')
	email2 = serializers.EmailField(label= 'Confirm email')
	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'email2',
			'password', 
		]

		extra_kwargs = {'password':{'write_only':True}}

	def validate_email(self, value):
		data = self.get_initial()
		email1 = data.get('email2')
		email2 = value
		if email1 != email2:
			raise ValidationError('Please check email, Emails have to match')

		user_qs = User.objects.filter(email=email2)
		if user_qs.exists():
			raise ValidationError('This user has already registered')

		return value

	def validate_email2(self, value):
		data = self.get_initial()
		email1 = data.get('email')
		email2 = value
		if email1 != email2:
			raise ValidationError('Please check email, Emails have to match')
		return value

	def create(self, validated_data):
		print(validated_data)
		username = validated_data['username']
		first_name = validated_data['first_name']
		last_name = validated_data['last_name']
		email = validated_data['email']
		password = validated_data['password']
		user_obj = User(
				username = username,
				first_name = first_name,
				last_name = last_name,
				email = email,
			)
		user_obj.set_password(password)
		user_obj.save()
		return validated_data


			
class UserLoginSerializer(serializers.ModelSerializer):
	token = serializers.CharField(allow_blank=True, read_only=True)
	username = serializers.CharField(required=False, allow_blank=True)
	email = serializers.EmailField(label= 'Email address', required=False, allow_blank=True)
	
	class Meta:
		model = User
		fields = [
			'username',
			'email',
			'password',
			'token', 
		]

		extra_kwargs = {'password':{'write_only':True}}

	def validate(self, data):
		user_obj = None
		email = data.get('email', None)
		username = data.get('username', None)
		password = data['password']
		if not email and not username:
			raise ValidationError('Please use either username or email for login')

		user = User.objects.filter(
				Q(email=email) |
				Q(username=username)
			).distinct()
		user = user.exclude(email__isnull=True).exclude(email__iexact='')
		if user.exists() and user.count() == 1:
			user_obj = user.first()
		else:
			raise ValidationError('Username or email is not valid')

		if user_obj:
			if not user_obj.check_password(password):
				raise ValidationError('Incorrect credentials please try again')
		data['token'] = 'SOME RANDOM TOKEN'
		print(user_obj, data)
	
		return data			
			

'''
Inside User app authenticated users only
'''
class UserSerializer(serializers.HyperlinkedModelSerializer):
	groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all())
	# user_detail_url = HyperlinkedIdentityField(
	# 	view_name='user:user_detail', 
	# 	lookup_field='id'
		
		# )
	# employee = serializers.PrimaryKeyRelatedField(queryset, many=False)

	class Meta:
		model = User
		fields = (
				'id', 'username' , 
					'first_name', 'last_name',
					# 'user_detail_url',
					# 'detail',
					'groups',
					'is_active'
				)

	def create(self, validated_data):
		group_data = validated_data.pop('groups')
		print(validated_data)
		# print (group_data)
		user = User.objects.create(**validated_data)
		# Group.objects.create(**validated_data)
		return user


class GroupSerializer(serializers.ModelSerializer):
	user = serializers.HiddenField(default=0)
	groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all())
	class Meta:
		model = User
		fields = ('groups', 'user')

		def update(self, instance, validated_data):
			instance.groups = validated_data.get('groups', instance.groups)
			instance.save()
			return instance
			
class EmployeeSerializer(serializers.Serializer):
	
	title = serializers.CharField(required=False, allow_blank=True)
	department = serializers.CharField(required=False, allow_blank=True)
	employee_id = serializers.IntegerField(required=False, min_value=None)
		


class MemberCreateSerializer(serializers.ModelSerializer):
	#Creating a new member by an authenticated users
	# username = serializers.CharField(required=True, allow_blank=True)
	# first_name = serializers.CharField(required=False, allow_blank=True)
	# last_name = serializers.CharField(required=False, allow_blank=True)
	# email = serializers.EmailField(required=True, allow_blank=False)
	# password = serializers.CharField(source='user.password')
	employee = EmployeeSerializer()
	# is_active = serializers.BooleanField(required=True)
	# group = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
			'username',
			'first_name',
			'last_name',
			'email',
			'password',
			# 'group',
			'employee',
			'is_active', 
		]

		extra_kwargs = {'password':{'write_only':True}}

	
	def create(self, validated_data):
		print('Validated data',validated_data)

	def get_group(self, obj):

		group = Group.objects.all()
		print(group)

		# return GroupSerializer(group, many=True).data

		# pages = self.pages_data
		# # id_s = self.id_data
		# print('Pages', pages)
		# # print('id_s', pages.pk)
		# # Create the book instance
		# book = Book.objects.create(title=validated_data['title'])

		# # Create or update each page instance
		# for item in pages:
		#     page = Page(text=item, book=book)
		#     page.save()
	   
		# return book










class TeamCreateSerializer(serializers.ModelSerializer):

	class Meta:
		model = Team
		fields = ('tename',)

		def create(self, validated_data):
			return Team.objects.create(**validated_data)

class TeamSerializer(serializers.ModelSerializer):
	team_delete_url = HyperlinkedIdentityField(
		view_name='user:team_delete', 
		lookup_field='pk'
		)
	add_member_url = HyperlinkedIdentityField(
		view_name='user:update', 
		lookup_field='pk'
		)
	add_members_team_url = HyperlinkedIdentityField(
		view_name='user:add_team_member', 
		lookup_field='pk'
		)

	class Meta:
		model = Team
		fields = ('pk',
					'tename', 
					'team_delete_url', 
					'add_member_url', 
					'add_members_team_url'
				)

class UpdateTeamNameSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ('tename',)
		

class AddTeamMemberSerializer(serializers.Serializer):
	# user = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
	tename = serializers.ReadOnlyField()
	user = serializers.SerializerMethodField()

	def __init__(self, *args,**kwargs):

		# self.pages_data = kwargs.get('data', {}).get('pages')
		if 'data' in kwargs: 
			self.user_data = kwargs['data'].getlist('user')

		super(AddTeamMemberSerializer, self).__init__(*args,**kwargs)

	def get_user(self, obj):
		user = User.objects.all()

		return UserSerializer(user, many=True).data


	



	def update(self, instance, validated_data):
		instance.tename = validated_data['tename']
		instance.save()
		print(instance)
		users = self.user_data
		print(users)
		# for user in users:
		#     user = User(text=user, team=instance)
		#     user.save()

		return instance

# 		def update(self, instance, validated_data):
			# instance.tename = validated_data.get('tename', instance.user)
			# users = validated_data.pop('tename')
			# team = instance.tename
			# print(users)
			# instance.tename = validated_data.get('tename', instance.tename)
			
		# # 	instance.save()
		# # 	# for item in validated_data['user']:
		# # 	# 	page = User(id=item['user_id'], username=username['username'], team=instance)
		# # 	# 	page.save()
		# # 	# for user in users:
		# # 	# 	instance.user = validated_data.get('user', instance.user)
		# 	instance.save()
		# 	return instance



		# def update(self, instance, validated_data):
  #   		# Update the book instance
  #   		instance.title = validated_data['title']
  #   		instance.save()

  #   		# Delete any pages not included in the request
  #   		page_ids = [item['page_id'] for item in validated_data['pages']]
  #   			for page in instance.books:
  #       			if page.id not in page_ids:
  #           		page.delete()

  #  			 # Create or update page instances that are in the request

  #   		return instance




