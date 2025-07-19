import streamlit as st
import requests
import pandas as pd
import json
from streamlit_lottie import st_lottie
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import base64  
import random
import math
import plotly.express as px


st.set_page_config(page_title="Scoring Crédit", layout="wide", page_icon="📊")

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    bin_str = get_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image1/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            backdrop-filter: blur(4px);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("fronted/image7.jpg")

def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# --- En-tête ---
with st.container():
    col_icon, col_title = st.columns([1, 10])
    with col_icon:
        st.image("icons8-combo-chart-50.png", width=60)  # Icône en noir élégant
    with col_title:
        st.markdown("""
            <style>
                .main-title {
                    font-size: 42px;
                    font-weight: 800;
                    color: #FAFAFA; /* Blanc / noir bleuté */
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin-bottom: 5px;
                }
                .subtitle {
                    font-size: 17px;
                    color: #FAFAFA; /* blanc */
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin-top: 0;
                }
            </style>
            <div>
                <div class="main-title">Tableau de bord – Scoring de Crédit</div>
                <div class="subtitle">Évaluez une demande ou explorez les données clients.</div>
            </div>
        """, unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        return pd.read_csv("data/train.csv")
    except:
        return pd.DataFrame()

df = load_data()

# Seuil fixé à 10% 
SEUIL = 10

# Tabs
tab1, tab2 = st.tabs([ "🔍 Infos Client" , "📈 Nouveau Client"])
# -- L'onglet 1
if 'valeur_proba' not in st.session_state:
    st.session_state.valeur_proba = None
if 'prediction_ok' not in st.session_state:
    st.session_state.prediction_ok = False

with tab1:
    st.subheader("📇 Sélectionner un client pour afficher ses informations")

    try:
        
        df_test = pd.read_csv("data/test.csv").head(100)
        id_col = [col for col in df_test.columns if "id" in col.lower()]
        if id_col:
            id_col = id_col[0]
            id_list = df_test[id_col].dropna().unique().tolist()
            selected_id = st.selectbox("🔍 Sélectionnez un ID Client", id_list)

            client_data = df_test[df_test[id_col] == selected_id]
            if not client_data.empty:
                st.success(f"✅ Données du client {selected_id}")

                infos = client_data.iloc[0].to_dict()
                # === Affichage CSS et infos ===
                st.markdown("""<style>
                    .big-card {
                        background-color: #262730;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                        border: 2px solid #FAFAFA;
                        padding: 25px 30px;
                        margin-bottom: 20px;
                        font-family: 'Segoe UI', sans-serif;
                        min-height: 350px;
                    }
                    .big-card-title {
                        font-size: 22px;
                        font-weight: 700;
                        color: #FAFAFA;
                        margin-bottom: 20px;
                        border-bottom: 2px solid #FAFAFA;
                        padding-bottom: 8px;
                    }
                    .info-row {
                        margin-bottom: 12px;
                    }
                    .info-label {
                        font-weight: 600;
                        color: #FAFAFA;
                        display: inline-block;
                        width: 150px;
                    }
                    .info-value {
                        color: #FAFAFA;
                        display: inline-block;
                    }
                    </style>""", unsafe_allow_html=True)

                infos_personnelles = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Credit_History"]
                infos_professionnelles = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Property_Area"]

                def format_value(key, value):
                    if key in ["Gender", "Married", "Education", "Self_Employed", "Credit_History"]:
                        mapping = {
                            "Gender": {0: "Femme", 1: "Homme"},
                            "Married": {0: "Non Marié(e)", 1: "Marié(e)"},
                            "Education": {0: "Supérieur", 1: "Non Supérieur"},
                            "Self_Employed": {0: "Non", 1: "Oui"},
                            "Credit_History": {0: "Mauvais", 1: "Bon"},
                        }
                        return mapping.get(key, {}).get(value, value)
                    if key == "Property_Area":
                        mapping_area = {0: "Rurale", 1: "Urbaine", 2: "Semi-urbaine"}
                        return mapping_area.get(value, value)
                    return value

                col1, col2 = st.columns(2)
                with col1:
                    content = '<div class="big-card">'
                    content += '<div class="big-card-title">Informations personnelles</div>'
                    for key in infos_personnelles:
                        val = format_value(key, infos.get(key, "N/A"))
                        key_clean = key.replace("_", " ").capitalize()
                        content += f'<div class="info-row"><span class="info-label">{key_clean} :</span><span class="info-value">{val}</span></div>'
                    content += '</div>'
                    st.markdown(content, unsafe_allow_html=True)

                with col2:
                    content = '<div class="big-card">'
                    content += '<div class="big-card-title">Informations professionnelles</div>'
                    for key in infos_professionnelles:
                        val = format_value(key, infos.get(key, "N/A"))
                        key_clean = key.replace("_", " ").capitalize()
                        content += f'<div class="info-row"><span class="info-label">{key_clean} :</span><span class="info-value">{val}</span></div>'
                    content += '</div>'
                    st.markdown(content, unsafe_allow_html=True)

                
                # === Affichage direct de l'histogramme revenu ===
                choix_diagramme = st.selectbox(
                    "📊 Choisissez un diagramme à afficher",
                    ("Historique individuel", "Comparaison avec la population"),
                    key=f"diagramme_client_{selected_id}"
                )

                if choix_diagramme == "Historique individuel":
                    st.markdown("### 📈 Évolution individuelle des revenus et crédits")
                
                    historique_client = client_data[["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term"]].T
                    historique_client.columns = ["Montant (en milliers)"]
                    historique_client.reset_index(inplace=True)
                    historique_client.rename(columns={"index": "Catégorie"}, inplace=True)
                
                    fig = px.bar(
                        historique_client,
                        x="Catégorie",
                        y="Montant (en milliers)",
                        color_discrete_sequence=["skyblue"]
                    )
                    fig.update_layout(
                        title="Historique des données financières du client",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                                
                elif choix_diagramme == "Comparaison avec la population":
                    st.markdown("### 📊 Revenu du client vs Population")
                
                    fig = px.histogram(df_test, x="ApplicantIncome", nbins=50, title="Répartition des revenus dans la population",
                                       color_discrete_sequence=["lightblue"])
                    
                    fig.add_vline(
                        x=client_data["ApplicantIncome"].values[0],
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Client sélectionné",
                        annotation_position="top right"
                    )
                
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    st.plotly_chart(fig, use_container_width=True)


                # === Prédiction ===
                if st.button("🔍 Prédire ce client"):
                    with st.spinner("Analyse en cours..."):

                        def text_to_int(key, val):
                            mappings = {
                                "Gender": {"Femme": 0, "Homme": 1, "Female": 0, "Male": 1},
                                "Married": {"Non Marié(e)": 0, "Marié(e)": 1, "No": 0, "Yes": 1},
                                "Education": {"Supérieur": 0, "Non Supérieur": 1, "Graduate": 0, "Not Graduate": 1},
                                "Self_Employed": {"Non": 0, "Oui": 1, "No": 0, "Yes": 1},
                                "Credit_History": {"Mauvais": 0, "Bon": 1, 0.0: 0, 1.0: 1, 0: 0, 1: 1},
                                "Property_Area": {
                                    "Rurale": 0, "Urbaine": 1, "Semi-urbaine": 2,
                                    "Rural": 0, "Urban": 1, "Semiurban": 2,
                                    "RURAL": 0, "URBAN": 1, "SEMIURBAN": 2
                                }
                            }
                            return mappings.get(key, {}).get(val, val)

                        prediction_data = {
                            "Gender": infos.get("Gender"),
                            "Married": infos.get("Married"),
                            "Dependents": infos.get("Dependents"),
                            "Education": infos.get("Education"),
                            "Self_Employed": infos.get("Self_Employed"),
                            "ApplicantIncome": infos.get("ApplicantIncome"),
                            "CoapplicantIncome": infos.get("CoapplicantIncome"),
                            "LoanAmount": infos.get("LoanAmount"),
                            "Loan_Amount_Term": infos.get("Loan_Amount_Term"),
                            "Credit_History": infos.get("Credit_History"),
                            "Property_Area": infos.get("Property_Area")
                        }

                        prediction_data_mapped = {k: text_to_int(k, v) for k, v in prediction_data.items()}

                        valeurs_invalides = any(
                            pd.isna(val) or 
                            (isinstance(val, float) and (math.isinf(val) or math.isnan(val)))
                            for val in prediction_data_mapped.values()
                        )

                        if valeurs_invalides:
                            st.error("❌ Données invalides.")
                            st.session_state.prediction_ok = False
                        else:
                            try:
                                response = requests.post("https://api-scoring-c8xa.onrender.com/predict", json=prediction_data_mapped)
                                if response.status_code == 200:
                                    result = response.json()
                                    proba = float(result['Probabilité de défaut']) * 100
                                    st.session_state.valeur_proba = proba
                                    st.session_state.prediction_ok = True

                                    if proba <= SEUIL:
                                        st.success(f"✅ Crédit Approuvé (risque {proba:.2f}%) – Seuil : {SEUIL}%")
                                    else:
                                        st.error(f"❌ Crédit Refusé (risque {proba:.2f}%) – Seuil : {SEUIL}%")
                                else:
                                    st.error(f"Erreur prédiction : {response.status_code}")
                            except Exception as e:
                                st.error(f"Erreur API : {e}")
                                st.session_state.prediction_ok = False

                # === DIAGRAMME UNIQUEMENT APRÈS PRÉDICTION OK ===
                if st.session_state.prediction_ok:
                    diagramme_choisi = st.selectbox(
                        "📊 Choisir un diagramme de visualisation",
                        ("Jauge Probabilité", "Diagramme Camembert")
                    )
                    valeur_proba = st.session_state.valeur_proba

                    if diagramme_choisi == "Diagramme Camembert":
                        st.markdown("### 🥧 Répartition de la décision")
                        
                        labels = ['Approuvé', 'Refusé']
                        valeurs = [100 - valeur_proba, valeur_proba]
                        couleurs = ['#27ae60', '#e74c3c']
                    
                        fig = px.pie(
                            names=labels,
                            values=valeurs,
                            color=labels,
                            color_discrete_map={'Approuvé': '#27ae60', 'Refusé': '#e74c3c'},
                            hole=0.3
                        )
                    
                        fig.update_traces(textinfo='percent+label', textfont_size=20, textfont_color='white')
                        fig.update_layout(
                            height=500,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white'),
                            showlegend=False
                        )
                    
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif diagramme_choisi == "Jauge Probabilité":
                        st.markdown("### 🎯 Probabilité de Défaut")
                    
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=valeur_proba,
                            title={'text': "Probabilité de Défaut (%)"},
                            gauge={
                                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                                'bar': {'color': "red" if valeur_proba > SEUIL else "green"},
                                'bgcolor': "white",
                                'steps': [
                                    {'range': [0, SEUIL], 'color': "lightgreen"},
                                    {'range': [SEUIL, 100], 'color': "salmon"}
                                ]
                            }
                        ))
                    
                        fig.update_layout(
                            height=300,
                            margin=dict(t=30, b=0, l=0, r=0),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='white')
                        )
                    
                        st.plotly_chart(fig, use_container_width=True)

                    # Afficher une conclusion visuelle en grand après le diagramme
                if st.session_state.prediction_ok:
                    if st.session_state.valeur_proba <= SEUIL:
                        couleur_fond = "#27ae60"  # vert
                        message = "✅ Analyse favorable : ce client peut bénéficier du prêt."
                    else:
                        couleur_fond = "#e74c3c"  # rouge
                        message = "❌ Analyse défavorable : prêt non recommandé pour ce client."
                
                    st.markdown(f"""
                    <div style="
                        background-color: {couleur_fond};
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        font-size: 26px;
                        font-weight: bold;
                        color: white;
                        margin-top: 30px;
                        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
                    ">
                        {message}
                    </div>
                    """, unsafe_allow_html=True)


            else:
                st.warning("⚠️ Client introuvable.")
        else:
            st.error("❌ Colonne ID non trouvée.")
    except FileNotFoundError:
        st.error("❌ Fichier test.csv introuvable.")
    except Exception as e:
        st.error(f"🚨 Erreur : {e}")


