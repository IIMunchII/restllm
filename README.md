# REST LLM
This repository is work in progress!

The repository contains a functioning REST API based on LiteLLM and the interface from OpenAI to instruct and chat models using their familiar completion API. The REST API is build with FastAPI wraps the LLM functionalities together with a Redis backend for CRUD operations.

## Authentication

The API uses Oauth2 implementation in FastAPI for authentication. Currently there is login endpoint `/v1/authentication/token` and a `/v1/authentication/signup`. The password hashing algorithm defaults to `argon2`.

## Setup development environment
To setup for development use poetry to install the package.
```bash
poetry install
```

You can also run the full application with backends using docker compose. Run `docker compose build` to build the local image. Then run `docker compose up` to run the application.

Check endpoint http://localhost:8000/docs for Swagger UI.

## Roadmap
Below are some of the progressions in the repo

| Feature                                         | Status      |
|-------------------------------------------------|-------------|
| CRUD endpoints for Chat                         | ✅ Done     |
| CRUD endpoints for Prompts and PromptTemplates  | ✅ Done     |
| CRUD endpoints for custom functions             | ✅ Done     |
| Endpoints for premade function calls            | ✅ Done     |
| Events endpoint for listening to events         | 🟥 In progress |
| User authentication                             | 🟥 In progress |
| Reset password and email verification           | 🟥 In progress |
| Setup GitHub actions pipeline                   | 🟥 Coming |
| Acceptance tests and unittests                  | 🟥 Coming |
| Helm Chart for deployment on Kubernetes         | 🟥 Coming |