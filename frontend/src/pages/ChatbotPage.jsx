import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { chatService }  from '@/services/chatService';
import { resumeService } from '@/services/resumeService';
import ChatSidebar from '@/components/chat/ChatSidebar';
import ChatWindow  from '@/components/chat/ChatWindow';
import EmptyState  from '@/components/common/EmptyState';
import { FiMessageCircle, FiUpload } from 'react-icons/fi';
import { Link } from 'react-router-dom';

export default function ChatbotPage() {
  // ── State ──────────────────────────────────────────────────────────────
  const [sessions,          setSessions]          = useState([]);
  const [activeSessionId,   setActiveSessionId]   = useState(null);
  const [messages,          setMessages]          = useState([]);
  const [isLoading,         setIsLoading]         = useState(false);
  const [isSidebarLoading,  setIsSidebarLoading]  = useState(false);
  const [resumes,           setResumes]           = useState([]);
  const [selectedResumeId,  setSelectedResumeId]  = useState('');
  const [activeTitle,       setActiveTitle]       = useState('');
  const [voiceLang,         setVoiceLang]         = useState('en-US');

  // ── Load resumes on mount ─────────────────────────────────────────────
  useEffect(() => {
    resumeService.listResumes(1, 50)
      .then(d => {
        const items = d.items || [];
        setResumes(items);
        if (items.length > 0) setSelectedResumeId(items[0].id);
      })
      .catch(() => {});
    loadSessions();
  }, []);

  // ── Load sessions ─────────────────────────────────────────────────────
  const loadSessions = async () => {
    try {
      const data = await chatService.listSessions();
      setSessions(data.items || []);
    } catch {
      // silent — user may have no sessions yet
    }
  };

  // ── Select a session ──────────────────────────────────────────────────
  const handleSelectSession = useCallback(async (sessionId) => {
    if (sessionId === activeSessionId) return;
    setActiveSessionId(sessionId);
    setMessages([]);
    setIsLoading(true);
    try {
      const data = await chatService.getHistory(sessionId);
      setMessages(data.messages || []);
      setActiveTitle(data.session?.title || '');
    } catch {
      toast.error('Failed to load chat history.');
    } finally {
      setIsLoading(false);
    }
  }, [activeSessionId]);

  // ── Create new session ────────────────────────────────────────────────
  const handleNewSession = async () => {
    if (!selectedResumeId) {
      toast.error('Please select a resume first.');
      return;
    }
    setIsSidebarLoading(true);
    try {
      const resumeName = resumes.find(r => r.id === selectedResumeId)?.file_name || 'Resume';
      const title = `Chat – ${resumeName.replace(/\.[^.]+$/, '').slice(0, 25)}`;
      const session = await chatService.startSession(selectedResumeId, title);

      // Add to sidebar and auto-select
      setSessions(prev => [session, ...prev]);
      setActiveSessionId(session.id);
      setActiveTitle(session.title);
      setMessages([]);

      // Load welcome message
      const history = await chatService.getHistory(session.id);
      setMessages(history.messages || []);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start chat.');
    } finally {
      setIsSidebarLoading(false);
    }
  };

  // ── Delete session ────────────────────────────────────────────────────
  const handleDeleteSession = async (sessionId) => {
    try {
      await chatService.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setMessages([]);
        setActiveTitle('');
      }
      toast.success('Chat deleted.');
    } catch {
      toast.error('Failed to delete chat.');
    }
  };

  // ── Send message ──────────────────────────────────────────────────────
  const handleSendMessage = async (text) => {
    if (!activeSessionId) {
      // Auto-create session if none active
      if (!selectedResumeId) {
        toast.error('Please select a resume and start a new chat first.');
        return;
      }
      await handleNewSession();
      return;
    }

    // Optimistically add user message
    const optimisticId = `opt-${Date.now()}`;
    const optimisticMsg = {
      id:         optimisticId,
      session_id: activeSessionId,
      role:       'user',
      message:    text,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, optimisticMsg]);
    setIsLoading(true);

    try {
      const data = await chatService.sendMessage(activeSessionId, text);

      // Replace optimistic message with real one
      setMessages(prev =>
        prev
          .filter(m => m.id !== optimisticId)
          .concat([data.user_message, data.assistant_message])
      );

      // Update session updated_at in sidebar
      setSessions(prev =>
        prev.map(s =>
          s.id === activeSessionId
            ? { ...s, updated_at: new Date().toISOString() }
            : s
        )
      );
    } catch (err) {
      // Remove optimistic message on failure
      setMessages(prev => prev.filter(m => m.id !== optimisticId));
      toast.error(err.response?.data?.detail || 'Failed to send message.');
    } finally {
      setIsLoading(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className="flex h-[calc(100vh-4rem)] -m-6 overflow-hidden rounded-none bg-slate-50">

      {/* Sidebar */}
      <ChatSidebar
        sessions={sessions}
        activeId={activeSessionId}
        loading={isSidebarLoading}
        onSelect={handleSelectSession}
        onCreate={handleNewSession}
        onDelete={handleDeleteSession}
        resumes={resumes}
        selectedResumeId={selectedResumeId}
        onResumeChange={setSelectedResumeId}
      />

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0">
        {activeSessionId ? (
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            sessionTitle={activeTitle}
            onSend={handleSendMessage}
            voiceLang={voiceLang}
            onVoiceLangChange={setVoiceLang}
          />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <EmptyState
              icon={FiMessageCircle}
              title={
                resumes.length === 0
                  ? 'Upload a resume first'
                  : 'Start a new conversation'
              }
              description={
                resumes.length === 0
                  ? 'Upload your resume to begin chatting with your AI Resume Coach.'
                  : 'Select a resume on the left, then click "New Chat" to start.'
              }
              action={
                resumes.length === 0 ? (
                  <Link to="/home" className="btn-primary no-underline">
                    <FiUpload className="w-4 h-4" /> Upload Resume
                  </Link>
                ) : (
                  <button onClick={handleNewSession} className="btn-primary" disabled={!selectedResumeId}>
                    <FiMessageCircle className="w-4 h-4" /> New Chat
                  </button>
                )
              }
            />
          </div>
        )}
      </div>
    </div>
  );
}