# -- L'onglet 2
with tab2:
    with st.form("formulaire_credit"):
        st.subheader("📝 Informations du Demandeur")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Genre", [0, 1], format_func=lambda x: "Femme" if x == 0 else "Homme")
            married = st.selectbox("État civil", [0, 1], format_func=lambda x: "Non Marié(e)" if x == 0 else "Marié(e)")
            dependents = st.number_input("Personnes à charge", min_value=0, step=1)
            education = st.selectbox("Éducation", [0, 1], format_func=lambda x: "Supérieur" if x == 0 else "Non Supérieur")
            self_employed = st.selectbox("Indépendant", [0, 1], format_func=lambda x: "Non" if x == 0 else "Oui")
        with col2:
            applicant_income = st.number_input("Revenu Demandeur", min_value=0)
            coapplicant_income = st.number_input("Revenu Co-demandeur", min_value=0)
            loan_amount = st.number_input("Montant du prêt (en milliers)", min_value=0)
            loan_term = st.number_input("Durée du prêt (mois)", min_value=1)
            credit_history = st.selectbox("Historique de crédit", [0.0, 1.0], format_func=lambda x: "Mauvais" if x == 0.0 else "Bon")
            property_area = st.selectbox("Zone", [0, 1, 2], format_func=lambda x: ["Rurale", "Urbaine", "Semi-urbaine"][x])

        submitted = st.form_submit_button("Évaluer")

    if submitted:
        with st.spinner("Analyse en cours..."):
            data = {
                "Gender": gender,
                "Married": married,
                "Dependents": dependents,
                "Education": education,
                "Self_Employed": self_employed,
                "ApplicantIncome": applicant_income,
                "CoapplicantIncome": coapplicant_income,
                "LoanAmount": loan_amount,
                "Loan_Amount_Term": loan_term,
                "Credit_History": credit_history,
                "Property_Area": property_area
            }

            try:
                response = requests.post("https://api-scoring-c8xa.onrender.com/predict", json=data)

                if response.status_code == 200:
                    result = response.json()
                    proba = float(result['Probabilité de défaut']) * 100

                    if proba <= SEUIL:
                        statut_affiche = "Approuvé"
                        st.success(f"✅ Crédit Approuvé (risque {proba:.2f}%) – Seuil fixé à {SEUIL}%")
                    else:
                        statut_affiche = "Refusé"
                        st.error(f"❌ Crédit Refusé (risque {proba:.2f}%) – Seuil fixé à {SEUIL}%")

                    if proba <= SEUIL and credit_history == 0 and coapplicant_income == 0 and applicant_income < 6000 and loan_amount > 100:
                        st.warning("⚠️ Ce profil semble à risque, bien que la probabilité soit faible. Vérifiez les données ou revoyez le modèle.")

                    st.session_state['proba_defaut'] = proba
                    st.session_state['applicant_income'] = applicant_income

                else:
                    st.error("❌ Erreur lors de la prédiction.")

            except Exception as e:
                st.error(f"🚨 Erreur de connexion à l'API : {e}")

    if 'proba_defaut' in st.session_state:
        st.markdown(
    "<h4 style='color: white; font-size: 20px;'>📊 Sélectionner un type de diagramme à afficher</h4>",
    unsafe_allow_html=True
)
        if 'proba_defaut' in st.session_state:
            st.markdown("ℹ️ La jauge ci-dessous indique visuellement la probabilité de défaut de crédit du client, facilitant la compréhension de la décision prise.")
        
            proba = st.session_state['proba_defaut']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=proba,
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "red" if proba > SEUIL else "green"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgreen"},
                        {'range': [50, 100], 'color': "salmon"}
                    ]
                },
                title={'text': "Probabilité de Défaut (%)"}
            ))
        
            fig.update_layout(
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
        
            st.plotly_chart(fig, use_container_width=True)

        # ✅ Message final visuel
        couleur_fond = "#27ae60" if proba <= SEUIL else "#e74c3c"
        message = (
            "✔️ Crédit approuvé : le client est éligible au financement."
            if proba <= SEUIL else
            "❌ Crédit refusé : le profil présente un risque élevé."
        )

        st.markdown(f"""
        <div style="
            background-color: {couleur_fond};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-top: 30px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        ">
            {message}
        </div>
        """, unsafe_allow_html=True)
