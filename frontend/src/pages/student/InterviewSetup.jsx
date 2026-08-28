import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';
import { 
  Sparkles, 
  Layers, 
  Cpu, 
  Server, 
  BrainCircuit, 
  Database,
  Smartphone,
  Cloud,
  ShieldCheck,
  MessageSquare, 
  ArrowRight, 
  Loader2, 
  Check, 
  Sliders,
  Volume2,
  DollarSign,
  Activity,
  Wrench,
  Scale,
  Palette,
  Users,
  Code
} from 'lucide-react';

export const InterviewSetup = () => {
  const navigate = useNavigate();
  const [domains, setDomains] = useState({
    'Full Stack Engineer': {
      description: 'End-to-end web applications, frontend frameworks, backend APIs, and databases.',
      stacks: ['MERN Stack (MongoDB, Express, React, Node)', 'React.js & Node.js', 'Next.js & TypeScript', 'Python FastAPI & React']
    },
    'Frontend Engineer': {
      description: 'Client-side applications, modern JavaScript frameworks, web performance, and responsive UI.',
      stacks: ['React.js & Hooks', 'Next.js & Server Components', 'Vue.js 3 & Nuxt', 'Angular & RxJS', 'TailwindCSS & UI Design Systems']
    },
    'Backend Engineer': {
      description: 'Server-side business logic, API gateways, database architectures, microservices, and scaling.',
      stacks: ['Node.js & Express / NestJS', 'Python FastAPI & AsyncIO', 'Python Django & ORM', 'Java Spring Boot & Hibernate', 'Go (Golang) Microservices']
    },
    'AI / ML Engineer': {
      description: 'Machine learning models, deep learning architectures, LLMs, NLP, and MLOps.',
      stacks: ['Deep Learning & PyTorch / TensorFlow', 'LLMs, Prompting & RAG (LangChain / LlamaIndex)', 'Computer Vision & OpenCV', 'MLOps, MLflow & Model Deployment']
    }
  });

  const [selectedRole, setSelectedRole] = useState('Full Stack Engineer');
  const [selectedTechStack, setSelectedTechStack] = useState(['MERN Stack (MongoDB, Express, React, Node)']);
  const [difficulty, setDifficulty] = useState('intermediate');
  const [questionCount, setQuestionCount] = useState(3);
  const [interviewType, setInterviewType] = useState('mixed');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const res = await apiClient.get('/interviews/domains');
        if (res.data && Object.keys(res.data).length > 0) {
          setDomains(res.data);
          const firstRole = Object.keys(res.data)[0];
          if (!selectedRole || !res.data[selectedRole]) {
            setSelectedRole(firstRole);
            if (res.data[firstRole]?.stacks?.length > 0) {
              setSelectedTechStack([res.data[firstRole].stacks[0]]);
            }
          }
        }
      } catch (err) {
        console.warn('Using default fallback domain catalog.');
      }
    };
    fetchDomains();
  }, []);

  const handleRoleSelect = (roleName) => {
    setSelectedRole(roleName);
    const domainData = domains[roleName];
    if (domainData && domainData.stacks && domainData.stacks.length > 0) {
      setSelectedTechStack([domainData.stacks[0]]);
    } else {
      setSelectedTechStack([]);
    }
  };

  const toggleTechStack = (stackName) => {
    if (selectedTechStack.includes(stackName)) {
      if (selectedTechStack.length > 1) {
        setSelectedTechStack(selectedTechStack.filter(s => s !== stackName));
      }
    } else {
      setSelectedTechStack([...selectedTechStack, stackName]);
    }
  };

  const domainIcons = {
    'Full Stack Engineer': Layers,
    'Frontend Engineer': Cpu,
    'Backend Engineer': Server,
    'AI / ML Engineer': BrainCircuit,
    'Data Science & Analytics': Database,
    'Mobile App Developer': Smartphone,
    'DevOps & Cloud Systems': Cloud,
    'Cybersecurity & Network Security': ShieldCheck,
    'Product Management': Sliders,
    'Finance & Accounting': DollarSign,
    'Healthcare & Clinical': Activity,
    'Core Engineering (Mech/Civil/Elec)': Wrench,
    'Legal & Corporate Compliance': Scale,
    'Creative & UI/UX Design': Palette,
    'Customer-Facing & HR': Users,
    'Behavioral & Leadership': MessageSquare,
  };

  const handleStartInterview = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.post('/interviews/sessions', {
        role: selectedRole,
        difficulty,
        question_count: questionCount,
        interview_type: interviewType,
        tech_stack: selectedTechStack
      });

      const sessionId = res.data.session_id;
      navigate(`/interview/room/${sessionId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initialize interview session.');
      setLoading(false);
    }
  };

  const activeDomain = domains[selectedRole] || { stacks: [] };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Interactive AI Interview Simulator</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Configure Your Tailored Voice Interview
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Choose your target domain and technologies you know. Our agent will tailor questions specifically to your tech stack.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold">
          {error}
        </div>
      )}

      {/* 1. Domain Selection */}
      <div className="space-y-4">
        <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
          1. Select Target Domain / Track
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.keys(domains).map((domainName) => {
            const Icon = domainIcons[domainName] || Layers;
            const isSelected = selectedRole === domainName;
            const domainInfo = domains[domainName];

            return (
              <button
                key={domainName}
                type="button"
                onClick={() => handleRoleSelect(domainName)}
                className={`p-5 rounded-2xl border text-left transition-all relative overflow-hidden group ${
                  isSelected
                    ? 'glass-panel bg-brand-900/30 border-brand-500 shadow-xl shadow-brand-500/15 ring-1 ring-brand-500'
                    : 'glass-panel hover:border-slate-700 bg-dark-900/40 text-slate-400'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${
                    isSelected ? 'bg-brand-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  {isSelected && (
                    <div className="w-5 h-5 rounded-full bg-brand-500 text-white flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </div>
                  )}
                </div>

                <h3 className={`text-base font-bold mb-1 ${isSelected ? 'text-white' : 'text-slate-200'}`}>
                  {domainName}
                </h3>
                <p className="text-xs text-slate-400 line-clamp-2">
                  {domainInfo?.description || 'Technical & domain competencies'}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Tech Stack Specialization Selection */}
      {activeDomain?.stacks && activeDomain.stacks.length > 0 && (
        <div className="glass-panel p-6 rounded-2xl border border-brand-500/30 bg-dark-900/60 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Code className="w-4 h-4 text-brand-400" />
              <label className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                2. Select Technologies / Tech Stacks You Know
              </label>
            </div>
            <span className="text-xs text-slate-400">
              {selectedTechStack.length} selected
            </span>
          </div>

          <p className="text-xs text-slate-400">
            The AI interviewer will customize questions and evaluation metrics specifically for these technologies:
          </p>

          <div className="flex flex-wrap gap-2 pt-2">
            {activeDomain.stacks.map((stack) => {
              const isChecked = selectedTechStack.includes(stack);
              return (
                <button
                  key={stack}
                  type="button"
                  onClick={() => toggleTechStack(stack)}
                  className={`px-4 py-2.5 rounded-xl text-xs font-semibold border transition-all flex items-center space-x-2 ${
                    isChecked
                      ? 'bg-brand-600/30 border-brand-500 text-white shadow-md shadow-brand-500/10 ring-1 ring-brand-500'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                  }`}
                >
                  <div className={`w-4 h-4 rounded flex items-center justify-center border ${
                    isChecked ? 'bg-brand-500 border-brand-400 text-white' : 'border-slate-700 bg-slate-800'
                  }`}>
                    {isChecked && <Check className="w-3 h-3 stroke-[3]" />}
                  </div>
                  <span>{stack}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 3. Difficulty & Question Count */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Difficulty */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
            3. Interview Difficulty Level
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: 'entry', label: 'Entry Level', sub: 'Foundations' },
              { id: 'intermediate', label: 'Mid-Level', sub: 'Standard Tech' },
              { id: 'senior', label: 'Senior Lead', sub: 'Deep Architecture' },
            ].map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setDifficulty(d.id)}
                className={`p-3 rounded-xl border text-center transition-all ${
                  difficulty === d.id
                    ? 'bg-brand-600/20 border-brand-500 text-white shadow-md'
                    : 'bg-dark-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="text-xs font-bold">{d.label}</div>
                <div className="text-[10px] text-slate-400">{d.sub}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Question Count */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
            4. Session Duration / Question Count
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { count: 2, label: 'Quick Sprint', time: '~4 mins' },
              { count: 3, label: 'Standard (Recommended)', time: '~7 mins' },
              { count: 5, label: 'Full Mock', time: '~12 mins' },
            ].map((q) => (
              <button
                key={q.count}
                type="button"
                onClick={() => setQuestionCount(q.count)}
                className={`p-3 rounded-xl border text-center transition-all ${
                  questionCount === q.count
                    ? 'bg-brand-600/20 border-brand-500 text-white shadow-md'
                    : 'bg-dark-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="text-xs font-bold">{q.count} Questions</div>
                <div className="text-[10px] text-slate-400">{q.time}</div>
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* Launch CTA */}
      <div className="flex flex-col sm:flex-row items-center justify-between p-6 rounded-2xl glass-panel border border-brand-500/30 bg-gradient-to-r from-brand-950/40 via-dark-900 to-accent-950/40 gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
            <Volume2 className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">
              {selectedRole} — {selectedTechStack.length > 0 ? selectedTechStack[0].split('(')[0] : 'Standard'} Voice Session
            </h4>
            <p className="text-xs text-slate-400">Browser microphone permissions will be requested on start.</p>
          </div>
        </div>

        <button
          onClick={handleStartInterview}
          disabled={loading}
          className="w-full sm:w-auto flex items-center justify-center space-x-2 px-8 py-4 rounded-xl bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-500 hover:to-accent-500 text-white font-extrabold text-sm shadow-xl shadow-brand-600/30 transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <span>Enter Voice Interview Studio</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

    </div>
  );
};
