import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../api/supabaseClient';
import { useAuth } from '../../context/AuthContext';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import apiClient from '../../api/client';

export const AuthCallback = () => {
  const [statusMessage, setStatusMessage] = useState('Authenticating with Google...');
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError || !session) {
          throw new Error(sessionError?.message || 'Failed to retrieve OAuth session.');
        }

        const supabaseUser = session.user;
        const email = supabaseUser.email;
        const name = supabaseUser.user_metadata?.full_name || supabaseUser.user_metadata?.name || email.split('@')[0];
        const role = localStorage.getItem('careervoice_oauth_role') || 'student';

        setStatusMessage(`Welcome ${name}! Signing in...`);

        // Authenticate directly via dedicated Google OAuth endpoint
        const userData = await loginWithGoogle(email, name, role);

        setStatusMessage('Success! Redirecting to dashboard...');
        setTimeout(() => {
          if (userData.role === 'recruiter') {
            navigate('/recruiter/dashboard');
          } else {
            navigate('/dashboard');
          }
        }, 1000);

      } catch (err) {
        console.error('OAuth Callback Error:', err);
        setError(err.message || 'Google authentication failed.');
      }
    };

    handleAuthCallback();
  }, [navigate, loginWithGoogle]);

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="glass-panel p-8 rounded-2xl max-w-md w-full text-center space-y-4 border border-slate-800 shadow-2xl">
        {error ? (
          <div className="space-y-4">
            <div className="inline-flex p-3 rounded-full bg-red-500/10 text-red-400">
              <AlertCircle className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">Authentication Failed</h3>
            <p className="text-sm text-slate-400">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-sm transition-all"
            >
              Back to Sign In
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="inline-flex p-3 rounded-full bg-brand-500/10 text-brand-400 animate-pulse">
              <Loader2 className="w-8 h-8 animate-spin" />
            </div>
            <h3 className="text-xl font-bold text-white">Completing Sign-In</h3>
            <p className="text-sm text-slate-400">{statusMessage}</p>
          </div>
        )}
      </div>
    </div>
  );
};
