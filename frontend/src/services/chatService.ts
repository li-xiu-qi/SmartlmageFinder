import { ChatStreamEvent, StartChatStreamParams } from '@/types/chat';

const BASE = '/api/v1/ai';

export function startChatStream(
  params: StartChatStreamParams,
  onEvent: (e: ChatStreamEvent) => void
) {
  const { query, conversationId, userId } = params;
  const controller = params.abortController || new AbortController();

  const body = JSON.stringify({
    query,
    conversation_id: conversationId,
    user_id: userId,
    limit: 20,
  });

  const reqId = 'req_' + Date.now();

  fetch(`${BASE}/recommend/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    signal: controller.signal,
  })
    .then(async (resp) => {
      if (!resp.ok || !resp.body) {
        onEvent({ type: 'error', message: '响应异常' });
        return;
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE 基于 \n\n 分段
        let idx;
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const chunk = buffer.slice(0, idx).trim();
          buffer = buffer.slice(idx + 2);
          if (!chunk) continue;
          // 解析 event: 与 data:
          const lines = chunk.split('\n');
          let eventName = '';
          let dataLine = '';
          for (const line of lines) {
            if (line.startsWith('event:')) eventName = line.replace('event:', '').trim();
            else if (line.startsWith('data:')) dataLine += line.slice(5).trim();
            else dataLine += line.trim();
          }
          try {
            const dataObj = dataLine ? JSON.parse(dataLine) : {};
            if (eventName === 'rewrite_start') {
              onEvent({ type: 'rewrite_start', raw: dataObj });
            } else if (eventName === 'assistant_delta') {
              onEvent({ type: 'assistant_delta', delta: dataObj.delta || '' });
            } else if (eventName === 'complete') {
              onEvent({ type: 'complete', payload: dataObj });
            } else if (eventName === 'error') {
              onEvent({ type: 'error', message: dataObj.message || '未知错误' });
            }
          } catch (e) {
            // ignore parse error
          }
        }
      }
    })
    .catch((err) => {
      if (controller.signal.aborted) return;
      onEvent({ type: 'error', message: err.message || '网络错误' });
    });

  return {
    conversationId: conversationId || '',
    requestId: reqId,
    cancel: () => controller.abort(),
  };
}
