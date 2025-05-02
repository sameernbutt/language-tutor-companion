import React, { useState } from 'react';
import ChatInterface from './ChatInterface';
import './styles.css';

function App() {
  return (
    <div className="app">
      <h1>AI Language Tutor</h1>
      <ChatInterface />
    </div>
  );
}

export default App;