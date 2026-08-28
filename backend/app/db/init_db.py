import json
import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User, Profile, UserRole
from app.models.interview import InterviewSession, Question, Answer, InterviewStatus, QuestionType
from app.models.evaluation import AnswerEvaluation, SessionReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Complete Domain Catalog Matrix mapping domains to descriptions and specific tech stack specializations
DOMAIN_CATALOG = {
    "Full Stack Engineer": {
        "description": "End-to-end web applications, frontend frameworks, backend APIs, and database architectures.",
        "icon": "Layers",
        "stacks": [
            "MERN Stack (MongoDB, Express, React, Node)",
            "React.js & Node.js",
            "Next.js & TypeScript",
            "Python FastAPI & React",
            "Python Django & Vue.js",
            "Java Spring Boot & Angular",
            "PostgreSQL & REST APIs"
        ]
    },
    "Frontend Engineer": {
        "description": "Client-side applications, modern JavaScript frameworks, web performance, and responsive UI/UX.",
        "icon": "Cpu",
        "stacks": [
            "React.js & Hooks",
            "Next.js & Server Components",
            "Vue.js 3 & Nuxt",
            "Angular & RxJS",
            "TailwindCSS & UI Design Systems",
            "Web Performance & Accessibility (a11y)",
            "TypeScript & State Management"
        ]
    },
    "Backend Engineer": {
        "description": "Server-side business logic, API gateways, database architectures, microservices, and scaling.",
        "icon": "Server",
        "stacks": [
            "Node.js & Express / NestJS",
            "Python FastAPI & AsyncIO",
            "Python Django & ORM",
            "Java Spring Boot & Hibernate",
            "Go (Golang) Microservices",
            "C# .NET Core & Entity Framework",
            "PostgreSQL, MySQL & Redis / MongoDB"
        ]
    },
    "AI / ML Engineer": {
        "description": "Machine learning models, deep learning architectures, Large Language Models (LLMs), NLP, and MLOps.",
        "icon": "BrainCircuit",
        "stacks": [
            "Deep Learning & PyTorch / TensorFlow",
            "LLMs, Prompting & RAG (LangChain / LlamaIndex)",
            "Computer Vision & OpenCV",
            "MLOps, MLflow & Model Deployment",
            "NLP & Transformers (Hugging Face)",
            "Data Science & Scikit-Learn"
        ]
    },
    "Data Science & Analytics": {
        "description": "Data pipelines, predictive analytics, SQL databases, statistical modeling, and BI dashboards.",
        "icon": "Database",
        "stacks": [
            "SQL & Data Warehousing (Snowflake / BigQuery)",
            "Python Pandas & NumPy Analysis",
            "Tableau & PowerBI Analytics",
            "Statistical Modeling & A/B Testing",
            "Spark & Distributed Data Processing"
        ]
    },
    "Mobile App Developer": {
        "description": "Cross-platform and native mobile application engineering for iOS and Android devices.",
        "icon": "Smartphone",
        "stacks": [
            "React Native & Expo",
            "Flutter & Dart",
            "iOS Native (Swift & SwiftUI)",
            "Android Native (Kotlin & Jetpack Compose)"
        ]
    },
    "DevOps & Cloud Systems": {
        "description": "Infrastructure automation, container orchestration, CI/CD pipelines, cloud administration, and monitoring.",
        "icon": "Cloud",
        "stacks": [
            "Kubernetes & Docker Containerization",
            "AWS Cloud Architecture & Services",
            "CI/CD Pipelines (GitHub Actions / Jenkins)",
            "Infrastructure as Code (Terraform / Ansible)",
            "Observability & Monitoring (Prometheus / Grafana)"
        ]
    },
    "Cybersecurity & Network Security": {
        "description": "Application security, network defense, ethical hacking, identity management, and incident response.",
        "icon": "ShieldCheck",
        "stacks": [
            "Ethical Hacking & Penetration Testing",
            "Application Security & OWASP Top 10",
            "Cloud Security & IAM",
            "Incident Response & Digital Forensics"
        ]
    },
    "Product Management": {
        "description": "Product strategy, roadmap prioritization, market research, requirements definition, and agile delivery.",
        "icon": "Sliders",
        "stacks": [
            "Agile / Scrum & Sprint Planning",
            "Technical Product Specs & APIs",
            "Product Analytics & Growth (Mixpanel/Amplitude)",
            "B2B SaaS Roadmaps & Stakeholder Alignment"
        ]
    },
    "Finance & Accounting": {
        "description": "Financial modeling, corporate accounting standards, audit compliance, and investment analysis.",
        "icon": "DollarSign",
        "stacks": [
            "Financial Modeling & DCF Valuation",
            "Corporate Accounting (GAAP / IFRS)",
            "Audit, Reconciliation & Internal Controls",
            "Risk Management & Investment Analysis"
        ]
    },
    "Healthcare & Clinical": {
        "description": "Clinical protocols, patient triage, health informatics, EHR compliance, and diagnostic communication.",
        "icon": "Activity",
        "stacks": [
            "Clinical Protocol & Patient Triage",
            "Healthcare IT & HIPAA / EHR Systems",
            "Medical Diagnostics & Patient Communication",
            "Telehealth & Patient Safety Protocols"
        ]
    },
    "Core Engineering (Mech/Civil/Elec)": {
        "description": "Structural analysis, CAD design, power systems, microcontrollers, and QA fabrication.",
        "icon": "Wrench",
        "stacks": [
            "CAD & Structural FEA Stress Analysis",
            "Embedded Systems & Microcontrollers",
            "Power Systems & Circuit Design",
            "QA Testing & Fabrication Specifications"
        ]
    },
    "Legal & Corporate Compliance": {
        "description": "Contract negotiation, risk mitigation, corporate governance, and regulatory compliance.",
        "icon": "Scale",
        "stacks": [
            "Contract Law & Indemnification Clauses",
            "Regulatory Compliance (GDPR / SOC2 / HIPAA)",
            "Corporate Governance & Vendor Risk"
        ]
    },
    "Creative & UI/UX Design": {
        "description": "User experience research, interaction design, wireframing, component design systems, and usability.",
        "icon": "Palette",
        "stacks": [
            "UI Design & Design Systems (Figma)",
            "User Research & Usability Testing",
            "Interaction Design & Dynamic Wireframing"
        ]
    },
    "Customer-Facing & HR": {
        "description": "Talent sourcing, client retention, conflict resolution, equity strategies, and HR policy design.",
        "icon": "Users",
        "stacks": [
            "Technical Recruitment & Sourcing",
            "Customer Success & Enterprise Retention",
            "Talent Strategy & DEI Frameworks",
            "HR Policy & Conflict De-escalation"
        ]
    },
    "Behavioral & Leadership": {
        "description": "STAR behavioral frameworks, executive leadership, conflict navigation, and team agility.",
        "icon": "MessageSquare",
        "stacks": [
            "Executive Leadership & Strategy",
            "STAR Framework Storytelling",
            "Conflict Resolution & Team Agility"
        ]
    }
}

