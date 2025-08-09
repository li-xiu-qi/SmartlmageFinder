/**
 * AI 对话推荐相关类型
 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  image_ids?: number[];
  metadata?: any;
  images_brief?: Array<{ id: number; score?: number; title?: string; tags?: string[]; public_url?: string }>; // 本轮推荐的精简图片
}

export interface ChatStreamCompletePayload {
  request_id: string;
  conversation_id: string;
  image_ids: number[];
  images_brief: Array<{ id: number; score?: number; title?: string; tags?: string[]; public_url?: string }>;
  assistant_text: string;
  total_found: number;
}

export type ChatStreamEvent =
  | { type: 'rewrite_start'; raw: any }
  | { type: 'assistant_delta'; delta: string }
  | { type: 'complete'; payload: ChatStreamCompletePayload }
  | { type: 'error'; message: string };

export interface StartChatStreamParams {
  query: string;
  conversationId?: string;
  userId?: string;
  abortController?: AbortController;
}

export interface ChatStreamHandle {
  conversationId: string;
  requestId: string;
  cancel: () => void;
}
