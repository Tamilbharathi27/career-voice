import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';
import { useAudioRecorder } from '../../hooks/useAudioRecorder';
import { AIAvatar } from '../../components/interview/AIAvatar';
import { WaveformVisualizer } from '../../components/interview/WaveformVisualizer';
import { 
  Mic, 
  Square, 
  Volume2, 
  VolumeX, 
  Send, 
  Sparkles, 
  AlertCircle, 
  CheckCircle2, 
  RotateCcw, 
  Loader2, 
  Clock, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';

export const VoiceInterview = () => {
  const { id: sessionId } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [aiState, setAiState] = useState('idle'); // 'idle' | 'speaking' | 'listening' | 'thinking' | 'analyzing'
  const [voiceSpeechEnabled, setVoiceSpeechEnabled] = useState(true);
  const [lastEvaluation, setLastEvaluation] = useState(null);
  const [editableTranscript, setEditableTranscript] = useState('');
  const [error, setError] = useState(null);

  const {
    isRecording,
    recordingDuration,
    audioBlob,
    audioUrl,
    liveTranscript,
    audioLevel,
    analyserNode,
    startRecording,
    stopRecording,
    resetRecording,
  } = useAudioRecorder();

  // Load Session Data
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await apiClient.get(`/interviews/sessions/${sessionId}`);
        setSession(res.data);
        
        if (res.data.status === 'completed') {
          navigate(`/interview/report/${sessionId}`);
          return;
        }

        // Find current active unanswered question
        const unanswered = res.data.questions.find((q) => !q.answer);
        if (unanswered) {
          setCurrentQuestion(unanswered);
          setQuestionIndex(unanswered.order_index);
        } else if (res.data.questions.length > 0) {
          setCurrentQuestion(res.data.questions[res.data.questions.length - 1]);
        }
      } catch (err) {
        setError('Failed to load interview session. Please return to dashboard.');
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [sessionId, navigate]);

  // Update live transcript in text box
  useEffect(() => {
    if (liveTranscript) {
      setEditableTranscript(liveTranscript);
    }
  }, [liveTranscript]);

  // Read question aloud via Text-to-Speech when new question loads
  useEffect(() => {
    if (currentQuestion && voiceSpeechEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setAiState('speaking');

      const utterance = new SpeechSynthesisUtterance(currentQuestion.question_text);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      utterance.lang = 'en-US';

      utterance.onend = () => {
        setAiState('idle');
      };
      utterance.onerror = () => {
        setAiState('idle');
      };

      window.speechSynthesis.speak(utterance);
    } else {
      setAiState('idle');
    }

    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [currentQuestion, voiceSpeechEnabled]);

  // Handle Recording Toggle
  const handleToggleRecord = async () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    if (isRecording) {
      stopRecording();
      setAiState('idle');
    } else {
      resetRecording();
      setEditableTranscript('');
      setAiState('listening');
      await startRecording();
    }
  };

  // Submit Answer to AI Pipeline
  const handleSubmitAnswer = async () => {
    if (!audioBlob && !editableTranscript) {
      alert('Please record an answer or provide a transcript before submitting.');
      return;
    }

    setSubmitting(true);
    setAiState('analyzing');
    setError(null);

    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('question_id', currentQuestion.id);
    formData.append('duration_seconds', recordingDuration || 15);
    formData.append('live_transcript', editableTranscript || liveTranscript || '');
    
    // Provide blob or create placeholder audio if text only
    const finalBlob = audioBlob || new Blob(['mock_audio_stream'], { type: 'audio/webm' });
    formData.append('audio', finalBlob, 'response.webm');

    try {
      const res = await apiClient.post('/voice/submit-answer', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setLastEvaluation(res.data.evaluation);
      resetRecording();
      setEditableTranscript('');

      if (res.data.is_completed) {
        // Complete interview and redirect to report
        setTimeout(() => {
          navigate(`/interview/report/${sessionId}`);
        }, 2200);
      } else if (res.data.next_question) {
        // Load next dynamic question
        setCurrentQuestion(res.data.next_question);
        setQuestionIndex(res.data.next_question.order_index);
        setAiState('idle');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze answer. Please try submitting again.');
      setAiState('idle');
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Entering AI Voice Studio...</p>
      </div>
    );
  }

  const totalQuestions = session?.question_count || 3;
  const progressPercent = Math.round(((questionIndex + 1) / totalQuestions) * 100);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Header & Progress */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 glass-panel rounded-2xl border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400 font-extrabold text-sm">
            Q{questionIndex + 1}
          </div>
          <div>
            <div className="flex items-center flex-wrap gap-2">
              <h2 className="text-sm font-bold text-white">{session?.role} Mock Interview</h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 capitalize">
                {session?.difficulty}
              </span>
              {session?.tech_stack && session.tech_stack.map((ts, idx) => (
                <span key={idx} className="text-[10px] px-2 py-0.5 rounded-md bg-brand-500/10 border border-brand-500/30 text-brand-300 font-semibold">
                  {typeof ts === 'string' ? ts.split('(')[0].trim() : ts}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Question {questionIndex + 1} of {totalQuestions}
            </p>
          </div>
        </div>

        {/* Audio Toggle & Progress Bar */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setVoiceSpeechEnabled(!voiceSpeechEnabled)}
            className={`p-2 rounded-xl border text-xs font-semibold flex items-center space-x-1.5 transition-colors ${
              voiceSpeechEnabled
                ? 'bg-brand-600/20 border-brand-500/40 text-brand-300'
                : 'bg-dark-900 border-slate-800 text-slate-400'
            }`}
            title="Toggle AI Speech Voice Readout"
          >
            {voiceSpeechEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            <span className="hidden sm:inline">{voiceSpeechEnabled ? 'Voice ON' : 'Muted'}</span>
          </button>

          <div className="w-36 flex flex-col space-y-1">
            <div className="flex justify-between text-[10px] font-semibold text-slate-400">
              <span>Progress</span>
              <span>{progressPercent}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-brand-500 to-accent-500 rounded-full transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center space-x-2 text-red-400 text-xs font-semibold">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left / AI Interviewer Panel */}
        <div className="lg:col-span-5 glass-panel rounded-3xl p-6 border border-slate-800 flex flex-col items-center justify-between min-h-[420px]">
          
          <div className="w-full flex justify-between items-center text-xs text-slate-400">
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-accent-400" />
              <span>Adaptive Agent</span>
            </span>
            <span className="px-2 py-0.5 rounded-md bg-slate-800 text-brand-300 font-semibold text-[11px]">
              {currentQuestion?.competency || 'Core Competency'}
            </span>
          </div>

          {/* AI Avatar */}
          <AIAvatar state={aiState} role={`${session?.role} Interviewer`} />

          {/* Question Text Box */}
          <div className="w-full p-4 rounded-2xl bg-dark-900/90 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] uppercase tracking-wider font-bold text-brand-400">
                {currentQuestion?.is_followup ? '⚡ Dynamic Follow-Up Question' : 'Primary Question'}
              </span>
              <button
                onClick={() => {
                  if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance(currentQuestion.question_text);
                    setAiState('speaking');
                    u.onend = () => setAiState('idle');
                    window.speechSynthesis.speak(u);
                  }
                }}
                className="text-slate-400 hover:text-white p-1"
                title="Replay Voice"
              >
                <Volume2 className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-sm sm:text-base font-semibold text-slate-100 leading-relaxed">
              "{currentQuestion?.question_text}"
            </p>
          </div>

        </div>

        {/* Right / Candidate Voice Capture Studio */}
        <div className="lg:col-span-7 space-y-5 flex flex-col">
          
          {/* Real-time Waveform Canvas */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Mic className={`w-4 h-4 ${isRecording ? 'text-red-400 animate-pulse' : 'text-slate-400'}`} />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  {isRecording ? 'Microphone Active' : 'Spoken Audio Capture'}
                </span>
              </div>

              {/* Timer */}
              <div className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-slate-300">
                <Clock className="w-3.5 h-3.5 text-brand-400" />
                <span>{formatTime(recordingDuration)}</span>
              </div>
            </div>

            {/* Canvas Waveform */}
            <WaveformVisualizer
              isRecording={isRecording}
              analyserNode={analyserNode}
              audioLevel={audioLevel}
            />

            {/* Recording Controls */}
            <div className="flex items-center justify-center space-x-4 pt-2">
              
              <button
                type="button"
                onClick={handleToggleRecord}
                disabled={submitting}
                className={`flex items-center justify-center space-x-2 px-8 py-3.5 rounded-2xl font-bold text-sm shadow-xl transition-all ${
                  isRecording
                    ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-600/30 scale-105 animate-pulse'
                    : 'bg-brand-600 hover:bg-brand-500 text-white shadow-brand-600/30 hover:scale-105'
                }`}
              >
                {isRecording ? (
                  <>
                    <Square className="w-4 h-4 fill-white" />
                    <span>Stop Recording</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-4 h-4" />
                    <span>{audioBlob ? 'Re-record Answer' : 'Start Spoken Answer'}</span>
                  </>
                )}
              </button>

              {audioUrl && !isRecording && (
                <button
                  type="button"
                  onClick={resetRecording}
                  className="p-3 rounded-2xl bg-dark-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-colors"
                  title="Reset Audio"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              )}

            </div>

          </div>

          {/* Transcript & Response Submission */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3 flex-1 flex flex-col justify-between">
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-brand-400" />
                  <span>Speech-to-Text Live Transcript</span>
                </label>
                <span className="text-[11px] text-slate-400">Live speech or edit manually</span>
              </div>

              <textarea
                rows={4}
                value={editableTranscript}
                onChange={(e) => setEditableTranscript(e.target.value)}
                placeholder="Your spoken response will be transcribed here in real-time as you speak..."
                className="w-full p-3 bg-dark-900/90 border border-slate-700/80 rounded-2xl text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 leading-relaxed"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-400">
                {editableTranscript ? `${editableTranscript.split(/\s+/).filter(Boolean).length} words spoken` : 'Waiting for voice input...'}
              </span>

              <button
                type="button"
                onClick={handleSubmitAnswer}
                disabled={submitting || isRecording || (!audioBlob && !editableTranscript)}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-bold text-xs sm:text-sm shadow-lg shadow-brand-600/30 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Evaluating Multi-Modal Signals...</span>
                  </>
                ) : (
                  <>
                    <span>Submit & Next Question</span>
                    <Send className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

          </div>

        </div>

      </div>

      {/* Immediate Evaluation Toast / Pill if available */}
      {lastEvaluation && (
        <div className="p-4 rounded-2xl bg-brand-950/70 border border-brand-500/40 glass-panel flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-fade-in shadow-xl">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-extrabold text-sm">
              {lastEvaluation.composite_score}%
            </div>
            <div>
              <h4 className="text-xs font-bold text-white flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Answer Evaluated Successfully!</span>
              </h4>
              <p className="text-xs text-slate-300 mt-0.5">
                Cadence: <b className="text-brand-300">{lastEvaluation.pace_wpm} WPM</b> • Fillers: <b className="text-brand-300">{lastEvaluation.filler_words_count}</b> • {lastEvaluation.feedback_text}
              </p>
            </div>
          </div>
          <span className="text-[11px] font-bold text-brand-400 px-3 py-1 rounded-full bg-brand-900/50 border border-brand-500/30">
            Agent dynamically adjusting next question...
          </span>
        </div>
      )}

    </div>
  );
};
