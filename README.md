# AI Language Tutor & Companion 🌍

An interactive AI-powered language learning application that helps users practice conversations and vocabulary exercises in multiple languages using Mistral 7B.

## Features ✨

- **Conversation Mode**: Practice natural conversations with an AI tutor
- **Exercise Mode**: Vocabulary exercises including translations, multiple choice, and conjugation
- **Multi-Language Support**: Spanish, Urdu, Italian, French, Finnish, German, Swahili, Indonesian, and Icelandic
- **Proficiency Levels**: Novice, Beginner, Intermediate, and Advanced
- **Dark Mode**: Easy on the eyes during late-night study sessions
- **CEFR-Aligned**: Vocabulary and responses aligned with CEFR proficiency levels

## Tech Stack 🛠️

### Frontend
- React 18
- Axios for API calls
- CSS for styling

### Backend
- FastAPI (Python)
- Groq API (Mixtral-8x7B model - free tier)
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

### Backend Deployment (Recommended: Render, Railway, or Heroku)

The backend needs to be deployed to a platform that supports Python/FastAPI. **Note: Netlify does not support Python backends.**

#### Option 1: Render (Recommended - Free Tier Available)

1. Create account at [render.com](https://render.com)
2. Create a new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GROQ_API_KEY`
6. Deploy!

#### Option 2: Railway

1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Set root directory to `backend`
4. Add `GROQ_API_KEY` environment variable
5. Railway auto-detects Python and deploys

#### Option 3: Heroku

1. Create `Procfile` in backend folder:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy via Heroku CLI or GitHub integration

### Frontend Deployment (Netlify)

1. Create account at [netlify.com](https://netlify.com)
2. Click "New site from Git"
3. Connect your GitHub repository
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
5. Add environment variable:
   - `REACT_APP_API_URL` = Your deployed backend URL (e.g., `https://your-backend.onrender.com`)
6. Deploy!

**Important**: Make sure to update `REACT_APP_API_URL` in Netlify's environment variables to point to your deployed backend URL.

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
- [ ] Mobile responsive improvements

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
