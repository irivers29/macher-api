# Macher API

This repository contains the macher API for our web application. It integrates a database, handles user management and provides the necessary endpoints for the web application to work

## Local Setup
### Clone the Repository
```bash
git clone git@github.com:irivers29/macher-api.git
cd macher-api
```

### Start devbox environment

```bash
devbox shell
```

### Start local database
If you want to test everything locally for development, you will need to start a local postgresql container. In a separate terminal, or from the docker UI, start the corresponding container. 
```bash
cd local-database
docker build -t my-postgres-db .
docker run --name my-postgres -p 5432:5432 -d my-postgres-db
```
To stop, kill and rerun the database, run:
```bash
docker ps
docker stop <container-id>
docker rm <container-id>
docker run --name my-postgres -p 5432:5432 -d my-postgres-db
```

## Run App

The App can be run locally with the following:
```bash
uvicorn app.main:app --reload --log-level debug 
```

## Project Structure

app/
* Contains all code relevant for the App
local-database/
* Contains the Dockerfile to build the image to run a local database for testing