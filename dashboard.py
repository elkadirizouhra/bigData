import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

OUTPUT_DIR = "/mnt/c/Users/dell/Desktop/Chocolux Free Website Template - Free-CSS.com/output"

def load_data(start_date, end_date, article_filter=None):
    """
    Charger et filtrer les données entre deux dates et, si spécifié, filtrer par article.
    """
    all_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    all_data = []

    for file_name in all_files:
        # Extraire la date du fichier
        file_date = file_name[:8]
        if start_date <= file_date <= end_date:
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            # Lire le fichier et ajouter les données au DataFrame
            with open(file_path, 'r') as file:
                lines = file.readlines()  # Lire toutes les lignes du fichier
                for line in lines:
                    try:
                        # Diviser la ligne en deux parties principales : "date_id + id" et le reste
                        date_id_and_id, rest = line.strip().split("  ", 1)
                        
                        # Extraire les parties individuelles
                        date_id = date_id_and_id.strip()
                        article_id, article, total_sales = rest.split("|")
                        
                        # Ajouter les données au tableau final
                        all_data.append([date_id, article_id.strip(), article.strip(), int(total_sales.strip())])
                    except Exception as e:
                        print(f"Ligne invalide ignorée : {line.strip()} - {e}")

    # Créer un DataFrame à partir des données collectées
    df = pd.DataFrame(all_data, columns=["Date", "Article ID", "Article", "Total Sales"])

    if article_filter:
        df = df[df['Article'].str.contains(article_filter, case=False)]  # Filtrer par article si spécifié

    return df


# ---------------------
# Interface utilisateur
# ---------------------
st.set_page_config(page_title="Dashboard des Ventes", layout="wide")

st.title("📊 Dashboard des Ventes")
st.sidebar.header("📅 Filtres")

# Sélection des dates avec un selectbox
start_date = st.sidebar.text_input("Date de début (YYYYMMDD)", "20241101")
end_date = st.sidebar.text_input("Date de fin (YYYYMMDD)", "20241130")
article_filter = st.sidebar.text_input("Filtrer par article", "")

if st.sidebar.button("Charger les données"):
    # Charger les données filtrées
    data = load_data(start_date, end_date, article_filter)

    if not data.empty:
        st.write(f"### 📅 Données entre {start_date} et {end_date}")

        # Afficher le tableau des données avec tri et filtrage
        st.dataframe(data.sort_values(by="Total Sales", ascending=False), height=300)

        # Mise en page : colonnes
        col1, col2 = st.columns(2)

        # Graphique 1 : Diagramme circulaire - Répartition des ventes par article
        with col1:
            fig1 = px.pie(data, values="Total Sales", names="Article", title="Répartition des ventes par Article", 
                          color="Article", color_discrete_sequence=px.colors.qualitative.Set3)
            fig1.update_traces(textinfo="percent+label", pull=[0.1, 0, 0, 0])
            st.plotly_chart(fig1, use_container_width=True)

        # Graphique 2 : Histogramme des ventes totales par article
        with col2:
            fig2 = px.bar(data, x="Article", y="Total Sales", color="Article", title="Total des ventes par Article",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(barmode='stack', xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)

        # Graphique 3 : Courbe cumulée des ventes par jour
        aggregated_by_date = data.groupby("Date").sum().reset_index()
        aggregated_by_date["Cumulative Sales"] = aggregated_by_date["Total Sales"].cumsum()

        st.write("### 📈 Évolution des ventes par jour (Cumulé)")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=aggregated_by_date["Date"], y=aggregated_by_date["Cumulative Sales"],
                                  mode="lines+markers", name="Ventes cumulées", line=dict(color="royalblue", width=3)))
        fig3.update_layout(title="Évolution des ventes cumulées par jour", xaxis_title="Date", yaxis_title="Ventes cumulées")
        st.plotly_chart(fig3, use_container_width=True)

        # Statistiques supplémentaires
        st.write("### 📊 Statistiques")
        total_sales = data["Total Sales"].sum()
        top_article = data.groupby("Article")["Total Sales"].sum().idxmax()
        st.metric("💰 Total des ventes", f"{total_sales} unités")
        st.metric("🔥 Article le plus vendu", top_article)
    else:
        st.error("❌ Aucune donnée trouvée pour cette plage de dates.")
