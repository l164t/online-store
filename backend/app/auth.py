from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Load the .env file so os.getenv() can read our secrets
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# CryptContext tells passlib which hashing algorithm to use.
# bcrypt is the industry standard for passwords — it's intentionally slow,
# which makes brute-force attacks take years instead of seconds.
# deprecated="auto" means if we ever switch algorithms, old hashes still work.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Takes a plain password ("mypassword123") and returns a hash
# ("$2b$12$...something unreadable...").
# The hash is what we store in the database — never the real password.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Takes a plain password and a stored hash and returns True or False.
# We never "decrypt" the hash — we hash the attempt and compare.
# passlib handles this comparison safely.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Creates a JWT token.
# data: a dict of things to encode into the token — we put the user's email in here.
# The token has three parts: header.payload.signature
# Anyone can decode header and payload — never put sensitive info in a token.
# Only the server can verify the signature.
def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    # Set when this token expires — current time + 30 minutes (from .env)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add the expiry time into the token payload
    # "exp" is a standard JWT field — jose checks it automatically
    to_encode.update({"exp": expire})

    # Sign and encode the token using our secret key
    # If anyone changes even one character of the token, this signature breaks
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Decodes and validates a JWT token.
# Returns the email if the token is valid, None if it's invalid or expired.
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # "sub" = subject = who this token is for
        return email
    except JWTError:
        return None