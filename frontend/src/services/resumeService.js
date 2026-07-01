import api from './api';

export const resumeService = {
  async uploadResume(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onUploadProgress
        ? (e) => onUploadProgress(Math.round((e.loaded * 100) / e.total))
        : undefined,
    });
    return response.data;
  },

  async analyzeResume(resumeId, jobDescription = '') {
    const response = await api.post(`/resumes/${resumeId}/analyze`, {
      job_description: jobDescription,
    });
    return response.data;
  },

  async getResume(resumeId) {
    const response = await api.get(`/resumes/${resumeId}`);
    return response.data;
  },

  async listResumes(page = 1, pageSize = 10) {
    const response = await api.get('/resumes/', { params: { page, page_size: pageSize } });
    return response.data;
  },

  async deleteResume(resumeId) {
    const response = await api.delete(`/resumes/${resumeId}`);
    return response.data;
  },
};

export const analysisService = {
  async getAnalysis(analysisId) {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  },

  async getHistory(page = 1, pageSize = 10) {
    const response = await api.get('/analysis/history', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async deleteAnalysis(analysisId) {
    const response = await api.delete(`/analysis/${analysisId}`);
    return response.data;
  },
};
