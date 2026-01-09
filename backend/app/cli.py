import asyncio
import click
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.user import UserRole
from app.services.auth import create_user, get_user_by_email

async def _create_admin(email: str, password: str) -> None:
    async with async_session_maker() as db:
        existing = await get_user_by_email(db, email)
        if existing:
            if existing.role == UserRole.ADMIN:
                click.echo(f"Admin user {email} already exists.")
                return
            else:
                # Upgrade to admin
                existing.role = UserRole.ADMIN
                await db.commit()
                click.echo(f"User {email} upgraded to admin.")
                return

        user = await create_user(db, email, password, role=UserRole.ADMIN)
        click.echo(f"Admin user created: {user.email}")

@click.group()
def cli():
    """Task Manager CLI"""
    pass

@cli.command()
@click.option("--email", prompt=True, help="Admin email address")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password")
def create_admin(email: str, password: str):
    """Create a new admin user."""
    if len(password) < 8:
        click.echo("Error: Password must be at least 8 characters.", err=True)
        return

    asyncio.run(_create_admin(email, password))

if __name__ == "__main__":
    cli()
