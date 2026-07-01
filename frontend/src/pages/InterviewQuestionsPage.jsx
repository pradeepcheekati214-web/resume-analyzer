import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  FiCode, FiUsers, FiUser, FiFolder, FiCloud,
  FiDatabase, FiCpu, FiLayout, FiChevronDown, FiChevronUp,
  FiPlay, FiRefreshCw, FiCheckCircle, FiHelpCircle, FiZap
} from 'react-icons/fi';
import { HiOutlineLightBulb } from 'react-icons/hi';
import { questionService, interviewService } from '@/services/aiService';
import { resumeService } from '@/services/resumeService';
import DifficultyBadge from '@/components/common/DifficultyBadge';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import SkeletonCard from '@/components/common/SkeletonCard';
import EmptyState from '@/components/common/EmptyState';
import CopyButton from '@/components/common/CopyButton';

// ---------------------------------------------------------------------------
// Category metadata
// ---------------------------------------------------------------------------
const CATEGORY_META = {
  technical_questions:  { label: 'Technical',   icon: FiCode,     color: 'text-primary-600',   bg: 'bg-primary-50'   },
  behavioral_questions: { label: 'Behavioral',  icon: FiUsers,    color: 'text-secondary-600', bg: 'bg-secondary-50' },
  hr_questions:         { label: 'HR',          icon: FiUser,     color: 'text-warning-600',   bg: 'bg-warning-50'   },
  project_questions:    { label: 'Project',     icon: FiFolder,   color: 'text-success-600',   bg: 'bg-success-50'   },
  aws_questions:        { label: 'AWS',         icon: FiCloud,    color: 'text-orange-600',    bg: 'bg-orange-50'    },
  python_questions:     { label: 'Python',      icon: FiCpu,      color: 'text-blue-600',      bg: 'bg-blue-50'      },
  react_questions:      { label: 'React',       icon: FiLayout,   color: 'text-cyan-600',      bg: 'bg-cyan-50'      },
  database_questions:   { label: 'Database',    icon: FiDatabase, color: 'text-purple-600',    bg: 'bg-purple-50'    },
};

