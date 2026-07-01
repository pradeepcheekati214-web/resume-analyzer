import api from './api';

// ── AI Resume Suggestions ─────────────────────────────────────────────────
export const aiSuggestionService = {
  async generate(analysisId, regenerate = false) {
    const res = await api.post('/ai/resume-suggestions', { analysis_id: analysisId, regenerate });
    return res.data;
  },
  async getById(suggestionId) {
    const res = await api.get(`/ai/resume-suggestions/${suggestionId}`);
    return res.data;
  },
  async getByAnalysis(analysisId) {
    const res = await api.get(`/ai/resume-suggestions/by-analysis/${analysisId}`);
    return res.data;
  },
};

// ── Job Match ─────────────────────────────────────────────────────────────
export const jobMatchService = {
  async create(payload) {
    const res = await api.post('/ai/job-match', payload);
    return res.data;
  },
  async getById(matchId) {
    const res = await api.get(`/ai/job-match/${matchId}`);
    return res.data;
  },
  async getHistory(page = 1, pageSize = 10) {
    const res = await api.get('/ai/job-match/history', { params: { page, page_size: pageSize } });
    return res.data;
  },
  async delete(matchId) {
    await api.delete(`/ai/job-match/${matchId}`);
  },
};

// ── Interview Questions ───────────────────────────────────────────────────
export const questionService = {
  async generate(payload) {
    // Explicitly map fields so company_name is always included
    const body = {
      resume_id:       payload.resume_id,
      job_title:       payload.job_title       || null,
      company_name:    payload.company_name    || null,
      job_description: payload.job_description || null,
    };
    const res = await api.post('/ai/interview/questions', body);
    return res.data;
  },
  async getById(qsId) {
    const res = await api.get(`/ai/interview/questions/${qsId}`);
    return res.data;
  },
};

// ── Mock Interview ────────────────────────────────────────────────────────
export const interviewService = {
  async start(questionSetId, mode = 'text') {
    const res = await api.post('/ai/interview/start', { question_set_id: questionSetId, mode });
    return res.data;
  },
  async getNextQuestion(interviewId) {
    const res = await api.get(`/ai/interview/${interviewId}/next`);
    return res.data;
  },
  async submitAnswer(payload) {
    const res = await api.post('/ai/interview/answer', payload);
    return res.data;
  },
  async finish(interviewId) {
    const res = await api.post(`/ai/interview/${interviewId}/finish`);
    return res.data;
  },
  async getResult(interviewId) {
    const res = await api.get(`/ai/interview/${interviewId}/result`);
    return res.data;
  },
  async getHistory(page = 1, pageSize = 10) {
    const res = await api.get('/ai/interview/history/list', { params: { page, page_size: pageSize } });
    return res.data;
  },
  async delete(interviewId) {
    await api.delete(`/ai/interview/${interviewId}`);
  },
};
