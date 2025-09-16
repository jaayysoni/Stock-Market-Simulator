from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate  # Make sure you have this Pydantic schema
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fetch user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Fetch user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Create user
def create_user(db: Session, user: UserCreate):
    password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password = password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Verify password
def verify_password(plain_password: str, password: str) -> bool:
    return pwd_context.verify(plain_password, password)