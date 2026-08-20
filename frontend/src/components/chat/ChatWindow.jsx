import { useEffect, useRef, useState } from 'react';
import { FiSend, FiVolume2, FiVolumeX, FiUser } from 'react-icons/fi';
import { HiOutlineSparkles } from 'react-icons/hi';
import ReactMarkdown from 'react-markdown';
import clsx from 'clsx';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import VoiceAssistant from '@/components/chat/VoiceAssistant';
import { formatDate } from '@/utils/formatters';

// Quick-reply suggestion chips
const QUICK_SUGGESTIONS = [
  'How can I improve my resume?',
  'What skills am I missing?',
  'Rewrite my professional summary',
  'Suggest projects for my skill set',
  'Generate interview questions',
  'Explain my ATS score',
  'Suggest career paths',
];

function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 mb-4">
      <div className="w-7 h-7 rounded-full bg-primary-600 flex items-center justify-center shrink-0">
        <HiOutlineSparkles className="w-4 h-4 text-white" />
      </div>
      <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="w-2 h-2 rounded-full bg-primary-400 animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ msg, onSpeak, onStopSpeak, isSpeaking, speakingMsgId }) {
  const isUser = msg.role === 'user';
  const isThisSpeaking = isSpeaking && speakingMsgId === msg.id;

  return (
    <div className={clsx('flex items-end gap-2 mb-4 group', isUser && 'flex-row-reverse')}>
      {/* Avatar */}
      <div className={clsx(
        'w-7 h-7 rounded-full flex items-center justify-center shrink-0 mb-1',
        isUser ? 'bg-slate-200' : 'bg-primary-600'
      )}>
        {isUser
          ? <FiUser className="w-3.5 h-3.5 text-slate-500" />
          : <HiOutlineSparkles className="w-4 h-4 text-white" />
        }
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[78%] px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed',
        isUser
          ? 'bg-primary-600 text-white rounded-br-none'
          : 'bg-white border border-slate-100 text-slate-800 rounded-bl-none'
      )}>
        {isUser ? (
          <p className="whitespace-pre-wrap">{msg.message}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5">
            <ReactMarkdown>{msg.message}</ReactMarkdown>
          </div>
        )}

        {/* Timestamp + speak button */}
        <div className={clsx(
          'flex items-center gap-2 mt-1.5',
          isUser ? 'justify-start' : 'justify-between'
        )}>
          <span className={clsx('text-xs', isUser ? 'text-primary-200' : 'text-slate-400')}>
            {formatDate(msg.created_at, 'h:mm a')}
          </span>

          {!isUser && (
            <button
              onClick={() => isThisSpeaking ? onStopSpeak() : onSpeak(msg.id, msg.message)}
              className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-primary-600 transition-all"
              title={isThisSpeaking ? 'Stop' : 'Listen'}
            >
              {isThisSpeaking
                ? <FiVolumeX className="w-3.5 h-3.5" />
                : <FiVolume2 className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ChatWindow({
  messages     = [],
  isLoading    = false,
  sessionTitle = '',
  onSend,
  voiceLang,
  onVoiceLangChange,
}) {
  const [input,  setInput]  = useState('');
  const [speakingMsgId, setSpeakingMsgId] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const bottomRef   = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');
    onSend(text);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceResult = (transcript) => {
    if (transcript.trim()) onSend(transcript.trim());
  };

  const handleQuickSuggestion = (text) => {
    if (isLoading) return;
    onSend(text);
  };

  const handleSpeak = (msgId, text) => {
    setSpeakingMsgId(msgId);
    setIsSpeaking(true);
    // Use speech synthesis via VoiceAssistant child component — pass via event
    window.dispatchEvent(new CustomEvent('chat:speak', { detail: { text, lang: voiceLang } }));
  };

  const handleStopSpeak = () => {
    setSpeakingMsgId(null);
    setIsSpeaking(false);
    window.dispatchEvent(new CustomEvent('chat:speak:stop'));
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex-1 flex flex-col h-full min-w-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 bg-white flex items-center justify-between shrink-0">
        <div>
          <h2 className="font-semibold text-slate-900 flex items-center gap-2">
            <HiOutlineSparkles className="w-4 h-4 text-primary-600" />
            {sessionTitle || 'AI Resume Coach'}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Ask anything about your resume
          </p>
        </div>

        {/* Voice language selector */}
        <div className="flex items-center gap-2">
          <select
            className="input py-1.5 text-xs w-32"
            value={voiceLang}
            onChange={e => onVoiceLangChange(e.target.value)}
            title="Voice language"
          >
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (UK)</option>
            <option value="hi-IN">Hindi</option>
            <option value="te-IN">Telugu</option>
          </select>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-4">
        {isEmpty && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-primary-50 flex items-center justify-center mb-4">
              <HiOutlineSparkles className="w-8 h-8 text-primary-400" />
            </div>
            <h3 className="font-semibold text-slate-700 mb-1">Your AI Resume Coach</h3>
            <p className="text-slate-400 text-sm max-w-xs">
              Start a conversation about your resume. Ask anything!
            </p>

            {/* Quick suggestion chips */}
            <div className="flex flex-wrap gap-2 justify-center mt-6 max-w-md">
              {QUICK_SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleQuickSuggestion(s)}
                  className="px-3 py-1.5 text-xs rounded-full border border-primary-200 text-primary-700
                             bg-primary-50 hover:bg-primary-100 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble
            key={msg.id}
            msg={msg}
            onSpeak={handleSpeak}
            onStopSpeak={handleStopSpeak}
            isSpeaking={isSpeaking}
            speakingMsgId={speakingMsgId}
          />
        ))}

        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Quick suggestions (shown when there are messages) */}
      {!isEmpty && !isLoading && (
        <div className="px-6 py-2 flex gap-2 overflow-x-auto scrollbar-thin shrink-0">
          {QUICK_SUGGESTIONS.slice(0, 4).map((s, i) => (
            <button
              key={i}
              onClick={() => handleQuickSuggestion(s)}
              className="shrink-0 px-3 py-1 text-xs rounded-full border border-slate-200 text-slate-600
                         hover:border-primary-300 hover:text-primary-700 hover:bg-primary-50 transition-colors whitespace-nowrap"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input bar */}
      <div className="px-6 py-4 border-t border-slate-100 bg-white shrink-0">
        <div className="flex items-end gap-3 bg-slate-50 rounded-2xl border border-slate-200
                        focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100
                        transition-all px-4 py-3">
          <textarea
            ref={textareaRef}
            className="flex-1 bg-transparent resize-none text-sm text-slate-800 placeholder-slate-400
                       focus:outline-none max-h-32 leading-relaxed"
            rows={1}
            placeholder="Ask me anything about your resume… (Enter to send, Shift+Enter for new line)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            style={{ height: 'auto', minHeight: '24px' }}
            onInput={e => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
            }}
          />

          <div className="flex items-center gap-1.5 shrink-0">
            {/* Voice assistant button */}
            <VoiceAssistant
              lang={voiceLang}
              onResult={handleVoiceResult}
            />

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="w-8 h-8 rounded-xl bg-primary-600 text-white flex items-center justify-center
                         hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed
                         transition-colors active:scale-95"
              title="Send (Enter)"
            >
              {isLoading
                ? <LoadingSpinner size="sm" className="!text-white" />
                : <FiSend className="w-3.5 h-3.5" />
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
