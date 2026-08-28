import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { ScoreRadarChart } from '../../components/interview/ScoreRadarChart';
import { 
  ArrowLeft, 
  Download, 
  Award, 
  Volume2, 
  Brain, 
  Mic2, 
  TrendingUp, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2,
  FileText,
  UserCheck
} from 'lucide-react';

export const CandidateDetail = () => {
  const { sessionId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [decision, setDecision] = useState('review'); // 'pass' | 'review' | 'reject'
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidateReport = async () => {
      try {
        const res = await apiClient.get(`/reports/sessions/${sessionId}`);
        setReport(res.data);
      } catch (err) {
        setError('Failed to fetch candidate report.');
      } finally {
        setLoading(false);
      }
    };
    fetchCandidateReport();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-accent-500 animate-spin" />
        <p className="text-sm text-slate-400">Loading candidate audit details...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">Report Not Found</h2>
        <Link to="/recruiter/dashboard" className="text-accent-400 font-semibold text-sm">
          Return to Candidate Pipeline
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Back button & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <Link
          to="/recruiter/dashboard"
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Candidate Pipeline</span>
        </Link>

        {/* Recruiter Recommendation Action */}
        <div className="flex items-center space-x-3">
          <span className="text-xs text-slate-400 font-semibold">Hiring Decision:</span>
          <div className="flex rounded-xl p-1 bg-dark-900 border border-slate-800">
            <button
              onClick={() => setDecision('pass')}
              className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                decision === 'pass'
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Advance to Onsite
            </button>
            <button
              onClick={() => setDecision('review')}
              className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                decision === 'review'
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Hold for Review
            </button>
            <button
              onClick={() => setDecision('reject')}
              className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                decision === 'reject'
                  ? 'bg-red-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Decline
            </button>
          </div>
        </div>
      </div>

      {/* Candidate Banner */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 bg-gradient-to-r from-accent-950/40 via-dark-900 to-brand-950/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xl">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-accent-500/20 text-accent-300 border border-accent-500/30">
              Candidate Evaluation Audit
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight mt-1">
            {report.candidate_name}
          </h1>
          <p className="text-xs text-slate-400">
            {report.candidate_email} • Applied for <b className="text-white">{report.role}</b> ({report.difficulty})
          </p>
        </div>

        <div className="flex items-center space-x-4 bg-dark-950/80 p-4 rounded-2xl border border-slate-800">
          <div className="text-right">
            <span className="text-xs text-slate-400">Overall Score</span>
            <p className="text-2xl font-black text-accent-400">{report.overall_score}%</p>
          </div>
          <div className={`px-3 py-1 rounded-xl text-xs font-bold uppercase ${
            report.overall_score >= 80 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
            'bg-brand-500/10 text-brand-400 border border-brand-500/30'
          }`}>
            {report.overall_score >= 80 ? 'Recommended' : 'Candidate Progressing'}
          </div>
        </div>
      </div>

      {/* Multi-modal Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Radar */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-white">
            Skill & Competency Breakdown
          </h3>
          <ScoreRadarChart data={report.competency_breakdown} />
        </div>

        {/* Evaluation Summary */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-slate-800 space-y-6">
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4" />
              <span>Key Strengths</span>
            </h4>
            <ul className="space-y-1.5">
              {report.strengths?.map((s, idx) => (
                <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-1.5">
              <AlertTriangle className="w-4 h-4" />
              <span>Identified Growth Areas</span>
            </h4>
            <ul className="space-y-1.5">
              {report.weaknesses?.map((w, idx) => (
                <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

      </div>

      {/* Questions & Audio Inspection */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <FileText className="w-4 h-4 text-accent-400" />
          <span>Detailed Candidate Responses & Audio Replay</span>
        </h3>

        <div className="space-y-4">
          {report.questions_detail?.map((q, idx) => (
            <div key={q.id} className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-accent-600/20 text-accent-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                    Q{idx + 1}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white">"{q.question_text}"</h4>
                    <span className="text-[11px] text-slate-400">Competency: {q.competency || 'General'}</span>
                  </div>
                </div>

                {q.evaluation && (
                  <span className="text-base font-black text-accent-400">
                    {q.evaluation.composite_score}%
                  </span>
                )}
              </div>

              {/* Transcript */}
              {q.transcript && (
                <div className="p-4 rounded-xl bg-dark-900 border border-slate-800 space-y-1">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Candidate Transcript:</span>
                  <p className="text-xs text-slate-200 leading-relaxed italic">
                    "{q.transcript}"
                  </p>
                </div>
              )}

              {/* Audio Player if available */}
              {q.audio_url && (
                <div className="flex items-center space-x-3 pt-1">
                  <Volume2 className="w-4 h-4 text-accent-400 shrink-0" />
                  <audio controls src={q.audio_url} className="w-full h-8 rounded" />
                </div>
              )}

              {/* Telemetry pill row */}
              {q.evaluation && (
                <div className="flex flex-wrap gap-2 text-[11px] pt-1">
                  <span className="px-2.5 py-1 rounded-lg bg-dark-900 border border-slate-800 text-slate-300">
                    Pace: <b>{q.evaluation.pace_wpm} WPM</b>
                  </span>
                  <span className="px-2.5 py-1 rounded-lg bg-dark-900 border border-slate-800 text-slate-300">
                    Fillers: <b>{q.evaluation.filler_words_count}</b>
                  </span>
                  <span className="px-2.5 py-1 rounded-lg bg-dark-900 border border-slate-800 text-slate-300">
                    NLP Relevance: <b>{q.evaluation.nlp_score}%</b>
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
