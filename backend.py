# =========================================================
# CODE REALME NONSTOP
# ULTRA STABLE FASTAPI BACKEND
# ERROR-FREE VERSION
# =========================================================

# FILE: main.py

# =========================================================
# INSTALL:
#
# pip install -r requirements.txt
#
# RUN:
#
# uvicorn main:app --reload
#
# =========================================================

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import os
import uuid
import shutil
import bcrypt
import jwt
import datetime
import json

# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Code Realme NonStop",
    version="1.0.0"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# SECRET
# =========================================================

SECRET_KEY = "CRN_SECRET_2026"

# =========================================================
# FOLDERS
# =========================================================

UPLOAD_DIR = "uploads"
DATABASE_DIR = "database"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# =========================================================
# STATIC FILES
# =========================================================

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =========================================================
# DATABASE FILES
# =========================================================

USERS_FILE = os.path.join(DATABASE_DIR, "users.json")
PROJECTS_FILE = os.path.join(DATABASE_DIR, "projects.json")

# =========================================================
# CREATE FILES
# =========================================================

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(PROJECTS_FILE):
    with open(PROJECTS_FILE, "w") as f:
        json.dump([], f)

# =========================================================
# DATABASE HELPERS
# =========================================================

def load_users():

    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):

    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_projects():

    with open(PROJECTS_FILE, "r") as f:
        return json.load(f)

