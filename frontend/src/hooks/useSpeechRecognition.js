import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useSpeechRecognition
 * Wraps the browser Web Speech API SpeechRecognition.
 *
 * @param {object} options
 * @param {string}   options.lang         - BCP-47 language code (default 'en-US')
 * @param {boolean}  options.continuous   - Keep listening after first result
 * @param {function} options.onResult     - Called with the transcript string
 * @param {function} options.onError      - Called with the error message string
 */
function useSpeechRecognition({
  lang = 'en-US',
  continuous = false,
  onResult = () => {},
  onError  = () => {},
} = {}) {
  const [isListening,   setIsListening]   = useState(false);
  const [transcript,    setTranscript]    = useState('');
  const [isSupported,   setIsSupported]   = useState(false);
  const [permissionErr, setPermissionErr] = useState('');
  const recognitionRef = useRef(null);

  // Detect support
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SR);
  }, []);

  const start = useCallback(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      onError('Speech recognition is not supported in this browser.');
      return;
    }

    setPermissionErr('');
    setTranscript('');

    const recognition = new SR();
    recognition.lang              = lang;
    recognition.continuous        = continuous;
    recognition.interimResults    = true;
    recognition.maxAlternatives   = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event) => {
      let interim = '';
      let final   = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) final += t;
        else interim += t;
      }
      const combined = (final || interim).trim();
      setTranscript(combined);
      if (final) onResult(final.trim());
    };

    recognition.onerror = (event) => {
      let msg = 'Speech recognition error.';
      if (event.error === 'not-allowed' || event.error === 'permission-denied') {
        msg = 'Microphone permission denied. Please allow microphone access in your browser.';
      } else if (event.error === 'no-speech') {
        msg = 'No speech detected. Please try again.';
      } else if (event.error === 'network') {
        msg = 'Network error during speech recognition.';
      } else if (event.error === 'audio-capture') {
        msg = 'No microphone found. Please connect a microphone.';
      }
      setPermissionErr(msg);
      onError(msg);
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  }, [lang, continuous, onResult, onError]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const toggle = useCallback(() => {
    if (isListening) stop();
    else start();
  }, [isListening, start, stop]);

  // Cleanup on unmount
  useEffect(() => () => recognitionRef.current?.abort(), []);

  return {
    isListening,
    transcript,
    isSupported,
    permissionErr,
    start,
    stop,
    toggle,
  };
}

export default useSpeechRecognition;
