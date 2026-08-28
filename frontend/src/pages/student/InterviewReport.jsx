import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { ScoreRadarChart } from '../../components/interview/ScoreRadarChart';
import { 
  Award, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  Volume2, 
  Sparkles, 
  Brain, 
  Mic2, 
  TrendingUp, 
  ArrowLeft, 
  ChevronDown, 
  ChevronUp, 
  Loader2,
  FileText,
  Clock
} from 'lucide-react';

export const InterviewReport = () => {
  const { id: sessionId } = useParams();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [expandedQuestion, setExpandedQuestion] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await apiClient.get(`/reports/sessions/${sessionId}`);
        setReportData(res.data);
      } catch (err) {
        setError('Failed to fetch interview report.');
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [sessionId]);

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await apiClient.get(`/reports/sessions/${sessionId}/pdf`, {
        responseType: 'blob',
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CareerVoice_Report_${sessionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Could not generate PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
        <p className="text-sm text-slate-400">Compiling multi-modal evaluation report...</p>
      </div>
    );
  }

  if (error || !reportData) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">Report Not Found</h2>
        <p className="text-sm text-slate-400">{error || 'Could not load report details.'}</p>
        <Link to="/dashboard" className="inline-flex items-center space-x-2 text-brand-400 text-sm font-semibold">
          <ArrowLeft className="w-4 h-4" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  const {
    candidate_name,
    role,
    difficulty,
    tech_stack,
    overall_score,
    technical_score,
    communication_score,
    confidence_score,
    strengths,
    weaknesses,
    recommendations,
    competency_breakdown,
    questions_detail,
    completed_at
  } = reportData;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link
          to="/dashboard"
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Candidate Dashboard</span>
        </Link>

        <button
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white text-xs font-bold shadow-lg shadow-brand-600/20 transition-all disabled:opacity-50"
        >
          {downloadingPdf ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          <span>Download PDF Report</span>
        </button>
      </div>

      {/* Banner Card */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 bg-gradient-to-r from-brand-950/40 via-dark-900 to-accent-950/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xl">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-brand-500/20 border border-brand-500/30 text-brand-300">
              Mock Interview Scorecard
            </span>
            <span className="text-xs text-slate-400">
              • {completed_at ? new Date(completed_at).toLocaleDateString() : 'Completed'}
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            {role} Evaluation Report
          </h1>
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <p className="text-sm text-slate-300">
              Candidate: <b className="text-white">{candidate_name}</b> | Difficulty: <b className="text-brand-400 capitalize">{difficulty}</b>
            </p>
            {tech_stack && tech_stack.map((ts, idx) => (
              <span key={idx} className="text-[11px] px-2.5 py-0.5 rounded-md bg-brand-500/10 border border-brand-500/30 text-brand-300 font-semibold">
                {typeof ts === 'string' ? ts.split('(')[0].trim() : ts}
              </span>
            ))}
          </div>
        </div>

        {/* Big Overall Score Badge */}
        <div className="flex items-center space-x-4 bg-dark-950/80 p-4 rounded-2xl border border-slate-800 shrink-0">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-brand-600 to-accent-600 p-0.5 shadow-lg shadow-brand-500/30 flex items-center justify-center">
            <div className="w-full h-full bg-dark-950 rounded-2xl flex flex-col items-center justify-center">
              <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-brand-300">
                {overall_score}%
              </span>
              <span className="text-[9px] font-bold uppercase tracking-wider text-brand-400">Composite</span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold text-white">
              {overall_score >= 80 ? '🌟 High Readiness' : overall_score >= 65 ? '👍 Solid Baseline' : '📈 Developing'}
            </span>
            <span className="text-[11px] text-slate-400">
              {overall_score >= 80 ? 'Ready for formal tech rounds' : 'Focus on feedback recommendations'}
            </span>
          </div>
        </div>
      </div>

      {/* Multi-Modal Score Metrics Breakdown Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Brain className="w-5 h-5" />
            </div>
            <span className="text-2xl font-extrabold text-blue-400">{technical_score}%</span>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Technical NLP & Relevance</h4>
            <p className="text-xs text-slate-400 mt-0.5">Keyword coverage, domain concepts, and question accuracy</p>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Mic2 className="w-5 h-5" />
            </div>
            <span className="text-2xl font-extrabold text-purple-400">{communication_score}%</span>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Speech & Vocal Delivery</h4>
            <p className="text-xs text-slate-400 mt-0.5">Pace cadence, filler-word suppression, and audio clarity</p>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <span className="text-2xl font-extrabold text-emerald-400">{confidence_score}%</span>
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Confidence & Sentiment</h4>
            <p className="text-xs text-slate-400 mt-0.5">Conviction in delivery, positive tone, and structured composure</p>
          </div>
        </div>

      </div>

      {/* Competencies & Qualitative Coaching Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Radar / Competencies */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-brand-400" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Competency Radar Breakdown
            </h3>
          </div>
          <ScoreRadarChart data={competency_breakdown} />
        </div>

        {/* Strengths & Weaknesses */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-800 space-y-6 flex flex-col justify-between">
          
          {/* Strengths */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <h3 className="text-sm font-bold uppercase tracking-wider">Observed Strengths</h3>
            </div>
            <ul className="space-y-2">
              {strengths?.map((s, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
              <h3 className="text-sm font-bold uppercase tracking-wider">Improvement Priorities</h3>
            </div>
            <ul className="space-y-2">
              {weaknesses?.map((w, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-xs text-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Actionable Recommendations */}
          <div className="p-4 rounded-2xl bg-dark-900 border border-slate-800 space-y-2">
            <h4 className="text-xs font-bold text-brand-300 uppercase tracking-wider">
              Coaching Recommendations for Next Session
            </h4>
            <ul className="space-y-1.5">
              {recommendations?.map((r, idx) => (
                <li key={idx} className="text-xs text-slate-400 flex items-start space-x-2">
                  <span className="text-brand-400 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

        </div>

      </div>

      {/* Detailed Question By Question Analysis */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <FileText className="w-4 h-4 text-brand-400" />
          <span>Question-by-Question Multi-Modal Audit</span>
        </h3>

        <div className="space-y-4">
          {questions_detail?.map((q, idx) => {
            const isExpanded = expandedQuestion === idx;
            const ev = q.evaluation;

            return (
              <div
                key={q.id}
                className="glass-panel rounded-2xl border border-slate-800 overflow-hidden transition-all"
              >
                {/* Accordion Trigger */}
                <button
                  type="button"
                  onClick={() => setExpandedQuestion(isExpanded ? null : idx)}
                  className="w-full p-5 flex items-center justify-between text-left hover:bg-slate-900/40 transition-colors"
                >
                  <div className="flex items-start space-x-3.5">
                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-xs font-bold text-brand-400 shrink-0 mt-0.5">
                      Q{idx + 1}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-bold text-white">{q.competency || 'Competency'}</span>
                        {q.is_followup && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">
                            Dynamic Follow-up
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-300 mt-1 line-clamp-1">
                        "{q.question_text}"
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    {ev && (
                      <span className="text-sm font-extrabold text-brand-400">
                        {ev.composite_score}%
                      </span>
                    )}
                    {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                  </div>
                </button>

                {/* Expanded Question Details */}
                {isExpanded && ev && (
                  <div className="p-6 border-t border-slate-800/80 bg-dark-950/60 space-y-5">
                    
                    {/* Metrics Bar */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="p-3 rounded-xl bg-dark-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Speaking Pace</span>
                        <p className="text-sm font-bold text-brand-400">{ev.pace_wpm} WPM</p>
                      </div>
                      <div className="p-3 rounded-xl bg-dark-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Filler Words</span>
                        <p className="text-sm font-bold text-amber-400">{ev.filler_words_count} detected</p>
                      </div>
                      <div className="p-3 rounded-xl bg-dark-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Technical NLP</span>
                        <p className="text-sm font-bold text-blue-400">{ev.nlp_score}%</p>
                      </div>
                      <div className="p-3 rounded-xl bg-dark-900 border border-slate-800">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Vocal Delivery</span>
                        <p className="text-sm font-bold text-emerald-400">{ev.voice_score}%</p>
                      </div>
                    </div>

                    {/* Spoken Transcript */}
                    {q.transcript && (
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                          Candidate Spoken Transcript:
                        </span>
                        <p className="p-3.5 rounded-xl bg-dark-900 border border-slate-800 text-xs text-slate-200 leading-relaxed italic">
                          "{q.transcript}"
                        </p>
                      </div>
                    )}

                    {/* Audio playback if file exists */}
                    {q.audio_url && (
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1">
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>Voice Recording Playback:</span>
                        </span>
                        <audio controls src={q.audio_url} className="w-full h-9 rounded-lg" />
                      </div>
                    )}

                    {/* Coach Feedback */}
                    {ev.feedback_text && (
                      <div className="p-3.5 rounded-xl bg-brand-950/40 border border-brand-500/20 text-xs text-brand-200">
                        <b className="text-white">AI Coach Feedback: </b>
                        {ev.feedback_text}
                      </div>
                    )}

                    {/* Model Answer Suggestion */}
                    {ev.suggested_answer && (
                      <div className="space-y-1">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                          Recommended Model Approach:
                        </span>
                        <p className="text-xs text-slate-400">
                          {ev.suggested_answer}
                        </p>
                      </div>
                    )}

                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
