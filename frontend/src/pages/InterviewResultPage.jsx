import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiArrowLeft, FiRepeat, FiCheckCircle, FiAlertCircle, FiTrendingUp } from 'react-icons/fi';
import { interviewService } from '@/services/aiService';
import ScoreRing from '@/components/common/ScoreRing';
import ProgressBar from '@/components/common/ProgressBar';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import DifficultyBadge from '@/components/common/DifficultyBadge';
import { formatDate } from '@/utils/formatters';
import toast from 'react-hot-toast';

export default function InterviewResultPage() {
  const { interviewId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    interviewService.getResult(interviewId)
      .then(setResult)
      .catch(() => toast.error('Failed to load result.'))
      .finally(() => setLoading(false));
  }, [interviewId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  if (!result) return null;

  const passed = (result.overall_score || 0) >= 60;
  const tabs = ['overview', 'answers', 'improvements'];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Nav */}
      <div className="flex items-center justify-between">
        <Link to="/interview/history" className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 no-underline">
          <FiArrowLeft className="w-4 h-4" /> Interview History
        </Link>
        <Link to="/interview/questions" className="btn-secondary btn-sm">
          <FiRepeat className="w-3.5 h-3.5" /> New Interview
        </Link>
      </div>

      {/* Hero */}
      <div className={`card border-2 ${passed ? 'border-success-200 bg-success-50' : 'border-warning-200 bg-warning-50'}`}>
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <ScoreRing score={Math.round(result.overall_score || 0)} size={130}
            label={passed ? 'Passed' : 'Needs Work'} />
          <div className="flex-1 text-center sm:text-left">
            <div className="flex items-center gap-2 justify-center sm:justify-start mb-2">
              <h1 className="text-2xl font-bold text-slate-900">Interview Complete</h1>
              {passed
                ? <span className="badge-green text-sm">Passed</span>
                : <span className="badge-yellow text-sm">Keep Practicing</span>}
            </div>
            <p className="text-slate-600 text-sm">{result.overall_feedback}</p>
            <div className="mt-3 flex flex-wrap gap-4 justify-center sm:justify-start">
              {[
                { label: 'Questions', value: result.answered },
                { label: 'Technical', value: `${Math.round(result.technical_score || 0)}%` },
                { label: 'Communication', value: `${Math.round(result.communication_score || 0)}%` },
                { label: 'Grammar', value: `${Math.round(result.grammar_score || 0)}%` },
              ].map(s => (
                <div key={s.label} className="text-center">
                  <p className="text-lg font-bold text-primary-700">{s.value}</p>
                  <p className="text-xs text-slate-500">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-100 rounded-xl w-fit">
        {tabs.map(t => (
          <button key={t} onClick={() => setActiveTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all
              ${activeTab === t ? 'bg-white text-primary-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}>
            {t}
          </button>
        ))}
      </div>

      {/* Overview tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
          {/* Score breakdown */}
          <div className="card space-y-3">
            <h3 className="font-semibold text-slate-900">Score Breakdown</h3>
            <ProgressBar label="Technical Accuracy" value={result.technical_score || 0} />
            <ProgressBar label="Communication"      value={result.communication_score || 0} />
            <ProgressBar label="Confidence"         value={result.confidence_score || 0} />
            <ProgressBar label="Grammar & Clarity"  value={result.grammar_score || 0} />
          </div>
          {/* Strengths */}
          <div className="space-y-4">
            {result.strengths?.length > 0 && (
              <div className="card">
                <h3 className="font-semibold text-success-700 mb-3 flex items-center gap-2">
                  <FiCheckCircle className="w-4 h-4" /> Strengths
                </h3>
                <ul className="space-y-2">
                  {result.strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <FiCheckCircle className="w-3.5 h-3.5 text-success-500 mt-0.5 shrink-0" />{s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.weaknesses?.length > 0 && (
              <div className="card">
                <h3 className="font-semibold text-warning-700 mb-3 flex items-center gap-2">
                  <FiAlertCircle className="w-4 h-4" /> Areas to Improve
                </h3>
                <ul className="space-y-2">
                  {result.weaknesses.map((w, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <FiAlertCircle className="w-3.5 h-3.5 text-warning-500 mt-0.5 shrink-0" />{w}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Answers tab */}
      {activeTab === 'answers' && (
        <div className="space-y-4 animate-fade-in">
          {(result.answers || []).map((a, i) => (
            <div key={i} className="card space-y-3">
              <div className="flex items-start gap-3">
                <span className="text-sm font-bold text-slate-400 w-6 shrink-0">Q{i + 1}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="badge-blue capitalize text-xs">{a.question_category?.replace('_', ' ')}</span>
                    <DifficultyBadge difficulty={a.question_difficulty} />
                    <span className={`ml-auto text-lg font-bold ${(a.score||0) >= 70 ? 'text-success-600' : (a.score||0) >= 50 ? 'text-warning-600' : 'text-danger-600'}`}>
                      {Math.round(a.score || 0)}%
                    </span>
                  </div>
                  <p className="font-medium text-slate-800 text-sm">{a.question_text}</p>
                </div>
              </div>
              <div className="ml-9 space-y-2">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs font-semibold text-slate-400 uppercase mb-1">Your Answer</p>
                  <p className="text-sm text-slate-700">{a.answer_text}</p>
                </div>
                {a.feedback && (
                  <div className="p-3 bg-primary-50 rounded-lg border border-primary-100">
                    <p className="text-xs font-semibold text-primary-700 uppercase mb-1">Feedback</p>
                    <p className="text-sm text-slate-700">{a.feedback}</p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Improvements tab */}
      {activeTab === 'improvements' && (
        <div className="card animate-fade-in">
          <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <FiTrendingUp className="w-4 h-4 text-primary-600" /> Action Plan
          </h3>
          <ul className="space-y-3">
            {(result.improvements || []).map((imp, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0">
                  {i + 1}
                </span>
                <p className="text-sm text-slate-700">{imp}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
