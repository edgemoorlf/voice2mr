export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface ChatResponse {
  session_id: string;
  content: string;
  timestamp: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
} 