import { useEffect, useRef, useCallback } from 'react';
import { analysisService } from '@/services/resumeService';
import { ANALYSIS_STATUS } from '@/utils/constants';

/**
 * Polls an analysis by ID until its status is completed or failed.
 *
 * @param {string|null} analysisId
 * @param {function} onComplete - called with the final analysis object
 * @param {function} onError    - called on failure
 * @param {number}   interval   - polling interval in ms (default 3000)
 */
function useAnalysisPolling(analysisId, onComplete, onError, interval = 3000) {
  const timerRef = useRef(null);
  const activeRef = useRef(false);

  const stop = useCallback(() => {
    activeRef.current = false;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!analysisId) return;

    activeRef.current = true;

    const poll = async () => {
      if (!activeRef.current) return;
      try {
        const data = await analysisService.getAnalysis(analysisId);
        if (data.status === ANALYSIS_STATUS.COMPLETED) {
          stop();
          onComplete?.(data);
        } else if (data.status === ANALYSIS_STATUS.FAILED) {
          stop();
          onError?.(new Error(data.error_message || 'Analysis failed'));
        } else {
          timerRef.current = setTimeout(poll, interval);
        }
      } catch (err) {
        stop();
        onError?.(err);
      }
    };

    poll();
    return stop;
  }, [analysisId, interval, onComplete, onError, stop]);

  return { stop };
}

export default useAnalysisPolling;
