import React, { useState } from 'react';

interface Message {
  text: string;
  sender: 'patient' | 'doctor';
}

interface Props {
  onSendMessage: (message: string) => void;
}

const Chatbox: React.FC<Props> = ({ onSendMessage }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = () => {
    if (inputValue.trim() !== '') {
      setMessages((prevMessages) => [...prevMessages, { text: inputValue, sender: 'patient' }]);
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbox">
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender === 'patient' ? 'patient' : 'doctor'}`}>
            {message.text}
          </div>
        ))}
      </div>
      <input
        type="text"
        value={inputValue}
        onChange={(event) => setInputValue(event.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type a message..."
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};

export default Chatbox;