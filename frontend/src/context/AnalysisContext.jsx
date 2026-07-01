import { createContext, useContext, useState, useCallback } from 'react';
import { resumeService, analysisService } from '@/services/resumeService';

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadAndAnalyze = useCallback(async (file, jobDescription = '') => {
    setIsUploading(true);
    setUploadProgress(0);
    try {
      const uploadResult = await resumeService.uploadResume(file, setUploadProgress);
      setIsUploading(false);
      setIsAnalyzing(true);
      const analysis = await resumeService.analyzeResume(uploadResult.id, jobDescription);
      setCurrentAnalysis(analysis);
      return analysis;
    } finally {
      setIsUploading(false);
      setIsAnalyzing(false);
      setUploadProgress(0);
    }
  }, []);

  const fetchAnalysis = useCallback(async (id) => {
    const analysis = await analysisService.getAnalysis(id);
    setCurrentAnalysis(analysis);
    return analysis;
  }, []);

  const fetchHistory = useCallback(async (page = 1) => {
    const data = await analysisService.getHistory(page);
    setHistory(data.items || []);
    return data;
  }, []);

  const clearCurrentAnalysis = useCallback(() => setCurrentAnalysis(null), []);

  return (
    <AnalysisContext.Provider value={{
      currentAnalysis, history,
      isUploading, isAnalyzing, uploadProgress,
      uploadAndAnalyze, fetchAnalysis, fetchHistory, clearCurrentAnalysis,
    }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error('useAnalysis must be used inside AnalysisProvider');
  return ctx;
}
