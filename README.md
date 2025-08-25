# Test Convertor backend

## Pre-requisites 
- Ensure you have docker on your machine


Initialize the project and Python virtual environment
```bash
git clone https://github.com/ssuprun89/testConverter
cd ai-lab-api
python3 -m venv .venv
source .venv/bin/activate
pip insall poetry
poetry install
```

Run local development server:
```bash
uvicorn app.main:app --reload
```

## Dockerized version ### 

Docker build:
```bash
docker build -t convert . 
docker run -p 8000:8000 convert
 ```