QUESTION_BANK = {
    # 1. Full Stack Engineer
    "Full Stack Engineer": [
        {
            "question_text": "Could you walk me through the architecture of a full-stack web application you built, explaining how frontend state syncs with backend REST/GraphQL APIs and the database?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Full-Stack Architecture",
            "expected_keywords": json.dumps(["React", "API", "database", "state", "backend", "REST", "Node", "MongoDB", "Express", "PostgreSQL"]),
            "tech_stack": "MERN Stack (MongoDB, Express, React, Node)"
        },
        {
            "question_text": "In a MERN stack application, how do you structure Express middleware for JWT authentication and securely pass user identity down to MongoDB query operations?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "MERN & Backend Auth",
            "expected_keywords": json.dumps(["Express", "JWT", "middleware", "MongoDB", "Mongoose", "bearer token", "req.user"]),
            "tech_stack": "MERN Stack (MongoDB, Express, React, Node)"
        },
        {
            "question_text": "How do you handle client-side caching and state updates in React when dealing with rapid real-time updates from Node.js server endpoints?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "React & Node State Sync",
            "expected_keywords": json.dumps(["React Query", "Redux", "WebSockets", "useEffect", "optimistic UI", "Node.js"]),
            "tech_stack": "React.js & Node.js"
        },
        {
            "question_text": "Tell me about a challenging full-stack production bug you encountered across the network boundary. How did you isolate whether it was in frontend state or backend database handlers?",
            "question_type": QuestionType.BEHAVIORAL.value,
            "competency": "Full-Stack Debugging",
            "expected_keywords": json.dumps(["network tab", "server logs", "stack trace", "reproduce", "root cause", "post-mortem"])
        }
    ],

    # 2. Frontend Engineer
    "Frontend Engineer": [
        {
            "question_text": "Can you explain how the React Virtual DOM diffing algorithm works, and how custom hooks and memoization (useMemo, useCallback) prevent unnecessary re-renders?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "React Architecture & Performance",
            "expected_keywords": json.dumps(["Virtual DOM", "reconciliation", "diffing", "useMemo", "useCallback", "memo", "props"]),
            "tech_stack": "React.js & Hooks"
        },
        {
            "question_text": "In Next.js, how do Server Components differ from Client Components, and how do you decide when to fetch data at build-time vs request-time?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Next.js SSR & Rendering",
            "expected_keywords": json.dumps(["Server Components", "SSR", "SSG", "ISR", "use client", "hydration", "bundle size"]),
            "tech_stack": "Next.js & Server Components"
        },
        {
            "question_text": "How do you enforce WCAG accessibility (a11y) guidelines and responsive design across complex dynamic design systems?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Accessibility & Design Systems",
            "expected_keywords": json.dumps(["ARIA", "semantic HTML", "keyboard focus", "screen reader", "TailwindCSS", "media queries"]),
            "tech_stack": "TailwindCSS & UI Design Systems"
        }
    ],

    # 3. Backend Engineer
    "Backend Engineer": [
        {
            "question_text": "How would you design a distributed rate-limiting middleware in Node.js or Python FastAPI using Redis sliding windows to prevent API abuse?",
            "question_type": QuestionType.SYSTEM_DESIGN.value,
            "competency": "API & Rate Limiting",
            "expected_keywords": json.dumps(["Redis", "sliding window", "token bucket", "FastAPI", "Express", "middleware", "429 Too Many Requests"]),
            "tech_stack": "Node.js & Express / NestJS"
        },
        {
            "question_text": "Explain ACID properties in relational databases (PostgreSQL/MySQL) versus eventual consistency in NoSQL databases, and how indexing impacts high-write throughput.",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Database Systems & Storage",
            "expected_keywords": json.dumps(["ACID", "PostgreSQL", "B-tree index", "replication", "eventual consistency", "NoSQL"]),
            "tech_stack": "PostgreSQL, MySQL & Redis / MongoDB"
        },
        {
            "question_text": "In Python FastAPI, how does asynchronous request processing (async/await) differ from synchronous blocking code, and how do background task queues prevent event loop starvation?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Async I/O & FastAPI",
            "expected_keywords": json.dumps(["async await", "event loop", "uvicorn", "Celery", "background tasks", "Pydantic"]),
            "tech_stack": "Python FastAPI & AsyncIO"
        }
    ],

    # 4. AI / ML Engineer
    "AI / ML Engineer": [
        {
            "question_text": "Can you explain the self-attention mechanism in Transformer architectures, and how multi-head attention computes Query, Key, and Value matrices in PyTorch?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Deep Learning & Transformers",
            "expected_keywords": json.dumps(["PyTorch", "attention", "query key value", "multi-head", "embeddings", "positional encoding"]),
            "tech_stack": "Deep Learning & PyTorch / TensorFlow"
        },
        {
            "question_text": "Walk me through how you design a Retrieval-Augmented Generation (RAG) system using vector databases like Pinecone/FAISS and LangChain to minimize LLM hallucinations.",
            "question_type": QuestionType.SYSTEM_DESIGN.value,
            "competency": "LLMs & RAG Architecture",
            "expected_keywords": json.dumps(["RAG", "vector database", "embeddings", "LangChain", "chunking", "cosine similarity", "hallucination"]),
            "tech_stack": "LLMs, Prompting & RAG (LangChain / LlamaIndex)"
        },
        {
            "question_text": "How do you detect data drift and concept drift in production ML models, and what automation triggers retraining in an MLOps pipeline?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "MLOps & Model Monitoring",
            "expected_keywords": json.dumps(["MLOps", "model drift", "feature store", "Evidently", "retraining", "MLflow", "distribution shift"]),
            "tech_stack": "MLOps, MLflow & Model Deployment"
        }
    ],

    # 5. Data Science & Analytics
    "Data Science & Analytics": [
        {
            "question_text": "How do you optimize complex SQL queries involving window functions, multi-table JOINs, and CTEs on millions of rows in Snowflake or BigQuery?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Data Warehousing & SQL",
            "expected_keywords": json.dumps(["SQL", "window functions", "partitioning", "BigQuery", "Snowflake", "CTE", "query execution plan"]),
            "tech_stack": "SQL & Data Warehousing (Snowflake / BigQuery)"
        },
        {
            "question_text": "Describe how you validate sample size, calculate statistical power, and control for p-hacking when evaluating A/B test results for product changes.",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "A/B Testing & Statistics",
            "expected_keywords": json.dumps(["A/B test", "p-value", "confidence interval", "sample size", "null hypothesis", "statistical power"]),
            "tech_stack": "Statistical Modeling & A/B Testing"
        }
    ],

    # 6. Mobile App Developer
    "Mobile App Developer": [
        {
            "question_text": "How do you manage mobile app offline state, local database synchronization (AsyncStorage/SQLite), and smooth 60fps animations in React Native or Flutter?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Mobile State & Performance",
            "expected_keywords": json.dumps(["React Native", "Flutter", "AsyncStorage", "SQLite", "reanimated", "bridge", "native thread"]),
            "tech_stack": "React Native & Expo"
        },
        {
            "question_text": "In iOS (Swift/SwiftUI) or Android (Kotlin), how do you prevent memory leaks caused by retain cycles and manage background execution tasks?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Native Mobile Memory Management",
            "expected_keywords": json.dumps(["Swift", "Kotlin", "retain cycle", "weak self", "ARC", "coroutines", "WorkManager"]),
            "tech_stack": "iOS Native (Swift & SwiftUI)"
        }
    ],

    # 7. DevOps & Cloud Systems
    "DevOps & Cloud Systems": [
        {
            "question_text": "Walk me through how you configure a Kubernetes Cluster with Helm charts, ingress controllers, auto-scaling (HPA), and zero-downtime rolling deployments.",
            "question_type": QuestionType.SYSTEM_DESIGN.value,
            "competency": "Kubernetes & Orchestration",
            "expected_keywords": json.dumps(["Kubernetes", "Helm", "HPA", "ingress", "pod", "rolling update", "declarative"]),
            "tech_stack": "Kubernetes & Docker Containerization"
        },
        {
            "question_text": "How do you structure modular Infrastructure as Code (IaC) with Terraform for AWS multi-environment setups (dev, staging, prod) using remote state locking?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Infrastructure as Code",
            "expected_keywords": json.dumps(["Terraform", "AWS", "S3 backend", "DynamoDB lock", "modules", "state drift", "plan"]),
            "tech_stack": "Infrastructure as Code (Terraform / Ansible)"
        }
    ],

    # 8. Cybersecurity & Network Security
    "Cybersecurity & Network Security": [
        {
            "question_text": "How do you audit web applications for OWASP Top 10 vulnerabilities like SQL Injection, Cross-Site Scripting (XSS), and Broken Access Control?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "AppSec & OWASP",
            "expected_keywords": json.dumps(["OWASP", "XSS", "SQLi", "CSRF", "sanitization", "content security policy", "penetration testing"]),
            "tech_stack": "Application Security & OWASP Top 10"
        }
    ],

    # 9. Product Management
    "Product Management": [
        {
            "question_text": "How do you prioritize competing technical debt vs user-facing features using frameworks like RICE or MoSCoW when engineering resources are tight?",
            "question_type": QuestionType.SITUATIONAL.value,
            "competency": "Roadmap & Prioritization",
            "expected_keywords": json.dumps(["RICE", "MoSCoW", "ROI", "trade-offs", "stakeholders", "technical debt"]),
            "tech_stack": "Agile / Scrum & Sprint Planning"
        }
    ],

    # 10. Finance & Accounting
    "Finance & Accounting": [
        {
            "question_text": "Walk me through building a Discounted Cash Flow (DCF) model, detailing how you determine Weighted Average Cost of Capital (WACC) and terminal value.",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Financial Modeling & Valuation",
            "expected_keywords": json.dumps(["DCF", "WACC", "free cash flow", "terminal value", "discount rate", "EBITDA"]),
            "tech_stack": "Financial Modeling & DCF Valuation"
        }
    ],

    # 11. Healthcare & Clinical
    "Healthcare & Clinical": [
        {
            "question_text": "How do you manage emergency clinical triage when patient volume exceeds bed capacity while adhering strictly to HIPAA and patient safety standards?",
            "question_type": QuestionType.SITUATIONAL.value,
            "competency": "Clinical Triage & Compliance",
            "expected_keywords": json.dumps(["triage", "acuity", "vital signs", "HIPAA", "escalation", "safety protocol"]),
            "tech_stack": "Clinical Protocol & Patient Triage"
        }
    ],

    # 12. Core Engineering
    "Core Engineering (Mech/Civil/Elec)": [
        {
            "question_text": "How do you perform Finite Element Analysis (FEA) stress calculations and select appropriate safety factors for high-vibration structural load cases?",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "FEA Structural Design",
            "expected_keywords": json.dumps(["FEA", "von Mises stress", "factor of safety", "yield strength", "CAD", "load cases"]),
            "tech_stack": "CAD & Structural FEA Stress Analysis"
        }
    ],

    # 13. Legal & Compliance
    "Legal & Corporate Compliance": [
        {
            "question_text": "How do you negotiate limitation of liability and indemnification clauses in SaaS enterprise vendor contracts to mitigate corporate legal risk?",
            "question_type": QuestionType.SITUATIONAL.value,
            "competency": "Contract Risk & Indemnification",
            "expected_keywords": json.dumps(["indemnification", "limitation of liability", "breach", "governing law", "risk allocation"]),
            "tech_stack": "Contract Law & Indemnification Clauses"
        }
    ],

    # 14. Creative & UI/UX Design
    "Creative & UI/UX Design": [
        {
            "question_text": "Walk me through your design system architecture in Figma, explaining how tokenization (color, spacing, typography) keeps UI components scalable across projects.",
            "question_type": QuestionType.TECHNICAL.value,
            "competency": "Figma & Design Systems",
            "expected_keywords": json.dumps(["Figma", "design tokens", "component library", "auto layout", "design system", "accessibility"]),
            "tech_stack": "UI Design & Design Systems (Figma)"
        }
    ],

    # 15. Customer-Facing & HR
    "Customer-Facing & HR": [
        {
            "question_text": "Describe how you design a structured technical recruiting workflow that minimizes unconscious bias while evaluating engineering competency.",
            "question_type": QuestionType.BEHAVIORAL.value,
            "competency": "Recruitment & Talent Strategy",
            "expected_keywords": json.dumps(["rubric", "structured interview", "unconscious bias", "competency matrix", "sourcing"]),
            "tech_stack": "Technical Recruitment & Sourcing"
        }
    ],

    # 16. Behavioral & Leadership
    "Behavioral & Leadership": [
        {
            "question_text": "Tell me about a high-stakes crisis where team members disagreed on technical strategy under a tight deadline. How did you steer alignment using the STAR framework?",
            "question_type": QuestionType.BEHAVIORAL.value,
            "competency": "STAR Crisis Leadership",
            "expected_keywords": json.dumps(["Situation", "Task", "Action", "Result", "alignment", "de-escalation", "decision"]),
            "tech_stack": "STAR Framework Storytelling"
        }
    ]
}

