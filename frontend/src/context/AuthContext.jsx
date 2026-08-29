import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';
import { auth, googleProvider } from '../api/firebaseClient';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut as firebaseSignOut,
  updateProfile
} from 'firebase/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('careervoice_user');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('careervoice_token') || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCurrentUser = async () => {
      const storedToken = localStorage.getItem('careervoice_token');
      if (storedToken) {
        try {
          const res = await apiClient.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('careervoice_user', JSON.stringify(res.data));
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          logout();
        }
      }
      setLoading(false);
    };

    fetchCurrentUser();
  }, []);

  const login = async (email, password) => {
    // 1. Firebase Authentication (with graceful fallback for demo accounts)
    let firebaseUser = null;
    try {
      if (auth?.app?.options?.apiKey && !auth.app.options.apiKey.includes('DummyKey')) {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        firebaseUser = userCredential.user;
      }
    } catch (fbErr) {
      console.warn('Firebase Login notice:', fbErr.message);
    }

    // 2. Synchronize / login with backend API
    const res = await apiClient.post('/auth/login', { email, password });
    const { access_token, refresh_token, user: userData } = res.data;

    localStorage.setItem('careervoice_token', access_token);
    localStorage.setItem('careervoice_refresh_token', refresh_token);
    localStorage.setItem('careervoice_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const register = async (name, email, password, role = 'student') => {
    // 1. Firebase User Creation
    try {
      if (auth?.app?.options?.apiKey && !auth.app.options.apiKey.includes('DummyKey')) {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        if (name && userCredential.user) {
          await updateProfile(userCredential.user, { displayName: name });
        }
      }
    } catch (fbErr) {
      console.warn('Firebase Register notice:', fbErr.message);
    }

    // 2. Synchronize / register with backend API & Database
    const res = await apiClient.post('/auth/register', { name, email, password, role });
    const { access_token, refresh_token, user: userData } = res.data;

    localStorage.setItem('careervoice_token', access_token);
    localStorage.setItem('careervoice_refresh_token', refresh_token);
    localStorage.setItem('careervoice_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const loginWithGoogle = async (email, name = null, role = 'student') => {
    const res = await apiClient.post('/auth/google', { email, name, role });
    const { access_token, refresh_token, user: userData } = res.data;

    localStorage.setItem('careervoice_token', access_token);
    localStorage.setItem('careervoice_refresh_token', refresh_token);
    localStorage.setItem('careervoice_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);
    return userData;
  };

  const loginWithFirebaseGoogle = async (role = 'student') => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const fbUser = result.user;
      return await loginWithGoogle(fbUser.email, fbUser.displayName, role);
    } catch (err) {
      console.error('Firebase Google Sign-In error:', err);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await firebaseSignOut(auth);
    } catch (err) {
      console.warn('Firebase signout note:', err);
    }

    // Purge all token and session storage
    localStorage.clear();
    sessionStorage.clear();

    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      loginWithGoogle,
      loginWithFirebaseGoogle,
      logout,
      setUser
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

