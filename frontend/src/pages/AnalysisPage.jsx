import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';import { FiArrowLeft, FiDownload, FiRefreshCw } from 'react-icons/fi';
import { HiOutlineSparkles } from 'react-icons/hi';
import toast from 'react-hot-toast';
import { useAnalysis } from '@/context/AnalysisContext';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ATSScoreRing from '@/components/analysis/ATSScoreRing';
import ScoreBreakdown from '@/components/analysis/ScoreBreakdown';
import SkillsSection from '@/components/analysis/SkillsSection';
import MissingKeywords from '@/components/analysis/MissingKeywords';
import SuggestionsSection from '@/components/analysis/SuggestionsSection';
import ResumeMetaCard from '@/components/analysis/ResumeMetaCard';
import { formatDate } from '@/utils/formatters';
import { getScoreLabel, getScoreBgColor } from '@/utils/constants';

function AnalysisPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { fetchAnalysis } = useAnalysis();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchAnalysis(id)
      .then(setAnalysis)
      .catch(() => setError('Analysis not found or could not be loaded.'))
      .finally(() => setLoading(false));
  }, [id, fetchAnalysis]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <LoadingSpinner size="xl" />
        <p className="text-slate-500 text-sm animate-pulse">Loading analysis results…</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
        <p className="text-danger-600 font-medium">{error || 'Something went wrong.'}</p>
        <button onClick={() => navigate('/home')} className="btn-primary">Go Home</button>
      </div>
    );
  }

  const score = analysis.ats_score ?? 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Breadcrumb / back */}
      <div className="flex items-center justify-between">
        <Link
          to="/home"
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 no-underline transition-colors"
        >
          <FiArrowLeft className="w-4 h-4" /> Back to Upload
        </Link>
        <p className="text-xs text-slate-400">
          Analyzed {formatDate(analysis.created_at, 'MMM d, yyyy · h:mm a')}
        </p>
      </div>

      {/* Header card */}
      <div className={`card border-2 ${getScoreBgColor(score)}`}>
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
          <ATSScoreRing score={score} size={140} />
          <div className="flex-1 text-center sm:text-left">
            <div className="flex items-center gap-2 justify-center sm:justify-start mb-1">
              <h1 className="text-2xl font-bold text-slate-900">ATS Score</h1>
              <span className={`badge ${score >= 80 ? 'badge-green' : score >= 60 ? 'badge-blue' : score >= 40 ? 'badge-yellow' : 'badge-red'}`}>
                {getScoreLabel(score)}
              </span>
            </div>
            <p className="text-slate-600 text-sm max-w-md">
              {score >= 80
                ? 'Your resume is highly optimised for ATS systems. Great work!'
                : score >= 60
                ? 'Your resume passes most ATS filters. A few tweaks will push it higher.'
                : score >= 40
                ? 'Your resume needs improvement to reliably pass ATS screening.'
                : 'Your resume requires significant work to pass ATS systems.'}
            </p>

            <div className="mt-4 flex flex-wrap gap-4 justify-center sm:justify-start text-sm">
              <Stat label="Skills Found"   value={analysis.skills_found?.length ?? 0} />
              <Stat label="Missing Skills" value={analysis.missing_skills?.length ?? 0} color="text-danger-600" />
              <Stat label="Suggestions"    value={analysis.suggestions?.length ?? 0} color="text-warning-600" />
              <Stat label="Keywords"       value={analysis.keywords_matched ?? 0} />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 shrink-0">
            <Link to={`/ai/suggestions/${id}`} className="btn-primary btn-sm no-underline">
              <HiOutlineSparkles className="w-3.5 h-3.5" /> AI Suggestions
            </Link>
            <Link to="/job-match" className="btn-secondary btn-sm no-underline">
              <FiRefreshCw className="w-3.5 h-3.5" /> Job Match
            </Link>
            <Link to="/interview/questions" className="btn-secondary btn-sm no-underline">
              Interview Prep
            </Link>
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column — 2/3 */}
        <div className="lg:col-span-2 space-y-6">
          <ScoreBreakdown breakdown={analysis.score_breakdown} />
          <SkillsSection skills={analysis.skills_found ?? []} />
          <MissingKeywords keywords={analysis.missing_skills ?? []} />
          <SuggestionsSection suggestions={analysis.suggestions ?? []} />
        </div>

        {/* Right column — 1/3 */}
        <div className="space-y-6">
          <ResumeMetaCard analysis={analysis} />
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color = 'text-primary-700' }) {
  return (
    <div className="text-center">
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}

export default AnalysisPage;
