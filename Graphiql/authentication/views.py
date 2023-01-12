from django.shortcuts import render

# Create your views here.
import jwt
from django.shortcuts import redirect, render
from authentication.models import User
from Graphiql.settings import SECRET_KEY, DOMAIN
from django.http import HttpResponse, HttpResponseNotFound

def activate_account(request, token):
    email = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])["user"]
    try:
        user = User.objects.get(email=email)
        user.is_verify = True
        user.save()
        print(user.is_verify)
        return redirect(f'{DOMAIN}graphql/')
    except Exception as e:
        return HttpResponseNotFound(content=str(e))