# This module classifies the risk level of pregnancy symptoms and provides recommendations.
def classify_risk(symptoms):
    text = " ".join(symptoms).lower()
    if "heavy bleeding" in text or "severe pain" in text or "no fetal movement" in text:
        return "High", "Immediate visit to ER or OB emergency care."
    elif "spotting" in text or "persistent vomiting" in text or "mild hypertension" in text:
        return "Medium", "Contact your doctor within 24 hours."
    else:
        return "Low", "Monitor at home and follow routine prenatal care."
