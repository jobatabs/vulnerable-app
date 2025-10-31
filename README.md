# Vulnerable web app

This is a intentionally vulnerable web app that demonstrates several security flaws. This project is part of the Cyber Security Base series of courses from the University of Helsinki.

## Get started

You will need:

- the dependency management system Poetry installed. See [their website](https://python-poetry.org/docs/#installing-with-pipx) for instructions.
- a PostgreSQL server you have access to. Remember that you can run Postgres inside a local Docker container!

You can then launch the app instance locally:

1. Create .env, containing
    
        SECRET_KEY=<secret>
        DATABASE_URL=<pointing to a postgres:// instance>

A good way to generate the secret key would be:

        $ python3
        >>> import secrets
        >>> secrets.token_hex(16)
        '123456789abcdef'

2. Install dependencies and activate venv using Poetry.

        $ poetry install
        $ poetry shell

3. Utilise schema

        $ psql < schema.sql

4. Now start the instance

        $ flask run

5. After creating a user in the web app, make yourself admin

        $ psql
        => UPDATE users SET role=1 WHERE username='<your username here>';
        => \q
