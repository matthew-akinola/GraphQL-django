import jwt

from django.template.loader import render_to_string
from Graphiql.settings import SECRET_KEY, DOMAIN
from mailjet_rest import Client
import os, environ




env = environ.Env()
environ.Env.read_env(".env")
from_email = os.environ.get("EMAIL_HOST_USER")
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")


def send_confirmation_email(email):
    token = jwt.encode({'user': email}, SECRET_KEY,
                       algorithm='HS256')
    context = {
        'small_text_detail': 'Thank you for '
                             'creating an account. '
                             'Please verify your email '
                             'address to set up your account.',
        'email': email,
        'domain': DOMAIN,
        'token': token,
    }
    # locates our email.html in the templates folder
    msg_html = render_to_string('./email.html', context)
    print(token)
    print(api_key)
    absurl = f"{DOMAIN}?token={token}"
    email_body = (
        "Hi " + " " + email + ":\n" + "Use link below to verify your email"
        "\n" + absurl
    )
    data = {
        "Messages": [
            {
                "From": {
                    "Email": f"{from_email}",
                    "Name": "freehouse",
                },
                "To": [{"Email": f"{email}", "Name": f"{email}"}],
                "Subject": "Email Verification",
                "TextPart": "Click on the below link to verify your Email!",
                "HTMLPart": email_body,
            }
        ]
    }
    try:
        mailjet = Client(auth=("b18aa7a06a161ece4e553644a6686f17", "5e786bec334bf879db2fa89678ed5953"), version="v3.1")
        mailjet_result = mailjet.send.create(data=data)
        return mailjet_result
    except Exception as e:
        return str(e)


    