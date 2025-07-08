# API Scoring Crédit – XGBoost + Flask

Cette API prédit la **probabilité de défaut de paiement** d’un client bancaire à partir de données financières américaines récupérées sur le site : https://www.kaggle.com/competitions/GiveMeSomeCredit/data?select=cs-test.csv.  
Elle repose sur un modèle **XGBoost équilibré** exposé via une API REST en Flask.

---

## Fonctionnalités

- Prédiction du risque de défaut (`probabilite_defaut`)
- Interprétation simple (`risque_estime`)
- Recommandation de banque (`banques_recommandees`)
- Utilisable depuis n'importe quel site web via requête POST

---

## Structure du projet

```
projet_scoring/
├── api/
│   └── api.py                    # Code Flask
├── models/
│   └── modele_xgboost.pkl        # Modèle entraîné
├── requirements-api.txt         # Dépendances pour Render
├── render.yaml                  # Déploiement Render
├── test_api.py                  # Script local de test
├── notebooks/
│   └── 01_exploration.ipynb     # Entraînement + visualisation
├── README.md
```


##  1. Déploiement GitHub

```bash
git init
git add .
git commit -m "Initial scoring API"
git remote add origin https://github.com/ton-utilisateur/ton-repo.git
git push -u origin main
```

## 2. Déploiement Render
> Prérequis : un compte sur https://render.com

Nouveau service → "Web Service"

Connecter son dépôt GitHub

Renseigner :

Build Command : pip install -r requirements-api.txt

Start Command : gunicorn api.api:app

Environnement : Python

Fichier render.yaml à la racine (optionnel)

L’API sera accessible à une URL du type :
```  
https://scoring-api.onrender.com/predict
```

## 3. Intégration front-end
En JavaScripts :
```
fetch("https://scoring-api.onrender.com/predict", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    age: 35,
    MonthlyIncome: 3000,
    NumberOfTimes90DaysLate: 1,
    contrat: "CDI",
    apport: 8000,
    revenu: 2500,
    // + autres champs requis par le modèle
  })
})
.then(res => res.json())
.then(data => {
  console.log("Risque :", data.risque_estime);
});

```

## 📮 Endpoint disponible

### `POST /predict`

Envoie un objet JSON représentant un profil client.

#### Exemple d’entrée :
```json
{
  "RevolvingUtilizationOfUnsecuredLines": 0.3,
  "age": 35,
  "NumberOfTime30-59DaysPastDueNotWorse": 0,
  "DebtRatio": 0.45,
  "MonthlyIncome": 3000,
  "NumberOfOpenCreditLinesAndLoans": 4,
  "NumberOfTimes90DaysLate": 1,
  "NumberRealEstateLoansOrLines": 1,
  "NumberOfTime60-89DaysPastDueNotWorse": 0,
  "NumberOfDependents": 2,
  "contrat": "CDI",
  "apport": 8000,
  "revenu": 2500,
  "âge": 35
}

```
