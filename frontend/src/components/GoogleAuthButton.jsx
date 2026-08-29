import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const GoogleAuthButton = ({ label = "Continue with Google", role = "student", onError }) => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { loginWithFirebaseGoogle } = useAuth();

  const handleGoogleSignIn = async () => {
    setLoading(true);
    if (onError) onError(null);

    try {
      // Direct Firebase Google OAuth Popup
      const userData = await loginWithFirebaseGoogle(role);
      
      if (userData.role === 'recruiter') {
        navigate('/recruiter/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Firebase Google Sign-In Error:', err);
      let errorMsg = 'Google authentication failed. Please try again.';
      
      if (err.code === 'auth/popup-closed-by-user') {
        errorMsg = 'Sign-in popup was closed before completing verification.';
      } else if (err.code === 'auth/unauthorized-domain') {
        errorMsg = 'This domain is not authorized in Firebase Console -> Authentication -> Settings -> Authorized domains.';
      } else if (err.code === 'auth/popup-blocked') {
        errorMsg = 'Popup blocked by browser. Please allow popups for this site.';
      } else if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      if (onError) onError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleGoogleSignIn}
      disabled={loading}
      className="w-full flex items-center justify-center space-x-3 py-2.5 px-4 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 hover:border-slate-600 text-slate-200 text-sm font-semibold shadow-md transition-all disabled:opacity-60 disabled:cursor-not-allowed group"
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
      ) : (
        <svg className="w-4 h-4 transition-transform group-hover:scale-105" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
          />
        </svg>
      )}
      <span>{label}</span>
    </button>
  );
};


