import streamlit as st
import requests
import json
from datetime import datetime
from utils import sort_sponsors

# Configuration des Webhooks

webhook_url_search_test = "https://thom1100.app.n8n.cloud/webhook-test/0984f6ea-828c-4125-b542-47e255c55025"
webhook_url_search_prod = "https://thom1100.app.n8n.cloud/webhook/0984f6ea-828c-4125-b542-47e255c55025"
webhook_url_search = webhook_url_search_prod
webhook_url_detail_test = "https://thom1100.app.n8n.cloud/webhook-test/de9c6903-7dfb-49d5-b757-dc8cf239570f"
webhook_url_detail_prod = "https://thom1100.app.n8n.cloud/webhook/de9c6903-7dfb-49d5-b757-dc8cf239570f"
webhook_url_detail = webhook_url_detail_prod
webhook_url_extract_test = "https://thom1100.app.n8n.cloud/webhook-test/3fde3a0d-2564-4d80-af29-000b04448596"
webhook_url_extract_prod = "https://thom1100.app.n8n.cloud/webhook/3fde3a0d-2564-4d80-af29-000b04448596"
webhook_url_extract = webhook_url_extract_prod

API_KEY = st.secrets["N8N_API_KEY"]

# Initialisation de la session
if 'sponsors_data' not in st.session_state:
    st.session_state.sponsors_data = []
if 'request_context' not in st.session_state:
    st.session_state.request_context = None

# ============================================
# SECTION 1 : RECHERCHE INITIALE
# ============================================
st.title("🏆 Recherche de Sponsors pour Clubs de Ligue 1")

st.header("Paramètres de recherche - Club et Similarity Feature")

# Choix du club
import streamlit as st

# Dictionnaire clubs Ligue 1 & Ligue 2 → Région
clubs_regions = {
    # Ligue 1
    "Paris Saint-Germain": "Île-de-France",
    "AS Monaco": "Provence-Alpes-Côte d'Azur",
    "Olympique de Marseille": "Provence-Alpes-Côte d'Azur",
    "Olympique Lyonnais": "Auvergne-Rhône-Alpes",
    "Lille OSC": "Hauts-de-France",
    "Stade Rennais": "Bretagne",
    "RC Lens": "Hauts-de-France",
    "OGC Nice": "Provence-Alpes-Côte d'Azur",
    "Montpellier HSC": "Occitanie",
    "Toulouse Football Club": "Occitanie",
    "FC Nantes": "Pays de la Loire",
    "Stade Brestois": "Bretagne",
    "RC Strasbourg": "Grand Est",
    "Stade de Reims": "Grand Est",
    "Le Havre AC": "Normandie",
    "FC Lorient": "Bretagne",
    "Clermont Foot": "Auvergne-Rhône-Alpes",
    "FC Metz": "Grand Est",

    # Ligue 2
    "AS Saint-Étienne": "Auvergne-Rhône-Alpes",
    "Bordeaux": "Nouvelle-Aquitaine",
    "Paris FC": "Île-de-France",
    "SM Caen": "Normandie",
    "AC Ajaccio": "Corse",
    "SC Bastia": "Corse",
    "USL Dunkerque": "Hauts-de-France",
    "Amiens SC": "Hauts-de-France",
    "EA Guingamp": "Bretagne",
    "Pau FC": "Nouvelle-Aquitaine",
    "Grenoble Foot": "Auvergne-Rhône-Alpes",
    "Rodez AF": "Occitanie",
    "Quevilly Rouen": "Normandie",
    "US Concarneau": "Bretagne",
    "ESTAC Troyes": "Grand Est",
    "Valenciennes FC": "Hauts-de-France",
    "Annecy FC": "Auvergne-Rhône-Alpes",
    "Laval": "Pays de la Loire"
}

club_options = list(clubs_regions.keys())

st.title("🔍 Sélection du club & critère de similarité")

# Sélection du club
chosen_club = st.selectbox("Sélectionnez un club de Ligue 1 ou Ligue 2", club_options)

# Choix du critère de similarité
similarity_feature = st.radio(
    "Choisir la similarité",
    ["Région", "Chiffre d'affaires"],
    help="Critère utilisé pour trouver des sponsors similaires"
)

if similarity_feature == "Chiffre d'affaires":
    st.write("📊 Sélectionnez un chiffre d'affaires approximatif (en millions d'euros)")
    chosen_revenue = st.slider(
        "Chiffre d'affaires",
        min_value=2.5,
        max_value=500.0,
        value=20.0,
        step=1.0,
        format="%0.0f M€"
    )
    chosen_region = None

else:
    chosen_region = clubs_regions[chosen_club]
    chosen_revenue = None
    st.info(f"📍 **Région détectée automatiquement : {chosen_region}**")


# Bouton pour lancer la recherche
if st.button("🔍 Rechercher des sponsors", type="primary", use_container_width=True):
    # Préparation des données pour la requête IA
    search_data = {
    "ClubName": chosen_club,
    "SimilarityFeature": similarity_feature,
    "Chiffre_d_affaires": chosen_revenue if similarity_feature == "Chiffre d'affaires" else None,
    "Region": chosen_region if similarity_feature == "Région" else None
}

    # Envoi de la requête POST au Webhook
    with st.spinner("🔍 Recherche en cours..."):
        try:
            response = requests.post(webhook_url_search, json=search_data, timeout=60, headers={"Dataxx": API_KEY})

            # Vérification de la réponse
            if response.status_code == 200:
                st.success("✅ Recherche réussie !")

                # Récupération des résultats
                raw_response = response.json()

                # Extraire le texte contenant le JSON
                try:
                    llm_text = raw_response[0]["content"]["parts"][0]["text"]
                except Exception as e:
                    st.error("❌ Erreur : Impossible d'extraire les données du LLM")
                    st.write("Structure reçue :")
                    st.json(raw_response)
                    st.stop()

                # Convertir le texte JSON en dictionnaire Python
                try:
                    extracted_info = json.loads(llm_text)
                except json.JSONDecodeError:
                    st.error("❌ Le modèle a renvoyé du texte non-JSON")
                    st.code(llm_text)
                    st.stop()


                # Sauvegarde des résultats dans session_state
                st.session_state.sponsors_data = extracted_info.get("Sponsors", [])
                st.session_state.request_context = {
                    "ClubName": chosen_club,
                    "SimilarityFeature": similarity_feature,
                    "Chiffre_d_affaires": chosen_revenue,
                    "Region": chosen_region
                }

                # Affichage des résultats
                st.write("📊 Sponsors trouvés :")
                st.json(extracted_info)

                st.balloons()
            else:
                st.error(f"❌ Erreur lors de l'envoi des données (Code: {response.status_code})")

                # Détecter spécifiquement les erreurs de webhook N8N
                try:
                    error_response = response.json()
                    error_message = error_response.get("message", "").lower()

                    # Erreur: nœud "Respond to Webhook" non utilisé
                    if response.status_code == 500 and "unused respond to webhook" in error_message:
                        st.error("⚠️ **Le workflow N8N n'atteint jamais le nœud 'Respond to Webhook'**")
                        st.warning("""
                        **Problème :** Le workflow s'est terminé sans passer par le nœud de réponse,
                        donc N8N ne peut pas fermer la connexion HTTP correctement.
                        """)
                    # Erreur: webhook pas configuré pour POST
                    elif response.status_code == 404 and "not registered for post" in error_message:
                        st.warning("⚠️ **Webhook N8N non configuré pour POST**")
                    # Erreur: webhook non enregistré (mode test)
                    elif response.status_code == 404 and "not registered" in error_message:
                        st.warning("⚠️ **Webhook N8N non enregistré**")
                except:
                    pass

        except requests.exceptions.Timeout:
            st.error("⏱️ Timeout : Le webhook n'a pas répondu dans les temps (30 secondes)")
        except requests.exceptions.ConnectionError:
            st.error(f"🔌 Erreur de connexion : Impossible de joindre le webhook")
            st.info(f"Vérifiez que l'URL est correcte : `{webhook_url_search}`")
        except Exception as e:
            st.error(f"❌ Erreur inattendue : {str(e)}")
            st.exception(e)

# ============================================
# SECTION 2 : SÉLECTION DU SPONSOR
# ============================================

if "sponsors_data" in st.session_state and st.session_state.sponsors_data:
    st.divider()
    st.header("Investissements d'une entreprise dans le monde du sport")

    # Affichage du contexte précédent
    if st.session_state.request_context:
        with st.expander("ℹ️ Contexte de la recherche"):
            st.write(f"**Club :** {chosen_club}")
            st.write(f"**Critère de similarité :** {similarity_feature}")
            if similarity_feature == "Chiffre d'affaires":
                st.write(f"**Chiffre d'affaires :** {chosen_revenue} M€")
            else:
                st.write(f"**Région :** {chosen_region}")

    sponsors_list = st.session_state.sponsors_data

    # Sécurité : vérifier que c'est bien une liste de dicts
    if not isinstance(sponsors_list, list) or not all(isinstance(x, dict) for x in sponsors_list):
        st.error("❌ Format de données sponsor invalide. Attendu : Liste de dictionnaires.")
        st.json(sponsors_list)
        st.stop()

    if len(sponsors_list) == 0:
        st.warning("⚠️ Aucun sponsor trouvé.")
        st.stop()

    # Construire dictionnaire {Nom Sponsor : données}
    sponsors_dict = {
        sponsor.get("SponsorName", f"Sponsor {i+1}"): sponsor
        for i, sponsor in enumerate(sponsors_list)
    }

    # Sélection du sponsor
    st.subheader("👆 Choisissez une des entreprises")
    selected_sponsor_name = st.selectbox(
        "Sponsor sélectionné",
        options=list(sponsors_dict.keys()),
        label_visibility="collapsed"
    )

    # Affichage des détails du sponsor
    if selected_sponsor_name:
        selected_sponsor = sponsors_dict[selected_sponsor_name]

        st.write("📋 Informations du sponsor sélectionné :")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Type :** {selected_sponsor.get('SponsorType', 'N/A')}")
            st.info(f"**Région :** {selected_sponsor.get('Region', 'N/A')}")
        with col2:
            st.info(f"**Chiffre d'affaires :** {selected_sponsor.get('Chiffre_d_affaires', 'N/A')} M€")
            st.info(f"**Période :** {selected_sponsor.get('Dates du sponsoring', 'N/A')}")

        # Stocker l'état
        st.session_state.selected_sponsor = selected_sponsor
        st.session_state.selected_sponsor_name = selected_sponsor_name

        st.success("✅ Sponsor sélectionné ! Passez à l'étape 3 pour l'analyse.")


# ============================================
# SECTION 3 : REQUÊTE DÉTAILLÉE AU SPONSOR
# ============================================
if 'selected_sponsor' in st.session_state:
    st.divider()
    st.header("Analyse détaillée du sponsor")

    # Affichage du sponsor sélectionné pour rappel
    st.info(f"🎯 Sponsor à analyser : **{st.session_state.selected_sponsor_name}**")


    # Bouton pour envoyer la requête détaillée
    if st.button("🚀 Lancer l'analyse détaillée", type="primary", use_container_width=True):
        # Préparation des données pour N8N
        detailed_data = {
            "SponsorName": st.session_state.selected_sponsor.get("SponsorName"),
            "SponsorType": st.session_state.selected_sponsor.get("SponsorType"),
            "Region": st.session_state.selected_sponsor.get("Region"),
            "Chiffre_d_affaires": st.session_state.selected_sponsor.get("Chiffre_d_affaires"),
            "Dates_du_sponsoring": st.session_state.selected_sponsor.get("Dates du sponsoring")
        }


        with st.spinner("⏳ Requête en cours d'exécution..."):
            try:
                # Envoi de la requête POST au Webhook N8N
                response_2 = requests.post(webhook_url_detail, json=detailed_data, timeout=60, headers={"Dataxx": API_KEY})

                # Vérification de la réponse
                if response_2.status_code == 200:
                    st.success("✅ Requête envoyée avec succès !")
                    raw_response_2 = response_2.json()

# Extraire le texte contenant le JSON
                    try:
                        llm_text_2 = raw_response_2[0]["content"]["parts"][0]["text"]
                    except Exception as e:
                        st.error("❌ Erreur : Impossible d'extraire les données du LLM")
                        st.write("Structure reçue :")
                        st.json(raw_response_2)
                        st.stop()

                    # Convertir le texte JSON en dictionnaire Python
                    try:
                        extracted_info_2 = json.loads(llm_text_2)
                    except json.JSONDecodeError:
                        st.error("❌ Le modèle a renvoyé du texte non-JSON")
                        st.code(llm_text_2)
                        st.stop()

                    # Sauvegarde des résultats dans session_state
                    st.session_state.sponsored_sports_data = extracted_info_2
                    st.session_state.request_context = {
                        "SponsorName": selected_sponsor_name
                    }

                    # Affichage des résultats
                    st.write("📊 Clubs et Sports reliés au sponsor trouvés :")
                    st.json(extracted_info_2)

                    st.balloons()

                    # Détecter spécifiquement les erreurs de webhook N8N
                    try:
                        error_response = response_2.json()
                        error_message = error_response.get("message", "").lower()

                        # Erreur: nœud "Respond to Webhook" non utilisé
                        if response_2.status_code == 500 and "unused respond to webhook" in error_message:
                            st.error("⚠️ **Le workflow N8N n'atteint jamais le nœud 'Respond to Webhook'**")
                            st.warning("""
                            **Problème :** Le workflow s'est terminé sans passer par le nœud de réponse,
                            donc N8N ne peut pas fermer la connexion HTTP correctement.
                            """)

                        # Erreur: webhook pas configuré pour POST
                        elif response_2.status_code == 404 and "not registered for post" in error_message:
                            st.warning("⚠️ **Webhook N8N non configuré pour POST**")

                        # Erreur: webhook non enregistré (mode test)
                        elif response_2.status_code == 404 and "not registered" in error_message:
                            st.warning("⚠️ **Webhook N8N non enregistré**")
                    except:
                        pass


            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout : Le nœud Response N8N n'a pas répondu dans les temps")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Erreur de connexion : Impossible de joindre le webhook N8N")
                st.info(f"Vérifiez que l'URL est correcte : `{webhook_url_detail}`")
            except Exception as e:
                st.error(f"❌ Erreur inattendue : {str(e)}")
                st.exception(e)

# ============================================
# SECTION 4 : SÉLECTION DU CLUB/SPORT
# ============================================
if 'sponsored_sports_data' in st.session_state and st.session_state.sponsored_sports_data:
    st.divider()
    st.header("Choisir un club/sport pour analyse complète")

    # Afficher le sponsor pour rappel
    st.info(f"🎯 Analyse des sponsors du club/sport : **{st.session_state.selected_sponsor_name}**")

    clubs_list = st.session_state.sponsored_sports_data

    # Sécurité : vérifier que c'est bien une liste de dicts
    if not isinstance(clubs_list, list) or not all(isinstance(x, dict) for x in clubs_list):
        st.error("❌ Format de données sponsor invalide. Attendu : Liste de dictionnaires.")
        st.json(clubs_list)
        st.stop()

    if len(clubs_list) == 0:
        st.warning("⚠️ Aucun partenaire sportif trouvé.")
        st.stop()

    # Construire dictionnaire {Nom Sponsor : données}
    clubs_dict = {
        club.get("ClubOrSport", f"Club {i+1}"): club
        for i, club in enumerate(clubs_list)
    }

    # Sélection du sponsor
    st.subheader("👆 Choisissez un sponsor")
    selected_club_name = st.selectbox(
        "Club/Sport sélectionné",
        options=list(clubs_dict.keys()),
        label_visibility="collapsed"
    )


    # Afficher les détails du club/sport sélectionné
    if selected_club_name:
        selected_club = clubs_dict[selected_club_name]

        st.write("📋 Informations du club/sport sélectionné :")

        # Affichage formaté des informations
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Club/Sport :** {selected_club.get('ClubOrSport', 'N/A')}")
        with col2:
            st.info(f"**Date de sponsoring :** {selected_club.get('SponsoringPeriod', 'N/A')}")
        with col3:
            st.info(f"**Montant annuel investi (estimation):** {selected_club.get('EstimatedYearlyInvestment', 'N/A')}")

        # Sauvegarder le club sélectionné
        st.session_state.selected_club = selected_club
        st.session_state.selected_club_name = selected_club_name

        st.success("✅ Club/Sport sélectionné ! Vous pouvez lancer la recherche de sponsors.")

# ============================================
# SECTION 5 : RECHERCHE COMPLÈTE DES SPONSORS DU CLUB/SPORT
# ============================================
if 'selected_club' in st.session_state:
    st.divider()
    st.header("Analyse complète des sponsors du club/sport")

    # Affichage du club sélectionné pour rappel
    st.info(f"🎯 Recherche des sponsors de : **{st.session_state.selected_club_name}**")

    # Bouton pour envoyer la requête finale
    if st.button("🚀 Lancer la recherche complète des sponsors", type="primary", use_container_width=True):
        # Préparation des données pour N8N
        final_data = {
            "Club_Sport": st.session_state.selected_club.get("ClubOrSport"),
            "SponsoringDate": st.session_state.selected_club.get("SponsoringPeriod"),
            "Amount_invested_yearly": st.session_state.selected_club.get("EstimatedYearlyInvestment")
        }



        with st.spinner("⏳ Recherche des sponsors des 10 dernières années..."):
            try:
                # Envoi de la requête POST au Webhook N8N
                response_3 = requests.post(webhook_url_extract, json=final_data, timeout=60, headers={"Dataxx": API_KEY})

                # Vérification de la réponse
                if response_3.status_code == 200:
                    st.success("✅ Recherche complète réussie !")

                    # Tentative de récupération des données JSON
                    try:
                        # Récupération du JSON renvoyé par n8n (format OpenAI style)
                        raw_response_3 = response_3.json()

                        # Extraire le texte contenant le JSON
                        try:
                            llm_text_3 = raw_response_3[0]["content"]["parts"][0]["text"]
                        except Exception as e:
                            st.error("❌ Erreur : Impossible d'extraire les données du LLM")
                            st.write("Structure reçue :")
                            st.json(raw_response_3)
                            st.stop()

                        # Convertir le texte JSON en dictionnaire Python
                        try:
                            extracted_info_3 = json.loads(llm_text_3)
                        except json.JSONDecodeError:
                            st.error("❌ Le modèle a renvoyé du texte non-JSON")
                            st.code(llm_text_3)
                            st.stop()

                        # Stocker dans la session
                        # Si extracted_info_3 est une liste de dicts
                        if isinstance(extracted_info_3, list):
                            sponsors = extracted_info_3
                        # Si c'est un dict unique (rare ici)
                        elif isinstance(extracted_info_3, dict):
                            sponsors = [extracted_info_3]
                        else:
                            sponsors = []

                        st.session_state.sponsors_final_data = sponsors
                        st.session_state.request_context = {
                            "ClubOrSport": st.session_state.selected_club.get("ClubOrSport"),
                            "SponsoringPeriod": st.session_state.selected_club.get("SponsoringPeriod"),
                            "EstimatedYearlyInvestment": st.session_state.selected_club.get("EstimatedYearlyInvestment")
                        }


                        reference_region = st.session_state.selected_club.get("Region")
                        sponsors_sorted = sort_sponsors(sponsors, reference_region)

                        st.success(f"✅ {len(sponsors_sorted)} sponsor(s) trouvé(s)")
                        st.write("📋 **Sponsors triés :**")

                        # Affichage propre sponsor par sponsor
                        for idx, sponsor in enumerate(sponsors_sorted, 1):
                            with st.expander(f"#{idx} - {sponsor.get('Sponsor', 'Sans nom')}", expanded=False):

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write(f"🏷️ Type : {sponsor.get('SponsorType', 'N/A')}")

                                    region = sponsor.get('Region')
                                    if region:
                                        if reference_region and region.lower() == reference_region.lower():
                                            st.success(f"📍 Région : {region} ⭐")
                                        else:
                                            st.info(f"📍 Région : {region}")

                                with col2:
                                    st.write(f"💰 Montant : {sponsor.get('EstimatedRevenue', 'Unknown')}")
                                    st.write(f"📅 Période : {sponsor.get('SponsoringPeriod', 'N/A')}")


                    except Exception as e:
                        st.error("❌ Erreur inattendue")
                        st.exception(e)

                    # Détecter spécifiquement les erreurs de webhook N8N
                    try:
                        error_response = response_3.json()
                        error_message = error_response.get("message", "").lower()

                        # Erreur: nœud "Respond to Webhook" non utilisé
                        if response_3.status_code == 500 and "unused respond to webhook" in error_message:
                            st.error("⚠️ **Le workflow N8N n'atteint jamais le nœud 'Respond to Webhook'**")
                            st.warning("""
                            **Problème :** Le workflow s'est terminé sans passer par le nœud de réponse,
                            donc N8N ne peut pas fermer la connexion HTTP correctement.
                            """)
                        # Erreur: webhook pas configuré pour POST
                        elif response_3.status_code == 404 and "not registered for post" in error_message:
                            st.warning("⚠️ **Webhook N8N non configuré pour POST**")
                        # Erreur: webhook non enregistré (mode test)
                        elif response_3.status_code == 404 and "not registered" in error_message:
                            st.warning("⚠️ **Webhook N8N non enregistré**")
                    except:
                        pass

            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout : La requête n'a pas répondu dans les temps")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Erreur de connexion : Impossible de joindre le webhook N8N")
                st.info(f"Vérifiez que l'URL est correcte : `{webhook_url_extract}`")
            except Exception as e:
                st.error(f"❌ Erreur inattendue : {str(e)}")
                st.exception(e)
