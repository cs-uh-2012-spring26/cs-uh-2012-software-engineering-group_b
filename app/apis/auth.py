"""Auth endpoints for user registration with token validation."""
from flask import request
from flask_restx import Namespace, Resource, abort, fields
import bcrypt
from flask_jwt_extended import create_access_token
from functools import wraps
from http import HTTPStatus
from app.db import DB
from app.db.users import PASSWORD_HASH, build_user_document, create_user, get_user_by_email, get_user_by_phone

from app.apis import MSG

api = Namespace("auth", description="    Endpoints for logging in, registering, and validating token")

# Example tokens
VALID_TOKENS = {
    "trainer-secret-123": "trainer",
    "admin-secret-456": "admin",
}

# Models for Swagger
register_model = api.model(
    "RegisterRequest",
    {
        "token": fields.String(example="trainer-secret-123", description="Registration token (optional - omit for user role)"),
        "name": fields.String(required=True, example="John Trainer", description="User name"),
        "email": fields.String(required=True, example="john@example.com", description="User email"),
        "phone": fields.String(example="+971-504-555-0100", description="User phone"),
        "birth_date": fields.String(example="1990-01-15", description="User birth date"),
        "password": fields.String(required=True, example="secure_password_123", description="User password"),
    },
)

login_model = api.model(
    "LoginRequest",
    {
        "email": fields.String(required=True, example="john@example.com", description="User email"),
        "password": fields.String(required=True, example="secure_password_123", description="User password"),
    }
)

register_response = api.model(
    "RegisterResponse",
    {
        "user_id": fields.String(example="uuid-here"),
            "role": fields.String(example="member", enum=["member", "trainer", "admin"]),
            "message": fields.String(example="User registered as member"),
        "access_token": fields.String(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="JWT access token for authenticated requests"),
    },
)

validate_token_model = api.model(
    "ValidateTokenRequest",
    {
        "token": fields.String(required=True, example="trainer-secret-123", description="Token to validate"),
    },
)

validate_token_response = api.model(
    "ValidateTokenResponse",
    {
        "valid": fields.Boolean(example=True),
        "role": fields.String(example="trainer", enum=["trainer", "admin"]),
    },
)


def validate_token(f):
    """Validate optional registration invite token; defaults to 'member' when absent."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()

        token = data.get("token") if data else None

        if token:
            # Validate token if provided
            role = VALID_TOKENS.get(token)
            if not role:
                abort(403, "Invalid or expired token")
        else:
            # Default to 'member' role if no token provided
            role = "member"

        # Inject role into request context
        request.registration_role = role

        return f(*args, **kwargs)

    return decorated_function

@api.route('/register')
class Register(Resource):
    """Register a new user. Optional token grants trainer/admin rights; omit token for basic user role."""
    
    @api.expect(register_model)
    @api.response(HTTPStatus.CREATED, "User registered", register_response)
    @api.response(HTTPStatus.FORBIDDEN, "Invalid token")
    @validate_token
    def post(self):
        """REGISTER NEW ACCOUNT: allowed for guests"""
        data = request.get_json()
        role = request.registration_role
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")

        # Reject duplicate accounts
        if email and get_user_by_email(email) is not None:
            return {MSG: "Email already registered"}, HTTPStatus.CONFLICT
        if phone and get_user_by_phone(phone) is not None:
            return {MSG: "Phone already registered"}, HTTPStatus.CONFLICT
        
        # Hash password with bcrypt (salt is generated automatically)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Build and create user document
        user_doc = build_user_document(
            name=data.get("name"),
            email=data.get("email"),
            password_hash=password_hash,
            role=role,
            phone=data.get("phone"),
            birth_date=data.get("birth_date"),
        )
        
        created_user = create_user(user_doc)
        user_id = created_user.get("user_id")
        
        # Issue JWT access token for immediate use
        access_token = create_access_token(
            identity=email,
            additional_claims={"role": role, "user_id": user_id}
        )
        
        return {
            "user_id": user_id,
            "role": role,
            "message": f"User registered as {role}",
            "access_token": access_token,
        }, HTTPStatus.CREATED


@api.route('/validate-token')
class ValidateToken(Resource):
    """Validate if a token is valid for registration."""
    
    @api.expect(validate_token_model)
    @api.response(HTTPStatus.OK, "Token is valid", validate_token_response)
    @api.response(HTTPStatus.BAD_REQUEST, "Token is invalid")
    def post(self):
        """VALIDATE TOKEN: INTERNAL"""
        data = request.get_json()
        token = data.get("token")
        
        if not token or token not in VALID_TOKENS:
            return {"valid": False}, HTTPStatus.BAD_REQUEST
        
        return {"valid": True, "role": VALID_TOKENS[token]}, HTTPStatus.OK
    

@api.route('/login')
class Login(Resource):
    """Log in existing user; check if account exists and verify password"""

    @api.expect(login_model)
    @api.response(HTTPStatus.OK, "successful login!")
    @api.response(HTTPStatus.BAD_REQUEST, "incomplete data")
    @api.response(HTTPStatus.NOT_FOUND, "user not found")
    def post(self):
        """LOG INTO ACCOUNT: allowed for members, trainers, and admins"""
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # validate fields
        if not email:
            return {MSG: "email is required"}, HTTPStatus.BAD_REQUEST
        if data.get("phone"):
            return {MSG: "phone login is not supported; use email"}, HTTPStatus.BAD_REQUEST
        # validate password
        if not password:
            return {
                MSG: "password is required"
            }, HTTPStatus.BAD_REQUEST
        
        
        # get user associated with account
        user = get_user_by_email(email)
        if user is None:
            return {MSG: "User not found!"}, HTTPStatus.NOT_FOUND 
        
        # verify that password hash matches
        if not bcrypt.checkpw(password.encode('utf-8'), user.get(PASSWORD_HASH).encode('utf-8')):
            return {MSG: "Login credentials and password do not match"}, HTTPStatus.BAD_REQUEST
        
        access_token = create_access_token(
            identity=user.get("email") or user.get("user_id"),
            additional_claims={
                "role": user.get("role", "guest"),
                "user_id": user.get("user_id"),
            },
        )
        
        return {
            MSG: "successful login!", "access_token": access_token
        }, HTTPStatus.OK



        
        


        
    

