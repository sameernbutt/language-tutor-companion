// App.js
import React, { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import './styles.css';

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <div className="app">
      <div className="header">
        <h1>AI Language Tutor & Companion</h1>
        <button 
          className="dark-mode-toggle"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
      <ChatInterface darkMode={darkMode} />
    </div>
  );
}

export default App;