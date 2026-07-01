import { useState } from 'react';
import { FiCode, FiChevronDown, FiChevronUp } from 'react-icons/fi';

const SKILL_COLORS = ['badge-blue', 'badge-green', 'badge-yellow', 'badge-gray'];

function SkillsSection({ skills }) {
  const safeSkills = Array.isArray(skills) ? skills : [];
  const [expanded, setExpanded] = useState(false);
  const MAX_VISIBLE = 15;
  const visible = expanded ? safeSkills : safeSkills.slice(0, MAX_VISIBLE);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FiCode className="w-5 h-5 text-primary-600" />
          <h2 className="font-semibold text-slate-900">Skills Detected</h2>
          <span className="badge-blue">{safeSkills.length}</span>
        </div>
      </div>

      {safeSkills.length === 0 ? (
        <p className="text-slate-400 text-sm">No skills detected in this resume.</p>
      ) : (
        <>
          <div className="flex flex-wrap gap-2">
            {visible.map((skill, i) => (
              <span key={`${skill}-${i}`} className={SKILL_COLORS[i % SKILL_COLORS.length]}>
                {skill}
              </span>
            ))}
          </div>

          {safeSkills.length > MAX_VISIBLE && (
            <button
              onClick={() => setExpanded((v) => !v)}
              className="mt-3 text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
            >
              {expanded
                ? <><FiChevronUp className="w-3.5 h-3.5" /> Show less</>
                : <><FiChevronDown className="w-3.5 h-3.5" /> Show {safeSkills.length - MAX_VISIBLE} more</>
              }
            </button>
          )}
        </>
      )}
    </div>
  );
}

export default SkillsSection;
