import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  FiTarget, FiUpload, FiBriefcase, FiTrash2,
  FiArrowRight, FiAlertCircle, FiCheckCircle, FiClock
} from 'react-icons/fi';
import { HiOutlineChartBar } from 'react-icons/hi';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { jobMatchService } from '@/services/aiService';
import { resumeService } from '@/services/resumeService';
import ScoreRing from '@/components/common/ScoreRing';
import ProgressBar from '@/components/common/ProgressBar';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import SkeletonCard, { SkeletonGrid } from '@/components/common/SkeletonCard';
import EmptyState from '@/components/common/EmptyState';
import { formatRelativeTime } from '@/utils/formatters';

export default function JobMatchPage() {
  const [resumes, setResumes]   = useState([]);
  const [history, setHistory]   = useState([]);
  const [result,  setResult]    = useState(null);
  const [loading, setLoading]   = useState(false);
  const [histLoading, setHistLoading] = useState(true);

  const [form, setForm] = useState({
    resume_id: '', job_title: '', company_name: '', job_description: '',
  });

  useEffect(() => {
    resumeService.listResumes(1, 50)
      .then(d => setResumes(d.items || []))
      .catch(() => {});
    jobMatchService.getHistory(1, 5)
      .then(d => setHistory(d.items || []))
      .catch(() => {})
      .finally(() => setHistLoading(false));
  }, []);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!form.resume_id) { toast.error('Please select a resume.'); return; }
    if (form.job_description.trim().length < 50) {
      toast.error('Please provide a job description (min 50 characters).');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const data = await jobMatchService.create(form);
      setResult(data);
      setHistory(prev => [data, ...prev.slice(0, 4)]);
      toast.success('Job match analysis complete!');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    await jobMatchService.delete(id).catch(() => {});
    setHistory(prev => prev.filter(h => h.id !== id));
    if (result?.id === id) setResult(null);
    toast.success('Deleted.');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="section-title flex items-center gap-2">
          <FiTarget className="w-6 h-6 text-primary-600" /> Job Description Match Analyzer
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          See exactly how well your resume matches a job posting — with skills, keywords, and gap analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input form */}
        <form onSubmit={handleAnalyze} className="card space-y-4">
          <h2 className="font-semibold text-slate-900">Analyze a Job Match</h2>

          <div>
            <label className="label">Select Resume</label>
            <select className="input" value={form.resume_id}
              onChange={e => setForm(p => ({ ...p, resume_id: e.target.value }))}>
              <option value="">-- Choose a resume --</option>
              {resumes.map(r => (
                <option key={r.id} value={r.id}>{r.file_name}</option>
              ))}
            </select>
            {resumes.length === 0 && (
              <p className="error-message mt-1">
                No resumes uploaded yet.{' '}
                <Link to="/home" className="text-primary-600">Upload one →</Link>
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Job Title <span className="text-slate-400">(optional)</span></label>
              <input className="input" placeholder="e.g. Senior Engineer"
                value={form.job_title}
                onChange={e => setForm(p => ({ ...p, job_title: e.target.value }))} />
            </div>
            <div>
              <label className="label">Company <span className="text-slate-400">(optional)</span></label>
              <input className="input" placeholder="e.g. Amazon"
                value={form.company_name}
                onChange={e => setForm(p => ({ ...p, company_name: e.target.value }))} />
            </div>
          </div>

          <div>
            <label className="label">Job Description <span className="text-danger-500">*</span></label>
            <textarea className="input resize-none leading-relaxed" rows={8}
              placeholder="Paste the full job description here…"
              value={form.job_description}
              onChange={e => setForm(p => ({ ...p, job_description: e.target.value }))} />
            <p className="text-xs text-slate-400 mt-1">{form.job_description.length} chars (min 50)</p>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full btn-lg">
            {loading ? <><LoadingSpinner size="sm" /> Analyzing…</> : <><FiTarget className="w-4 h-4" /> Analyze Match</>}
          </button>
        </form>

        {/* Result */}
        <div>
          {loading && (
            <div className="space-y-3">
              <div className="card flex items-center justify-center py-12 animate-pulse">
                <div className="text-center space-y-3">
                  <LoadingSpinner size="xl" />
                  <p className="text-slate-500 text-sm">Analyzing match with AI…</p>
                </div>
              </div>
              <SkeletonCard lines={4} />
            </div>
          )}

          {!loading && !result && (
            <EmptyState icon={FiTarget} title="No result yet"
              description="Fill in the form and click Analyze Match to see your results." />
          )}

          {!loading && result && <MatchResult result={result} />}
        </div>
      </div>

      {/* History */}
      {!histLoading && history.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <FiClock className="w-4 h-4 text-primary-600" /> Recent Match Analyses
          </h2>
          <div className="space-y-2">
            {history.map(h => (
              <div key={h.id}
                className="flex items-center gap-4 p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group"
                onClick={() => jobMatchService.getById(h.id).then(setResult).catch(() => toast.error('Load failed'))}>
                <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
                  <FiBriefcase className="w-5 h-5 text-primary-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800">{h.job_title || 'Untitled Role'} {h.company_name ? `@ ${h.company_name}` : ''}</p>
                  <p className="text-xs text-slate-400">{formatRelativeTime(h.created_at)}</p>
                </div>
                <span className={`text-lg font-bold ${h.overall_match >= 70 ? 'text-success-600' : h.overall_match >= 50 ? 'text-primary-600' : 'text-warning-600'}`}>
                  {Math.round(h.overall_match)}%
                </span>
                <button onClick={e => { e.stopPropagation(); handleDelete(h.id); }}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-danger-50 text-slate-400 hover:text-danger-500">
                  <FiTrash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MatchResult({ result }) {
  const radarData = [
    { subject: 'Skills',     value: Math.round(result.skills_match     || 0) },
    { subject: 'Experience', value: Math.round(result.experience_match || 0) },
    { subject: 'Education',  value: Math.round(result.education_match  || 0) },
    { subject: 'Keywords',   value: Math.round(result.keyword_match    || 0) },
    { subject: 'ATS',        value: Math.round(result.ats_compatibility || 0) },
  ];

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Overall score */}
      <div className="card flex items-center gap-6">
        <ScoreRing score={Math.round(result.overall_match)} size={110} label="Match" />
        <div className="flex-1 space-y-3">
          <ProgressBar label="Skills Match"      value={result.skills_match}      size="sm" />
          <ProgressBar label="Experience"        value={result.experience_match}  size="sm" />
          <ProgressBar label="Keywords"          value={result.keyword_match}     size="sm" />
          <ProgressBar label="ATS Compatibility" value={result.ats_compatibility} size="sm" />
        </div>
      </div>

      {/* Radar chart */}
      <div className="card">
        <h3 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
          <HiOutlineChartBar className="w-4 h-4 text-primary-600" /> Match Breakdown
        </h3>
        <ResponsiveContainer width="100%" height={220}>
          <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
            <PolarGrid stroke="#e2e8f0" />
            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <Tooltip formatter={v => [`${v}%`]} contentStyle={{ borderRadius: 8, fontSize: 12 }} />
            <Radar dataKey="value" stroke="#2563eb" fill="#2563eb" fillOpacity={0.2} strokeWidth={2} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Matching / Missing skills */}
      <div className="grid grid-cols-2 gap-4">
        {result.matching_skills?.length > 0 && (
          <div className="card">
            <p className="text-xs font-semibold text-success-600 uppercase tracking-wider mb-2">
              ✓ Matching Skills ({result.matching_skills.length})
            </p>
            <div className="flex flex-wrap gap-1.5">
              {result.matching_skills.map((s, i) => (
                <span key={i} className="badge-green text-xs">{s}</span>
              ))}
            </div>
          </div>
        )}
        {result.missing_skills?.length > 0 && (
          <div className="card">
            <p className="text-xs font-semibold text-danger-600 uppercase tracking-wider mb-2">
              ✗ Missing Skills ({result.missing_skills.length})
            </p>
            <div className="flex flex-wrap gap-1.5">
              {result.missing_skills.map((s, i) => (
                <span key={i} className="badge-red text-xs">{s}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Skill Gap */}
      {result.skill_gap_analysis?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-900 mb-3">Skill Gap Analysis</h3>
          <div className="space-y-2">
            {result.skill_gap_analysis.map((g, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100 text-sm">
                <FiAlertCircle className="w-4 h-4 text-warning-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-slate-800">{g.skill}</p>
                  <p className="text-slate-500">{g.gap}</p>
                  <p className="text-primary-600 text-xs mt-0.5">{g.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {result.recommendations?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-slate-900 mb-3">Recommendations</h3>
          <ul className="space-y-2">
            {result.recommendations.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <FiCheckCircle className="w-4 h-4 text-primary-500 shrink-0 mt-0.5" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
