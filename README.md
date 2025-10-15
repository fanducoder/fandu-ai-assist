# Chat Application

A full-stack chat application with a React frontend and Flask backend.

## Project Structure

```
genai-capstone-project/
├── backend/          # Flask API server
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
│
└── frontend/         # React application
    ├── public/
    ├── src/
    ├── package.json
    └── README.md
```

## Quick Start

### Backend Setup

1. Navigate to the backend folder:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend folder:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## Features

### Frontend
- Modern dark mode UI with gradient effects
- Real-time chat interface
- Message timestamps
- Typing indicator
- Smooth animations and transitions
- Responsive design for mobile and desktop
- Send messages with Enter key or Send button

### Backend
- RESTful API with Flask
- CORS enabled for frontend communication
- Health check endpoint
- Error handling
- Easy to extend with AI/chatbot logic

## Usage

1. Start both the backend and frontend servers
2. Open your browser to `http://localhost:3000`
3. Type a message in the input field at the bottom
4. Press Enter or click the Send button
5. The message will be sent to the backend API
6. The response will appear in the chat window above

## Customization

You can customize the chat bot logic by modifying the `/api/chat` endpoint in `backend/app.py`. Currently, it echoes the user's message, but you can integrate:
- OpenAI GPT API
- Custom ML models
- Rule-based chatbot logic
- Database integration
- And more!

## Technology Stack

**Frontend:**
- React 18
- CSS3 with custom animations
- Fetch API

**Backend:**
- Python 3
- Flask
- Flask-CORS

## License

MIT

