"""rls

Revision ID: fe86397600e9
Revises: 0d8b0e18ce08
Create Date: 2026-10-06 19:13:46.113337
"""

from typing import Sequence, Union

from alembic import op

revision: str = "fe86397600e9"
down_revision: Union[str, None] = "0d8b0e18ce08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("create role authenticated nologin")
    op.execute(
        "create role authenticator login noinherit password 'authenticator_password'"
    )
    op.execute("grant authenticated to authenticator")

    op.execute("grant usage on schema public to authenticated")
    op.execute(
        "grant select, insert, update, delete on public.document to authenticated"
    )

    op.execute("alter table public.document enable row level security")
    op.execute(
        """
        create policy tenant_isolation on public.document
        to authenticated
        using (
            tenant_id = (current_setting('request.jwt.claims', true)::json ->> 'tenant_id')::uuid
        )
        with check (
            tenant_id = (current_setting('request.jwt.claims', true)::json ->> 'tenant_id')::uuid
        )
        """
    )


def downgrade() -> None:
    op.execute("drop policy tenant_isolation on public.document")
    op.execute("alter table public.document disable row level security")
    op.execute("revoke all on public.document from authenticated")
    op.execute("revoke usage on schema public from authenticated")
    op.execute("drop role authenticator")
    op.execute("drop role authenticated")
