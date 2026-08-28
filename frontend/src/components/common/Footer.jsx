import React from 'react';
import { Mic2, Sparkles, Heart } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-dark-950/60 py-8 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded-lg bg-brand-600/30 flex items-center justify-center">
            <Mic2 className="w-3.5 h-3.5 text-brand-400" />
          </div>
          <span className="text-sm font-semibold text-slate-300">
            Career<span className="text-brand-500">Voice</span> AI
          </span>
          <span className="text-xs text-slate-500">| Modern Mock Interview Platform</span>
        </div>

        <div className="flex items-center space-x-6 text-xs text-slate-400">
          <span className="flex items-center space-x-1">
            <span>Powered by</span>
            <Sparkles className="w-3 h-3 text-accent-400 inline" />
            <span className="text-slate-300 font-medium">Whisper, FastAPI & React</span>
          </span>
          <span>© {new Date().getFullYear()} Career Voice. All rights reserved.</span>
        </div>

      </div>
    </footer>
  );
};
