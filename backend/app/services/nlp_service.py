import re
import json
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# STAR Method Markers
STAR_PATTERNS = {
    "situation": [
        r"\bwhen I was\b", r"\bat my previous\b", r"\bin my last role\b", 
        r"\bthe project was\b", r"\bwe were working on\b", r"\bthe context was\b", r"\bour team was\b"
    ],
    "task": [
        r"\bmy responsibility\b", r"\bi needed to\b", r"\bthe goal was\b", 
        r"\bthe challenge was\b", r"\bwe had to\b", r"\bmy objective\b", r"\bi was tasked with\b"
    ],
    "action": [
        r"\bi decided to\b", r"\bi implemented\b", r"\bi built\b", r"\bi designed\b", 
        r"\bi wrote\b", r"\bi refactored\b", r"\bi resolved\b", r"\bmy approach was\b", r"\bi led\b"
    ],
    "result": [
        r"\bas a result\b", r"\bwhich resulted in\b", r"\bwe achieved\b", 
        r"\bdecreased by\b", r"\bincreased by\b", r"\bimproved\b", r"\bthe outcome was\b", r"\bsuccessfully delivered\b"
    ]
}

# Positive confidence indicators and weak hedge markers
CONFIDENCE_MARKERS = [
    r"\bconfident\b", r"\bdefinitely\b", r"\bensured\b", r"\bexecuted\b", 
    r"\boptimized\b", r"\bspearheaded\b", r"\bdelivered\b", r"\bexpert\b", r"\bmastered\b"
]

HESITATION_MARKERS = [
    r"\bi think maybe\b", r"\bi guess\b", r"\bnot really sure\b", 
    r"\bprobably\b", r"\bsomewhat\b", r"\bsort of maybe\b"
]

class NLPService:
    """Natural Language Processing and semantic evaluation engine."""

    def analyze_answer(self, question_text: str, transcript: str, expected_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Evaluate spoken transcript for semantic relevance, keyword coverage, and STAR structure."""
        if not transcript or len(transcript.strip()) < 5:
            return {
                "relevance_score": 0.0,
                "keyword_coverage_score": 0.0,
                "star_score": 0.0,
                "completeness_score": 0.0,
                "sentiment_score": 0.0,
                "overall_nlp_score": 0.0,
                "matched_keywords": [],
                "missing_keywords": expected_keywords or [],
                "star_breakdown": {"situation": False, "task": False, "action": False, "result": False}
            }

        transcript_lower = transcript.lower()
        question_lower = question_text.lower()

        # 1. Keyword Coverage
        target_keywords = expected_keywords or self._extract_default_keywords(question_text)
        matched_keywords = []
        missing_keywords = []

        for kw in target_keywords:
            if re.search(r"\b" + re.escape(kw.lower()) + r"\b", transcript_lower):
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        coverage_ratio = len(matched_keywords) / max(1, len(target_keywords))
        keyword_score = round(coverage_ratio * 100.0, 1)

        # 2. Semantic Relevance (Word Overlap & Key Term Association)
        stop_words_set = {"what", "when", "where", "which", "could", "would", "about", "your", "with", "from", "have", "this", "that", "tell", "explain", "describe", "handle", "regarding", "experience"}
        q_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", question_lower)) - stop_words_set
        t_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", transcript_lower))
        overlap = len(q_words.intersection(t_words))

        if len(matched_keywords) == 0 and overlap == 0:
            relevance_score = 0.0
        else:
            relevance_score = round(min(100.0, (overlap * 20.0) + (coverage_ratio * 60.0)), 1)

        # 3. STAR Structure Adherence
        star_breakdown = {}
        star_points = 0
        for component, patterns in STAR_PATTERNS.items():
            matched = any(re.search(pat, transcript_lower) for pat in patterns)
            star_breakdown[component] = matched
            if matched:
                star_points += 25

        star_score = float(star_points)

        # 4. Completeness and Depth (Length & Structure)
        word_count = len(transcript.split())
        if len(matched_keywords) == 0 and overlap == 0:
            completeness_score = 0.0
        elif word_count >= 80:
            completeness_score = 92.0
        elif word_count >= 45:
            completeness_score = 82.0
        elif word_count >= 20:
            completeness_score = 65.0
        else:
            completeness_score = 35.0

        # 5. Sentiment / Confidence Score
        confidence_hits = sum(1 for p in CONFIDENCE_MARKERS if re.search(p, transcript_lower))
        hesitation_hits = sum(1 for p in HESITATION_MARKERS if re.search(p, transcript_lower))
        
        if len(matched_keywords) == 0 and overlap == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = round(
                max(30.0, min(95.0, 60.0 + (confidence_hits * 6.0) - (hesitation_hits * 8.0))), 
                1
            )

        # 6. Overall NLP Composite Score
        if len(matched_keywords) == 0 and overlap == 0:
            overall_nlp_score = 0.0
        else:
            overall_nlp_score = round(
                (relevance_score * 0.40) + 
                (keyword_score * 0.30) + 
                (star_score * 0.15) + 
                (completeness_score * 0.15),
                1
            )

        return {
            "relevance_score": relevance_score,
            "keyword_coverage_score": keyword_score,
            "star_score": star_score,
            "completeness_score": completeness_score,
            "sentiment_score": sentiment_score,
            "overall_nlp_score": overall_nlp_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "star_breakdown": star_breakdown
        }

    def _extract_default_keywords(self, question_text: str) -> List[str]:
        """Extract baseline keywords from the question if not explicitly provided."""
        stop_words = {"what", "when", "where", "which", "could", "would", "about", "your", "with", "from", "have", "this", "that", "tell", "explain", "describe", "handle"}
        words = re.findall(r"\b[a-zA-Z]{4,}\b", question_text)
        filtered = [w.capitalize() for w in words if w.lower() not in stop_words]
        return list(dict.fromkeys(filtered))[:6]

nlp_service = NLPService()
