from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Initialisation de l'app Flask
app = Flask(__name__)

SEUIL_OPTIMAL = 0.735


# Chargement du modèle
model = joblib.load("../models/modele_xgboost.pkl")  # adapte le chemin si besoin

# Définition de quelques règles simples pour les profils bancaires
def recommander_banques(profil):
    recommandations = []

    if profil.get("contrat") == "CDI" and profil.get("apport", 0) < 10000:
        recommandations.append("Banque traditionnelle")

    if profil.get("apport", 0) > 30000 and profil.get("contrat") in ["CDI", "fonctionnaire"]:
        recommandations.append("Banque en ligne")

    if profil.get("revenu", 0) < 2500 or profil.get("âge", 0) < 30:
        recommandations.append("Banque mutualiste")

    return recommandations

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    # Liste exacte des colonnes attendues par ton modèle
    colonnes_modele = [
        "RevolvingUtilizationOfUnsecuredLines",
        "age",
        "NumberOfTime30-59DaysPastDueNotWorse",
        "DebtRatio",
        "MonthlyIncome",
        "NumberOfOpenCreditLinesAndLoans",
        "NumberOfTimes90DaysLate",
        "NumberRealEstateLoansOrLines",
        "NumberOfTime60-89DaysPastDueNotWorse",
        "NumberOfDependents"
    ]

    # Extraction des seules variables utiles pour le modèle
    data_modele = {k: data[k] for k in colonnes_modele if k in data}

    df_input = pd.DataFrame([data_modele])

    try:

        proba = model.predict_proba(df_input)[0, 1]

        is_defaut = proba >= SEUIL_OPTIMAL
        interpretation = "Risque élevé de défaut" if is_defaut else "Risque faible"

        banques = recommander_banques(data)
        return jsonify({
            "probabilite_defaut": float(round(proba, 3)),
            "risque_estime": interpretation,
            "banques_recommandees": banques
        })


    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
