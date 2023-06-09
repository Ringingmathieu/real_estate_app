import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

############################################### FONCTION
def difference(valeur_a, valeur_b):
    diff = ((valeur_b-valeur_a)/valeur_a)
    return "{:.0%}".format(diff)

reverse_mois = {1:'janvier', 2:'fevrier', 3:'mars', 4: 'avril', 5: 'mai', 6: 'juin', 7: 'juillet', 8: 'aout', 9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'decembre'}
utility_month = ['janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre']
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
############################################### INIT SIDEBAR
st.sidebar.title("POWER IMMO")

############################################### CHARGEMENT DF
df = pd.read_csv('df_17.csv')
df = df.dropna(subset=['code_postal'])
#st.write(df)
############################################### FILTRES
# int variables filtres
code_p_unique = df['code_postal'].unique()
annee_dispo = [2022,2021,2020,2019,2018]
tableau_arrondi = sorted(np.round(code_p_unique).astype(int), reverse=False)
default = ['Toutes les communes']

col1, col2,col3 = st.columns(3)
with col1:
    select_annee = st.selectbox('Selection de l\'année',options=annee_dispo, index=0)
with col2:
    select_cp = st.selectbox('Code postal', options=[*default,*tableau_arrondi])


# si le select commune existe on filtre
if select_cp != 'Toutes les communes':
    df = df[(df["code_postal"] == select_cp)]

# creation du df vente / m2 graph
filtered_df = df[(df["annee"] == select_annee) & (df["type_local"] == "Maison")]
pperm_m = filtered_df.groupby("mois").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())
filtered_df = df[(df["annee"] == select_annee) & (df["type_local"] == "Appartement")]
pperm_a = filtered_df.groupby("mois").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())

if len(pperm_a) == 0:
    pperm_a = pd.DataFrame(columns=['1'])
if len(pperm_m) == 0:
    pperm_m = pd.DataFrame(columns=['0'])
    

combined_df_vente = pd.concat([pperm_m, pperm_a], axis=1)
combined_df_vente.columns = ['Maison', 'Appartement']
#combined_df_vente = combined_df_vente.rename(columns={0: "Maison", 1: "Appartement"})

# creation du df volume /vente graph
filtered_df = df[(df["annee"] == select_annee) & (df["type_local"] == "Maison")]
pperm_m1 = filtered_df.groupby("mois").apply(lambda x: x["id_mutation"].count())
filtered_df = df[(df["annee"] == select_annee) & (df["type_local"] == "Appartement")]
pperm_a1 = filtered_df.groupby("mois").apply(lambda x: x["id_mutation"].count())

if len(pperm_a1) == 0:
    pperm_a1 = pd.DataFrame(columns=['1'])
if len(pperm_m1) == 0:
    pperm_m1 = pd.DataFrame(columns=['0'])
    
combined_df_vol= pd.concat([pperm_m1, pperm_a1], axis=1)
combined_df_vol.columns = ['Maison', 'Appartement']
#combined_df_vol = combined_df_vol.rename(columns={0: "Maison", 1: "Appartement"})

############################################### MAINPAGE
dyna_default = "Charente Maritime"
if select_cp == "Toutes les communes":  
    dynamique_title = "Prix de l'immobilier " + dyna_default + " en " + str(select_annee)
else:
    dynamique_title = "Prix de l'immobilier de la commune : " + str(select_cp) + " en " + str(select_annee)
st.subheader(dynamique_title)

st.divider()

# metrics

# caclcul metrics maison
filtered_df_maison_m2 = df[(df["annee"] == select_annee) & (df["type_local"] == "Maison")]
pperm_m_m = filtered_df_maison_m2.groupby("annee").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())
vente_maison_per_an = str(filtered_df_maison_m2.shape[0])
# calcul metric appartement
filtered_df_appartement_m2 = df[(df["annee"] == select_annee) & (df["type_local"] == "Appartement")]
pperm_m_a = filtered_df_appartement_m2.groupby("annee").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())
vente_appartement_per_an = str(filtered_df_appartement_m2.shape[0])

# calcul métric comparaison N-1 si existant
if select_annee != min(annee_dispo):
    filtered_df_maison_m2_before = df[(df["annee"] == select_annee-1) & (df["type_local"] == "Maison")]
    pperm_m_m_before = filtered_df_maison_m2_before.groupby("annee").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())
    #st.write(pperm_m_m_before.iloc[0])
    dif_percent_maison = difference(pperm_m_m_before.iloc[0],pperm_m_m.iloc[0])

    filtered_df_appartement_m2_before = df[(df["annee"] == select_annee-1) & (df["type_local"] == "Appartement")]
    pperm_m_a_before = filtered_df_appartement_m2_before.groupby("annee").apply(lambda x: x["valeur_fonciere"].sum() / x["surface_reelle_bati"].sum())
    if (len(pperm_m_a_before) == 0) and (len(pperm_m_a) == 0):
        dif_percent_appartement = "0 %"
    else:
        #st.write(pperm_m_a_before)
        dif_percent_appartement = difference(pperm_m_a_before.iloc[0],pperm_m_a.iloc[0])
else:
    dif_percent_maison = "0 %"
    dif_percent_appartement = "0 %"

# init metric principal
if len(pperm_m_m) != 0:
    metric1 = str(round(pperm_m_m.iloc[0]))+ " €/m²"
else:
    metric1= "null"
    
if len(pperm_m_a) != 0:
    metric2 = str(round(pperm_m_a.iloc[0]))+ " €/m²"
else:
    metric2 = "null"

# init dif % metric

col1, col2, col3 = st.columns(3)
col1.metric("Prix m² maisons", metric1, dif_percent_maison)
col2.metric("Prix m² Appartements", metric2, dif_percent_appartement)
with col3:
    st.write('Nombre de ventes sur un an')
    st.write(vente_maison_per_an,""" maisons<br/>""",vente_appartement_per_an,""" appartements""", unsafe_allow_html=True)

#graph
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("Evolution des prix de ventes / m2")
    st.line_chart(combined_df_vente)
with col2:
    st.subheader("Evolution du volume de ventes")
    #st.write(combined_df_vol)
    combined_df_vol = combined_df_vol.fillna(0)
    st.line_chart(combined_df_vol)

st.divider()
st.subheader("Carte des ventes DVF")

############################################### MAP

#filtered features map
df_map = df[df['annee'] == select_annee]
df_map = df_map.dropna(subset=['valeur_fonciere'])
df_map = df_map.drop(df_map[df_map['type_local'] == 'Local industriel. commercial ou assimilé'].index)
df_map = df_map.drop(df_map[df_map['type_local'] == 'Dépendance'].index)

price_commune = pd.read_csv('Price_commune.csv')

df_data = px.data.carshare()


# trace build
fig_5 = px.scatter_mapbox(df_map, lat="latitude", lon="longitude", color="type_local", size="valeur_fonciere",
                  color_discrete_map={"Maison": '#636EFA', 'Appartement' : '#00CC96'}, size_max=75, zoom=7,
                  mapbox_style="carto-positron" )
fig_5.update_traces(opacity=0.7)
fig_5.update_layout(height=600)
# fig_5.add_trace(
#     ff.create_hexbin_mapbox(
#     data_frame=price_commune, lat="latitude", lon="longitude",
#     nx_hexagon=50, opacity=0.5, labels={"color": "Prix au m2"},
#     min_count=1, color="price_per_carre_2022"
# )
# )


# view trace
st.plotly_chart(fig_5, use_container_width=True)


# trouver une commune entre plusieurs paramétres.

# remplacer le multislect par des checkbox par catégorie.
