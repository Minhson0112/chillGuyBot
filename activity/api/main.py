import os
import json
from typing import Optional

import mysql.connector
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(title="Chill Guy Merge Game API")


class DiscordTokenRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


class ClientLogRequest(BaseModel):
    message: str
    data: Optional[dict] = None


class GameOverRequest(BaseModel):
    score: int = Field(ge=0)
    sun_time: Optional[int] = Field(default=None, ge=0)


def getDbConnection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def getBearerToken(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    return authorization.removeprefix("Bearer ").strip()


def getDiscordUser(accessToken: str):
    response = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {accessToken}"},
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Discord token")

    return response.json()


@app.get("/health")
def healthCheck():
    return {"status": "ok"}


@app.post("/api/client-log")
def saveClientLog(request: ClientLogRequest):
    logData = {
        "message": request.message,
        "data": request.data if request.data is not None else {},
    }

    print(f"[client-log] {json.dumps(logData, ensure_ascii=False)}", flush=True)

    return {"status": "ok"}


@app.post("/api/discord/token")
def exchangeDiscordToken(request: DiscordTokenRequest):
    clientId = os.getenv("DISCORD_CLIENT_ID")
    clientSecret = os.getenv("DISCORD_CLIENT_SECRET")

    if not clientId or not clientSecret:
        raise HTTPException(status_code=500, detail="Discord OAuth credentials are not configured")

    tokenData = {
        "client_id": clientId,
        "client_secret": clientSecret,
        "grant_type": "authorization_code",
        "code": request.code,
    }

    if request.redirect_uri:
        tokenData["redirect_uri"] = request.redirect_uri

    response = requests.post(
        "https://discord.com/api/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=tokenData,
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Discord token exchange failed")

    return response.json()


@app.post("/api/game-over")
def saveGameOver(request: GameOverRequest, authorization: Optional[str] = Header(default=None)):
    accessToken = getBearerToken(authorization)
    discordUser = getDiscordUser(accessToken)
    userId = int(discordUser["id"])

    try:
        connection = getDbConnection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO merge_game_play_history (
                user_id,
                score,
                sun_time
            ) VALUES (
                %s,
                %s,
                %s
            )
            """,
            (userId, request.score, request.sun_time),
        )
        connection.commit()
        playHistoryId = cursor.lastrowid
    except mysql.connector.IntegrityError as error:
        raise HTTPException(status_code=400, detail="Member does not exist") from error
    finally:
        if "cursor" in locals():
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()

    return {
        "id": playHistoryId,
        "user_id": userId,
        "score": request.score,
        "sun_time": request.sun_time,
    }
