FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "project_health.cli", "analyze", "--input", "data/input", "--output", "outputs", "--db", "storage/project_health.sqlite"]
