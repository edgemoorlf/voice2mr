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

// Component to render message content with special handling for medical records
const MessageContent = ({ content, role }: { content: string, role: 'user' | 'assistant' }) => {
  // Check if the content looks like a medical record with improved detection
  const isMedicalRecord = role === 'assistant' && (
    content.includes('病历记录') || 
    content.includes('Medical Record') ||
    content.includes('患者信息') || 
    content.includes('主诉') ||
    content.includes('Chief Complaint') ||
    content.includes('现病史') ||
    content.includes('Present Illness') ||
    content.includes('既往史') ||
    content.includes('Past Medical History') ||
    content.includes('过敏史') ||
    content.includes('Allergies') ||
    content.includes('家族史') ||
    content.includes('Family History') ||
    content.includes('体格检查') ||
    content.includes('Physical Examination') ||
    content.includes('辅助检查') ||
    content.includes('Auxiliary Examination') ||
    content.includes('诊断') ||
    content.includes('Diagnosis') ||
    content.includes('处置意见') ||
    content.includes('Treatment Plan') ||
    content.includes('中医辩证') ||
    content.includes('TCM Diagnosis') ||
    content.includes('中药处方') ||
    content.includes('TCM Prescription') ||
    // Look for the new markdown format pattern
    /\*\*[^*]+\*\*\s*：?\s*/.test(content) ||
    // Check for multiple sections with asterisks (fallback for old format)
    (content.match(/\*\s*\*/g) || []).length >= 3
  );

  // Medical record display with support for both old and new formats
  if (isMedicalRecord) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-full">
        <div className="flex items-center mb-3">
          <div className="w-3 h-3 bg-blue-600 rounded-full mr-2"></div>
          <h3 className="font-bold text-blue-800 text-lg">医疗记录 / Medical Record</h3>
        </div>
        <div className="space-y-3 text-gray-700 leading-relaxed">
          {content.split('\n').map((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return null;
            
            // Skip the intro line
            if (trimmedLine.includes('根据您提供的资料') || trimmedLine.includes('我将整理成病历记录')) {
              return (
                <div key={index} className="mb-2 text-blue-700 italic">
                  {trimmedLine}
                </div>
              );
            }
            
            // NEW FORMAT: Check for markdown-style headers: **Section:** or **Section**
            const newFormatMatch = trimmedLine.match(/^\*\*([^*]+)\*\*\s*：?\s*(.*)$/);
            if (newFormatMatch) {
              const sectionName = newFormatMatch[1].trim();
              const sectionContent = newFormatMatch[2].trim();
              
              return (
                <div key={index} className="mb-4">
                  <h4 className="font-semibold text-blue-800 mb-2 border-b border-blue-200 pb-1 text-base">
                    {sectionName}
                  </h4>
                  {sectionContent && (
                    <div className="ml-4 text-gray-700 leading-relaxed">{sectionContent}</div>
                  )}
                </div>
              );
            }
            
            // OLD FORMAT: Check for section headers with pattern: * *section** or * *section：** 
            const oldFormatMatch = trimmedLine.match(/^\*\s*\*([^*]+)\*\*?\s*：?\s*(.*)$/);
            if (oldFormatMatch) {
              const sectionName = oldFormatMatch[1].trim().replace(/：$/, ''); // Remove trailing colon
              const sectionContent = oldFormatMatch[2].trim();
              
              return (
                <div key={index} className="mb-4">
                  <h4 className="font-semibold text-blue-800 mb-2 border-b border-blue-200 pb-1">
                    {sectionName}
                  </h4>
                  {sectionContent && (
                    <div className="ml-4 text-gray-700">{sectionContent}</div>
                  )}
                </div>
              );
            }
            
            // Check if it's a numbered list or bullet point (starts with number or dash)
            if (trimmedLine.match(/^\d+\.\s/) || trimmedLine.startsWith('- ')) {
              return (
                <div key={index} className="ml-8 mb-1 flex">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>{trimmedLine.replace(/^(\d+\.\s*|\-\s*)/, '')}</span>
                </div>
              );
            }
            
            // Check if it's a sub-item (starts with dash but inside a section)
            if (trimmedLine.startsWith('-')) {
              return (
                <div key={index} className="ml-8 mb-1 flex">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>{trimmedLine.substring(1).trim()}</span>
                </div>
              );
            }
            
            // Regular content - check if it's continuation of previous section
            return (
              <div key={index} className="ml-4 mb-1 text-gray-700">
                {trimmedLine}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return <ReactMarkdown>{content}</ReactMarkdown>;
};

export default function Chat({ medicalRecord, dict }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioChunks = useRef<Blob[]>([]);

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
      const requestBody = {
        prompt: content,
        role: 'patient',
        session_id: sessionId,
        medical_records: medicalRecord || '',
        history: messages.filter(m => !['welcome-message', 'initial-assistant-message'].includes(m.id)).map(m => m.content)
      };

      console.log('🚀 SENDING REQUEST TO BACKEND:', requestBody);

      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('📡 BACKEND RESPONSE STATUS:', response.status);
      console.log('📡 BACKEND RESPONSE HEADERS:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to get response from server.' }));
        console.error('❌ BACKEND ERROR RESPONSE:', errorData);
        throw new Error(errorData.detail || 'Failed to get response');
      }

      const data: ChatResponse = await response.json();
      
      console.log('✅ BACKEND SUCCESS RESPONSE:', data);
      console.log('📝 BACKEND CONTENT (first 500 chars):', data.content.substring(0, 500));
      console.log('📝 BACKEND CONTENT (full):', data.content);
      console.log('🔍 CONTENT TYPE CHECK:', {
        includesMedicalRecord: data.content.includes('病历记录'),
        includesDoubleStar: /\*\*[^*]+\*\*/.test(data.content),
        includesSingleStar: /\*\s*\*[^*]+\*\*/.test(data.content),
        contentLength: data.content.length,
        lineCount: data.content.split('\n').length
      });

      setSessionId(data.session_id);

      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('💥 ERROR IN HANDLE MESSAGE:', error);
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
              className={`max-w-[85%] rounded-lg px-4 py-3 break-words ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-50 text-gray-900'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">
                <MessageContent content={message.content} role={message.role} />
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
            autoFocus
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
