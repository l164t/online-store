from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token, decode_access_token

# prefix="/auth" means all routes here start with /auth automatically.
router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2PasswordBearer tells FastAPI where to look for the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- REGISTER ---
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Depends(get_db) is FastAPI's dependency injection.
    # FastAPI calls get_db() automatically, gets a db session,
    # passes it in here, and closes it when the function returns.
    # You never call get_db() yourself.

    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        # 400 Bad Request — the client sent invalid data
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create the user — hash the password before storing
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --- LOGIN ---
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    # We give the same error whether the email doesn't exist OR the password
    # is wrong — this prevents attackers from knowing which one failed.
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled"
        )

    # Create a token with the user's email as the subject
    token = create_access_token(data={"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}


# --- GET CURRENT USER ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = decode_access_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up the user in the database
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# --- PROTECTED ROUTE EXAMPLE ---
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # If we get here, the token was valid and current_user is the logged-in User object
    return current_user