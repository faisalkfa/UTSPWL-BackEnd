import jwt
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import forbidden_view_config

class JWTAuthenticationPolicy(CallbackAuthenticationPolicy):
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def encode_token(self, user_id):
        payload = {"sub": user_id}
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.DecodeError:
            return None

def includeme(config):

    secret_key = "shjoi1o3r901fjIJOd21390f092ejvqqD9017Fj03Jdj09j1fSBNKNDF11q21ejq"

    # Your JWT callback function
    def jwt_callback(user_id, request):
        # Implement logic to return the user ID based on the JWT token
        # For example, you can decode the JWT and extract the user ID
        # Make sure to handle any exceptions that may occur during decoding
        return user_id  # Return the user ID

    # Configure JWTAuthenticationPolicy with the callback
    authentication_policy = JWTAuthenticationPolicy(
        secret_key=secret_key
    )

    # Set the authentication policy in your Pyramid configuration
    config.set_authentication_policy(authentication_policy)

    # authentication_policy = JWTAuthenticationPolicy(secret=secret_key, callback=your_jwt_callback)
    # config.set_authentication_policy(authentication_policy)

    # Configure ACLAuthorizationPolicy (you can define your own authorization logic)
    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)

@forbidden_view_config()
def forbidden(request):
    response = HTTPForbidden()
    response.json = {"message": "Access denied"}
    return response