# 📍 Table of Contents
* [Project Overview](#Flag-Management-System)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Security Features](#security-features)
* [API Reference](#api-reference)
* [Setup & Installation](#setup--installation)
* [Testing](#testing)
* [CI/CD Workflow](#cicd-workflow)
* [Contributing](#contributing)



## Flag Management System

This is a Backend CRUD application built to manage system "flags", dynamic configurations that control application behavior. Instead of hard-coding settings, this API allows you to create, retrieve, update, and delete flags through a secure administrative interface.



### Features

* **Flag CRUD Engine:** A complete set of endpoints to manage the lifecycle of system flags (Create, Read, Update, Delete).
* **Admin Security:** Implementation of token-based access to protect sensitive configuration changes from unauthorized access.
* **Database Integration:** Utilizes **SQLAlchemy** to handle persistent storage and reliable state management of flag data.
* **Zero-Config Setup:** A Docker-first approach that allows the entire system to spin up with a single command—no local Python installation required.
* **CI/CD Pipeline:** A multi-stage GitHub Actions workflow that automatically runs unit tests via **Pytest** and performs a container smoke test on every push.


## Security Features

To ensure system integrity and protect against unauthorized configuration changes, the following security measures are implemented:

* **Password Hashing:** Utilizes `bcrypt` via **Passlib** for industry-standard, salt-protected secure storage.
* **JWT Authentication:** Implements **OAuth2 Bearer Tokens** with a strict **5-minute expiration** window to significantly reduce the risk of token hijacking.
* **Granular Authorization:** Critical state-changing routes (`POST`, `PATCH`, `DELETE`) are double-guarded, requiring both a valid **User JWT** and a secondary **X-Admin-Token** in the request header.
* **Rate Limiting:** Integrated **SlowAPI** to mitigate brute-force attempts and credential stuffing on authentication and flag-sensitive endpoints.


### Tech Stack

* **Framework:** FastAPI
* **Validation:** Pydantic V2
* **Testing:** Pytest / HTTPX
* **DevOps:** Docker, GitHub Actions
* **Database:** SQLAlchemy (SQLite/PostgreSQL)


###  API Reference

#### Authentication
| Method | Endpoint | Description | Rate Limit |
| :--- | :--- | :--- | :--- |
| `POST` | `/signup` | Register a new user with password validation | 10 req/min |
| `POST` | `/login` | Authenticate and receive a Bearer JWT token | - |

#### Flag Management
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/flags/` | Retrieve all flags for the user | JWT Token |
| `POST` | `/flags/` | Create a new system flag | **JWT + Admin Token** |
| `PATCH` | `/flags/{env}/{name}` | Toggle flag state  | **JWT + Admin Token**  |
| `DELETE` | `/flags/{env}/{name}` | Remove a flag from the system | **JWT + Admin Token**  |


### Setup & Installation

Since this project is optimized for containerization, you do not need to set up a local Python virtual environment.

1. Clone the Repository

```Bash
   git clone https://github.com/nuelkoya/Flag-Management-System.git \
   cd Flag-Management-System
```

2. Configure Environment Variables
Create a .env file in the root directory and add the following:

- DATABASE_URL=sqlite:///./test.db
- SECRET_KEY=your_super_secret_key
- X_ADMIN_TOKEN=your_admin_token
- USER_PASSWORD=your_secure_password

3. Run with Docker
The easiest way to get started is to build and run the container:

4. Build the image
```
    docker build -t flag-management .
```

5. Run the container
```
    docker run --env-file .env -p 8000:8000 flag-management
```

The API will be available at http://localhost:8000 and interactive docs at /docs.


### Testing

The CI Pipeline automatically runs tests on every push. To run them manually inside Docker:
```
    docker run --env-file .env flag-management python3 -m pytest
```

### CI/CD Workflow

This project utilizes GitHub Actions to ensure code reliability:

Build Stage: Installs dependencies and runs the Pytest suite.

Docker Stage: Builds the image and performs a "Smoke Test" to ensure the container starts and responds to health checks.


### Contributing

Fork the Project

Create your Feature Branch (git checkout -b feature/new-feature)

Commit your Changes (git commit -m 'feat: Add new-feature')

Push to the Branch (git push origin feature/new-feature)

Open a Pull Request


