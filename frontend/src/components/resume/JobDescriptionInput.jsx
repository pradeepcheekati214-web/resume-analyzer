import { useState } from 'react';
import { FiBriefcase, FiChevronDown, FiChevronUp } from 'react-icons/fi';

function JobDescriptionInput({ value, onChange, disabled }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-slate-200 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 hover:bg-slate-100 transition-colors"
      >
        <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <FiBriefcase className="w-4 h-4 text-primary-500" />
          <span>Add Job Description</span>
          <span className="badge-blue ml-1">Optional — improves accuracy</span>
        </div>
        {expanded
          ? <FiChevronUp className="w-4 h-4 text-slate-400" />
          : <FiChevronDown className="w-4 h-4 text-slate-400" />
        }
      </button>

      {expanded && (
        <div className="p-4 bg-white">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            rows={5}
            placeholder="Paste the job description here to get targeted keyword matching and role-specific suggestions…"
            className="input resize-none text-sm leading-relaxed"
            aria-label="Job description"
          />
          <p className="text-xs text-slate-400 mt-1.5">
            Providing a job description allows us to check your resume against role-specific keywords.
          </p>
        </div>
      )}
    </div>
  );
}

export default JobDescriptionInput;
