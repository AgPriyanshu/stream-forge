from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from enums import ProcessingJobStatus, ProcessingJobType
from sqlalchemy import Column, func, text
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


def enum_column(enum_cls: type[Enum]) -> Column:
    # Stored as VARCHAR holding the enum values, so PostgREST clients see "pending", not "PENDING".
    return Column(
        SAEnum(
            enum_cls,
            native_enum=False,
            length=32,
            values_callable=lambda e: [member.value for member in e],
        ),
        nullable=False,
    )


class BaseSQLModel(SQLModel):
    # Server defaults let PostgREST inserts omit these columns.
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"server_default": func.now()},
    )


class Tenant(BaseSQLModel, table=True):
    name: str

    # Relationships.
    users: list["User"] = Relationship(back_populates="tenant")
    documents: list["Document"] = Relationship(back_populates="tenant")
    processing_jobs: list["ProcessingJob"] = Relationship(back_populates="tenant")


class User(BaseSQLModel, table=True):
    name: str
    email: str = Field(unique=True)
    password_hash: str
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)

    # Relationships.
    tenant: Tenant = Relationship(back_populates="users")
    documents: list["Document"] = Relationship(back_populates="owner")


class Document(BaseSQLModel, table=True):
    filename: str
    storage_key: str
    owner_id: UUID = Field(foreign_key="user.id", index=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)

    # Relationships.
    owner: User = Relationship(back_populates="documents")
    tenant: Tenant = Relationship(back_populates="documents")
    processing_jobs: list["ProcessingJob"] = Relationship(back_populates="document")


class ProcessingJob(BaseSQLModel, table=True):
    status: ProcessingJobStatus = Field(
        default=ProcessingJobStatus.PENDING,
        sa_column=enum_column(ProcessingJobStatus),
    )
    job_type: ProcessingJobType = Field(sa_column=enum_column(ProcessingJobType))
    document_id: UUID = Field(foreign_key="document.id", index=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)

    # Relationships.
    document: Document = Relationship(back_populates="processing_jobs")
    tenant: Tenant = Relationship(back_populates="processing_jobs")
