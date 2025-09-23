# ElevateCRM Runbook

This runbook provides step-by-step instructions for setting up and running the ElevateCRM application locally.

## Prerequisites

- Docker and Docker Compose
- Node.js and npm
- Python and pip

## Local Development

### 1. Clone the Repository
```bash
git clone <repository-url>
cd elevate-crm
```

### 2. Configure Environment Variables
Copy the `.env.example` file to `.env` and fill in the required values.
```bash
cp .env.example .env
```

### 3. Install Dependencies
Install the necessary dependencies for the backend and frontend.

**Backend:**
```bash
pip install -r backend/requirements-complete.txt
```

**Frontend:**
```bash
npm install
```

### 4. Run the Application with Docker Compose
This is the recommended method for running all services together.
```bash
docker-compose up --build
```
The application will be available at `http://localhost:3000`.

## Building for Production

### 1. Build the Frontend
```bash
npm run build
```

### 2. Build the Docker Images
```bash
docker-compose build
```

## Running Tests

### Backend Tests
```bash
pytest backend/tests/
```

### Frontend E2E Tests
```bash
npx playwright test
```

## Seeding Demo Data
To populate the database with demo data, you can run the following command. This is automatically run when starting the application with Docker Compose if the database is empty.
```bash
python backend/manage.py seed-demo
