# Bot Generator Streamlit App

This is a Streamlit-based web application that allows users to generate AI-powered Telegram bots. The app integrates with a FastAPI backend to process knowledge base files and clone voices using 11labs.

## Features
- Upload and process knowledge base files (PDFs, text files, etc.)
- Clone voice samples for personalized bot responses
- Generate and deploy Telegram bots with predefined prompts and configurations
- Integrates with FastAPI backend for processing

## Requirements

Ensure you have the following installed before running the application:
- Python 3.11+
- `pip` package manager
- A running FastAPI backend
- `.env` file with the `BACKEND_URL` variable set

## Installation & Setup

### Clone the repository:
```bash
$ git clone <repository_url>
$ cd <repository_folder>
```

### Install dependencies:
```bash
$ pip install -r requirements.txt
```

### Create a `.env` file:
```bash
$ echo "BACKEND_URL=<your_backend_url>" > .env
```

### Run the application:
```bash
$ streamlit run app.py
```

The app will start at `http://localhost:8501`.

## Running with Docker

You can also deploy the application using Docker.

### Build the Docker image:
```bash
$ docker build -t bot-generator .
```

### Run the container:
```bash
$ docker run -p 8501:8501 --env-file .env bot-generator
```

The application will be available at `http://localhost:8501`.

## API Endpoints Used
- `POST /process_knowledge_base` - Processes uploaded knowledge base files
- `POST /process_voice_clone` - Clones voice samples
- `POST /create_bot` - Generates a new Telegram bot

## License
MIT License

## Author
Developed by [Your Name].