// ---------------------------------------------------------------------------
// Individual question accordion
// ---------------------------------------------------------------------------
function QuestionAccordion({ q, index }) {
  const [open, setOpen] = useState(false);
  const keyPoints       = Array.isArray(q.key_points)         ? q.key_points         : [];
  const followUps       = Array.isArray(q.follow_up_questions) ? q.follow_up_questions : [];
  const keywords        = Array.isArray(q.expected_keywords)   ? q.expected_keywords   : [];

  return (
    <div className={`border rounded-xl overflow-hidden transition-colors
      ${open ? 'border-primary-200 shadow-sm' : 'border-slate-100 hover:border-primary-100'}`}>

      {/* Question header — always visible */}
      <button
        className="w-full flex items-start gap-3 px-4 py-3.5 text-left hover:bg-slate-50 transition-colors"
        onClick={() => setOpen(v => !v)}
      >
        <span className="text-xs font-bold text-slate-300 tabular-nums w-6 shrink-0 mt-0.5">
          Q{q.id}
        </span>
        <span className="flex-1 text-sm font-medium text-slate-800 leading-relaxed">
          {q.question}
        </span>
        <DifficultyBadge difficulty={q.difficulty} className="shrink-0 ml-2" />
        {open
          ? <FiChevronUp   className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          : <FiChevronDown className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />}
      </button>

      {/* Expanded content */}
      {open && (
        <div className="border-t border-slate-100 bg-slate-50/60 space-y-4 p-4">

          {/* Tip */}
          {q.tips && (
            <div className="flex items-start gap-2.5 p-3 bg-primary-50 rounded-lg border border-primary-100">
              <HiOutlineLightBulb className="w-4 h-4 text-primary-600 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-semibold text-primary-700 mb-0.5">How to Answer</p>
                <p className="text-sm text-slate-700">{q.tips}</p>
              </div>
            </div>
          )}

          {/* Expected answer */}
          {q.expected_answer && (
            <div className="rounded-lg border border-success-200 bg-success-50 overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 border-b border-success-200">
                <div className="flex items-center gap-1.5">
                  <FiCheckCircle className="w-3.5 h-3.5 text-success-600" />
                  <p className="text-xs font-semibold text-success-700 uppercase tracking-wider">
                    Expected Answer
                  </p>
                </div>
                <CopyButton text={q.expected_answer} label="Copy" className="py-0.5 text-xs" />
              </div>
              <p className="px-3 py-2.5 text-sm text-slate-700 leading-relaxed">
                {q.expected_answer}
              </p>
            </div>
          )}

          {/* Key points */}
          {keyPoints.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <FiZap className="w-3.5 h-3.5 text-warning-500" />
                <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  Key Points to Cover
                </p>
              </div>
              <ul className="space-y-1.5">
                {keyPoints.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                    <span className="w-4 h-4 rounded-full bg-warning-100 text-warning-700 flex items-center
                                     justify-center text-xs font-bold shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {pt}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Follow-up questions */}
          {followUps.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <FiHelpCircle className="w-3.5 h-3.5 text-secondary-500" />
                <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  Possible Follow-ups
                </p>
              </div>
              <ul className="space-y-1.5">
                {followUps.map((fu, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-600 italic">
                    <span className="text-secondary-400 shrink-0">→</span>
                    {fu}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Expected keywords */}
          {keywords.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Keywords to Mention
              </p>
              <div className="flex flex-wrap gap-1.5">
                {keywords.map((kw, i) => (
                  <span key={i} className="badge-blue text-xs">{kw}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Category section (collapsible)
// ---------------------------------------------------------------------------
function CategorySection({ catKey, questions }) {
  const [expanded, setExpanded] = useState(true);
  const meta = CATEGORY_META[catKey] || {
    label: catKey.replace('_questions','').replace('_',' '),
    icon: FiCode, color: 'text-primary-600', bg: 'bg-primary-50',
  };
  const Icon = meta.icon;
  if (!questions?.length) return null;

  const difficulties = questions.reduce((acc, q) => {
    acc[q.difficulty] = (acc[q.difficulty] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="card">
      <button className="w-full flex items-center gap-3 mb-1" onClick={() => setExpanded(v => !v)}>
        <div className={`w-8 h-8 rounded-lg ${meta.bg} flex items-center justify-center shrink-0`}>
          <Icon className={`w-4 h-4 ${meta.color}`} />
        </div>
        <span className="font-semibold text-slate-900 flex-1 text-left">
          {meta.label} Questions
        </span>
        {/* Difficulty pills */}
        <div className="hidden sm:flex items-center gap-1">
          {difficulties.easy   && <span className="badge-green  text-xs">{difficulties.easy}   easy</span>}
          {difficulties.medium && <span className="badge-yellow text-xs">{difficulties.medium} medium</span>}
          {difficulties.hard   && <span className="badge-red    text-xs">{difficulties.hard}   hard</span>}
        </div>
        <span className="badge-blue ml-1">{questions.length}</span>
        {expanded
          ? <FiChevronUp   className="w-4 h-4 text-slate-400 shrink-0" />
          : <FiChevronDown className="w-4 h-4 text-slate-400 shrink-0" />}
      </button>

      {expanded && (
        <div className="mt-3 space-y-2">
          {questions.map((q, i) => <QuestionAccordion key={i} q={q} index={i} />)}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Summary stats bar
// ---------------------------------------------------------------------------
function QuestionSummary({ qs, totalQ, onStart, starting }) {
  const allQuestions = Object.keys(CATEGORY_META).flatMap(k => qs[k] || []);
  const easy   = allQuestions.filter(q => q.difficulty === 'easy').length;
  const medium = allQuestions.filter(q => q.difficulty === 'medium').length;
  const hard   = allQuestions.filter(q => q.difficulty === 'hard').length;

  return (
    <div className="card">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="font-semibold text-slate-900">
            {totalQ} Personalised Questions Ready
          </h2>
          <p className="text-sm text-slate-500 mt-0.5">
            Based on your resume · {qs.job_title || 'Software Engineer'} role
          </p>
          <div className="flex items-center gap-2 mt-2">
            {easy   > 0 && <span className="badge-green  text-xs">{easy}   easy</span>}
            {medium > 0 && <span className="badge-yellow text-xs">{medium} medium</span>}
            {hard   > 0 && <span className="badge-red    text-xs">{hard}   hard</span>}
          </div>
        </div>
        <button onClick={onStart} disabled={starting} className="btn-primary btn-lg shrink-0">
          {starting ? <LoadingSpinner size="sm" /> : <FiPlay className="w-4 h-4" />}
          {starting ? 'Starting…' : `Start Mock Interview (${totalQ} Q)`}
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function InterviewQuestionsPage() {
  const navigate = useNavigate();
  const [resumes,  setResumes]  = useState([]);
  const [qs,       setQs]       = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [starting, setStarting] = useState(false);
  const [form, setForm] = useState({
    resume_id:       '',
    job_title:       '',
    company_name:    '',
    job_description: '',
  });

  useEffect(() => {
    resumeService.listResumes(1, 50)
      .then(d => setResumes(d.items || []))
      .catch(() => {});
  }, []);

  const set = (key, val) => setForm(p => ({ ...p, [key]: val }));

  const generate = async (e) => {
    e.preventDefault();
    if (!form.resume_id) { toast.error('Please select a resume.'); return; }
    setLoading(true);
    setQs(null);
    try {
      const data = await questionService.generate(form);
      setQs(data);
      if (data.status === 'failed') {
        toast.error(data.error_message || 'Generation failed.');
      } else {
        toast.success(`${data.total_questions} tailored questions generated!`);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startInterview = async () => {
    if (!qs) return;
    setStarting(true);
    try {
      const interview = await interviewService.start(qs.id);
      navigate(`/interview/${interview.id}`);
    } catch {
      toast.error('Could not start interview.');
    } finally {
      setStarting(false);
    }
  };

  const totalQ = qs
    ? (qs.total_questions || Object.keys(CATEGORY_META).reduce((n, k) => n + (qs[k]?.length || 0), 0))
    : 0;

  const activeCategories = qs
    ? Object.keys(CATEGORY_META).filter(k => (qs[k]?.length || 0) > 0)
    : [];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">

      {/* Header */}
      <div>
        <h1 className="section-title flex items-center gap-2">
          <FiCpu className="w-6 h-6 text-primary-600" /> AI Interview Question Generator
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Generates questions <strong>only</strong> from your resume skills, projects, and the job description.
          Never asks about technologies you haven't listed.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={generate} className="card space-y-4">
        <h2 className="font-semibold text-slate-900">Generate Questions</h2>

        {/* Row 1: Resume + Job Title */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="label">
              Resume <span className="text-danger-500">*</span>
            </label>
            <select className="input" value={form.resume_id}
              onChange={e => set('resume_id', e.target.value)}>
              <option value="">-- Select a resume --</option>
              {resumes.map(r => (
                <option key={r.id} value={r.id}>{r.file_name}</option>
              ))}
            </select>
            {resumes.length === 0 && (
              <p className="text-xs text-warning-600 mt-1">
                No resumes found — upload one on the Home page first.
              </p>
            )}
          </div>
          <div>
            <label className="label">
              Job Title <span className="text-slate-400">(optional)</span>
            </label>
            <input className="input" placeholder="e.g. Associate Software Engineer"
              value={form.job_title}
              onChange={e => set('job_title', e.target.value)} />
          </div>
        </div>

        {/* Row 2: Company */}
        <div>
          <label className="label">
            Company Name <span className="text-slate-400">(optional — enables company-specific questions)</span>
          </label>
          <input className="input" placeholder="e.g. Accenture, Amazon, Google"
            value={form.company_name}
            onChange={e => set('company_name', e.target.value)} />
          <p className="text-xs text-slate-400 mt-1">
            Supported companies: Accenture, Infosys, TCS, Wipro, Cognizant, Amazon, Google, Microsoft
          </p>
        </div>

        {/* Row 3: JD */}
        <div>
          <label className="label">
            Job Description <span className="text-slate-400">(optional — greatly improves relevance)</span>
          </label>
          <textarea className="input resize-none leading-relaxed" rows={5}
            placeholder="Paste the job description here to generate questions tailored to the exact role requirements…"
            value={form.job_description}
            onChange={e => set('job_description', e.target.value)} />
          {form.job_description.length > 0 && (
            <p className="text-xs text-slate-400 mt-1">{form.job_description.length} chars</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-1">
          <button type="submit" disabled={loading || !form.resume_id} className="btn-primary btn-lg">
            {loading
              ? <><LoadingSpinner size="sm" /> Generating…</>
              : <><FiRefreshCw className="w-4 h-4" /> Generate Questions</>}
          </button>
          {qs && totalQ > 0 && (
            <button type="button" onClick={startInterview} disabled={starting}
              className="btn-secondary btn-lg">
              {starting ? <LoadingSpinner size="sm" /> : <FiPlay className="w-4 h-4" />}
              Start Interview ({totalQ} Q)
            </button>
          )}
        </div>
      </form>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4 animate-pulse">
          {[1, 2, 3].map(i => <SkeletonCard key={i} lines={5} />)}
        </div>
      )}

      {/* Results */}
      {!loading && qs && qs.status === 'completed' && totalQ > 0 && (
        <div className="space-y-4 animate-fade-in">
          <QuestionSummary qs={qs} totalQ={totalQ} onStart={startInterview} starting={starting} />
          {activeCategories.map(catKey => (
            <CategorySection key={catKey} catKey={catKey} questions={qs[catKey]} />
          ))}
        </div>
      )}

      {/* Error state */}
      {!loading && qs && qs.status === 'failed' && (
        <div className="card border-danger-200 text-center py-8">
          <p className="text-danger-600 font-medium">Generation failed</p>
          <p className="text-slate-400 text-sm mt-1">{qs.error_message}</p>
          <button onClick={() => setQs(null)} className="btn-secondary btn-sm mt-4">Try Again</button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !qs && (
        <EmptyState
          icon={FiCpu}
          title="No questions yet"
          description="Select your resume, optionally add a job description, and click Generate Questions."
        />
      )}
    </div>
  );
}
