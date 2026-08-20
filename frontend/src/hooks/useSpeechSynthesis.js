import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useSpeechSynthesis
 * Wraps the browser Web Speech API SpeechSynthesis.
 *
 * @param {object} options
 * @param {string} options.lang  - BCP-47 language code (default 'en-US')
 * @param {number} options.rate  - Speech rate 0.1-10 (default 1)
 * @param {number} options.pitch - Pitch 0-2 (default 1)
 */
function useSpeechSynthesis({
  lang  = 'en-US',
  rate  = 1,
  pitch = 1,
} = {}) {
  const [isSpeaking,  setIsSpeaking]  = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [voices,      setVoices]      = useState([]);
  const utteranceRef = useRef(null);

  // Detect support and load voices
  useEffect(() => {
    if (!window.speechSynthesis) return;
    setIsSupported(true);

    const loadVoices = () => {
      const available = window.speechSynthesis.getVoices();
      setVoices(available);
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;
    return () => { window.speechSynthesis.onvoiceschanged = null; };
  }, []);

  /**
   * Speak a text string.
   * Strips markdown bold/italic markers before speaking.
   */
  const speak = useCallback((text, options = {}) => {
    if (!window.speechSynthesis) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    // Strip markdown symbols so they are not read aloud
    const clean = text
      .replace(/\*\*(.*?)\*\*/g, '$1')  // **bold**
      .replace(/\*(.*?)\*/g,     '$1')  // *italic*
      .replace(/#{1,6}\s/g,      '')    // headings
      .replace(/`(.*?)`/g,       '$1')  // inline code
      .replace(/•/g,             '')    // bullets
      .replace(/---/g,           '')    // dividers
      .trim();

    const speakLang = options.lang || lang;

    // Pick best matching voice
    const voice =
      voices.find(v => v.lang === speakLang) ||
      voices.find(v => v.lang.startsWith(speakLang.split('-')[0])) ||
      voices[0] ||
      null;

    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang  = speakLang;
    utterance.rate  = options.rate  ?? rate;
    utterance.pitch = options.pitch ?? pitch;
    if (voice) utterance.voice = voice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend   = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [voices, lang, rate, pitch]);

  const cancel = useCallback(() => {
    window.speechSynthesis?.cancel();
    setIsSpeaking(false);
  }, []);

  const toggle = useCallback((text, options) => {
    if (isSpeaking) cancel();
    else speak(text, options);
  }, [isSpeaking, cancel, speak]);

  // Available language codes from loaded voices
  const availableLangs = [...new Set(voices.map(v => v.lang))].sort();

  useEffect(() => () => window.speechSynthesis?.cancel(), []);

  return {
    isSpeaking,
    isSupported,
    voices,
    availableLangs,
    speak,
    cancel,
    toggle,
  };
}

export default useSpeechSynthesis;
