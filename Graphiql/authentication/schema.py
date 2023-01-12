from email.policy import default
from django.contrib.auth import authenticate
from graphql_jwt.utils import jwt_encode, jwt_payload
import graphene
from graphene_django import DjangoObjectType
from pydantic import ValidationError
from authentication.send_mail import send_confirmation_email
from .models import User, Agent
from apartment.models import Apartment
from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
   class Meta:
       model = User
    
class AgentType(DjangoObjectType):
    class Meta:
        model = Agent
        fields = "__all__"
        depth = 1


class ApartmentType(DjangoObjectType):
    class Meta:
        model = Apartment



class CreateUser(graphene.Mutation):
   message = graphene.String()
   user = graphene.Field(UserType)

   class Arguments:
       email = graphene.String(required=True)
       phone_number = graphene.String(required=True)
       country = graphene.String(required=True)
       password = graphene.String(required=True)
       

   def mutate(self, info, **kwargs):
       user = User.objects.create_user(
           email=kwargs.get('email'),
           entry="Tenant",
           password=kwargs.get('password'),
           phone_number=kwargs.get('phone_number'),
           country=kwargs.get('country')
       )
       a = send_confirmation_email(email=user.email)
       return CreateUser(
           user=user, 
           message="Successfully created user, {}".format(user.email)
    )


# creating an agent object
class CreateAgent(graphene.Mutation):
   message = graphene.String()
   user = graphene.Field(UserType)
   class Arguments:
       email = graphene.String(required=True)
       phone_number = graphene.String(required=True)
       country = graphene.String(required=True)
       location = graphene.String(required=True)
       password = graphene.String(required=True)

   def mutate(self, info, **kwargs):
       agent_create = User.objects.create_user(
           email=kwargs.get('email'),
           entry="Agent",
           password=kwargs.get('password'),
           phone_number=kwargs.get('phone_number'),
           country=kwargs.get('country'),
       )
       location=kwargs.get('location')
       Agent.objects.create(
           user=agent_create, agent_location=location
       )
       a = send_confirmation_email(email=agent_create.email)
       print(a.json())
       return CreateAgent(
           user=agent_create, 
           message="Successfully created user, {}".format(agent_create.email)
    )



class SendToken(graphene.Mutation):
    message = graphene.String()
    class Arguments:
        email = graphene.String()
    def mutate(self, info, **kwargs):
        email = kwargs.get('email')
        try:
            User.objects.get(email=email)
            send_mails = send_confirmation_email(email)
            print(send_mails.json())
            if send_mails:
                return SendToken(message="email token sent!")
            return SendToken(message="Error occurred while sending mail, try again")
        except Exception as e:
            return SendToken(message=str(e))



class LoginUser(graphene.Mutation):
    message = graphene.String()
    token = graphene.String()
    verification_prompt = graphene.String()
    class Arguments:
        email = graphene.String()
        password = graphene.String()
    def mutate(self, info, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        user = authenticate(email=email, password=password)
        error_message = 'Invalid login credentials'
        success_message = "You logged in successfully."
        verification_error = 'Your email is not verified'
        if user:
            if user.is_verify:
                payload = jwt_payload(user)
                token = jwt_encode(payload)
                return LoginUser(token=token, message=success_message)
            return LoginUser(message=verification_error)
        return LoginUser(message=error_message)



class CreateApartment(graphene.Mutation):
    message = graphene.String()
    class Arguments:
      apartment_title = graphene.String()
      category = graphene.String()
      video_file = graphene.String(required=False, default=None)
      image_url = graphene.String()
      price = graphene.String()
      location = graphene.String()
      agent_name = graphene.String()
      description = graphene.String()
      features = graphene.String()
      locaton_info = graphene.String()
    def mutate(self, info, **kwargs):
        agent_name = kwargs.get('agent_name')
        try:
            get_agent = User.objects.get(name=agent_name)
            if get_agent.entry !='Agent':
                return ValidationError('Only agents can post apartments')
            Apartment.objects.create(**kwargs)
            return CreateApartment(message="Apartment created successfully")
        except Apartment.DoesNotExist:
            raise ValueError(f"Agent with name: {agent_name} does not exist!")



class Query(graphene.ObjectType):
    """
    Graphene query endpoints where data to be returned upon each query are defined.
    The object types of each endpoin is first defined and endpoints are created using 
    the 'resolve' function 
    """
    users = graphene.List(UserType)
    agents = graphene.List(AgentType)
    apartments = graphene.List(ApartmentType)

    def resolve_users(root, info):
        return get_user_model().objects.filter(entry='Tenant')

    def resolve_agents(root, info):
        return Agent.objects.select_related('user')

    def resolve_apartments(root, info):
        return Apartment.objects.all()


class Mutation(graphene.ObjectType):

   create_user = CreateUser.Field()
   create_agent = CreateAgent.Field()
   login_user = LoginUser.Field()
   send_token= SendToken.Field()