FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install FFmpeg
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Copy .env 
# COPY .env* ./

# Make port 80 available to the world outside this container
EXPOSE 8080

# Define environment variables (set these in Google Cloud Run)
ENV OPENAI_API_KEY=""
ENV PINECONE_API_KEY=""
ENV MEMORY_INDEX_NAME="chatbot-memory"
ENV MODEL_CHOICE="gpt-4o-mini"


# Run app.py when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]