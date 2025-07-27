FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('punkt', quiet=True);"
COPY models/ /app/models/
COPY src/ /app/
RUN mkdir -p /app/input /app/output
CMD ["python", "main.py"]