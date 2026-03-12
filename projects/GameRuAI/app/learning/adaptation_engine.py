from __future__ import annotations


class AdaptationEngine:
    def evaluate_improvement(self, *, previous_quality: float, current_quality: float) -> dict:
        delta = round(float(current_quality) - float(previous_quality), 4)
        if delta > 0.03:
            verdict = "improved"
        elif delta < -0.03:
            verdict = "regressed"
        else:
            verdict = "stable"
        return {"delta_quality": delta, "verdict": verdict}

