import React, { useState, useEffect } from 'react';
import apiClient from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { User, Briefcase, Award, FileText, Check, Loader2, Sparkles, Save } from 'lucide-react';

export const ProfilePage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    target_role: 'Full Stack Engineer',
    experience_level: 'Intermediate',
    skills: 'React, TypeScript, Python, FastAPI, SQL, Docker, Redis',
    bio: '',
    resume_text: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await apiClient.get('/users/profile');
        setProfile(res.data);
      } catch (err) {
        console.error('Failed to load profile:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      const res = await apiClient.put('/users/profile', profile);
      setProfile(res.data);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-brand-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Candidate Profile & Preferences
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Customize your target career track, key competencies, and background to tailor your AI mock interviews.
        </p>
      </div>

      {/* Form Card */}
      <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl">
        
        {savedSuccess && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-sm font-semibold">
            <Check className="w-5 h-5" />
            <span>Profile updated successfully!</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Target Role
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Briefcase className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  required
                  value={profile.target_role || ''}
                  onChange={(e) => setProfile({ ...profile, target_role: e.target.value })}
                  placeholder="e.g. Full Stack Engineer"
                  className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-slate-700/80 rounded-xl text-sm text-white focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Experience Level
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Award className="w-4 h-4" />
                </div>
                <select
                  value={profile.experience_level || 'Intermediate'}
                  onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                  className="w-full pl-10 pr-4 py-2.5 bg-dark-900 border border-slate-700/80 rounded-xl text-sm text-white focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  <option value="Entry">Entry Level (0-2 years)</option>
                  <option value="Intermediate">Intermediate / Mid-Level (2-5 years)</option>
                  <option value="Senior">Senior (5-8 years)</option>
                  <option value="Lead">Lead / Staff (8+ years)</option>
                </select>
              </div>
            </div>

          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Key Skills & Technologies (Comma-separated)
            </label>
            <textarea
              rows={2}
              value={profile.skills || ''}
              onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
              placeholder="e.g. React, Node.js, Python, PostgreSQL, AWS, Microservices"
              className="w-full p-3 bg-dark-900 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Bio / Candidate Summary
            </label>
            <textarea
              rows={3}
              value={profile.bio || ''}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
              placeholder="Brief summary of your background, career interests, and past projects..."
              className="w-full p-3 bg-dark-900 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Resume Text / Past Project Highlights (Optional)
            </label>
            <textarea
              rows={4}
              value={profile.resume_text || ''}
              onChange={(e) => setProfile({ ...profile, resume_text: e.target.value })}
              placeholder="Paste relevant resume bullet points to allow the AI to adapt behavioral questions to your experience..."
              className="w-full p-3 bg-dark-900 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white text-sm font-semibold shadow-lg shadow-brand-600/30 transition-all disabled:opacity-50"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Profile</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>

    </div>
  );
};
