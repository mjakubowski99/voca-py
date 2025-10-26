import asyncio
import uuid
from core.db import get_session, set_db_session_context
import typer
from datetime import datetime
from typing import Optional

from core.db import init_db
from src.user.application.command.create_user import CreateUserHandler, CreateUserCommand
from src.shared.util.hash import IHash
from core.container import container

app = typer.Typer(help="User management CLI")

async def init():
    set_db_session_context(uuid.uuid4())
    await init_db()
    

@app.command("create-user")
def create_user(
    email: str = typer.Option(..., prompt=True, help="User email"),
    name: str = typer.Option(..., prompt=True, help="Full name"),
    password: str = typer.Option(..., prompt=True, hide_input=True, confirmation_prompt=True),
    picture: Optional[str] = typer.Option(None, help="Profile picture URL"),
):
    """Create a new user from CLI"""
    async def _run():
        await init()

        handler = container.resolve(CreateUserHandler)

        command = CreateUserCommand(
            email=email,
            name=name,
            password=password,
            picture=picture,
            email_verified_at=datetime.utcnow(),
        )

        await handler.handle(command)
        await get_session().commit()
        typer.echo(f"✅ User {email} created successfully!")

    asyncio.run(_run())


if __name__ == "__main__":
    app()
