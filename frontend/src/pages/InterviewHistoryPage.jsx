import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiTrash2, FiCpu, FiClock } from 'react-icons/fi';
import { interviewService } from '@/services/aiService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import EmptyState from '@/components/common/EmptyState';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import toast from 'react-hot-toast';
import clsx from 'clsx';

export default function InterviewHistoryPage() {
  const [items,   setItems]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [page,    setPage]    = useState(1);
  const [total,   setTotal]   = useState(0);
  const PAGE_SIZE = 10;

  const load = (p) => {
    setLoading(true);
    interviewService.getHistory(p, PAGE_SIZE)
      .then(d => { setItems(d.items || []); setTotal(d.total || 0); })
      .catch(() => toast.error('Failed to load history.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(page); }, [page]);

  const handleDelete = async (id) => {
    await interviewService.delete(id).catch(() => {});
    setItems(prev => prev.filter(i => i.interview_id !== id));
    toast.success('Deleted.');
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="section-title">Interview History</h1>
          <p className="text-slate-500 text-sm mt-0.5">Track your mock interview performance over time.</p>
        </div>
        <Link to="/interview/questions" className="btn-primary btn-sm">
          + New Interview
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
      ) : items.length === 0 ? (
        <EmptyState icon={FiCpu} title="No interview history"
          description="Start your first mock interview to see results here."
          action={<Link to="/interview/questions" className="btn-primary">Start an Interview</Link>} />
      ) : (
        <>
          <div className="card overflow-hidden p-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50">
                  {['Role', 'Score', 'Technical', 'Communication', 'Duration', 'Date', 'Status', ''].map(h => (
                    <th key={h} className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider px-4 py-3">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {items.map(item => {
                  const passed = (item.overall_score || 0) >= 60;
                  return (
                    <tr key={item.id} className="hover:bg-slate-50/60 transition-colors group">
                      <td className="px-4 py-3">
                        <p className="font-medium text-slate-800">{item.job_title || 'General Interview'}</p>
                        <p className="text-xs text-slate-400">{item.total_questions} questions</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={clsx('text-lg font-bold', passed ? 'text-success-600' : 'text-warning-600')}>
                          {Math.round(item.overall_score || 0)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{Math.round(item.technical_score || 0)}%</td>
                      <td className="px-4 py-3 text-slate-600">{Math.round(item.communication_score || 0)}%</td>
                      <td className="px-4 py-3 text-slate-500">
                        {item.duration_minutes ? `${item.duration_minutes}m` : '—'}
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-xs whitespace-nowrap">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <span className={clsx('badge', passed ? 'badge-green' : 'badge-yellow')}>
                          {passed ? 'Passed' : 'Practice'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Link to={`/interview/${item.interview_id}/result`}
                            className="p-1.5 rounded-lg hover:bg-primary-50 text-slate-400 hover:text-primary-600">
                            <FiArrowRight className="w-4 h-4" />
                          </Link>
                          <button onClick={() => handleDelete(item.interview_id)}
                            className="p-1.5 rounded-lg hover:bg-danger-50 text-slate-400 hover:text-danger-500">
                            <FiTrash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-400">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="btn-secondary btn-sm disabled:opacity-40">Previous</button>
                <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)} className="btn-secondary btn-sm disabled:opacity-40">Next</button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
