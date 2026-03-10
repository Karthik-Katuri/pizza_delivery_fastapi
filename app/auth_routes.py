from fastapi import APIRouter, status, HTTPException, Depends
from app.database import Session
from app.schemas import SignUpModel, TokenResponse
from app.models import User
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user, get_db
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/signup", response_model=SignUpModel, status_code=status.HTTP_201_CREATED
)
def signup(user: SignUpModel, db=Depends(get_db)):
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    db_username = db.query(User).filter(User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        is_staff=user.is_staff,
        is_active=user.is_active,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@auth_router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.username})

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
