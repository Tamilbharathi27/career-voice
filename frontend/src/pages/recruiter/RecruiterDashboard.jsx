import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { 
  Users, 
  Search, 
  Filter, 
  Award, 
  CheckCircle2, 
  Clock, 
  ChevronRight, 
  Loader2, 
  ArrowUpRight,
  TrendingUp,
  Briefcase
} from 'lucide-react';

export const RecruiterDashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');

  useEffect(() => {
    const fetchRecruiterData = async () => {
      try {
        const res = await apiClient.get('/reports/recruiter/candidates');
        setCandidates(res.data);
      } catch (err) {
        console.error('Failed to load candidate reports:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRecruiterData();
  }, []);

  // Filter logic
  const filteredCandidates = candidates.filter((c) => {
    const matchesSearch = 
      c.candidate_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.candidate_email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.role.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesRole = roleFilter === 'all' || c.role === roleFilter;

    let matchesScore = true;
    if (scoreFilter === 'high') matchesScore = c.overall_score >= 80;
    else if (scoreFilter === 'mid') matchesScore = c.overall_score >= 65 && c.overall_score < 80;
    else if (scoreFilter === 'low') matchesScore = c.overall_score < 65;

    return matchesSearch && matchesRole && matchesScore;
  });

  const totalCandidates = candidates.length;
  const avgCandidateScore = totalCandidates > 0
    ? Math.round(candidates.reduce((acc, c) => acc + (c.overall_score || 0), 0) / totalCandidates)
    : 0;

  const readyCount = candidates.filter((c) => c.overall_score >= 80).length;

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-brand-500 animate-spin" />
        <p className="text-sm text-slate-400">Loading recruiter candidate pipeline...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-accent-500/20 text-accent-300 border border-accent-500/30">
              Recruiter & Talent Portal
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
            Candidate Pipeline & Comparative Analytics
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Review objective AI-evaluated candidate interviews, audio telemetry, and technical competency metrics.
          </p>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-accent-600/20 border border-accent-500/30 flex items-center justify-center text-accent-400">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Evaluated Candidates</p>
            <h3 className="text-2xl font-bold text-white">{totalCandidates}</h3>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Average Pipeline Score</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">{avgCandidateScore}%</h3>
              <span className="text-xs text-brand-400">Composite</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Interview Ready (≥80%)</p>
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-bold text-white">{readyCount}</h3>
              <span className="text-xs text-emerald-400">Recommended for Hire</span>
            </div>
          </div>
        </div>

      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search candidate name, email, role..."
            className="w-full pl-9 pr-4 py-2 bg-dark-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-accent-500"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 bg-dark-900 border border-slate-800 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-accent-500"
          >
            <option value="all">All Disciplines</option>
            <option value="Full Stack Engineer">Full Stack</option>
            <option value="Frontend Engineer">Frontend</option>
            <option value="Backend Engineer">Backend</option>
            <option value="AI / ML Engineer">AI / ML</option>
            <option value="Behavioral & Leadership">Behavioral</option>
          </select>

          <select
            value={scoreFilter}
            onChange={(e) => setScoreFilter(e.target.value)}
            className="px-3 py-2 bg-dark-900 border border-slate-800 rounded-xl text-xs text-slate-300 focus:outline-none focus:border-accent-500"
          >
            <option value="all">All Score Tiers</option>
            <option value="high">Top Tier (≥80%)</option>
            <option value="mid">Mid Tier (65-79%)</option>
            <option value="low">Needs Coaching (&lt;65%)</option>
          </select>
        </div>

      </div>

      {/* Candidate List Table */}
      <div className="glass-panel rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 border-b border-slate-800 text-slate-400 uppercase font-semibold">
              <tr>
                <th className="py-4 px-6">Candidate</th>
                <th className="py-4 px-6">Role & Difficulty</th>
                <th className="py-4 px-6">Overall Score</th>
                <th className="py-4 px-6">Multi-Modal Metrics</th>
                <th className="py-4 px-6">Date</th>
                <th className="py-4 px-6 text-right">Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredCandidates.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No matching candidate interviews found in pipeline.
                  </td>
                </tr>
              ) : (
                filteredCandidates.map((c) => (
                  <tr key={c.session_id} className="hover:bg-slate-900/40 transition-colors">
                    
                    {/* Candidate */}
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-accent-600/30 border border-accent-500/40 flex items-center justify-center font-bold text-accent-300">
                          {c.candidate_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-bold text-white text-sm">{c.candidate_name}</p>
                          <p className="text-[11px] text-slate-400">{c.candidate_email}</p>
                        </div>
                      </div>
                    </td>

                    {/* Role */}
                    <td className="py-4 px-6">
                      <p className="font-semibold text-slate-200">{c.role}</p>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 capitalize">
                        {c.difficulty}
                      </span>
                    </td>

                    {/* Overall Score */}
                    <td className="py-4 px-6">
                      <div className="flex items-center space-x-2">
                        <span className={`text-base font-extrabold ${
                          c.overall_score >= 80 ? 'text-emerald-400' : c.overall_score >= 65 ? 'text-brand-400' : 'text-amber-400'
                        }`}>
                          {c.overall_score}%
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${
                          c.overall_score >= 80 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                          c.overall_score >= 65 ? 'bg-brand-500/10 text-brand-400 border border-brand-500/30' :
                          'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                        }`}>
                          {c.overall_score >= 80 ? 'Ready' : c.overall_score >= 65 ? 'Review' : 'Growth'}
                        </span>
                      </div>
                    </td>

                    {/* Metrics Breakdown */}
                    <td className="py-4 px-6">
                      <div className="space-y-1 w-32">
                        <div className="flex justify-between text-[10px] text-slate-400">
                          <span>Tech: <b className="text-slate-200">{c.technical_score}%</b></span>
                          <span>Voice: <b className="text-slate-200">{c.communication_score}%</b></span>
                        </div>
                        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-accent-500" style={{ width: `${c.overall_score}%` }} />
                        </div>
                      </div>
                    </td>

                    {/* Date */}
                    <td className="py-4 px-6 text-slate-400">
                      {c.completed_at ? new Date(c.completed_at).toLocaleDateString() : 'N/A'}
                    </td>

                    {/* Action */}
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/recruiter/candidate/${c.session_id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-accent-600/20 hover:bg-accent-600 text-accent-300 hover:text-white border border-accent-500/30 text-xs font-semibold transition-all"
                      >
                        <span>Examine</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>

                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