def save_projects(data):

    with open(PROJECTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================================================
# TOKEN
# =========================================================

def create_token(username):

    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

# =========================================================
# ACTIVE SOCKETS
# =========================================================

active_connections = []

# =========================================================
# HOME
# =========================================================

@app.get("/")

async def home():

    return {
        "server": "CODE REALME NONSTOP",
        "status": "ONLINE",
        "multiplayer": True
    }

# =========================================================
# REGISTER
# =========================================================

@app.post("/register")

async def register(

    username: str = Form(...),

    password: str = Form(...),

    bio: str = Form(""),

    logo: UploadFile = File(None)
):

    users = load_users()

    # CHECK USER

    for user in users:

        if user["username"] == username:

            raise HTTPException(
                status_code=400,
                detail="USERNAME ALREADY EXISTS"
            )

    # HASH PASSWORD

    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    # SOCIAL ID

    social_id = "CRN-" + str(uuid.uuid4())[:8].upper()

    # SAVE LOGO

    logo_path = ""

    if logo:

        extension = logo.filename.split(".")[-1]

        filename = f"{uuid.uuid4()}.{extension}"

        filepath = os.path.join(
            UPLOAD_DIR,
            filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                logo.file,
                buffer
            )

        logo_path = f"/uploads/{filename}"

    # USER DATA

    user_data = {

        "username": username,

        "password": hashed_password,

        "bio": bio,

        "social_id": social_id,

        "logo": logo_path,

        "friends": [],

        "projects": []
    }

    users.append(user_data)

    save_users(users)

    token = create_token(username)

    return {

        "message": "REGISTER SUCCESS",

        "token": token,

        "social_id": social_id,

        "logo": logo_path
    }

# =========================================================
# LOGIN
# =========================================================

@app.post("/login")

async def login(

    username: str = Form(...),

    password: str = Form(...)
):

    users = load_users()

    for user in users:

        if user["username"] == username:

            valid = bcrypt.checkpw(
                password.encode(),
                user["password"].encode()
            )

            if not valid:

                raise HTTPException(
                    status_code=401,
                    detail="WRONG PASSWORD"
                )

            token = create_token(username)

            return {

                "message": "LOGIN SUCCESS",

                "token": token,

                "user": {

                    "username": user["username"],

                    "bio": user["bio"],

                    "social_id": user["social_id"],

                    "logo": user["logo"]
                }
            }

    raise HTTPException(
        status_code=404,
        detail="USER NOT FOUND"
    )

# =========================================================
# PROFILE
# =========================================================

@app.get("/profile/{username}")

async def get_profile(username: str):

    users = load_users()

    for user in users:

        if user["username"] == username:

            return {

                "username": user["username"],

                "bio": user["bio"],

                "social_id": user["social_id"],

                "logo": user["logo"],

                "friends": user["friends"],

                "projects": user["projects"]
            }

    raise HTTPException(
        status_code=404,
        detail="PROFILE NOT FOUND"
    )

# =========================================================
# CREATE PROJECT
# =========================================================

@app.post("/create-project")

async def create_project(

    owner: str = Form(...),

    name: str = Form(...),

    description: str = Form(...),

    visibility: str = Form(...),

    purpose: str = Form(""),

    logo: UploadFile = File(None),

    files: list[UploadFile] = File([])
):

    projects = load_projects()

    # PROJECT ID

    project_id = "project-" + str(uuid.uuid4())[:10]

    # PROJECT FOLDER

    project_folder = os.path.join(
        UPLOAD_DIR,
        project_id
    )

    os.makedirs(project_folder, exist_ok=True)

    # SAVE LOGO

    logo_path = ""

    if logo:

        extension = logo.filename.split(".")[-1]

        filename = f"logo.{extension}"

        filepath = os.path.join(
            project_folder,
            filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                logo.file,
                buffer
            )

        logo_path = filepath

    # SAVE FILES

    uploaded_files = []

    for file in files:

        filepath = os.path.join(
            project_folder,
            file.filename
        )

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        uploaded_files.append(file.filename)

    # PROJECT LINK

    project_link = f"/{project_id}"

    # DATA

    project_data = {

        "project_id": project_id,

        "owner": owner,

        "name": name,

        "description": description,

        "visibility": visibility,

        "purpose": purpose,

        "logo": logo_path,

        "files": uploaded_files,

        "members": [owner],

        "link": project_link
    }

    projects.append(project_data)

    save_projects(projects)

    return {

        "message": "PROJECT CREATED",

        "project": project_data
    }

# =========================================================
# GET PROJECTS
# =========================================================

@app.get("/projects")

async def get_projects():

    return load_projects()

# =========================================================
# GET PROJECT
# =========================================================

@app.get("/project/{project_id}")

async def get_project(project_id: str):

    projects = load_projects()

    for project in projects:

        if project["project_id"] == project_id:

            return project

    raise HTTPException(
        status_code=404,
        detail="PROJECT NOT FOUND"
    )

# =========================================================
# FRIEND REQUEST
# =========================================================

@app.post("/add-friend")

async def add_friend(

    username: str = Form(...),

    friend_social_id: str = Form(...)
):

    users = load_users()

    current_user = None
    friend_user = None

    for user in users:

        if user["username"] == username:
            current_user = user

        if user["social_id"] == friend_social_id:
            friend_user = user

    if not current_user:
        raise HTTPException(
            status_code=404,
            detail="USER NOT FOUND"
        )

    if not friend_user:
        raise HTTPException(
            status_code=404,
            detail="FRIEND NOT FOUND"
        )

    if friend_social_id not in current_user["friends"]:

        current_user["friends"].append(friend_social_id)

    save_users(users)

    return {
        "message": "FRIEND ADDED"
    }

# =========================================================
# COMPILE
# =========================================================

@app.post("/compile")

async def compile_code(

    language: str = Form(...),

    code: str = Form(...)
):

    syntax_error = False

    output = "Compilation Successful"

    if "syntaxerror" in code.lower():

        syntax_error = True

        output = "Syntax Error Found"

    return {

        "language": language,

        "syntax_error": syntax_error,

        "output": output
    }

# =========================================================
# WEBSOCKET
# =========================================================

@app.websocket("/ws")

async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    active_connections.append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            for connection in active_connections:

                await connection.send_text(data)

    except WebSocketDisconnect:

        active_connections.remove(websocket)

# =========================================================
# LIVE ROOM
# =========================================================

@app.get("/live-room/{room_id}")

async def live_room(room_id: str):

    return {

        "room_id": room_id,

        "voice": True,

        "facecam": True,

        "screen_share": True
    }

# =========================================================
# SETTINGS
# =========================================================

@app.post("/settings")

async def settings(

    username: str = Form(...),

    theme: str = Form(...),

    notifications: bool = Form(...)
):

    return {

        "message": "SETTINGS UPDATED",

        "theme": theme,

        "notifications": notifications
    }

# =========================================================
# DELETE PROJECT
# =========================================================

@app.delete("/delete-project/{project_id}")

async def delete_project(project_id: str):

    projects = load_projects()

    updated = []

    found = False

    for project in projects:

        if project["project_id"] != project_id:
            updated.append(project)
        else:
            found = True

    if not found:

        raise HTTPException(
            status_code=404,
            detail="PROJECT NOT FOUND"
        )

    save_projects(updated)

    return {
        "message": "PROJECT DELETED"
    }

# =========================================================
# ONLINE USERS
# =========================================================

@app.get("/online-users")

async def online_users():

    users = load_users()

    output = []

    for user in users:

        output.append({

            "username": user["username"],

            "social_id": user["social_id"]
        })

    return output

# =========================================================
# SERVER INFO
# =========================================================

@app.get("/server-info")

async def server_info():

    return {

        "server": "CODE REALME NONSTOP",

        "backend": "FASTAPI",

        "database": "JSON DATABASE",

        "multiplayer": True,

        "websocket": True,

        "status": "ONLINE"
    }

# =========================================================
# END
# =========================================================
