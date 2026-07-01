import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  FiArrowLeft, FiRefreshCw, FiDownload, FiUser,
  FiBriefcase, FiCode, FiAlertCircle, FiCheckCircle, FiList
} from 'react-icons/fi';
import { HiOutlineLightBulb, HiOutlineSparkles } from 'react-icons/hi';
import { aiSuggestionService } from '@/services/aiService';
import { analysisService } from '@/services/resumeService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import SkeletonCard from '@/components/common/SkeletonCard';
import CopyButton from '@/components/common/CopyButton';
import EmptyState from '@/components/common/EmptyState';

function SectionCard({ icon: Icon, title, children, color = 'text-primary-600', bg = 'bg-primary-50' }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
        <h3 className="font-semibold text-slate-900">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function AISuggestionsPage() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [suggestion, setSuggestion] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        // Load analysis info
        const a = await analysisService.getAnalysis(analysisId);
        setAnalysis(a);
        // Try to load existing suggestions
        const s = await aiSuggestionService.getByAnalysis(analysisId).catch(() => null);
        if (s) {
          setSuggestion(s);
        } else {
          // Auto-generate on first visit
          const generated = await aiSuggestionService.generate(analysisId);
          setSuggestion(generated);
        }
      } catch (err) {
        toast.error('Failed to load AI suggestions.');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [analysisId]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const s = await aiSuggestionService.generate(analysisId, true);
      setSuggestion(s);
      toast.success('Suggestions regenerated!');
    } catch {
      toast.error('Regeneration failed. Please try again.');
    } finally {
      setRegenerating(false);
    }
  };

  const handleDownload = () => {
    if (!suggestion) return;
    const lines = [
      '============================',
      'AI RESUME IMPROVEMENT REPORT',
      '============================\n',
      suggestion.professional_summary ? `PROFESSIONAL SUMMARY\n${suggestion.professional_summary}\n` : '',
      suggestion.experience_bullets?.length
        ? `IMPROVED EXPERIENCE BULLETS\n${suggestion.experience_bullets.map((b, i) => `${i + 1}. ${b}`).join('\n')}\n`
        : '',
      suggestion.skills_section ? `OPTIMIZED SKILLS SECTION\n${suggestion.skills_section}\n` : '',
      suggestion.missing_skills?.length
        ? `MISSING SKILLS\n${suggestion.missing_skills.map(s => `• ${s}`).join('\n')}\n`
        : '',
      suggestion.formatting_suggestions?.length
        ? `FORMATTING SUGGESTIONS\n${suggestion.formatting_suggestions.map(s => `• ${s}`).join('\n')}\n`
        : '',
      suggestion.industry_recommendations?.length
        ? `INDUSTRY RECOMMENDATIONS\n${suggestion.industry_recommendations.map(r => `• ${r}`).join('\n')}\n`
        : '',
    ].filter(Boolean).join('\n');

    const blob = new Blob([lines], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'ai_resume_suggestions.txt'; a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4 animate-fade-in">
        <div className="flex items-center gap-3 mb-2">
          <div className="skeleton h-4 w-24 rounded" />
        </div>
        <div className="card flex items-center gap-4 p-6 animate-pulse">
          <div className="w-12 h-12 rounded-xl bg-slate-200" />
          <div className="flex-1 space-y-2">
            <div className="h-5 bg-slate-200 rounded w-1/3" />
            <div className="h-3 bg-slate-200 rounded w-1/2" />
          </div>
        </div>
        {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} lines={4} />)}
      </div>
    );
  }

  if (!suggestion || suggestion.status === 'failed') {
    return (
      <EmptyState
        icon={HiOutlineSparkles}
        title="AI Suggestions Unavailable"
        description={suggestion?.error_message || 'Could not generate suggestions. Please try again.'}
        action={
          <button onClick={() => handleRegenerate()} className="btn-primary">
            <FiRefreshCw className="w-4 h-4" /> Try Again
          </button>
        }
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Link to={`/analysis/${analysisId}`}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-primary-600 no-underline">
          <FiArrowLeft className="w-4 h-4" /> Back to Analysis
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">
            Generated {suggestion.generation_count}x • {suggestion.model}
          </span>
          <button onClick={handleRegenerate} disabled={regenerating} className="btn-secondary btn-sm">
            {regenerating ? <LoadingSpinner size="sm" /> : <FiRefreshCw className="w-3.5 h-3.5" />}
            {regenerating ? 'Regenerating…' : 'Regenerate'}
          </button>
          <button onClick={handleDownload} className="btn-secondary btn-sm">
            <FiDownload className="w-3.5 h-3.5" /> Download
          </button>
        </div>
      </div>

      {/* Hero */}
      <div className="card bg-gradient-to-r from-primary-600 to-secondary-600 text-white">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
            <HiOutlineSparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">AI Resume Suggestions</h1>
            <p className="text-primary-100 text-sm mt-0.5">
              Personalized improvements powered by AI to boost your ATS score and land more interviews.
            </p>
          </div>
        </div>
      </div>

      {/* Professional Summary */}
      {suggestion.professional_summary && (
        <SectionCard icon={FiUser} title="Improved Professional Summary" color="text-primary-600" bg="bg-primary-50">
          <p className="text-slate-700 text-sm leading-relaxed bg-primary-50 rounded-lg p-4 border border-primary-100">
            {suggestion.professional_summary}
          </p>
          <div className="mt-3 flex justify-end">
            <CopyButton text={suggestion.professional_summary} label="Copy Summary" />
          </div>
        </SectionCard>
      )}

      {/* Experience Bullets */}
      {suggestion.experience_bullets?.length > 0 && (
        <SectionCard icon={FiBriefcase} title="Improved Experience Bullets" color="text-secondary-600" bg="bg-secondary-50">
          <div className="space-y-2">
            {suggestion.experience_bullets.map((bullet, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100 group">
                <FiCheckCircle className="w-4 h-4 text-success-500 mt-0.5 shrink-0" />
                <p className="text-sm text-slate-700 flex-1">{bullet}</p>
                <CopyButton text={bullet} label="" className="opacity-0 group-hover:opacity-100" />
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Skills Section */}
      {suggestion.skills_section && (
        <SectionCard icon={FiCode} title="Optimized Skills Section" color="text-success-600" bg="bg-success-50">
          <pre className="text-sm text-slate-700 whitespace-pre-wrap font-sans bg-slate-50 p-4 rounded-lg border border-slate-100">
            {suggestion.skills_section}
          </pre>
          <div className="mt-3 flex justify-end">
            <CopyButton text={suggestion.skills_section} label="Copy Skills" />
          </div>
        </SectionCard>
      )}

      {/* Missing Skills */}
      {suggestion.missing_skills?.length > 0 && (
        <SectionCard icon={FiAlertCircle} title="Missing Skills to Add" color="text-warning-600" bg="bg-warning-50">
          <p className="text-sm text-slate-500 mb-3">
            Add these to your resume if you have experience with them.
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestion.missing_skills.map((skill, i) => (
              <span key={i} className="badge-yellow">{skill}</span>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Keyword Improvements */}
      {suggestion.keyword_improvements?.length > 0 && (
        <SectionCard icon={HiOutlineLightBulb} title="Keyword Improvements" color="text-primary-600" bg="bg-primary-50">
          <div className="space-y-3">
            {suggestion.keyword_improvements.map((kw, i) => (
              <div key={i} className="rounded-lg border border-slate-100 overflow-hidden">
                <div className="grid grid-cols-2 divide-x divide-slate-100">
                  <div className="p-3 bg-danger-50">
                    <p className="text-xs font-semibold text-danger-600 mb-1 uppercase tracking-wider">Before</p>
                    <p className="text-sm text-slate-700">{kw.original}</p>
                  </div>
                  <div className="p-3 bg-success-50">
                    <p className="text-xs font-semibold text-success-600 mb-1 uppercase tracking-wider">After</p>
                    <p className="text-sm text-slate-700">{kw.improved}</p>
                  </div>
                </div>
                <div className="px-3 py-2 bg-slate-50 border-t border-slate-100">
                  <p className="text-xs text-slate-500"><span className="font-medium">Why:</span> {kw.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Grammar Corrections */}
      {suggestion.grammar_corrections?.length > 0 && (
        <SectionCard icon={FiCheckCircle} title="Grammar & Style Corrections" color="text-success-600" bg="bg-success-50">
          <div className="space-y-3">
            {suggestion.grammar_corrections.map((g, i) => (
              <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-100 text-sm">
                <div className="flex items-start gap-2 mb-1">
                  <span className="badge-red shrink-0">Before</span>
                  <span className="text-slate-600 line-through">{g.original}</span>
                </div>
                <div className="flex items-start gap-2 mb-1">
                  <span className="badge-green shrink-0">After</span>
                  <span className="text-slate-800 font-medium">{g.corrected}</span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{g.explanation}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* Two column: Formatting + Industry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {suggestion.formatting_suggestions?.length > 0 && (
          <SectionCard icon={FiList} title="Formatting Suggestions" color="text-secondary-600" bg="bg-secondary-50">
            <ul className="space-y-2">
              {suggestion.formatting_suggestions.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="w-5 h-5 bg-secondary-100 text-secondary-700 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">{i+1}</span>
                  {s}
                </li>
              ))}
            </ul>
          </SectionCard>
        )}
        {suggestion.industry_recommendations?.length > 0 && (
          <SectionCard icon={HiOutlineSparkles} title="Industry Recommendations" color="text-primary-600" bg="bg-primary-50">
            <ul className="space-y-2">
              {suggestion.industry_recommendations.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                  <FiCheckCircle className="w-4 h-4 text-primary-500 shrink-0 mt-0.5" />
                  {r}
                </li>
              ))}
            </ul>
          </SectionCard>
        )}
      </div>
    </div>
  );
}

export default AISuggestionsPage;
