# GraphQL Voting App

### Project Idea Summary

This project was built to learn the tech stacks of this voting app. It includes operation on users, vote topics and voting options. For more information, refer to the code base.

---

### Tech Stack Summary

This project uses:

- **SQLAlchemy, Alembic & PostgreSQL** as its ORM, migrations manager and database
- **Starlette-Graphene3, Graphene & Graphene-SQLAlchemy** for running graphql and integration with sqlalchemy in fastapi
- **APScheduler, Redis & Refresh tokens** for authenticating and authorizing users

---

### How to Use

#### 1. Clone the Repository

```bash
git clone https://github.com/nia3zzz/graphql-voting-app
cd graphql-voting-app
```

#### 2. Create Virtual Environment.

```bash
uv venv .venv
```

#### 3. Set Up ENV Variables

- Copy the variable from `.env.sample` into a new `.env` file and supply your PostgreSQL connection string.
- Also ensure `Redis` is active and running in your system.

#### 4. Install Dependencies.

- Install all the dependencies listed in `pyproject.toml` file through a command.

```
uv sync
```

#### 5. Run the Project

```bash
uv run fastapi dev src/server.py
```

---

## Documentation

All the documentations for Authentication Apis are listed in `/docs` page with examples of usage and expected results. For GraphQL docs they are listed at `/api/v1/graphql`.

---
