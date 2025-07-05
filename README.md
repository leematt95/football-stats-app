# football-stats-app

A modern, Dockerized Flask API for managing and querying football player statistics, backed by PostgreSQL and automated database migrations.

---

## 🚀 Features

- RESTful API for CRUD operations on football player data
- PostgreSQL database for persistent storage
- Automated schema migrations using Flask-Migrate
- Dockerized for consistent local development and deployment
- Environment configuration via `.env` file
- Production-ready entrypoint script for seamless startup

---

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Clone & Launch

```bash
git clone <your-repo-url>
cd football-stats-app
docker-compose down --volumes     # Optional: Remove previous data
docker-compose up --build
```

The API will be available at: `http://localhost:5000/api/players/`

---

## 📚 API Endpoints

### Get all players:
```http
GET /api/players/
```

### Add a player:
```http
POST /api/players/
```

#### Example JSON:
```json
{
  "name": "Lionel Messi",
  "position": "Forward",
  "team": "Inter Miami"
}
```

(Add more endpoints as your app evolves!)

---

## ⚙️ Environment Variables

Configure your `.env` file with the following (example values):

```ini
POSTGRES_DB=football_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepass123
FLASK_APP=app.main
FLASK_ENV=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI=postgresql://admin:securepass123@db:5432/football_db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

---

## 📂 Project Structure

```plaintext
football-stats-app/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── player.py
│   └── routes/
│       ├── __init__.py
│       └── players.py
├── migrations/           # Database migrations (auto-generated)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── entrypoint.sh
├── .env
├── .gitignore
└── README.md
```

---

## 🧰 Useful Commands

### Rebuild & reset the database:
```bash
docker-compose down --volumes
docker-compose up --build
```

### View logs:
```bash
docker-compose logs web
docker-compose logs db
```

### Stop all containers:
```bash
docker-compose down
```

---

## 👥 Contributing

1. Fork this repo and clone your fork.
2. Create a new branch for your feature/fix.
3. Commit and push your changes.
4. Open a pull request.

---

## 📝 License

MIT (or specify your preferred license)

---

Made with Flask, Docker, and a passion for football ⚽️