from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ScoringService:
    """Composite ML Multi-Modal Scoring Engine."""

    # Configurable Scoring Weights
    WEIGHT_NLP: float = 0.40          # Technical relevance & completeness
    WEIGHT_VOICE: float = 0.30        # Pace, clarity, filler words
    WEIGHT_SENTIMENT: float = 0.15    # Confidence and emotional poise
    WEIGHT_STAR: float = 0.15         # Structural rigor (STAR format)

    def calculate_answer_score(
        self,
        nlp_score: float,
        voice_score: float,
        sentiment_score: float,
        star_score: float
    ) -> float:
        """Calculate weighted composite score (0-100) for an individual answer."""
        if nlp_score == 0.0:
            return 0.0

        composite = (
            (nlp_score * self.WEIGHT_NLP) +
            (voice_score * self.WEIGHT_VOICE) +
            (sentiment_score * self.WEIGHT_SENTIMENT) +
            (star_score * self.WEIGHT_STAR)
        )
        return round(max(0.0, min(100.0, composite)), 1)

    def calculate_session_summary(self, answer_evaluations: List[Dict[str, Any]], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate per-question scores into comprehensive session metrics."""
        if not answer_evaluations:
            return {
                "overall_score": 0.0,
                "technical_score": 0.0,
                "communication_score": 0.0,
                "confidence_score": 0.0,
                "competency_breakdown": {}
            }

        total_composite = sum(e.get("composite_score", 0.0) for e in answer_evaluations)
        total_nlp = sum(e.get("nlp_score", 0.0) for e in answer_evaluations)
        total_voice = sum(e.get("voice_score", 0.0) for e in answer_evaluations)
        total_sentiment = sum(e.get("sentiment_score", 0.0) for e in answer_evaluations)

        n = len(answer_evaluations)
        overall_score = round(total_composite / n, 1)
        technical_score = round(total_nlp / n, 1)
        communication_score = round(total_voice / n, 1)
        confidence_score = round(total_sentiment / n, 1)

        # Calculate Competency Breakdown
        competency_scores: Dict[str, List[float]] = {}
        for i, eval_item in enumerate(answer_evaluations):
            comp_name = "General Proficiency"
            if i < len(questions) and questions[i].get("competency"):
                comp_name = questions[i]["competency"]
            
            if comp_name not in competency_scores:
                competency_scores[comp_name] = []
            score_val = eval_item["composite_score"] if ("composite_score" in eval_item and eval_item["composite_score"] is not None) else 0.0
            competency_scores[comp_name].append(score_val)

        competency_breakdown = {
            k: round(sum(v) / len(v), 1) for k, v in competency_scores.items()
        }

        # Add standard competencies if missing
        if "Technical Communication" not in competency_breakdown:
            competency_breakdown["Technical Communication"] = communication_score
        if "Problem Solving" not in competency_breakdown:
            competency_breakdown["Problem Solving"] = round((technical_score + overall_score) / 2, 1)

        return {
            "overall_score": overall_score,
            "technical_score": technical_score,
            "communication_score": communication_score,
            "confidence_score": confidence_score,
            "competency_breakdown": competency_breakdown
        }

scoring_service = ScoringService()
