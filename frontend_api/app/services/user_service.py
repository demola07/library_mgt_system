from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
