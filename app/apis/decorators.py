from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_restx import abort
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError

def require_roles(*allowed_roles):
    """Authorize users based on their JWT role claim.

    Supports both call styles:
    - @require_roles(["member", "guest"])
    - @require_roles("member", "guest")
    """
    if len(allowed_roles) == 1 and isinstance(allowed_roles[0], (list, tuple, set)):
        normalized_roles = set(allowed_roles[0])
    else:
        normalized_roles = set(allowed_roles)

    if not normalized_roles:
        raise ValueError("require_roles() requires at least one role")

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                #first verify a valid JWT is present in the request header
                verify_jwt_in_request()
            except (NoAuthorizationError, InvalidHeaderError) as e:
                abort(401, "Missing or invalid authorization header")
            
            #then extract the decoded payload (claims)
            claims = get_jwt()
            user_role = claims.get("role")
            
            #then heck if the user's role is in the allowed list
            if user_role not in normalized_roles:
                abort(403, f"role '{user_role}' has insufficient permissions. require to be: {sorted(normalized_roles)}")
            
            # 4. If authorized, proceed to the endpoint
            return fn(*args, **kwargs)
        return decorator
    return wrapper