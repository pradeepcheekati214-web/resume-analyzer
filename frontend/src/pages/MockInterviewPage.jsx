import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  FiSend, FiClock, FiChevronRight, FiFlag,
  FiCheckCircle, FiAlertCircle, FiZap, FiHelpCircle
} from 'react-icons/fi';
import { HiOutlineLightBulb } from 'react-icons/hi';
import { interviewService } from '@/services/aiService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import DifficultyBadge from '@/components/common/DifficultyBadge';
import ProgressBar from '@/components/common/ProgressBar';

const TIME_LIMIT = 120; // seconds per question

export default function MockInterviewPage() {
  const { interviewId } = useParams();
  const navigate        = useNavigate();

  const [questionData, setQuestionData] = useState(null);
  const [answer,       setAnswer]       = useState('');
  const [evaluation,   setEvaluation]   = useState(null);
  const [submitting,   setSubmitting]   = useState(false);
  const [finishing,    setFinishing]    = useState(false);
  const [loading,      setLoading]      = useState(true);
  const [timeLeft,     setTimeLeft]     = useState(TIME_LIMIT);
  const [timerActive,  setTimerActive]  = useState(false);
  const [startTime,    setStartTime]    = useState(null);
  const [showHint,     setShowHint]     = useState(false);
  const timerRef = useRef(null);

  const loadNextQuestion = useCallback(async () => {
    setLoading(true);
    setEvaluation(null);
    setAnswer('');
    setShowHint(false);
    setTimeLeft(TIME_LIMIT);
    try {
      const data = await interviewService.getNextQuestion(interviewId);
      setQuestionData(data);
      setTimerActive(true);
      setStartTime(Date.now());
    } catch (err) {
      if (err.response?.status === 400) {
        handleFinish();
      } else {
        toast.error('Failed to load question.');
        setLoading(false);
      }
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  useEffect(() => { loadNextQuestion(); }, [loadNextQuestion]);

  // Countdown timer
  useEffect(() => {
    if (!timerActive) { clearInterval(timerRef.current); return; }
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timerRef.current);
          setTimerActive(false);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [timerActive]);

  const handleSubmit = async () => {
    if (!answer.trim()) { toast.error('Please write an answer first.'); return; }
    setTimerActive(false);
    clearInterval(timerRef.current);
    setSubmitting(true);
    const timeTaken = startTime ? Math.round((Date.now() - startTime) / 1000) : 0;
    try {
      const eval_ = await interviewService.submitAnswer({
        interview_id:        interviewId,
        question_index:      questionData.question_index,
        question_text:       questionData.question.question,
        question_category:   questionData.question.category,
        question_difficulty: questionData.question.difficulty,
        answer_text:         answer,
        time_taken_secs:     timeTaken,
      });
      setEvaluation(eval_);
    } catch {
      toast.error('Failed to evaluate answer.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (questionData?.is_last) handleFinish();
    else loadNextQuestion();
  };

  const handleFinish = async () => {
    setFinishing(true);
    try {
      await interviewService.finish(interviewId);
      navigate(`/interview/${interviewId}/result`);
    } catch {
      toast.error('Failed to finish interview.');
      setFinishing(false);
    }
  };

  const fmtTime = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const timerColor = timeLeft > 60 ? 'text-success-600' : timeLeft > 30 ? 'text-warning-600' : 'text-danger-600 animate-pulse';

  if (loading || finishing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <LoadingSpinner size="xl" />
        <p className="text-slate-500 animate-pulse text-sm">
          {finishing ? 'Generating your results…' : 'Loading next question…'}
        </p>
      </div>
    );
  }

  if (!questionData) return null;

  const progress     = (questionData.question_index / questionData.total_questions) * 100;
  const q            = questionData.question;
  const keyPoints    = Array.isArray(q.key_points)          ? q.key_points          : [];
  const followUps    = Array.isArray(q.follow_up_questions)  ? q.follow_up_questions  : [];

  return (
    <div className="max-w-3xl mx-auto space-y-4 animate-fade-in">

      {/* Progress bar + timer */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1.5">
              <p className="text-sm font-medium text-slate-700">
                Question {questionData.question_index + 1} of {questionData.total_questions}
              </p>
              <span className={`flex items-center gap-1.5 font-bold text-lg tabular-nums ${timerColor}`}>
                <FiClock className="w-4 h-4" />
                {fmtTime(timeLeft)}
              </span>
            </div>
            <ProgressBar value={progress} max={100} showValue={false} size="sm" />
          </div>
          <button onClick={handleFinish} className="btn-ghost btn-sm text-danger-600 hover:bg-danger-50 shrink-0">
            <FiFlag className="w-3.5 h-3.5" /> End
          </button>
        </div>
      </div>

      {/* Question card */}
      <div className="card space-y-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="badge-blue capitalize text-xs">
            {(q.category || '').replace('_', ' ')}
          </span>
          <DifficultyBadge difficulty={q.difficulty} />
          {questionData.is_last && <span className="badge-gray text-xs">Last Question</span>}
        </div>

        <h2 className="text-lg font-semibold text-slate-900 leading-relaxed">
          {q.question}
        </h2>

        {/* Hint toggle */}
        {q.tips && !evaluation && (
          <div>
            <button
              onClick={() => setShowHint(v => !v)}
              className="flex items-center gap-1.5 text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              <HiOutlineLightBulb className="w-3.5 h-3.5" />
              {showHint ? 'Hide hint' : 'Show hint'}
            </button>
            {showHint && (
              <div className="mt-2 flex items-start gap-2 p-3 bg-primary-50 rounded-lg border border-primary-100 animate-fade-in">
                <HiOutlineLightBulb className="w-4 h-4 text-primary-600 shrink-0 mt-0.5" />
                <p className="text-sm text-slate-700">{q.tips}</p>
              </div>
            )}
          </div>
        )}

        {/* Key points (shown before answering as optional guide) */}
        {keyPoints.length > 0 && !evaluation && (
          <details className="group">
            <summary className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700 cursor-pointer font-medium select-none">
              <FiZap className="w-3.5 h-3.5 text-warning-500" />
              Key points to cover ({keyPoints.length})
            </summary>
            <div className="mt-2 pl-5 space-y-1">
              {keyPoints.map((pt, i) => (
                <p key={i} className="text-sm text-slate-600 flex items-start gap-1.5">
                  <span className="text-warning-500 shrink-0 font-bold">·</span>{pt}
                </p>
              ))}
            </div>
          </details>
        )}
      </div>

      {/* Answer textarea (only before evaluation) */}
      {!evaluation && (
        <div className="card space-y-3">
          <label className="label">Your Answer</label>
          <textarea
            className="input resize-none text-sm leading-relaxed"
            rows={7}
            placeholder="Type your answer here. Be specific — use examples from your own experience where possible."
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            disabled={submitting}
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-slate-400">{answer.length} characters</p>
            <div className="flex gap-2">
              <button onClick={handleFinish} className="btn-ghost btn-sm">Skip</button>
              <button
                onClick={handleSubmit}
                disabled={submitting || !answer.trim()}
                className="btn-primary"
              >
                {submitting
                  ? <><LoadingSpinner size="sm" /> Evaluating…</>
                  : <><FiSend className="w-4 h-4" /> Submit Answer</>}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Evaluation panel (shown after submission) */}
      {evaluation && (
        <div className="space-y-4 animate-slide-up">

          {/* Score row */}
          <div className="card">
            <h3 className="font-semibold text-slate-900 mb-3">AI Evaluation</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
              {[
                { label: 'Overall',      value: evaluation.score },
                { label: 'Technical',    value: evaluation.technical_accuracy },
                { label: 'Communication',value: evaluation.communication },
                { label: 'Completeness', value: evaluation.completeness },
              ].map(({ label, value }) => {
                const pct   = Math.round(value || 0);
                const color = pct >= 70 ? 'text-success-600' : pct >= 50 ? 'text-warning-600' : 'text-danger-600';
                return (
                  <div key={label} className="text-center p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <p className={`text-2xl font-bold ${color}`}>{pct}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                  </div>
                );
              })}
            </div>

            {/* Feedback */}
            {evaluation.feedback && (
              <div className="p-3 bg-primary-50 rounded-lg border border-primary-100">
                <p className="text-xs font-semibold text-primary-700 uppercase tracking-wider mb-1">Feedback</p>
                <p className="text-sm text-slate-700 leading-relaxed">{evaluation.feedback}</p>
              </div>
            )}
          </div>

          {/* Ideal answer */}
          {evaluation.ideal_answer && (
            <div className="card border-success-200 bg-success-50">
              <div className="flex items-center gap-2 mb-2">
                <FiCheckCircle className="w-4 h-4 text-success-600" />
                <p className="text-sm font-semibold text-success-700">Ideal Answer Covers</p>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">{evaluation.ideal_answer}</p>
            </div>
          )}

          {/* Follow-up questions */}
          {followUps.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <FiHelpCircle className="w-4 h-4 text-secondary-500" />
                <p className="text-sm font-semibold text-slate-700">Possible Follow-up Questions</p>
              </div>
              <ul className="space-y-1.5">
                {followUps.map((fu, i) => (
                  <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                    <span className="text-secondary-400 shrink-0 font-bold">→</span>
                    <span className="italic">{fu}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Keywords */}
          {evaluation.keywords_missed?.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <FiAlertCircle className="w-4 h-4 text-warning-500" />
                <p className="text-sm font-semibold text-slate-700">Keywords You Missed</p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {evaluation.keywords_missed.map((k, i) => (
                  <span key={i} className="badge-yellow">{k}</span>
                ))}
              </div>
            </div>
          )}
          {evaluation.keywords_used?.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <FiCheckCircle className="w-4 h-4 text-success-500" />
                <p className="text-sm font-semibold text-slate-700">Keywords You Used</p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {evaluation.keywords_used.map((k, i) => (
                  <span key={i} className="badge-green">{k}</span>
                ))}
              </div>
            </div>
          )}

          {/* Next button */}
          <button onClick={handleNext} className="btn-primary w-full btn-lg">
            {questionData.is_last
              ? 'Finish Interview & See Results'
              : <><FiChevronRight className="w-4 h-4" /> Next Question</>}
          </button>
        </div>
      )}
    </div>
  );
}
