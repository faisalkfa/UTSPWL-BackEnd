from pyramid.config import Configurator
from pyramid.request import Request, Response
from pyramid.session import SignedCookieSessionFactory
from pyramid.authorization import ACLAuthorizationPolicy, Allow
import threading

from .mygrpc.grpc_service import serve_grpc
from pyramid.authorization import ALL_PERMISSIONS

class RootACL(object):
    __acl__ = [
        (Allow, 'admin', ALL_PERMISSIONS),
        (Allow, 'reports', ['reports'])
    ]

    def __init__(self, request):
        pass

def add_role_principals(userid, request):
    return request.jwt_claims.get('roles', [])

def request_factory(environ):
    request = Request(environ)
    if request.is_xhr:
        request.response = Response()
        request.response.headerlist = []
        request.response.headerlist.extend(
            (
                ('Access-Control-Allow-Origin', '*'),
                ('Content-Type', 'application/json')
            )
        )
    return request

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:

        secret_key = "shjoi1o3r901fjIJOd21390f092ejvqqD9017Fj03Jdj09j1fSBNKNDF11q21ejq"

        # Security configuration
        config.set_root_factory(RootACL)
        config.set_authorization_policy(ACLAuthorizationPolicy())
        config.include('pyramid_jwt')
        config.set_jwt_authentication_policy(secret_key,
                                            auth_type='Bearer',
                                            algorithm='HS256',
                                            callback=add_role_principals)

        # Create a session factory
        session_factory = SignedCookieSessionFactory('2A5D8C5123FAF71DEBD7C669C3768')

        # Configure session management
        config.set_session_factory(session_factory)

        config.include('.cors')
    
        # make sure to add this before other routes to intercept OPTIONS
        config.add_cors_preflight_handler()
    

        config.include('pyramid_jinja2')
        config.include('.routes')
        config.include('.models')
        
        config.scan()

    # Jalankan layanan gRPC
    # serve_grpc()
    return config.make_wsgi_app()

if __name__ == '__main__':
    # Start the gRPC server in a separate thread
    grpc_thread = threading.Thread(target=serve_grpc)
    grpc_thread.daemon = True
    grpc_thread.start()

    # Start the Pyramid web server in the main thread
    main()
