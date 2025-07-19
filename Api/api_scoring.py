from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib  # Utiliser joblib uniquement

# Charger le modèle et le scaler
model = joblib.load("modele_logistic_regression.pkl")
scaler = joblib.load("scaler_minmax.pkl")

# Créer une instance de l'application FastAPI
app = FastAPI()

# Définir les données d'entrée attendues avec 11 colonnes
class ClientData(BaseModel):
    Gender: int
    Married: int
    Dependents: int
    Education: int
    Self_Employed: int
    ApplicantIncome: float
    CoapplicantIncome: float
    LoanAmount: float
    Loan_Amount_Term: float
    Credit_History: float
    Property_Area: int

# Route principale
@app.get("/")
def read_root():
    return {"message": "API de scoring de crédit opérationnelle 🎯"}

# Endpoint de prédiction
@app.post("/predict")
def predict(data: ClientData):
    input_data = np.array([[
        data.Gender,
        data.Married,
        data.Dependents,
        data.Education,
        data.Self_Employed,
        data.ApplicantIncome,
        data.CoapplicantIncome,
        data.LoanAmount,
        data.Loan_Amount_Term,
        data.Credit_History,
        data.Property_Area
    ]])

    # Appliquer la normalisation
    input_scaled = scaler.transform(input_data)

    # Prédiction
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1]

    statut = "Accepté" if prediction == 1 else "Refusé"

    return {
        "Statut Crédit": statut,
        "Probabilité de défaut": round(float(probability), 2)
    }
