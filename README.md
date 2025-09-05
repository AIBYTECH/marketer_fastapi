# Marketer - Digital Marketing Assistant

A FastAPI-based chatbot application that provides digital marketing assistance using Groq's LLM API. This application features a modern web interface with chat history management and real-time messaging.

## Features

- 🤖 AI-powered digital marketing assistant
- 💬 Real-time chat interface
- 📚 Chat history management
- 🎨 Modern, responsive UI
- 🔄 Multiple chat sessions
- ⚡ Fast API backend with FastAPI

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI**: LangChain with Groq API
- **Styling**: Custom CSS with Font Awesome icons

## Prerequisites

- Python 3.8 or higher
- Groq API key (get one from [Groq Console](https://console.groq.com/))

## Installation

1. **Clone or download the project**
   ```bash
   cd marketer_fast
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `env.example` to `.env`
   - Add your Groq API key to the `.env` file:
   ```
   API_KEY=your_actual_groq_api_key_here
   ```

## Running the Application

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000` to access the application.

## API Endpoints

- `GET /` - Serves the main web interface
- `POST /api/chat` - Send a message and get AI response
- `GET /api/chat/{chat_id}` - Get chat history by ID
- `GET /api/chats` - List all chat sessions
- `POST /api/chat/new` - Create a new chat session

## Usage

1. **Start a conversation**: Type your digital marketing questions in the input field
2. **Create new chats**: Click the "New Chat" button to start fresh conversations
3. **View chat history**: Access previous conversations from the sidebar
4. **Switch between chats**: Click on any chat in the history to resume that conversation

## Project Structure

```
marketer_fast/
├── main.py              # FastAPI backend application
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── README.md           # This file
└── static/             # Frontend files
    ├── index.html      # Main HTML page
    ├── style.css       # CSS styling
    └── script.js       # JavaScript functionality
```

## Configuration

The application uses the following environment variables:

- `API_KEY`: Your Groq API key (required)

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment

For production deployment, consider:

1. Using a production ASGI server like Gunicorn with Uvicorn workers
2. Setting up proper environment variable management
3. Implementing database storage for chat histories
4. Adding authentication and user management
5. Setting up proper logging and monitoring

## Troubleshooting

- **API Key Error**: Make sure your Groq API key is correctly set in the `.env` file
- **Port Already in Use**: Change the port in `main.py` or kill the process using port 8000
- **Module Not Found**: Ensure all dependencies are installed and the virtual environment is activated

## License

This project is open source and available under the MIT License.
