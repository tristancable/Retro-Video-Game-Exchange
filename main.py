from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import (
    UserCreate,
    UserResponse,
    UserUpdate,
    GameCreate,
    GameResponse,
    GameUpdate,
)
from db import games_collection, users_collection
from bson import ObjectId
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = users_collection.find_one({"_id": ObjectId(token)})
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    return user


def serialize_id(document):
    document["id"] = str(document["_id"])
    document.pop("_id")
    document.pop("password", None)
    return document


app = FastAPI(title="Retro Video Game Exchange API")


def add_user_links(user):
    user["_links"] = {
        "self": {"href": f"/users/{user['id']}"},
        "update": {"href": f"/users/{user['id']}", "method": "PUT"},
    }
    return user


def add_game_links(game):
    game["_links"] = {
        "self": {"href": f"/games/{game['id']}"},
        "owner": {"href": f"/users/{game['owner_id']}"},
        "update": {"href": f"/games/{game['id']}", "method": "PUT"},
        "delete": {"href": f"/games/{game['id']}", "method": "DELETE"},
    }
    return game


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": str(user["_id"]), "token_type": "bearer"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user_dict = user.model_dump()
    password_bytes = user_dict["password"].encode("utf-8")[:72]
    user_dict["password"] = pwd_context.hash(password_bytes)

    users_collection.insert_one(user_dict)

    created_user = users_collection.find_one({"email": user.email})
    created_user = serialize_id(created_user)
    return add_user_links(created_user)


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = serialize_id(user)
    return add_user_links(user)


@app.put("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    if str(current_user["_id"]) != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this user"
        )

    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})


@app.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate, owner_id: str = Query(...)):
    owner = users_collection.find_one({"_id": ObjectId(owner_id)})
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found"
        )

    game_dict = game.model_dump()
    game_dict["owner_id"] = owner_id

    result = games_collection.insert_one(game_dict)
    created_game = games_collection.find_one({"_id": result.inserted_id})
    created_game = serialize_id(created_game)
    return add_game_links(created_game)


@app.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: str):
    game = games_collection.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )
    game = serialize_id(game)
    return add_game_links(game)


@app.put("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_game(
    game_id: str,
    game_update: GameUpdate,
    current_user: dict = Depends(get_current_user),
):
    game = games_collection.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="You do not own this game")

    update_data = {k: v for k, v in game_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    games_collection.update_one({"_id": ObjectId(game_id)}, {"$set": update_data})


@app.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: str):
    game = games_collection.find_one({"_id": ObjectId(game_id)})
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    games_collection.delete_one({"_id": ObjectId(game_id)})


@app.get("/games", response_model=list[GameResponse])
def search_games(
    name: str = None, system: str = None, current_user: dict = Depends(get_current_user)
):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if system:
        query["system"] = {"$regex": system, "$options": "i"}

    games = games_collection.find(query)
    return [add_game_links(serialize_id(game)) for game in games]


# I used AI to help write this code
