# AI Language Tutor & Companion 🌍

An interactive AI-powered language learning application that helps users practice conversations and vocabulary exercises in multiple languages using Mistral 7B.

<https://ai-language-tutor-companion.netlify.app/>

## Features ✨

- **Conversation Mode**: Practice natural conversations with an AI tutor (now with "Start Conversation" button)
- **Exercise Mode**: Vocabulary exercises including translations, multiple choice, and conjugation
- **Multi-Language Support**: Spanish, Urdu, Italian, French, Finnish, German, Swahili, Indonesian, and Icelandic
- **Proficiency Levels**: Novice, Beginner, Intermediate, and Advanced
- **Modern UI**: Clean, responsive interface with dark mode support, auto-scrolling, and auto-focus
- **CEFR-Aligned**: Vocabulary and responses aligned with CEFR proficiency levels

## Tech Stack 🛠️

### Frontend
- React 18
- Axios for API calls
- CSS (Modernized with variables and flexbox)

### Backend
- FastAPI (Python)
- Groq API (Llama 3.1 8B Instant model - free tier)
- CORS enabled for cross-origin requests

## Project Structure 📁

```
ai_language_tutor/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── data/
│   │   └── vocab_by_level.json
│   └── prompts/             # Language-specific tutor prompts
│       ├── spanish_converser.txt
│       ├── spanish_tutor.txt
│       └── ... (other languages)
├── frontend/
│   ├── package.json
│   ├── .env.example         # Frontend env template
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── ChatInterface.js
│       ├── index.js
│       └── styles.css
└── README.md
```

## Prerequisites 📋

- Node.js 16+ and npm
- Python 3.8+
- Groq API key (free - get one at [console.groq.com](https://console.groq.com/))

## Getting Started 🚀

### 1. Clone the Repository

```bash
git clone https://github.com/sameernbutt/language-tutor-companion.git
cd language-tutor-companion
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your Groq API key
# GROQ_API_KEY=your_api_key_here

# Run the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file (optional for local dev)
cp .env.example .env

# For local development, the default API URL is http://localhost:8000

# Run the frontend
npm start
```

The application will be available at `http://localhost:3000`

## Deployment 🌐

This project is deployed on netlify. Link: <https://ai-language-tutor-companion.netlify.app/>

## Environment Variables 🔐

### Backend (.env)
| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (free tier with generous limits) |

### Frontend (.env)
| Variable | Description |
|----------|-------------|
| `REACT_APP_API_URL` | Backend API URL (default: `http://localhost:8000`) |

## API Endpoints 📡

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send a message and get tutor response |
| `/vocab-exercise` | POST | Generate a vocabulary exercise |
| `/grade-exercise` | POST | Grade an exercise submission |
| `/record-progress` | POST | Record user progress |

## Supported Languages 🗣️

| Language | Conversation | Exercises |
|----------|-------------|-----------|
| Spanish | ✅ | ✅ |
| Urdu | ✅ | ✅ |
| Italian | ✅ | ✅ |
| French | ✅ | ✅ |
| Finnish | ✅ | ✅ |
| German | ✅ | ✅ |
| Swahili | ✅ | ✅ |
| Indonesian | ✅ | ✅ |
| Icelandic | ✅ | ✅ |

## Known Limitations ⚠️

1. **Vocabulary data**: Only Spanish has comprehensive vocabulary data in `vocab_by_level.json`. Other languages need vocabulary additions.
2. **Session persistence**: Progress data is stored in memory and resets when the server restarts.
3. **No user authentication**: Currently no user accounts or persistent storage.

## Future Improvements 🔮

- [ ] Add database for persistent storage
- [ ] Implement user authentication
- [ ] Expand vocabulary data for all languages
- [ ] Add speech-to-text and text-to-speech
- [ ] Add progress tracking dashboard

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments 🙏

- [Groq](https://groq.com/) for the free Mixtral-8x7B API
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [React](https://reactjs.org/) for the frontend framework
