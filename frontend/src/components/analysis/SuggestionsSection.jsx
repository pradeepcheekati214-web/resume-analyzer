import { useState } from 'react';
import { FiChevronDown, FiChevronUp } from 'react-icons/fi';
import { HiOutlineLightBulb } from 'react-icons/hi';

const PRIORITY_STYLES = {
  high:   { badge: 'badge-red',    dot: 'bg-danger-500',  label: 'High' },
  medium: { badge: 'badge-yellow', dot: 'bg-warning-500', label: 'Medium' },
  low:    { badge: 'badge-green',  dot: 'bg-success-500', label: 'Low' },
};

function SuggestionItem({ suggestion, index }) {
  const [open, setOpen] = useState(false);
  const priority = suggestion.priority?.toLowerCase() || 'medium';
  const style = PRIORITY_STYLES[priority] || PRIORITY_STYLES.medium;

  return (
    <div className="border border-slate-100 rounded-xl overflow-hidden hover:border-primary-200 transition-colors">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-start gap-3 px-4 py-3.5 text-left hover:bg-slate-50 transition-colors"
      >
        <div className={`w-2 h-2 rounded-full ${style.dot} mt-1.5 shrink-0`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-slate-800">
              {suggestion.title || `Suggestion ${index + 1}`}
            </span>
            <span className={style.badge}>{style.label} priority</span>
          </div>
        </div>
        {open
          ? <FiChevronUp className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          : <FiChevronDown className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        }
      </button>

      {open && (
        <div className="px-4 pb-4 pt-1 bg-slate-50 border-t border-slate-100">
          <p className="text-sm text-slate-600 leading-relaxed">{suggestion.description}</p>
          {suggestion.example && (
            <div className="mt-3 p-3 bg-white rounded-lg border border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Example</p>
              <p className="text-sm text-slate-700 italic">"{suggestion.example}"</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function SuggestionsSection({ suggestions }) {
  const safeSuggestions = Array.isArray(suggestions) ? suggestions : [];

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-5">
        <HiOutlineLightBulb className="w-5 h-5 text-primary-600" />
        <h2 className="font-semibold text-slate-900">Improvement Suggestions</h2>
        {safeSuggestions.length > 0 && (
          <span className="badge-blue">{safeSuggestions.length}</span>
        )}
      </div>

      {safeSuggestions.length === 0 ? (
        <p className="text-slate-400 text-sm">No specific suggestions at this time.</p>
      ) : (
        <div className="space-y-2">
          {safeSuggestions.map((s, i) => (
            <SuggestionItem key={i} suggestion={s} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}

export default SuggestionsSection;
