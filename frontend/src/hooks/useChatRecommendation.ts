import { useRef, useState, useCallback } from 'react';
import { ChatMessage, ChatStreamEvent } from '@/types/chat';
import { startChatStream } from '@/services/chatService';

export function useChatRecommendation() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const assistantBufferRef = useRef('');
  const abortRef = useRef<AbortController | null>(null);

  const appendMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const start = useCallback((query: string) => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    assistantBufferRef.current = '';
    appendMessage({ role: 'user', content: query });

    const controller = new AbortController();
    abortRef.current = controller;

    startChatStream({ query, conversationId: conversationId || undefined, abortController: controller }, (evt: ChatStreamEvent) => {
      if (evt.type === 'rewrite_start') {
        if (!conversationId && evt.raw?.conversation_id) {
          setConversationId(evt.raw.conversation_id);
        }
      } else if (evt.type === 'assistant_delta') {
        assistantBufferRef.current += evt.delta;
        // 实时更新最后一个 assistant 草稿
        setMessages((prev) => {
          const copy = [...prev];
          // 查看最后是否是 assistant 草稿
            if (copy.length > 0 && copy[copy.length - 1].role === 'assistant' && copy[copy.length - 1].metadata?.draft) {
              copy[copy.length - 1] = { ...copy[copy.length - 1], content: assistantBufferRef.current };
            } else {
              copy.push({ role: 'assistant', content: assistantBufferRef.current, metadata: { draft: true } });
            }
          return copy;
        });
      } else if (evt.type === 'complete') {
    const brief = evt.payload.images_brief || [];
    // 替换最后一个草稿为正式消息，并附加本轮图片
        setMessages((prev) => {
          const copy = [...prev];
          if (copy.length > 0 && copy[copy.length - 1].role === 'assistant' && copy[copy.length - 1].metadata?.draft) {
      copy[copy.length - 1] = { role: 'assistant', content: evt.payload.assistant_text, image_ids: evt.payload.image_ids, images_brief: brief };
          } else {
      copy.push({ role: 'assistant', content: evt.payload.assistant_text, image_ids: evt.payload.image_ids, images_brief: brief });
          }
          return copy;
        });
        setLoading(false);
      } else if (evt.type === 'error') {
        setError(evt.message);
        setLoading(false);
      }
    });
  }, [appendMessage, conversationId]);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setLoading(false);
  }, []);

  return { conversationId, messages, loading, error, start, cancel };
}
