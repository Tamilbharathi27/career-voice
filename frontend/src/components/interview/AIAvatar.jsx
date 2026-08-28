import React from 'react';
import { Bot, Mic, Sparkles, Brain, Volume2 } from 'lucide-react';

export const AIAvatar = ({ state = 'idle', role = 'Technical Interviewer' }) => {
  // state: 'idle' | 'speaking' | 'listening' | 'thinking' | 'analyzing'

  const stateConfig = {
    idle: {
      label: 'Ready',
      icon: Bot,
      color: 'from-slate-600 to-slate-700',
      ringColor: 'border-slate-700',
      pulse: false,
      textColor: 'text-slate-400',
    },
    speaking: {
      label: 'AI Interviewer Speaking...',
      icon: Volume2,
      color: 'from-brand-600 to-accent-600',
      ringColor: 'border-brand-500/60',
      pulse: true,
      textColor: 'text-brand-400',
    },
    listening: {
      label: 'Listening to your answer...',
      icon: Mic,
      color: 'from-emerald-600 to-teal-500',
      ringColor: 'border-emerald-500/60',
      pulse: true,
      textColor: 'text-emerald-400',
    },
    thinking: {
      label: 'Transcribing & Processing...',
      icon: Brain,
      color: 'from-amber-600 to-orange-500',
      ringColor: 'border-amber-500/60',
      pulse: true,
      textColor: 'text-amber-400',
    },
    analyzing: {
      label: 'Analyzing NLP, Acoustics & Scoring...',
      icon: Sparkles,
      color: 'from-purple-600 to-pink-500',
      ringColor: 'border-purple-500/60',
      pulse: true,
      textColor: 'text-purple-400',
    },
  };

  const current = stateConfig[state] || stateConfig.idle;
  const IconComponent = current.icon;

  return (
    <div className="flex flex-col items-center justify-center p-6 text-center">
      {/* Outer Pulse Rings */}
      <div className="relative flex items-center justify-center">
        {current.pulse && (
          <>
            <div className={`absolute w-36 h-36 rounded-full border-2 ${current.ringColor} animate-ping opacity-30`} />
            <div className={`absolute w-32 h-32 rounded-full border-2 ${current.ringColor} animate-pulse-slow opacity-50`} />
          </>
        )}

        {/* Central Avatar Orb */}
        <div className={`relative z-10 w-24 h-24 rounded-full bg-gradient-to-tr ${current.color} p-1 shadow-2xl flex items-center justify-center transition-all duration-500 ${current.pulse ? 'scale-105 shadow-brand-500/30' : ''}`}>
          <div className="w-full h-full rounded-full bg-dark-950/40 backdrop-blur-sm flex items-center justify-center">
            <IconComponent className={`w-10 h-10 text-white ${current.pulse ? 'animate-bounce' : ''}`} />
          </div>
        </div>
      </div>

      {/* State Status Badge */}
      <div className="mt-4 flex flex-col items-center space-y-1">
        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800">
          <span className={`w-2 h-2 rounded-full ${current.pulse ? 'animate-ping' : ''} ${state === 'listening' ? 'bg-emerald-400' : state === 'speaking' ? 'bg-brand-400' : state === 'analyzing' ? 'bg-purple-400' : 'bg-slate-400'}`} />
          <span className={`text-xs font-semibold tracking-wide ${current.textColor}`}>
            {current.label}
          </span>
        </div>
        <span className="text-xs text-slate-400 font-medium">{role}</span>
      </div>
    </div>
  );
};
