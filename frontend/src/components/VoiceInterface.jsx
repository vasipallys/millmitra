import { useState, useEffect } from 'react';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

export const VoiceInterface = () => {
  const { isListening, transcript, startListening, stopListening } = useVoiceRecognition();
  const [aiResponse, setAiResponse] = useState('');

  const handleVoiceCommand = async (command) => {
    const response = await fetch('/api/ai/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: command, type: 'voice' })
    });
    
    const result = await response.json();
    setAiResponse(result.response);
  };

  return (
    <div className="voice-interface">
      <button 
        onClick={isListening ? stopListening : startListening}
        className={`voice-btn ${isListening ? 'listening' : ''}`}
      >
        🎤 {isListening ? 'Listening...' : 'Speak'}
      </button>
      {transcript && <p>You said: {transcript}</p>}
      {aiResponse && <div className="ai-response">{aiResponse}</div>}
    </div>
  );
};

export default VoiceInterface;