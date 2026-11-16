"""
OUTPUT / INTERPRETATION LAYER
Does NOT affect hybrid decision logic.
Hybrid remains frozen.
"""

IF_THRESHOLD = 0.05   # must MATCH frozen config

def compute_confidence_risk_severity(label, p_attack, if_score=None):
    """
    Computes confidence %, risk %, and severity level
    WITHOUT touching hybrid logic
    """

    # ATTACK (RF decides)
    if label == "Attack":
        confidence = p_attack * 100
        risk = p_attack * 100

    # NORMAL (RF decides)
    elif label == "Normal":
        confidence = (1 - p_attack) * 100
        risk = (1 - p_attack) * 10   # stays very low

    # SUSPICIOUS (IF decides)
    elif label == "Suspicious":
        confidence = min(
            100.0,
            ((IF_THRESHOLD - if_score) / abs(IF_THRESHOLD)) * 100
        )
        risk = 50 + 0.5 * confidence

    else:
        raise ValueError("Unknown label")

    # SEVERITY MAPPING (UPDATED – RISK-DRIVEN ONLY)
    if risk < 30:
        severity = "Low"
    elif risk < 70:
        severity = "Medium"
    else:
        severity = "High"

    return round(confidence), round(risk), severity
