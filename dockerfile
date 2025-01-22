# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies including Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl https://ollama.ai/install.sh | sh

# Copy the requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Download the Mistral model
RUN ollama pull mistral

# Expose the port Streamlit runs on
EXPOSE 8501

# Create a shell script to start both Ollama and Streamlit
RUN echo '#!/bin/bash\nollama serve & sleep 5 && streamlit run app.py --server.address=0.0.0.0' > start.sh
RUN chmod +x start.sh

# Command to run the script
CMD ["./start.sh"]