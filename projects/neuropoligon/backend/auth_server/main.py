# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Backend авторизации Нейрополигон: регистрация, код на почту, JWT, админ только для web-admin.
Запуск: uvicorn main:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import os
import random
import smtplib
import sqlite3
import string
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

DB_PATH = Path(os.getenv("AUTH_DB", Path(__file__).parent / "auth.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALG = "HS256"
CODE_TTL_MIN = int(os.getenv("CODE_TTL_MIN", "30"))
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").lower().strip()

ANDROID_CLIENT = "android"
WEB_ADMIN_CLIENT = "web-admin"
CLIENT_HEADER = "x-neuropoligon-client"

app = FastAPI(title="Neuropoligon Auth", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class VerifyBody(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)


class ResendBody(BaseModel):
    email: EmailStr


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                verified INTEGER NOT NULL DEFAULT 0,
                verify_code TEXT,
                verify_expires TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def client_kind(x_client: str | None) -> str:
    value = (x_client or ANDROID_CLIENT).lower()
    if value not in {ANDROID_CLIENT, WEB_ADMIN_CLIENT}:
        return ANDROID_CLIENT
    return value


def send_email(to: str, subject: str, body: str) -> None:
    if not SMTP_HOST or not SMTP_USER:
        print(f"[DEV MAIL] To={to} Subject={subject}\n{body}\n")
        return
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def issue_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def make_token(email: str, role: str) -> str:
    payload = {
        "sub": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=14),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/auth/register")
def register(
    body: RegisterBody,
    x_neuropoligon_client: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    email = body.email.lower()
    if ADMIN_EMAIL and email == ADMIN_EMAIL and client_kind(x_neuropoligon_client) != WEB_ADMIN_CLIENT:
        raise HTTPException(403, "Админ-регистрация только через веб-панель.")
    code = issue_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MIN)
    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    role = "admin" if ADMIN_EMAIL and email == ADMIN_EMAIL else "user"
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users (email, password_hash, role, verified, verify_code, verify_expires, created_at)
            VALUES (?, ?, ?, 0, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                password_hash=excluded.password_hash,
                verify_code=excluded.verify_code,
                verify_expires=excluded.verify_expires,
                verified=0
            """,
            (
                email,
                password_hash,
                role,
                code,
                expires.isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    send_email(
        email,
        "Код подтверждения — Нейрополигон",
        f"Ваш код: {code}\nДействует {CODE_TTL_MIN} мин.\n\nЕсли вы не регистрировались — проигнорируйте письмо.",
    )
    return {"message": "Код отправлен на вашу почту. Введите его в приложении."}


@app.post("/auth/resend")
def resend(body: ResendBody) -> dict[str, str]:
    email = body.email.lower()
    code = issue_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=CODE_TTL_MIN)
    with get_db() as conn:
        row = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            raise HTTPException(404, "Пользователь не найден. Сначала зарегистрируйтесь.")
        conn.execute(
            "UPDATE users SET verify_code=?, verify_expires=? WHERE email=?",
            (code, expires.isoformat(), email),
        )
        conn.commit()
    send_email(email, "Новый код — Нейрополигон", f"Код: {code}\nДействует {CODE_TTL_MIN} мин.")
    return {"message": "Код отправлен повторно."}


@app.post("/auth/verify")
def verify(
    body: VerifyBody,
    x_neuropoligon_client: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    email = body.email.lower()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            raise HTTPException(404, "Пользователь не найден.")
        if row["verify_code"] != body.code.strip():
            raise HTTPException(400, "Неверный код.")
        expires = datetime.fromisoformat(row["verify_expires"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(400, "Код истёк. Запросите новый.")
        conn.execute("UPDATE users SET verified=1, verify_code=NULL WHERE email=?", (email,))
        conn.commit()
        role = row["role"]
    if role == "admin" and client_kind(x_neuropoligon_client) != WEB_ADMIN_CLIENT:
        raise HTTPException(403, "Админ-вход только через веб-панель.")
    token = make_token(email, role)
    return {"token": token, "email": email, "role": role}


@app.post("/auth/login")
def login(
    body: LoginBody,
    x_neuropoligon_client: Annotated[str | None, Header()] = None,
) -> dict[str, str]:
    email = body.email.lower()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            raise HTTPException(401, "Неверная почта или пароль.")
        if not bcrypt.checkpw(body.password.encode(), row["password_hash"].encode()):
            raise HTTPException(401, "Неверная почта или пароль.")
        if not row["verified"]:
            raise HTTPException(403, "Подтвердите почту кодом из письма.")
        role = row["role"]
    if role == "admin" and client_kind(x_neuropoligon_client) != WEB_ADMIN_CLIENT:
        raise HTTPException(403, "Админ-вход только через веб-панель.")
    return {"token": make_token(email, role), "email": email, "role": role}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
