// ChatInterface.js
import React, { useState } from 'react';
import './styles.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ChatInterface({ darkMode }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [language, setLanguage] = useState('spanish');
  const [level, setLevel] = useState('novice');
  const [isLoading, setIsLoading] = useState(false);
  const [activeExercise, setActiveExercise] = useState(null);
  const [progress, setProgress] = useState({
    totalSessions: 0,
    averageScore: 0,
    vocabularyMastered: 0,
  });
  const [enableFeedback, setEnableFeedback] = useState(true);
  const [mode, setMode] = useState('conversation');

  const updateProgress = (isCorrect) => {
    const score = isCorrect ? 100 : 50;
    setProgress(prev => ({
      ...prev,
      totalSessions: prev.totalSessions + 1,
      averageScore: Math.round((prev.averageScore * prev.totalSessions + score) / (prev.totalSessions + 1)),
      vocabularyMastered: prev.vocabularyMastered + (isCorrect ? 1 : 0),
    }));
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = { text: inputText, sender: 'user' };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    const payload = {
      text: inputText,
      language,
      level,
      is_exercise: mode === 'exercise',
      enable_feedback: enableFeedback,
      target_answers: mode === 'exercise' && activeExercise ? activeExercise.target : []
    };

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, sender: 'tutor' }]);

      if (data.feedback?.is_correct !== undefined) {
        updateProgress(data.feedback.is_correct);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
      setActiveExercise(null);
    }
  };

  const handleStartConversation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: '',
          language,
          level,
          is_exercise: false,
          enable_feedback: false,
          start_conversation: true
        })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, sender: 'tutor' }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetExercise = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/vocab-exercise`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, level })
      });
      const data = await response.json();
      setActiveExercise(data);
      setMessages(prev => [...prev, {
        text: data.content,
        sender: 'exercise',
        exerciseType: data.type,
        instructions: data.instructions,
        target: data.target
      }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`chat-container ${darkMode ? 'dark' : ''}`}>
      <div className={`mode-toggle ${darkMode ? 'dark' : ''}`}>
        <button
          onClick={() => setMode('conversation')}
          className={mode === 'conversation' ? 'active' : ''}
        >
          Conversation
        </button>
        <button
          onClick={() => setMode('exercise')}
          className={mode === 'exercise' ? 'active' : ''}
        >
          Exercises
        </button>
      </div>

      <div className={`controls ${darkMode ? 'dark' : ''}`}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="spanish">Spanish</option>
          <option value="urdu">Urdu</option>
          <option value="italian">Italian</option>
          <option value="french">French</option>
          <option value="finnish">Finnish</option>
          <option value="german">German</option>
          <option value="swahili">Swahili</option>
          <option value="indonesian">Indonesian</option>
          <option value="icelandic">Icelandic</option>
        </select>
        <select value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="novice">Novice</option>
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
        {mode === 'conversation' && (
          <button onClick={handleStartConversation} disabled={isLoading}>
            Start Conversation
          </button>
        )}
        {mode === 'exercise' && (
          <button onClick={handleGetExercise} disabled={isLoading || activeExercise}>
            Get Exercise
          </button>
        )}
      </div>

      <div className={`messages ${darkMode ? 'dark' : ''}`}>
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender} ${darkMode ? 'dark' : ''}`}>
            {msg.sender === 'exercise' && (
              <div className="exercise-header">
                <span className="exercise-badge">{msg.exerciseType}</span>
              </div>
            )}
            {msg.instructions && (
              <div className="exercise-instructions">{msg.instructions}</div>
            )}
            <div className="message-content">{msg.text}</div>
            {msg.feedback && msg.feedback.is_correct !== undefined && (
              <div className="score-badge">
                {msg.feedback.is_correct ? "✅ Correct!" : "❌ Try again!"}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className={`message tutor ${darkMode ? 'dark' : ''}`}>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <div className={`input-area ${darkMode ? 'dark' : ''}`}>
        <input
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder={
            mode === 'exercise' && activeExercise
              ? "Type your answer..."
              : "Type a message..."
          }
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !inputText.trim()}>
          {mode === 'exercise' && activeExercise ? "Submit" : "Send"}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;