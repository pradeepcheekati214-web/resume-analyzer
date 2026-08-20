import { FiPlus, FiTrash2, FiMessageCircle, FiClock } from 'react-icons/fi';
import { formatRelativeTime } from '@/utils/formatters';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import clsx from 'clsx';

function ChatSidebar({
  sessions = [],
  activeId,
  loading,
  onSelect,
  onCreate,
  onDelete,
  resumes = [],
  selectedResumeId,
  onResumeChange,
}) {
  return (
    <aside className="w-64 shrink-0 bg-white border-r border-slate-100 flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-4 border-b border-slate-100">
        <h2 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
          <FiMessageCircle className="w-4 h-4 text-primary-600" />
          AI Resume Chatbot
        </h2>

        {/* Resume picker */}
        <select
          className="input text-xs mb-3"
          value={selectedResumeId}
          onChange={e => onResumeChange(e.target.value)}
        >
          <option value="">-- Select resume --</option>
          {resumes.map(r => (
            <option key={r.id} value={r.id}>{r.file_name}</option>
          ))}
        </select>

        {/* New chat button */}
        <button
          onClick={onCreate}
          disabled={!selectedResumeId || loading}
          className="btn-primary btn-sm w-full"
        >
          {loading ? <LoadingSpinner size="sm" /> : <FiPlus className="w-3.5 h-3.5" />}
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto scrollbar-thin py-2">
        {sessions.length === 0 && !loading && (
          <div className="px-4 py-8 text-center text-slate-400 text-sm">
            No chats yet.<br />Select a resume and start a new chat.
          </div>
        )}

        {sessions.map(session => (
          <div
            key={session.id}
            onClick={() => onSelect(session.id)}
            className={clsx(
              'group flex items-start gap-2 px-4 py-3 cursor-pointer transition-colors',
              activeId === session.id
                ? 'bg-primary-50 border-r-2 border-primary-600'
                : 'hover:bg-slate-50'
            )}
          >
            <FiMessageCircle
              className={clsx(
                'w-4 h-4 mt-0.5 shrink-0',
                activeId === session.id ? 'text-primary-600' : 'text-slate-400'
              )}
            />
            <div className="flex-1 min-w-0">
              <p className={clsx(
                'text-sm font-medium truncate',
                activeId === session.id ? 'text-primary-700' : 'text-slate-700'
              )}>
                {session.title}
              </p>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                <FiClock className="w-3 h-3" />
                {formatRelativeTime(session.updated_at || session.created_at)}
              </p>
              {session.message_count > 0 && (
                <p className="text-xs text-slate-300 mt-0.5">
                  {session.message_count} messages
                </p>
              )}
            </div>

            {/* Delete button */}
            <button
              onClick={e => { e.stopPropagation(); onDelete(session.id); }}
              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-danger-50 text-slate-400 hover:text-danger-500 transition-all shrink-0"
              title="Delete chat"
            >
              <FiTrash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default ChatSidebar;
