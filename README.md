
# KanMind Backend

KanMind is a Kanban task management application built with Django and Django REST Framework.

This project provides a REST API for managing users, boards, tasks, and comments. It was developed as part of the Developer Akademie Backend course.

## Features

- User registration and login with token authentication
- Create, view, update, and delete boards
- Add members to boards
- Create, view, update, and delete tasks
- Assign tasks to users and select reviewers
- Manage task status, priority, and due dates
- Create, view, and delete task comments
- Permission checks for boards, tasks, and comments
- Filter tasks assigned to the current user or awaiting their review

## Technologies

- Python
- Django
- Django REST Framework
- SQLite
- Django REST Framework Token Authentication
- django-cors-headers
- Coverage.py

## Installation

Clone the repository:

```bash
git clone https://github.com/Magdalena260/Kanmind-APP.git
cd Kanmind-APP
```

Create a virtual environment:

```bash
python -m venv env
```

Activate the virtual environment on Windows:

```powershell
.\env\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Apply the database migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API is available at:

`http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication

- `POST /api/registration/` – Register a new user
- `POST /api/login/` – Log in and receive an authentication token

### Boards

- `GET /api/boards/` – List accessible boards
- `POST /api/boards/` – Create a board
- `GET /api/boards/{id}/` – Retrieve board details
- `PATCH /api/boards/{id}/` – Update a board
- `DELETE /api/boards/{id}/` – Delete a board

### Tasks

- `POST /api/tasks/` – Create a task
- `GET /api/tasks/{id}/` – Retrieve a task
- `PATCH /api/tasks/{id}/` – Update a task
- `DELETE /api/tasks/{id}/` – Delete a task
- `GET /api/tasks/assigned-to-me/` – List assigned tasks
- `GET /api/tasks/reviewing/` – List tasks to review

### Comments

- `GET /api/tasks/{task_id}/comments/` – List task comments
- `POST /api/tasks/{task_id}/comments/` – Add a comment
- `DELETE /api/tasks/{task_id}/comments/{id}/` – Delete a comment

### Users

- `GET /api/email-check/?email=...` – Find a user by email address

## Authentication

Protected API endpoints require a token in the request header:

```text
Authorization: Token YOUR_TOKEN
```

## Testing

Run the automated tests:

```bash
python manage.py test
```

Measure test coverage:

```bash
coverage run --source=auth_app,kanban_app manage.py test
coverage report
```

The project aims for at least 95% test coverage.

## Project Structure

```text
kanmind_back/
├── auth_app/
│   └── api/
├── kanban_app/
│   └── api/
├── core/
├── manage.py
├── requirements.txt
└── README.md
```

## Frontend

The backend can be used with the KanMind frontend provided by Developer Akademie.

Frontend repository:
https://github.com/Developer-Akademie-Backendkurs/project.KanMind

For local development, the frontend can connect to the API at `http://127.0.0.1:8000/api/`.

## Author

Magdalena Laurisch

Developed as part of the Developer Akademie Backend course.
