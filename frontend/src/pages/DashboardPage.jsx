import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FiFileText, FiTrendingUp, FiAward, FiArrowRight, FiTrash2,
  FiFilter, FiSearch, FiTarget, FiCpu
} from 'react-icons/fi';
import { HiOutlineChartBar, HiOutlineSparkles } from 'react-icons/hi';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';
import { useAnalysis } from '@/context/AnalysisContext';
import { analysisService } from '@/services/resumeService';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import EmptyState from '@/components/common/EmptyState';
import ConfirmModal from '@/components/common/ConfirmModal';
import ATSScoreRing from '@/components/analysis/ATSScoreRing';
import { formatDate, formatRelativeTime, truncate } from '@/utils/formatters';
import { getScoreColor, getScoreLabel, getScoreBgColor } from '@/utils/constants';
import toast from 'react-hot-toast';
import clsx from 'clsx';

const SORT_OPTIONS = [
  { value: 'newest',    label: 'Newest First' },
  { value: 'oldest',    label: 'Oldest First' },
  { value: 'score_asc', label: 'Score: Low → High' },
  { value: 'score_desc',label: 'Score: High → Low' },
];

function DashboardPage() {
  const { fetchHistory } = useAnalysis();
  const [items, setItems]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState('');
  const [sort, setSort]         = useState('newest');
  const [deleteId, setDeleteId] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [page, setPage]         = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const load = (p = 1) => {
    setLoading(true);
    fetchHistory(p)
      .then((data) => {
        setItems(data.items || []);
        setTotalPages(Math.ceil((data.total || 0) / (data.page_size || 10)));
      })
      .catch(() => toast.error('Failed to load history.'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(page); }, [page]);  // eslint-disable-line react-hooks/exhaustive-deps

  // Client-side filter + sort
  const filtered = items
    .filter((i) => i.file_name?.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      if (sort === 'newest')     return new Date(b.created_at) - new Date(a.created_at);
      if (sort === 'oldest')     return new Date(a.created_at) - new Date(b.created_at);
      if (sort === 'score_asc')  return (a.ats_score ?? 0) - (b.ats_score ?? 0);
      if (sort === 'score_desc') return (b.ats_score ?? 0) - (a.ats_score ?? 0);
      return 0;
    });

  const handleDelete = async () => {
    if (!deleteId) return;
    setDeleting(true);
    try {
      await analysisService.deleteAnalysis(deleteId);
      setItems((prev) => prev.filter((i) => i.id !== deleteId));
      toast.success('Analysis deleted.');
    } catch {
      toast.error('Failed to delete analysis.');
    } finally {
      setDeleting(false);
      setDeleteId(null);
    }
  };

  // Stats
  const avgScore   = items.length ? Math.round(items.reduce((s, i) => s + (i.ats_score ?? 0), 0) / items.length) : 0;
  const bestScore  = items.length ? Math.max(...items.map((i) => i.ats_score ?? 0)) : 0;
  const scoreOver60 = items.filter((i) => (i.ats_score ?? 0) >= 60).length;

  // Chart data — last 7 analyses sorted by date
  const chartData = [...items]
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    .slice(-7)
    .map((i) => ({
      name: formatDate(i.created_at, 'MMM d'),
      score: i.ats_score ?? 0,
    }));

  // Score distribution for bar chart
  const distribution = [
    { range: '0-39',  count: items.filter((i) => (i.ats_score ?? 0) < 40).length,  fill: '#ef4444' },
    { range: '40-59', count: items.filter((i) => (i.ats_score ?? 0) >= 40 && (i.ats_score ?? 0) < 60).length, fill: '#f59e0b' },
    { range: '60-79', count: items.filter((i) => (i.ats_score ?? 0) >= 60 && (i.ats_score ?? 0) < 80).length, fill: '#2563eb' },
    { range: '80-100',count: items.filter((i) => (i.ats_score ?? 0) >= 80).length,  fill: '#22c55e' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="section-title">Dashboard</h1>
          <p className="text-slate-500 text-sm mt-0.5">Track your resume optimization progress</p>
        </div>
        <Link to="/home" className="btn-primary btn-sm self-start sm:self-auto">
          + New Analysis
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FiFileText}       label="Total Analyses" value={items.length}   color="bg-primary-50 text-primary-600" />
        <StatCard icon={HiOutlineChartBar} label="Average Score"  value={`${avgScore}%`} color="bg-secondary-50 text-secondary-600" />
        <StatCard icon={FiAward}          label="Best Score"     value={`${bestScore}%`} color="bg-success-50 text-success-600" />
        <StatCard icon={FiTrendingUp}     label="Score ≥ 60%"   value={scoreOver60}    color="bg-warning-50 text-warning-600" />
      </div>

      {/* Charts row */}
      {chartData.length >= 2 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend chart */}
          <div className="card lg:col-span-2">
            <h2 className="font-semibold text-slate-900 mb-4">Score Trend</h2>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#2563eb" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: 12 }}
                  formatter={(v) => [`${v}%`, 'ATS Score']}
                />
                <Area type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2.5} fill="url(#scoreGrad)" dot={{ fill: '#2563eb', r: 4 }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Distribution chart */}
          <div className="card">
            <h2 className="font-semibold text-slate-900 mb-4">Score Distribution</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distribution} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="range" tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: 12 }} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {distribution.map((entry, i) => (
                    <rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* History table */}
      <div className="card">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-5">
          <h2 className="font-semibold text-slate-900">Analysis History</h2>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 sm:w-56">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <input
                type="text" placeholder="Search by filename…"
                value={search} onChange={(e) => setSearch(e.target.value)}
                className="input pl-8 py-2 text-xs"
              />
            </div>
            {/* Sort */}
            <div className="relative">
              <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <select value={sort} onChange={(e) => setSort(e.target.value)}
                className="input pl-8 py-2 text-xs appearance-none pr-8 cursor-pointer">
                {SORT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12"><LoadingSpinner size="lg" /></div>
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={FiFileText}
            title="No analyses yet"
            description="Upload your first resume to see your analysis history here."
            action={<Link to="/home" className="btn-primary">Upload Resume</Link>}
          />
        ) : (
          <>
            <div className="overflow-x-auto -mx-6 scrollbar-thin">
              <table className="w-full text-sm min-w-[640px]">
                <thead>
                  <tr className="border-b border-slate-100">
                    {['Resume', 'ATS Score', 'Skills Found', 'Missing', 'Date', ''].map((h) => (
                      <th key={h} className="text-left text-xs font-semibold text-slate-400 uppercase tracking-wider px-6 py-2 first:pl-6">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {filtered.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
                            <FiFileText className="w-4 h-4 text-primary-500" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-800 text-sm leading-none">
                              {truncate(item.file_name, 30)}
                            </p>
                            <p className="text-xs text-slate-400 mt-0.5">{formatRelativeTime(item.created_at)}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-2">
                          <span className={`text-base font-bold ${getScoreColor(item.ats_score)}`}>
                            {item.ats_score ?? '—'}%
                          </span>
                          <span className={clsx(
                            'badge text-xs hidden sm:inline-flex',
                            item.ats_score >= 80 ? 'badge-green' :
                            item.ats_score >= 60 ? 'badge-blue' :
                            item.ats_score >= 40 ? 'badge-yellow' : 'badge-red'
                          )}>
                            {getScoreLabel(item.ats_score)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3 text-slate-600">{item.skills_count ?? '—'}</td>
                      <td className="px-6 py-3 text-slate-600">{item.missing_count ?? '—'}</td>
                      <td className="px-6 py-3 text-slate-500 text-xs whitespace-nowrap">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Link to={`/analysis/${item.id}`}
                            className="p-1.5 rounded-lg hover:bg-primary-50 text-slate-400 hover:text-primary-600 transition-colors"
                            title="View analysis">
                            <FiArrowRight className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => setDeleteId(item.id)}
                            className="p-1.5 rounded-lg hover:bg-danger-50 text-slate-400 hover:text-danger-500 transition-colors"
                            title="Delete"
                          >
                            <FiTrash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100">
                <p className="text-xs text-slate-400">Page {page} of {totalPages}</p>
                <div className="flex gap-2">
                  <button disabled={page === 1} onClick={() => setPage((p) => p - 1)} className="btn-secondary btn-sm disabled:opacity-40">
                    Previous
                  </button>
                  <button disabled={page === totalPages} onClick={() => setPage((p) => p + 1)} className="btn-secondary btn-sm disabled:opacity-40">
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <ConfirmModal
        isOpen={!!deleteId}
        title="Delete Analysis"
        message="This action cannot be undone. The analysis results will be permanently removed."
        confirmLabel={deleting ? 'Deleting…' : 'Delete'}
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
        danger
      />
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-xs text-slate-500 mt-0.5">{label}</p>
      </div>
    </div>
  );
}

export default DashboardPage;
