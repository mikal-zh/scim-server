from oic.oic import Client
from oic.oic.message import AuthorizationResponse
from oic.oauth2.exception import GrantError
from oic.oic import Grant
from oic import rndstr
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from app_config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, REDIRECT_URI
from flask import session

# Create OIDC client
client = Client(client_authn_method=CLIENT_AUTHN_METHOD)
client.provider_config(AUTHORITY)

# Register client
info = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uris": [REDIRECT_URI]
}
client.store_registration_info(info)

def get_authorization_url():
    session["state"] = rndstr()
    session["nonce"] = rndstr()

    req_auth = client.construct_AuthorizationRequest(
        request_args={
            "response_type": "code",
            "scope": ["openid", "profile", "email"],
            "redirect_uri": REDIRECT_URI,
            "state": session["state"],
            "nonce": session["nonce"]
        }
    )

    login_url = req_auth.request(client.authorization_endpoint)

    return login_url

def get_code(request):
    return request.args.get("code")

def get_state(request):
    return request.args.get("state")

def get_token(code, state):    
    # Initialize the grant with the authorization response
    auth_response = AuthorizationResponse(code=code, state=state)

    grant = Grant()
    grant.add_code(auth_response)
    client.grant[state] = grant

    token_request =  client.do_access_token_request(
        state=state,
        request_args={"code": code},
        authn_method="client_secret_post"
    )

    session["token"] = token_request["access_token"]
    session["id_token"] = token_request["id_token"]

    return session["token"]

def get_user_info(token=None):
    token = token or session.get("token")
    if not token:
        return None
    try:
        user = session.get("id_token")
        if not user:
            return client.do_user_info_request(state=session["state"], token=token)
        else:
            user.update(client.do_user_info_request(state=session["state"], token=token))
            return user
    except Exception:
        return None
    
def log_out(redirection_uri=None):
    try:
        req_logout = client.construct_EndSessionRequest(
            request_args={
                "state": session["state"],
                "post_logout_redirect_uri": redirection_uri or REDIRECT_URI
            }
        )

        return req_logout.request(client.end_session_endpoint)
    except GrantError:
        session.clear()
        return None