def init_db(db: Session) -> None:
    """Create all database tables and seed demo users."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Check for student user
    student = db.query(User).filter(User.email == "student@careervoice.ai").first()
    if not student:
        logger.info("Seeding demo student user...")
        student = User(
            name="Alex Chen",
            email="student@careervoice.ai",
            password_hash=get_password_hash("password123"),
            role=UserRole.STUDENT.value
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        profile = Profile(
            user_id=student.id,
            target_role="Full Stack Engineer",
            experience_level="Intermediate",
            skills="React, TypeScript, Python, FastAPI, SQL, Docker, Redis",
            bio="Passionate software engineer preparing for tech company mock interviews."
        )
        db.add(profile)
        db.commit()

    # Check for recruiter user
    recruiter = db.query(User).filter(User.email == "recruiter@careervoice.ai").first()
    if not recruiter:
        logger.info("Seeding demo recruiter user...")
        recruiter = User(
            name="Sarah Jenkins",
            email="recruiter@careervoice.ai",
            password_hash=get_password_hash("password123"),
            role=UserRole.RECRUITER.value
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

        recruiter_profile = Profile(
            user_id=recruiter.id,
            target_role="Technical Talent Partner",
            experience_level="Lead",
            skills="Technical Hiring, Talent Analytics, Interview Design",
            bio="Lead Technical Recruiter evaluating candidates for high-growth tech roles."
        )
        db.add(recruiter_profile)
        db.commit()

    logger.info("Database initialized successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    db.close()
