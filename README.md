# REST LLM
This repository is work in progress!

The repository contains a functioning REST API based on LiteLLM and the interface from OpenAI to instruct and chat models using their familiar completion API. The REST API is build with FastAPI wraps the LLM functionalities together with a Redis backend for CRUD operations.

The API is userbased and has a dummy-middleware that creates a User class object. Later this will change to a different implementation.

## Run the server
Run `docker compose build` to build the local image. Then run `docker compose up` to run the application.

Check endpoint http://localhost:8000/docs for Swagger UI.
