import { useEffect, useState } from 'react';
import { FiMic, FiMicOff, FiVolume2, FiVolumeX } from 'react-icons/fi';
import clsx from 'clsx';
import useSpeechRecognition from '@/hooks/useSpeechRecognition';
import useSpeechSynthesis   from '@/hooks/useSpeechSynthesis';
import toast from 'react-hot-toast';

/**
 * VoiceAssistant
 * Renders a microphone button for speech-to-text input.
 * Also listens for 'chat:speak' / 'chat:speak:stop' custom window events
 * to play back assistant messages.
 *
 * Props:
 *   lang       — BCP-47 language code (e.g. 'en-US', 'hi-IN', 'te-IN')
 *   onResult   — called with the recognised transcript string
 */
function VoiceAssistant({ lang = 'en-US', onResult }) {
  const [justRecognised, setJustRecognised] = useState(false);

  // ── Speech recognition (mic → text) ──────────────────────────────────
  const {
    isListening,
    transcript,
    isSupported: micSupported,
    permissionErr,
    toggle: toggleMic,
  } = useSpeechRecognition({
    lang,
    continuous: false,
    onResult: (text) => {
      onResult(text);
      setJustRecognised(true);
      setTimeout(() => setJustRecognised(false), 800);
    },
    onError: (err) => toast.error(err),
  });

  // ── Speech synthesis (text → voice) ──────────────────────────────────
  const {
    isSpeaking,
    isSupported: ttsSupported,
    speak,
    cancel,
  } = useSpeechSynthesis({ lang });

  // Listen for chat:speak / chat:speak:stop events from ChatWindow
  useEffect(() => {
    const handleSpeak = (e) => {
      const { text, lang: l } = e.detail || {};
      if (text) speak(text, { lang: l || lang });
    };
    const handleStop = () => cancel();

    window.addEventListener('chat:speak', handleSpeak);
    window.addEventListener('chat:speak:stop', handleStop);
    return () => {
      window.removeEventListener('chat:speak', handleSpeak);
      window.removeEventListener('chat:speak:stop', handleStop);
    };
  }, [speak, cancel, lang]);

  if (!micSupported && !ttsSupported) {
    return null; // Silently hide if browser has no speech support
  }

  return (
    <div className="flex items-center gap-1">
      {/* TTS indicator (playing back assistant message) */}
      {ttsSupported && isSpeaking && (
        <button
          onClick={cancel}
          className="w-7 h-7 rounded-lg flex items-center justify-center
                     bg-primary-50 text-primary-600 hover:bg-primary-100 transition-colors"
          title="Stop speaking"
        >
          <FiVolumeX className="w-3.5 h-3.5" />
        </button>
      )}

      {/* Mic button */}
      {micSupported && (
        <button
          onClick={toggleMic}
          title={
            permissionErr ||
            (isListening ? 'Stop recording' : `Speak in ${lang}`)
          }
          className={clsx(
            'w-8 h-8 rounded-xl flex items-center justify-center transition-all',
            isListening
              ? 'bg-danger-500 text-white animate-pulse shadow-lg shadow-danger-200'
              : justRecognised
              ? 'bg-success-500 text-white'
              : 'bg-slate-100 text-slate-500 hover:bg-primary-50 hover:text-primary-600'
          )}
        >
          {isListening ? (
            <FiMicOff className="w-3.5 h-3.5" />
          ) : (
            <FiMic className="w-3.5 h-3.5" />
          )}
        </button>
      )}

      {/* Listening transcript preview */}
      {isListening && transcript && (
        <div className="absolute bottom-20 left-4 right-4 z-20 bg-white border border-primary-200
                        rounded-xl px-4 py-2 shadow-lg text-sm text-slate-700 italic animate-fade-in">
          🎙 {transcript}
        </div>
      )}
    </div>
  );
}

export default VoiceAssistant;
