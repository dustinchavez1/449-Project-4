import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.services.users.main import get_db, get_secondary_db
from api.utils import hash_password, verify_password
from api.services.users.mkclaims import generate_claims

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    roles: List[int] = Field(Query(..., min_length=1))


class UserLogin(BaseModel):
    username: str
    password: str


# Register new user
@router.post('/register')
def register_user(
    user: UserCreate = Depends(),
    db: sqlite3.Connection = Depends(get_db)
):
	# Check if user already exists
    user_in_db = db.execute("SELECT id FROM Users WHERE username = ?", (user.username,)).fetchone()
    if user_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='There is already another user with this username.',
        )

	# Check for nonexistent roles
    for role in user.roles:
        role_in_db = db.execute("SELECT id FROM Roles WHERE id = ?", (role,)).fetchone()
        if role_in_db is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'The role id {role} does not exist.',
            )

    # Hash password and insert into Users/UserRoles
    hashed_password = hash_password(user.password)
    result = db.execute(
        """
        INSERT INTO Users (username, password) VALUES(?, ?)
        """, 
        (user.username, hashed_password)
    )

    for role in user.roles:
        db.execute(
            """
            INSERT INTO UserRoles (user_id, role_id) VALUES(?, ?)
            """, 
            (result.lastrowid, role)
        )
    db.commit()

    return {"detail": "User '"+user.username+"' registered successfully."}

# Check if password is correct
@router.get('/verify')
def check_password(
    login: UserLogin = Depends(),
    # Checks password from rotating secondary databases
    db: sqlite3.Connection = Depends(get_secondary_db)
):
    # Get user data from database
    user = db.execute("SELECT password, id FROM Users WHERE username = ?", (login.username,)).fetchone()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with the username '+login.username+' does not exist.',
        )
    hashed_password = user[0]
    user_id = user[1]  

    # Verify password hash
    if not verify_password(login.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password.',
        )

    # Get user roles from database
    userRoles = db.execute(
        """
        SELECT distinct Roles.name FROM Roles 
        JOIN UserRoles ON UserRoles.role_id = Roles.id 
        WHERE UserRoles.user_id = ?
        """,
        (user_id,)
    ).fetchall()

    # Generate JWT claims with access and refresh tokens
    roles = []
    for userRole in userRoles:
        # Access the data in each user tuple
        roles.append(userRole[0])

    return generate_claims(login.username, user_id, roles)
