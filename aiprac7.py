def diagnose(symptoms_input):
    # Define a basic disease-symptom database (a dictionary)
    disease_symptoms = {
        "Common Cold": ["cough", "sore throat", "runny nose", "fever"],
        "Flu": ["fever", "headache", "muscle pain", "cough", "fatigue"],
        "Migraine": ["headache", "nausea", "sensitivity to light"],
        "Diabetes": ["blurred vision", "excessive thirst", "frequent urination", "fatigue"],
        "Hypertension": ["headache", "chest pain", "fatigue", "blurred vision"],
        "COVID-19": ["fever", "dry cough", "fatigue", "loss of taste", "loss of smell"],
        "Malaria": ["fever", "chills", "headache", "nausea"],
    }

    # Normalize symptoms to lowercase for consistent matching
    symptoms_input = [symptom.lower().strip() for symptom in symptoms_input]

    # Store matching score for each disease
    disease_match_score = {}

    for disease, symptoms in disease_symptoms.items():
        # Count how many input symptoms appear in each disease symptoms list
        matches = len(set(symptoms_input) & set(symptoms))
        if matches > 0:
            disease_match_score[disease] = matches

    if not disease_match_score:
        return "No matching diseases found. Please consult a healthcare professional."

    # Sort diseases by descending match score
    sorted_diseases = sorted(disease_match_score.items(), key=lambda x: x[1], reverse=True)

    # Build result message
    results = "Possible diseases based on your symptoms:"
    for disease, score in sorted_diseases:
        results += f"- {disease} (matched {score} symptom{'s' if score > 1 else ''})"

    return results


if __name__ == "__main__":
    print("Welcome to the Simple Medical Diagnostic System")
    print("Please input symptoms separated by commas (e.g., fever, cough, headache): ")
    user_input = input()
    user_symptoms = user_input.split(",")

    diagnosis = diagnose(user_symptoms)
    print(" " + diagnosis)