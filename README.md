# Personalized Interview Generation Engine

This project is a sophisticated, AI-powered application designed to generate personalized interview questions. It leverages a multi-agent system built with LangGraph to create a tailored interview experience based on a candidate's resume and the job description.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Services](#services)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)

## Features

- **Personalized Interview Generation:** Generates a unique set of interview questions based on a candidate's resume and a job description.
- **Interactive Interview Sessions:** Allows candidates to answer questions one by one and receive follow-up questions based on their answers.
- **Resume Management:** Upload, store, and manage multiple versions of your resume.
- **Personalized Learning Roadmaps:** After completing an interview, the system can generate a personalized roadmap to help you improve your skills.
- **User Authentication:** Secure user authentication and management.

## Architecture

The application is built around a modular, service-oriented architecture, orchestrated with Docker Compose. The core of the application is a FastAPI server that manages the interview generation process.

The key components of the architecture are:

- **FastAPI Application:** The main entry point of the application, responsible for handling API requests, managing the interview generation workflow, and interacting with other services.
- **LangGraph Multi-Agent System:** A stateful, persistent graph of agents that work together to generate interview questions. The graph is defined using the `LangGraph` library and uses MongoDB for checkpointing, allowing interviews to be resumed even after a restart.
- **MongoDB:** The primary database for the application, used to store application data and to persist the state of the `LangGraph` interview generation process.
- **Redis and ARQ:** A Redis-backed queue system used for running background tasks, such as processing uploaded resumes and generating learning roadmaps for candidates.
- **Qdrant:** A vector database used for high-performance semantic search. This is likely used to find similar questions or to match candidate skills with job requirements.
- **LLM Integrations:** The application is integrated with multiple Large Language Models (LLMs) through the `LangChain` library, including models from Anthropic, Groq, HuggingFace, and OpenAI.

## Services

The `docker-compose.yml` file defines the following services:

- **`app`:** The main FastAPI application.
- **`mongodb`:** The MongoDB database.
- **`redis`:** The Redis server for the `ARQ` task queue.
- **`qdrant`:** The Qdrant vector database.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Poetry

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Set up the environment:**

    Create a `.env` file in the `server` directory and populate it with the necessary environment variables. You can use the `server/.env.example` file as a template.

3.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

    This will build the Docker images for each service and start the containers.

## Usage

The application is accessed through its REST API. The API is documented using Swagger UI, which is available at `/docs` when the application is running in development mode.

### API Endpoints

The main API router is located in `app/api/v1/router.py`. The available endpoints include:

- **`/healthz`:** A liveness probe to check if the application is running.

### Authentication

- `POST /api/v1/auth/register`: Register a new user.
- `POST /api/v1/auth/login`: Log in a user.
- `POST /api/v1/auth/refresh`: Refresh an access token.

### Users

- `GET /api/v1/users/me`: Get the current user's information.

### Resumes

- `POST /api/v1/resumes`: Upload a resume.
- `GET /api/v1/resumes`: List the current user's resumes.
- `GET /api/v1/resumes/{resume_uuid}`: Get a specific resume.
- `DELETE /api/v1/resumes/{resume_uuid}`: Delete a resume.

### Interviews

- `POST /api/v1/interviews`: Start a new interview session.
- `GET /api/v1/interviews`: List the current user's interviews.
- `GET /api/v1/interviews/{session_uuid}`: Get the details of a specific interview.
- `POST /api/v1/interviews/{session_uuid}/answer`: Submit an answer to a question.
- `POST /api/v1/interviews/{session_uuid}/abandon`: Abandon an interview session.

### Roadmaps

- `POST /api/v1/roadmaps`: Request a roadmap for a completed interview.
- `GET /api/v1/roadmaps`: List the current user's roadmaps.
- `GET /api/v1/roadmaps/{roadmap_uuid}`: Get a specific roadmap.

## Project Structure

```
.
├── docker-compose.yml
├── docs
│   └── personalised_interview_generation.drawio
├── server
│   ├── Agentic_wf
│   │   └── agents
│   │       └── generate_questions
│   ├── app
│   │   ├── api
│   │   │   └── v1
│   │   ├── config
│   │   ├── core
│   │   ├── db
│   │   └── utils
│   ├── main.py
│   ├── pyproject.toml
│   └── tests
└── ...
```

- **`docker-compose.yml`:** Defines the services, networks, and volumes for the application.
- **`docs`:** Contains documentation for the project, including architecture diagrams.
- **`server`:** The main application directory.
  - **`Agentic_wf`:** Contains the `LangGraph` agent definitions.
  - **`app`:** The main FastAPI application code.
    - **`api`:** API endpoint definitions.
    - **`config`:** Application configuration.
    - **`core`:** Core application logic, including middleware and exception handlers.
    - **`db`:** Database connection and interaction logic.
    - **`utils`:** Utility functions.
  - **`main.py`:** The entry point for the FastAPI application.
  - **`pyproject.toml`:** The project's dependencies and metadata.
  - **`tests`:** Unit and integration tests.
raction logic.
    - **`utils`:** Utility functions.
  - **`main.py`:** The entry point for the FastAPI application.
  - **`pyproject.toml`:** The project's dependencies and metadata.
  - **`tests`:** Unit and integration tests.
