import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { 
  Sparkles, 
  Play, 
  Award, 
  TrendingUp, 
  Clock, 
  CheckCircle2, 
  ArrowUpRight, 
  Mic2, 
  FileText, 
  Activity,
  AlertCircle,
  Loader2,
  ChevronRight
} from 'lucide-react';

export const StudentDashboard = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [sessionsRes, profileRes] = await Promise.all([
          apiClient.get('/interviews/sessions'),
          apiClient.get('/users/profile'),
        ]);
        setSessions(sessionsRes.data);
        setProfile(profileRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Compute summary stats
  const completedSessions = sessions.filter((s) => s.status === 'completed' && s.overall_score);
  const totalCompleted = completedSessions.length;
  const avgScore = totalCompleted > 0
    ? Math.round(completedSessions.reduce((acc, s) => acc + (s.overall_score || 0), 0) / totalCompleted)
    : 0;

  // Readiness Tier
  const getReadinessBadge = (score) => {
    if (score >= 85) return { label: 'Interview Ready (Top 10%)', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
    if (score >= 70) return { label: 'Competent & Progressing', color: 'text-brand-400 bg-brand-500/10 border-brand-500/30' };
    if (score > 0) return { label: 'Developing Fundamentals', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' };
    return { label: 'New Candidate', color: 'text-slate-400 bg-slate-500/10 border-slate-500/30' };
  };

  const readiness = getReadinessBadge(avgScore);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
        <p className="text-sm text-slate-400">Loading your candidate studio...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Welcome Banner */}
      <div className="relative rounded-3xl p-8 overflow-hidden glass-panel border border-slate-800 bg-gradient-to-r from-brand-950/40 via-dark-900 to-accent-950/40">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                Welcome back, {user?.name}! 👋
              </h1>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${readiness.color}`}>
                {readiness.label}
              </span>
            </div>
            <p className="text-sm text-slate-400 max-w-xl">
              Targeting <span className="text-brand-400 font-semibold">{profile?.target_role || 'Software Engineer'}</span>. 
              Practice realistic voice interviews with our dynamic AI agent and get instant acoustic and technical scoring.
            </p>
          </div>

          <Link
            to="/interview/setup"
            className="flex items-center space-x-2.5 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-bold shadow-xl shadow-brand-600/30 hover:scale-105 transition-all text-sm group"
          >
            <Play className="w-4 h-4 fill-white group-hover:translate-x-0.5 transition-transform" />
            <span>Launch Mock Interview</span>
          </Link>
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Average Score</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">{avgScore > 0 ? `${avgScore}%` : 'N/A'}</h3>
              {avgScore > 0 && <span className="text-xs text-emerald-400 font-semibold">+4% vs baseline</span>}
            </div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-accent-600/20 border border-accent-500/30 flex items-center justify-center text-accent-400">
            <Mic2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Interviews Completed</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">{totalCompleted}</h3>
              <span className="text-xs text-slate-400">mock sessions</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Target Cadence</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">135</h3>
              <span className="text-xs text-emerald-400 font-semibold">WPM (Optimal)</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">STAR Method Score</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">88%</h3>
              <span className="text-xs text-purple-400 font-semibold">Structured</span>
            </div>
          </div>
        </div>

      </div>

      {/* Recent Interview History */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-brand-400" />
            <h2 className="text-lg font-bold text-white">Recent Mock Interviews</h2>
          </div>
          <Link
            to="/interview/setup"
            className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center space-x-1"
          >
            <span>Start New Session</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {sessions.length === 0 ? (
          <div className="p-12 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500">
              <Mic2 className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-semibold text-white">No Mock Interviews Taken Yet</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Select your target role and take your first voice interview to receive comprehensive AI feedback.
              </p>
            </div>
            <Link
              to="/interview/setup"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold transition-colors"
            >
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Start First Interview</span>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-900/40 transition-colors"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-brand-400 shrink-0 mt-0.5">
                    <Mic2 className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <h4 className="text-sm font-bold text-white">{session.role}</h4>
                      <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 capitalize font-medium">
                        {session.difficulty}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-md uppercase tracking-wider font-bold ${
                        session.status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {session.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {new Date(session.started_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })} • {session.question_count} Questions
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 self-end sm:self-center">
                  {session.overall_score !== null && session.overall_score !== undefined ? (
                    <div className="text-right">
                      <span className="text-xs text-slate-400">Score</span>
                      <p className="text-base font-extrabold text-brand-400">
                        {session.overall_score}%
                      </p>
                    </div>
                  ) : null}

                  {session.status === 'completed' ? (
                    <Link
                      to={`/interview/report/${session.id}`}
                      className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-brand-600/20 hover:bg-brand-600 text-brand-300 hover:text-white border border-brand-500/30 text-xs font-semibold transition-all"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>View Report</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  ) : (
                    <Link
                      to={`/interview/room/${session.id}`}
                      className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-white border border-emerald-500/30 text-xs font-semibold transition-all"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Resume</span>
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
