import re
import typer


def validate_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise typer.BadParameter(f"{email} is not a valid email address.")
    return email


def validate_enviorment(environment):
    if environment not in ["dev", "production"]:
        raise typer.BadParameter("`environment` can't be other then [production & dev]")
    return environment

def validate_project_name(project_name):
    if not re.match(r"^[a-zA-Z0-9-_]+$", project_name):
        raise typer.BadParameter(f"{project_name} is not a valid project name.")
    return project_name