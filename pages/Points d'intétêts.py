import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

############################################### CONFIG
st.set_page_config(
    page_title="L'immoblier en Charente Maritime",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

############################################### CHARGEMENT DF
df = pd.read_csv('data/df_17.csv')
df = df.dropna(subset=['code_postal'])


############################################### MAP

# annee_dispo = [2022,2021,2020,2019,2018]
# select_annee = st.selectbox('Selection de l\'année',options=annee_dispo, index=0)

#importation des csv des traces
df_gare = pd.read_csv('data/gare_17.csv')
df_hopital = pd.read_csv('data/hopital_17.csv')
df_pharmacie = pd.read_csv('data/pharmacie_17.csv')
df_ecole = pd.read_csv('data/ecole_17.csv')
df_price = pd.read_csv('data/Price_commune.csv')
df_cinema = pd.read_csv('data/cinema_17.csv')
df_musee = pd.read_csv('data/musee_17.csv')
df_ecole_pl = df_ecole[df_ecole['Secteur Public/Privé'] == 'Public']
df_ecole_pv = df_ecole[df_ecole['Secteur Public/Privé'] == 'Privé']
df_covoit = pd.read_csv('data/covoiturage_17.csv')

#format des traces
x_gare = list(df_gare.iloc[:, 1])
y_gare = list(df_gare.iloc[:, 2])
name_gare = list(df_gare.iloc[:, 0])

y_hopital = list(df_hopital.iloc[:, 1])
x_hopital = list(df_hopital.iloc[:, 2])
name_hopital = list(df_hopital.iloc[:, 0])

y_pharmacie = list(df_pharmacie.iloc[:, 1])
x_pharmacie = list(df_pharmacie.iloc[:, 2])
name_pharmacie = list(df_pharmacie.iloc[:, 0])

y_ecole_pl = list(df_ecole_pl.iloc[:, 4])
x_ecole_pl = list(df_ecole_pl.iloc[:, 5])
name_ecole_pl = list(df_ecole_pl.iloc[:, 0])

y_ecole_pv = list(df_ecole_pv.iloc[:, 4])
x_ecole_pv = list(df_ecole_pv.iloc[:, 5])
name_ecole_pv = list(df_ecole_pv.iloc[:, 0])

y_cinema = list(df_cinema.iloc[:, -3])
x_cinema = list(df_cinema.iloc[:, -2])
name_cinema = list(df_cinema.iloc[:, 1])

y_musee = list(df_musee.iloc[:, -5])
x_musee = list(df_musee.iloc[:, -4])
name_musee = list(df_musee.iloc[:, 4])

y_covoit = list(df_covoit.iloc[:, -8])
x_covoit = list(df_covoit.iloc[:, -9])
name_covoit = list(df_covoit.iloc[:, 2])


a, b, c, d = st.columns(4)
with a:
    st.markdown("**Santé**")
    hopital = st.checkbox('Hopital')
    pharmacie = st.checkbox('Pharmacie')

with b:
    st.markdown("**Culture**")
    cinema = st.checkbox('Cinéma')
    musee = st.checkbox('Musée')

with c:
    st.markdown("**Education**")
    ecole_public = st.checkbox('Ecole Publique')
    ecole_prive = st.checkbox('Ecole privée')

with d:
    st.markdown("**Mobilité**")
    gare = st.checkbox('Gare')
    covoiturage = st.checkbox('Covoiturage')

#filtered features map
# df_map = df [df['annee'] == select_annee]


# remplacer les valeurs infinies par des NaN
df_price = df_price.replace([np.inf, -np.inf], np.nan)
# remplacer les données manquantes par la médiane
df_price['prix_m2_2020'].fillna(df_price['prix_m2_2020'].median(), inplace=True)
df_price['prix_m2_2021'].fillna(df_price['prix_m2_2021'].median(), inplace=True)
df_price['prix_m2_2022'].fillna(df_price['prix_m2_2022'].median(), inplace=True)
# arrondir le prix à deux unités
df_price['prix_m2_2020'] = df_price['prix_m2_2020'].apply(lambda x: round(x,2))
df_price['prix_m2_2021'] = df_price['prix_m2_2021'].apply(lambda x: round(x,2))
df_price['prix_m2_2022'] = df_price['prix_m2_2022'].apply(lambda x: round(x,2))

# trace build
fig_5 = px.scatter_mapbox(df_price, lat="latitude", lon="longitude"
                  ,size_max=30, zoom=8, text ="nom_commune",color="mediane_du_revenu_disponible_2020",
                  color_continuous_scale=px.colors.sequential.Viridis,
                  mapbox_style="carto-positron", height=600 )

fig_5.update_traces(opacity=0.7)

# if trace select
if gare:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_gare,
            lon=x_gare,
            mode='markers',
            text=name_gare,
            hoverinfo='text',
            marker=dict(size=10, color='blue', opacity=0.8),
            name="Gare"
        )
    )
if hopital:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_hopital,
            lon=x_hopital,
            mode='markers',
            text=name_hopital,
            hoverinfo='text',
            marker=dict(size=10, color='red', opacity=1),
            name="Hopital"
        )
    )

if pharmacie:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_pharmacie,
            lon=x_pharmacie,
            mode='markers',
            text=name_pharmacie,
            hoverinfo='text',
            marker=dict(size=10, color='#2FEB4B', opacity=1),
            name="Pharmacie"
        )
    )
if ecole_public:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_ecole_pl,
            lon=x_ecole_pl,
            mode='markers',
            text=name_ecole_pl,
            hoverinfo='text',
            marker=dict(size=10, color='grey', opacity=0.8),
            name="Ecole Publique"
        )
    )
if ecole_prive:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_ecole_pv,
            lon=x_ecole_pv,
            mode='markers',
            text=name_ecole_pv,
            hoverinfo='text',
            marker=dict(size=10, color='grey', opacity=0.8),
            name="Ecole Privée"
        )
    )
if cinema:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_cinema,
            lon=x_cinema,
            mode='markers',
            text=name_cinema,
            hoverinfo='text',
            marker=dict(size=10, color='yellow', opacity=0.8),
            name="Cinéma"
        )
    )
if musee:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_musee,
            lon=x_musee,
            mode='markers',
            text=name_musee,
            hoverinfo='text',
            marker=dict(size=10, color='orange', opacity=0.8),
            name="Musée"
        )
    )
if covoiturage:
    fig_5.add_trace(
        go.Scattermapbox(
            lat=y_covoit,
            lon=x_covoit,
            mode='markers',
            text=name_covoit,
            hoverinfo='text',
            marker=dict(size=10, color='#17becf', opacity=0.8),
            name="Covoiturage"
        )
    )
# view trace
fig_5.update_layout(title_text="title", margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600)

st.plotly_chart(fig_5, use_container_width=True)
