from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_restx import abort

def require_roles(allowed_roles):
    """decorator to authorize users based on their role claim in the JWT. must be called with a list of roles, e.g., @require_roles(["member"])"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            #first verify a valid JWT is present in the request header
            verify_jwt_in_request()
            
            #then extract the decoded payload (claims)
            claims = get_jwt()
            user_role = claims.get("role")
            
            #then heck if the user's role is in the allowed list
            if user_role not in allowed_roles:
                abort(403, f"role '{user_role}' has insufficient permissions. require to be: {allowed_roles}")
            
            # 4. If authorized, proceed to the endpoint
            return fn(*args, **kwargs)
        return decorator
    return wrapper