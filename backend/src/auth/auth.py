import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

# Login Flow link
# https://dev-1th49z0c.us.auth0.com/authorize?audience=coffee&response_type=token&client_id=zNm2vlytaTFtGFjL3KEpGcJXgMgmMB86&redirect_uri=http://127.0.0.1:8100

# Token for Manager
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNYX3BvdERQUTRCdFdfaWRJUmF3eSJ9.eyJpc3MiOiJodHRwczovL2Rldi0xdGg0OXowYy51cy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTY1MzMwOTc2NzE4MDY5MjczMjIiLCJhdWQiOiJjb2ZmZWUiLCJpYXQiOjE2NTc4ODA0MTIsImV4cCI6MTY1Nzk2NjgxMiwiYXpwIjoiek5tMnZseXRhVEZ0R0ZqTDNLRXBHY0pYZ01nbU1CODYiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.E-PwTOENi0NLZjPduXjGCi-kDrZrNnfchYsHnvZZOyBwu8euWVG3J4IS7nRisn1NNJU7Rj4Hx0XHM46L7frKchTGvDORc-DlAWXennxHsVBSm93LRfbd41XxB1X7nWpdmiVtFU5Eq_AD0qErSCsLSvftajRF77agML-z0RtYxTHspNk90-1JFG-OyPPepu-2QCByMjzYuVbVOMwiLTZhLKbYTquv943mBireUaGsuyE2JVcU4KhQ6_O-dx63rKrCkKHNCt8AxpeFkqJpYhNLmVTjkeapNHngNrdat1NEXS53KOYZ6SqvE4aYcfMddxqqK07CBwxHg3VYBkX8HnWc7w

# Token for Barista
# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNYX3BvdERQUTRCdFdfaWRJUmF3eSJ9.eyJpc3MiOiJodHRwczovL2Rldi0xdGg0OXowYy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjJjYzFhNDQ5OTI5ZWI2M2RiY2NiYTVjIiwiYXVkIjoiY29mZmVlIiwiaWF0IjoxNjU3ODgwNjIwLCJleHAiOjE2NTc5NjcwMjAsImF6cCI6InpObTJ2bHl0YVRGdEdGakwzS0VwR2NKWGdNZ21NQjg2Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiXX0.eKX_WfuLhNKfBUtdl1uxG66Q-s_0rWx0BCgaq7GaXDkXIBhfdBucIOAOsdPMpFu7rY4v4Yj54KWDpm9fnsr88Mv0mj9RYwNLwuTI3v-hxCmgsjqCvUjq-soJc-LxQe0CUUkMXEX0cZxMCOoDGx78JV3O9-xO8p6hW2jPh_2VC2L81O5IbMv8JnU_h4gFFITEq9h-1ZrNe85w8dcVi3k2_hG-XPkfnkZAq3jK6MLDGQ4H20JoPiLg6rzSbvKyu2Mp74nZCmEj3Z6lKxoc4SnUtzOQN0_5UZcDr2yWBhj0-V1BHZQeC-2XcZBjrvFELhlPYK9yCHvWFF7LP6N3_nrtLg

AUTH0_DOMAIN = 'dev-1th49z0c.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
                
            except AuthError as err:
                error = err.error
                error["status_code"] = err.status_code
                payload = error
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator