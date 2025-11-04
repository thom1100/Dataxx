
# 📊 Dataxx — Streamlit + n8n Automation App

Cette application permet d'exécuter des workflows via n8n depuis une interface Streamlit, afin d’automatiser la collecte et l'analyse de données de sponsoring de clubs.

---

## 🚀 Fonctionnalités

- Interface Streamlit simple et intuitive
- Interaction directe avec des workflows n8n
- Hébergement local **ou** via Streamlit Cloud
- 🔁 Automatisation des tâches data
- 🤖 Utilisation de **Gemini AI** comme LLM par défaut

---

## 🧠 Pourquoi Gemini et pas Perplexity ?

Nous avons choisi **Gemini** pour ce prototype car :

✅ Coût très faible pour démarrer (voire gratuit)  
✅ API simple à connecter rapidement  
✅ Pas besoin d’enregistrer une carte bancaire immédiatement  
❌ Perplexity demandait une configuration de paiement trop contraignante au début

> 📝 L'architecture reste compatible avec Perplexity si besoin plus tard.

---

## 📦 Installation

### 1️⃣ Cloner le repo

```bash
git clone https://github.com/ton-repo/dataxx.git
cd dataxx

### Créer un environnement et installer les librairies nécessaires

```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac / Linux
# 👇 sur Windows
.\.venv\Scripts\activate

pip install -r requirements.txt


### Lancer l'application

streamlit run app.py

