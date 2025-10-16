# Chat Application - Backend

A Flask-based backend API for the chat application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5050`

## API Endpoints

### POST /api/chat
Send a chat message and receive a response.

**Request Body:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "response": "Bot response",
  "status": "success"
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Customization

The current implementation provides a simple echo response. You can replace the logic in the `/api/chat` endpoint with your own chatbot or AI integration.

