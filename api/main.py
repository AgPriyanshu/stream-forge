import os
from uuid import uuid4

import aiofiles
from authentication import get_token_data
from db import get_session
from fastapi import APIRouter, Depends, FastAPI, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from models import Document, Tenant, User
from mq import publish
from schemas import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    TenantCreateRequest,
    TenantResponse,
    TokenData,
)
from security import DUMMY_HASH, create_access_token, hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth")


@api_router.get("/ping")
async def ping():
    return JSONResponse({"message": "pong"})


@api_router.post(
    "/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED
)
async def create_tenant(
    body: TenantCreateRequest, db_session: AsyncSession = Depends(get_session)
):
    tenant = Tenant(name=body.name)
    response = TenantResponse(id=tenant.id, name=tenant.name)
    db_session.add(tenant)
    await db_session.commit()

    return response


@auth_router.post(
    "/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: SignupRequest, db_session: AsyncSession = Depends(get_session)):
    tenant = await db_session.get(Tenant, body.tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        )

    existing = await db_session.exec(select(User).where(User.email == body.email))

    if existing.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        tenant_id=tenant.id,
    )
    db_session.add(user)

    # Built before commit, since attributes expire afterwards and lazy loads fail in async.
    access_token = create_access_token(user)

    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    return LoginResponse(access_token=access_token)


@auth_router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db_session: AsyncSession = Depends(get_session)):
    result = await db_session.exec(select(User).where(User.email == body.email))
    user = result.first()

    password_valid = verify_password(
        user.password_hash if user else DUMMY_HASH, body.password
    )

    if not user or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return LoginResponse(access_token=create_access_token(user))


@api_router.post("/upload-document")
async def upload_document(
    file: UploadFile,
    db_session: AsyncSession = Depends(get_session),
    token: TokenData = Depends(get_token_data),
):
    storage_key = f"/app/files/{token.tenant_id}/{uuid4()}-{file.filename}"
    os.makedirs(os.path.dirname(storage_key), exist_ok=True)
    if file.filename:
        document = Document(
            filename=file.filename,
            storage_key=storage_key,
            owner_id=token.user_id,
            tenant_id=token.tenant_id,
        )

        db_session.add(document)
        await db_session.commit()

        async with aiofiles.open(storage_key, "wb") as out_file:
            while content := await file.read(1024):
                await out_file.write(content)

        publish("document uploaded")
        return {"Result": "OK"}


api_router.include_router(auth_router)

app = FastAPI(
    title="StreamForge",
    version="0.0.0",
)


app.include_router(api_router)
