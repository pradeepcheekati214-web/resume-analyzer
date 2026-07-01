import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiFileText, FiArrowRight, FiClock } from 'react-icons/fi';
import { useAnalysis } from '@/context/AnalysisContext';
import { formatRelativeTime } from '@/utils/formatters';
import { getScoreColor, getScoreLabel } from '@/utils/constants';
import LoadingSpinner from '@/components/common/LoadingSpinner';

function RecentAnalyses() {
  const { fetchHistory } = useAnalysis();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory(1)
      .then((data) => setItems((data.items || []).slice(0, 5)))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [fetchHistory]);

  if (loading) return <div className="flex justify-center py-6"><LoadingSpinner /></div>;
  if (items.length === 0) return null;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-900">Recent Analyses</h2>
        <Link to="/dashboard" className="text-sm text-primary-600 font-medium hover:text-primary-700 flex items-center gap-1">
          View all <FiArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <Link
            key={item.id}
            to={`/analysis/${item.id}`}
            className="card-hover flex items-center gap-4 no-underline p-4"
          >
            <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center shrink-0">
              <FiFileText className="w-5 h-5 text-primary-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-800 truncate">{item.file_name}</p>
              <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
                <FiClock className="w-3 h-3" />
                {formatRelativeTime(item.created_at)}
              </p>
            </div>
            <div className="text-right shrink-0">
              <p className={`text-lg font-bold ${getScoreColor(item.ats_score)}`}>
                {item.ats_score}%
              </p>
              <p className="text-xs text-slate-400">{getScoreLabel(item.ats_score)}</p>
            </div>
            <FiArrowRight className="w-4 h-4 text-slate-300" />
          </Link>
        ))}
      </div>
    </div>
  );
}

export default RecentAnalyses;
