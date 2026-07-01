import { FiAlertCircle, FiPlus } from 'react-icons/fi';

function MissingKeywords({ keywords }) {
  const safeKeywords = Array.isArray(keywords) ? keywords : [];

  return (
    <div className="card border-l-4 border-warning-500">
      <div className="flex items-center gap-2 mb-4">
        <FiAlertCircle className="w-5 h-5 text-warning-500" />
        <h2 className="font-semibold text-slate-900">Missing Keywords</h2>
        {safeKeywords.length > 0 && (
          <span className="badge-yellow">{safeKeywords.length} missing</span>
        )}
      </div>

      {safeKeywords.length === 0 ? (
        <div className="flex items-center gap-2 text-success-600 text-sm">
          <span className="w-5 h-5 rounded-full bg-success-100 flex items-center justify-center text-xs font-bold">✓</span>
          Great! No critical keywords are missing from your resume.
        </div>
      ) : (
        <>
          <p className="text-sm text-slate-500 mb-3">
            Add these keywords to your resume to improve your ATS score and match job requirements better.
          </p>
          <div className="flex flex-wrap gap-2">
            {safeKeywords.map((kw, i) => (
              <div
                key={`${kw}-${i}`}
                className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium
                           bg-warning-50 text-warning-700 border border-warning-200 cursor-default
                           hover:bg-warning-100 transition-colors group"
              >
                <FiPlus className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                {kw}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default MissingKeywords;
