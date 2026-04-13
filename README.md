# Backend System Design Playground

A collection of backend system design implementations, focusing on building scalable and production-like services using modern backend technologies.

## Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Redis

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backend-system-design-playground
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Redis:
```bash
docker-compose up -d redis
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Access the API at:
[http://localhost:8000](http://localhost:8000)

## Project Structure

```
backend-system-design-playground/
├── services/
├── docker/               # Docker configurations
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
└── README.md             # Project documentation
```

## Tech Stack

- **Containerization**: Docker & Docker Compose
- **Testing**: pytest

## Testing

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Docker

Start all services:
```bash
docker-compose up -d
```

Stop all services:
```bash
docker-compose down
```

View logs:
```bash
docker-compose logs -f
```

## Configuration

Create a `.env` file in the project root:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```
