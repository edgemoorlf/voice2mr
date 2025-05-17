'use client'

import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline';
import type { Message, ChatResponse } from '@/types/chat';
import type { Dictionary } from '@/types/dictionary';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

interface ChatProps {
  medicalRecord?: string; // Make medical record optional
  dict: Dictionary;
}

export default function Chat({ medicalRecord, dict }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioChunks = useRef<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message when component mounts
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome-message',
        role: 'assistant',
        content: dict.chat.welcomeMessage,
        timestamp: Date.now(),
      };
      setMessages([welcomeMessage]);
    }
  }, [messages.length, dict.chat.welcomeMessage]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      audioChunks.current = [];

      recorder.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('files', audioBlob, 'voice-input.wav');
        
        setIsLoading(true);
        try {
          const response = await fetch('/api/v2mr', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Failed to process voice input');
          }

          const data = await response.json();
          const transcription = data.content;
          
          // Add transcription as user message and send to chat
          await handleMessage(transcription);
        } catch (error) {
          console.error('Error processing voice:', error);
          toast.error('Failed to process voice input. Please try typing instead.');
        } finally {
          setIsLoading(false);
        }

        // Clean up the media stream
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setIsRecording(true);
      toast.success(dict.chat.recordingStarted);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error(dict.chat.microphoneError);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      setIsRecording(false);
      toast.success(dict.chat.recordingStopped);
    }
  };

  const handleMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: content,
          role: 'patient',
          session_id: sessionId,
          medical_records: medicalRecord || '',
          history: messages.filter(m => !['welcome-message', 'initial-assistant-message'].includes(m.id)).map(m => m.content)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to get response from server.' }));
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data: ChatResponse = await response.json();
      setSessionId(data.session_id);

      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error('Failed to send message. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await handleMessage(input);
  };

  return (
    <div className="flex flex-col bg-white rounded-lg shadow min-h-[500px] max-h-[70vh]">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 break-words ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t sticky bottom-0 bg-white rounded-b-lg">
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            className={`rounded-lg px-3 py-2 ${
              isRecording 
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
          >
            {isRecording ? (
              <StopIcon className="h-5 w-5" />
            ) : (
              <MicrophoneIcon className="h-5 w-5" />
            )}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={dict.chat.inputPlaceholder}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || isRecording}
          />
          <button
            type="submit"
            disabled={isLoading || isRecording || !input.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
} 