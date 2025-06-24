# This module classifies the risk level of pregnancy symptoms and provides recommendations.
def classify_risk(symptoms):
    """
    Classify pregnancy symptom risk according to the PDF's Risk Output Labels:
      - Low: Normal fatigue, light nausea
      - Medium: Spotting, mild hypertension
      - High: Bleeding, pain, high BP, infection
    """
    text = " ".join(symptoms).lower()

    # HIGH risk keywords
    high_keywords = ["bleeding", "pain", "high bp", "hypertension", "infection"]
    if any(kw in text for kw in high_keywords):
        return "High", "Immediate visit to ER or OB emergency care."

    # MEDIUM risk keywords
    medium_keywords = ["spotting", "mild hypertension"]
    if any(kw in text for kw in medium_keywords):
        return "Medium", "Contact your doctor within 24 hours."

    # LOW risk — everything else
    return "Low", "Self-monitor and follow routine prenatal care."

