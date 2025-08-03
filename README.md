# ⚽ Football Stats Platform

A comprehensive, enterprise-grade application platform for Premier League player statistics with real-time data integration, advanced analytics, and professional British English terminology. Built with RESTful API architecture and modern web interfaces.

---

## 🌟 Features

- **Real-time Premier League Data**: 562+ players with 2024 season statistics from Understat API
- **Advanced Analytics**: Expected Goals (xG), Expected Assists (xA), and comprehensive performance metrics
- **RESTful API Design**: Professional endpoints with search, filtering, and pagination
- **British English Terminology**: Authentic UK football language ("Club", "Matches", "Goalkeeper")
- **Enterprise Architecture**: Docker containerization, PostgreSQL database, automated testing
- **Production Ready**: OpenShift deployment manifests, health checks, and monitoring

---

## � Quick Start

### Prerequisites

- [Docker](https://www.docker.com/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/) (2.0+)

### Launch the Application

```bash
git clone https://github.com/yourusername/football-stats-app.git
cd football-stats-app
docker-compose up --build
```

The API will be available at: `http://localhost:5000`

### Sample API Calls

```bash
# Get all players (with limit)
curl "http://localhost:5000/api/players/?limit=5"

# Search for players by name
curl "http://localhost:5000/api/players/?name=Haaland"

# Get specific player by ID
curl "http://localhost:5000/api/players/1"

# Pretty-print JSON response
curl "http://localhost:5000/api/players/?limit=2" | python3 -m json.tool
```

**Sample Response:**
```json
{
  "ID": 1,
  "Name": "Mohamed Salah",
  "Position": "Forward / Midfielder", 
  "Club": "Liverpool",
  "Goals": 29,
  "Assists": 18,
  "Matches": 38,
  "Minutes": 3392,
  "Expected_Goals": 27.71,
  "Expected_Assists": 15.86,
  "Shots": 130,
  "Key_Passes": 89,
  "Yellow_Cards": 1,
  "Red_Cards": 0,
  "Last_Updated": "2025-07-30T05:43:36.035986"
}
```

---

## 📊 Data Fields

### Player Statistics
- **Basic Info**: Name, Position (expanded from abbreviations), Club
- **Performance**: Goals, Assists, Matches, Minutes played
- **Advanced Metrics**: Expected Goals (xG), Expected Assists (xA)
- **Game Actions**: Shots, Key Passes
- **Discipline**: Yellow Cards, Red Cards
- **Metadata**: Last Updated timestamp

### Position Mapping
- `GK` → `Goalkeeper`
- `D` → `Defender`
- `M` → `Midfielder` 
- `F` → `Forward`
- Multiple positions shown as `Forward / Midfielder`

---

## 🏗️ Project Structure

```plaintext
football-stats-app/
├── app/                          # Flask application
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── player.py             # Enhanced player model (15 fields)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── players.py            # API endpoints with search
│   └── templates/
│       └── search.html           # Web interface
├── scripts/                      # Utility scripts
│   ├── demo_shell_escaping.sh
│   ├── lint.sh
│   └── run_api_tests.sh
├── docs/                         # Documentation
├── import_players.py             # Data import from Understat API
├── debug_api_data.py             # API debugging tools
├── test_api_pytest.py            # Comprehensive test suite
├── test_api_runtime.py           # Runtime validation tests
├── docker-compose.yml            # Multi-container setup
├── dockerfile                    # Container definition with curl
├── openshift-deployment.yaml     # Enterprise deployment
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── mypy.ini                     # Type checking
├── entrypoint.sh                # Container startup script
├── .env                         # Environment variables
└── README.md
```

---

## 🔧 Environment Variables

Create a `.env` file with the following configuration:

```bash
# Database Configuration
POSTGRES_DB=football_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=securepass123
DB_HOST=db
DB_PORT=5432

# Flask Configuration
FLASK_APP=app.main
FLASK_ENV=development
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
SECRET_KEY=your-secret-key-here

# Data Source Configuration
LEAGUE=epl
SEASON=2024

# Optional: Full database URL
DATABASE_URL=postgresql://admin:securepass123@db:5432/football_db
```

---

## 🧪 Testing & Quality Assurance

### Run the Test Suite
```bash
# Run all tests
docker-compose exec web python -m pytest test_api_pytest.py -v

# Run with coverage
docker-compose exec web python -m pytest test_api_pytest.py --cov=app

# Runtime validation tests
docker-compose exec web python test_api_runtime.py
```

### Code Quality Tools
```bash
# Run linting
./scripts/lint.sh

# Type checking with mypy
docker-compose exec web mypy app/

# Shell script validation  
./scripts/demo_shell_escaping.sh
```

### Test Coverage
- **30+ comprehensive tests** covering all endpoints
- **83.3% success rate** with performance benchmarking
- **Error handling validation** (404s, malformed requests)
- **Data integrity checks** (JSON structure, field validation)

---

## 📡 API Endpoints

### Player Operations

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/api/players/` | Get all players | `?limit=N`, `?name=search` |
| `GET` | `/api/players/<id>` | Get specific player | Player ID |
| `GET` | `/` | Web search interface | Browser access |

### Query Parameters
- **`limit`**: Number of results to return (e.g., `?limit=10`)
- **`name`**: Search by player name (e.g., `?name=Salah`)

### Response Codes
- **200**: Success
- **404**: Player not found
- **500**: Server error

---

## 🚀 Deployment

### Local Development
```bash
docker-compose up --build
```

### Production (OpenShift)
```bash
kubectl apply -f openshift-deployment.yaml
```

### Container Management
```bash
# View logs
docker-compose logs web -f

# Restart services
docker-compose restart web

# Reset database
docker-compose down --volumes && docker-compose up --build

# Execute commands in container
docker-compose exec web python import_players.py
```

---

## 🔄 Data Management

### Import Latest Player Data
```bash
docker-compose exec web python import_players.py
```

### Database Operations
```bash
# Access PostgreSQL
docker-compose exec db psql -U admin -d football_db

# View table structure
docker-compose exec db psql -U admin -d football_db -c "\d players"

# Check player count
docker-compose exec web python -c "
from app.models.player import Player, db
from app.main import app
with app.app_context():
    print(f'Total players: {Player.query.count()}')
"
```

---

## 🏆 Premier League Data

- **562 current players** from 2024 season
- **Real-time statistics** from Understat API
- **20 Premier League clubs** represented
- **Advanced metrics** including xG and xA
- **Professional data quality** with validation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`./scripts/run_api_tests.sh`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## � License

MIT License - see LICENSE file for details

---

**Built with Flask, PostgreSQL, Docker and a passion for Premier League football** ⚽🇬🇧