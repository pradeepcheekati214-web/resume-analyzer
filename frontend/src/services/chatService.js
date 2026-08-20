import api from './api';

export const chatService = {
  // ── Sessions ────────────────────────────────────────────────────────────
  async startSession(resumeId, title = 'New Chat') {
    const res = await api.post('/chat/start-session', {
      resume_id: resumeId,
      title,
    });
    return res.data;
  },

  async listSessions() {
    const res = await api.get('/chat/sessions');
    return res.data;  // { items: [], total }
  },

  async deleteSession(sessionId) {
    await api.delete(`/chat/session/${sessionId}`);
  },

  // ── Messages ─────────────────────────────────────────────────────────────
  async sendMessage(sessionId, message) {
    const res = await api.post('/chat/send-message', {
      session_id: sessionId,
      message,
    });
    return res.data;  // { user_message, assistant_message }
  },

  async getHistory(sessionId) {
    const res = await api.get(`/chat/history/${sessionId}`);
    return res.data;  // { session, messages: [] }
  },
};
