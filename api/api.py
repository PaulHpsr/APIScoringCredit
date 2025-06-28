from flask import Flask, request, jsonify
import joblib
import pandas as pd
import os
import json

# Initialisation de l'app Flask
app = Flask(__name__)

SEUIL_OPTIMAL = 0.735


# Chargement du modèle
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "modele_xgboost.pkl")
model = joblib.load(model_path)

# Chargement des profils bancaires depuis le fichier JSON
profils_path = os.path.join(os.path.dirname(__file__), "..", "profils_bancaires.json")
with open(profils_path, "r", encoding="utf-8") as f:
    profils_bancaires = json.load(f)
    
# Définition de règles pour les profils bancaires
def recommander_banques(profil_client):
    recommandations = []
    for profil in profils_bancaires:
        conditions = profil.get("conditions", {})
        revenu_min = conditions.get("revenu_minimum", 0)
        apport_min = conditions.get("apport_minimum", 0)
        contrats = conditions.get("contrats_acceptes", [])

        if (
            profil_client.get("revenu", 0) >= revenu_min
            and profil_client.get("apport", 0) >= apport_min
            and profil_client.get("contrat") in contrats
        ):
            recommandations.append(profil["type"])

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

    try:
        # Extraction des seules variables utiles pour le modèle
        data_modele = {k: data[k] for k in colonnes_modele if k in data}

        df_input = pd.DataFrame([data_modele])

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
