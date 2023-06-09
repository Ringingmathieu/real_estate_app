# voir pour garder le zoom de plolty chart au meme niveau que lors du clique pour eviter de rezommer a chaque fois


#### DEBUG A FAIRE SUR :
       # gerer les oulier sur les données max de Charente Maritime
        # peut etre retirer les outliers ou pour les montants de + de 15K/m2 faire opération (valeur_fonciere / superficie_terrain)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import geopandas as gpd

def afficher_barre_couleurs(prix_min, prix_max, prix_article):
    """
    param 1 = prix mini,
    param 2  = prix max,
    param 3 = prix a placer
    """
    # Vérifier que la liste de couleurs contient exactement 10 couleurs
    couleurs = ["#FFFF00", "#FFCC00", "#FF9900", "#FF6600", "#FF3300", "#FF0000", "#CC0000", "#990000", "#660000", "#330000"]
    # Trouver l'indice de la tranche de prix de l'article
    indice_article = int((prix_article - prix_min) / (prix_max - prix_min) * 10)

    # Afficher la barre de couleurs avec mise en évidence de la tranche de prix de l'article
    barre_couleurs = ""
    for i, couleur in enumerate(couleurs):
        if i == indice_article:
            barre_couleurs += f'<span style="background-color: {couleur}; display: inline-block; width: 9%; height: 20px; margin-right: 1px; border: 0px solid black;"></span>'
        else:
            barre_couleurs += f'<span style="background-color: {couleur}; display: inline-block; width: 9%; height: 10px; margin-right: 1px;"></span>'
        
    st.markdown(barre_couleurs, unsafe_allow_html=True)

def bloc(df, first, end):
        
    for i in range(first, end):
        ####
        cc, c, d = st.columns([1,5,2])
        type_bien = str(df.iloc[i, 30])
        
        surface = str(df.iloc[i, 31])+"m²"
        chambre = str(df.iloc[i, 32])+"pièces"
        nombre = df.iloc[i, 4]
        formatted_number = "{:,.0f}".format(nombre).replace(",", " ")
        prix = str(formatted_number)+" €"
        ######
        with cc:
            if type_bien == "Maison":
                st.image("https://cdn.icon-icons.com/icons2/1860/PNG/512/apartment_118092.png", width=60)
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/197/197722.png", width=60)
        with c:
            st.markdown(type_bien)
            st.write(surface, " / " ,chambre)
            
        with d:
            st.subheader(prix)
        st.divider()

def mean_min_max(df, colonne, commune="Charente-Maritime"):
    """
    1 - df = DataFrame,
    2 - colonne = str,
    3 - commune = par defaut Charente-Maritime,
    r = # r[mean, min, max]
    """
    r = []

    if commune == "Charente-Maritime": #la moyenne de toute les communes
        r.append(round(df[colonne].mean()))
    else:
        val = df.loc[df["nom_commune"] == commune, colonne] # pour le df ( Price_commune ) ==  1 ligne (deja des moyennes dans les valeurs)
        val = round(val)
        #st.write(val)
        val = int(val) 
        r.append(val)

    r.append(round(df[colonne].min()))
    r.append(round(df[colonne].max()))
    # r[mean, min, max]
    return r

############################################### CONFIG
st.set_page_config(
    page_title="L'immoblier en Charente Maritime",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

############################################### INIT SIDEBAR
st.sidebar.title("POWER IMMO")

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

########### GESTION DES SESSION et VARIABLE SESSION
#si session est vide on la remplie avec Charente maritime c'est le premier chargement
if 'commune_selection' not in st.session_state:
    st.session_state.commune_selection = "Charente-Maritime"
#################################################################### DEBUG A FAIRE SUR LA MAP GUA , dans le df LE GUA
if st.session_state.commune_selection == "Gua":
    st.session_state.commune_selection = "Le Gua"
if st.session_state.commune_selection == "Gué-d'Alleré":
    st.session_state.commune_selection = "Le Gué-d'Alleré"
if st.session_state.commune_selection == "Clisse":
    st.session_state.commune_selection = "La Clisse"
if st.session_state.commune_selection == "Brée-les-Bains":
    st.session_state.commune_selection = "La Brée-les-Bains"
if st.session_state.commune_selection == "Bois-Plage-en-Ré":
    st.session_state.commune_selection = "Le Bois-Plage-en-Ré"
if st.session_state.commune_selection == "Couarde-sur-Mer":
    st.session_state.commune_selection = "La Couarde-sur-Mer"
if st.session_state.commune_selection == "Portes-en-Ré":
    st.session_state.commune_selection = "Les Portes-en-Ré"
if st.session_state.commune_selection == "Château-d'Oléron":
    st.session_state.commune_selection = "Le Château-d'Oléron"
if st.session_state.commune_selection == "Tremblade":
    st.session_state.commune_selection = "La Tremblade"
if st.session_state.commune_selection == "Vallée":
    st.session_state.commune_selection = "La Vallée"
if st.session_state.commune_selection == "Rochelle":
    st.session_state.commune_selection = "La Rochelle"
if st.session_state.commune_selection == "Gripperie-Saint-Symphorien":
    st.session_state.commune_selection = "La Gripperie-Saint-Symphorien"
if st.session_state.commune_selection == "Vergne":
    st.session_state.commune_selection = "La Vergne"
    
    

if 'point' not in st.session_state:
    st.session_state.point = None
select_commune = None


############################################### CHARGEMENT DF
df = pd.read_csv('Price_commune.csv')
df_17 = pd.read_csv('df_17.csv')
###### tri df , je le fais ici mais faudrait le cleanner un peu plus, valeur fonciére none ou adjudiction a - de 200 Euros/m2 a kill a mon avis
df_17 = df_17[df_17['annee']==2022]
#st.dataframe(df)
####### MODIF DU DF JUSTE APRES ouverture en focntion des session a verifier si c'est judicieux
if st.session_state.commune_selection != "Charente-Maritime":
    df_17 = df_17.loc[df_17['nom_commune'] == st.session_state.commune_selection]

#st.dataframe(df_17)
#st.write(df_17.shape)
############################################### MAP + VUE D'ENSEMBLE

a,b = st.columns([1,2])
with a:
    vvsloc = st.selectbox("Sélectionnez un onglet", ("Vente", "Location"))

    if vvsloc == "Vente": # VUE ENSEMBLE VENTE
        # panel 1 vente
        st.write("""
                    <h4 style="text-align:center;font-weight:lighter">Prix de vente au m²</h4>
                    <h2 style="text-align:center">""",st.session_state.commune_selection,"""</h2>
                """, unsafe_allow_html=True)
        st.write("""<p style="text-align:center">Prix moyen au m2</p>""", unsafe_allow_html=True)
        if len(df_17):

            prix_mini_m2_vente_charente_M = mean_min_max(df,"prix_m2_2022")
            prix_mini_m2_vente_commune = mean_min_max(df,"prix_m2_2022", st.session_state.commune_selection)

            max_quartile = round(df['prix_m2_2022'].quantile([0.99]))

            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(prix_mini_m2_vente_commune[0]),""" €</p>""", unsafe_allow_html=True)
  
            afficher_barre_couleurs(int(prix_mini_m2_vente_charente_M[1]), int(max_quartile), int(prix_mini_m2_vente_commune[0]))
        else:
            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">no result</p>""", unsafe_allow_html=True)

    if vvsloc == "Location": # VUE ENSMBLE LOCATION
        # panel 1 Location
        st.write("""
                    <h4 style="text-align:center;font-weight:lighter">Prix de location au m²</h4>
                    <h2 style="text-align:center">""",st.session_state.commune_selection,"""</h2>
                """, unsafe_allow_html=True)
        prix_mean_loc_app = mean_min_max(df,"prix_loyer_appartement",st.session_state.commune_selection)
        prix_mean_loc_maison = mean_min_max(df,"prix_loyer_maison",st.session_state.commune_selection)
        prix_mean_loc_glob = round((prix_mean_loc_app[0]+prix_mean_loc_maison[0])/2)
        prix_min_loc_glob = round((prix_mean_loc_app[1]+prix_mean_loc_maison[1])/2)
        prix_max_loc_glob = round((prix_mean_loc_app[2]+prix_mean_loc_maison[2])/2)

        st.write("""<p style="text-align:center">Prix moyen au m2</p>""", unsafe_allow_html=True)
        st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(prix_mean_loc_glob),"""€</p>""", unsafe_allow_html=True)
        afficher_barre_couleurs(prix_min_loc_glob, prix_max_loc_glob, prix_mean_loc_glob)

with b:  # LA MAP

    link = "https://france-geojson.gregoiredavid.fr/repo/departements/17-charente-maritime/communes-17-charente-maritime.geojson"
    gdf = gpd.read_file(link)

    fig = go.Figure(go.Choroplethmapbox(geojson=gdf.geometry.__geo_interface__,
                                        locations=gdf.index,
                                        z=gdf.index,
                                        hovertemplate=gdf['nom'],
                                        marker_opacity=0.1,
                                        colorbar=None,
                                        showscale=False))

    fig.update_layout(mapbox_style="carto-positron",
                    mapbox_zoom=7,
                    mapbox_center={"lat": 45.8001, "lon": -1.1521},
                    margin={"r": 0, "t": 0, "l": 0, "b": 0}
                    )

    #st.plotly_chart(fig)

    point = plotly_events(fig, click_event=True)

    if st.button('Reset selection commune'):
        del(st.session_state.commune_selection)
        st.experimental_rerun()

    if point and st.session_state.point != point:
        st.session_state.point = point
        select_commune = gdf.iloc[point[0]["pointIndex"]]['nom']
        st.session_state.commune_selection = select_commune
        st.experimental_rerun()

ta, tb = st.tabs(["Détails de prix", "Le voisinage"])
with ta:
##################################### 
    if vvsloc == "Vente": # DETAIL SI SELECT == VENTE
        st.write("""<h3><span style="color:grey;font-weight:lighter">Prix vente des</span> appartements au m² : """,st.session_state.commune_selection,"""</h3>""", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            #### CALCUL SUR DF_17 PV MEAN APPART 
           
            if len(df_17[df_17['type_local'] == 'Appartement']):
                moyenne_appartement = df_17[df_17['type_local'] == 'Appartement']['valeur_fonciere'].mean()
                #st.write(df_17)
                moyenne_appartement_m2 = df_17[df_17['type_local'] == 'Appartement']['surface_reelle_bati'].mean()
                DF_moyenne_min_appartement = df_17[df_17['type_local'] == 'Appartement'].groupby('type_local')
                DF_moyenne_min_appartement = DF_moyenne_min_appartement[['valeur_fonciere', 'surface_reelle_bati']]
                moyenne_min_appartement = DF_moyenne_min_appartement.apply(lambda x: (x['valeur_fonciere'] / x['surface_reelle_bati']).min())
                DF_moyenne_max_appartement = df_17[df_17['type_local'] == 'Appartement'].groupby('type_local')
                DF_moyenne_max_appartement = DF_moyenne_max_appartement[['valeur_fonciere', 'surface_reelle_bati']]
                moyenne_max_appartement = DF_moyenne_max_appartement.apply(lambda x: (x['valeur_fonciere'] / x['surface_reelle_bati']).max())
                moyenne_appartement = round(moyenne_appartement/moyenne_appartement_m2)
                moyenne_min_appartement = round(moyenne_min_appartement[0])
                moyenne_max_appartement = round(moyenne_max_appartement[0])


            else:
                moyenne_min_appartement = "Aucun resultat"
                moyenne_appartement = "Aucun resultat"
                moyenne_max_appartement = "Aucun resultat"
            ####
            st.write("""<p style="text-align:center">prix de vente moyen d’un appartement non meublé</p>""", unsafe_allow_html=True)
            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(moyenne_appartement),""" €</p>""", unsafe_allow_html=True)
        with b:
            
            data_vente_appart = {
                " ": ["prix min ", "prix moyen", "prix haut"],
                "Prix de vente m2": [str(moyenne_min_appartement)+" €/m²", str(moyenne_appartement)+" €/m²", str(moyenne_max_appartement)+" €/m²"],
            }

            st.table(data_vente_appart)

        st.divider()

        st.write("""<h3><span style="color:grey;font-weight:lighter">Prix vente des</span> maisons au m² : """,st.session_state.commune_selection,"""</h3>""", unsafe_allow_html=True)

        a, b = st.columns(2)
        with a:
            #### CALCUL SUR DF_17 PV MEAN MAISON 
            if len(df_17[df_17['type_local'] == 'Maison']):
                #st.write(df_17)
                moyenne_maison = df_17[df_17['type_local'] == 'Maison']['valeur_fonciere'].mean()
                moyenne_maison_m2 = df_17[df_17['type_local'] == 'Maison']['surface_reelle_bati'].mean()
                     
                DF_moyenne_min_maison = df_17[df_17['type_local'] == 'Maison'].groupby('type_local')
                DF_moyenne_min_maison = DF_moyenne_min_maison[['valeur_fonciere', 'surface_reelle_bati']]
                moyenne_min_maison = DF_moyenne_min_maison.apply(lambda x: (x['valeur_fonciere'] / x['surface_reelle_bati']).min())
              
                DF_moyenne_max_maison = df_17[df_17['type_local'] == 'Maison'].groupby('type_local')
                DF_moyenne_max_maison = DF_moyenne_max_maison[['valeur_fonciere', 'surface_reelle_bati']]
                moyenne_max_maison = DF_moyenne_max_maison.apply(lambda x: (x['valeur_fonciere'] / x['surface_reelle_bati']).max())
                     
                moyenne_maison = round(moyenne_maison/moyenne_maison_m2)
                moyenne_min_maison = round(moyenne_min_maison[0])
                moyenne_max_maison = round(moyenne_max_maison[0])
            else:
                moyenne_min_maison = "Aucun resultat"
                moyenne_maison = "Aucun resultat"
                moyenne_max_maison = "Aucun resultat"
            ####
            st.write("""<p style="text-align:center">Prix de vente moyen d’une maison</p>""", unsafe_allow_html=True)
            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(moyenne_maison),""" €</p>""", unsafe_allow_html=True)
        with b:
            
            data_vente_maison = {
                " ": ["prix min ", "prix moyen", "prix haut"],
                "Prix de vente m2": [str(moyenne_min_maison)+" €/m²", str(moyenne_maison)+" €/m²", str(moyenne_max_maison)+" €/m²"],
            }

            st.table(data_vente_maison)

###############################
    if vvsloc == "Location": # DETAIL SI SELECT == LOCATION
        st.write("""<h3><span style="color:grey;font-weight:lighter">Loyer des</span> appartements au m² : """,st.session_state.commune_selection,"""</h3>""", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            st.write("""<p style="text-align:center">Loyer moyen d’un appartement non meublé</p>""", unsafe_allow_html=True)
            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(prix_mean_loc_app[0]),""" €</p>""", unsafe_allow_html=True)
        with b:
            # Données de la table location
            if st.session_state.commune_selection == "Charente-Maritime": 
                tab_prix_m2_min =str(prix_mean_loc_app[0])+" €/m²"
                tab_prix_m2_mean = mean_min_max(df,"prix_loyer_appartement_2p",st.session_state.commune_selection)
                tab_prix_m2_max = mean_min_max(df,"prix_loyer_appartement_3p",st.session_state.commune_selection)
                tab_prix_m2_mean = str(tab_prix_m2_mean[0])+" €/m²"
                tab_prix_m2_max = str(tab_prix_m2_max[2])+" €/m²"
            else:
                tab_prix_m2_min = df.loc[df["nom_commune"] == st.session_state.commune_selection, "prix_loyer_appartement"]
                tab_prix_m2_min = str(round(tab_prix_m2_min.iloc[0]))+"€/m²"
                tab_prix_m2_mean = df.loc[df["nom_commune"] == st.session_state.commune_selection, "prix_loyer_appartement_2p"]
                tab_prix_m2_mean = str(round(tab_prix_m2_mean.iloc[0]))+"€/m²"
                tab_prix_m2_max = df.loc[df["nom_commune"] == st.session_state.commune_selection, "prix_loyer_appartement_3p"]
                tab_prix_m2_max = str(round(tab_prix_m2_max.iloc[0]))+"€/m²"
            data = {
                "Type d'appartement": ["1 pièce", "2 pièce", "3 pièce +"],
                "Loyer au m² moyen Non meublé ": [tab_prix_m2_min,tab_prix_m2_mean,tab_prix_m2_max],
            }

            st.table(data)

        st.divider()

        st.write("""<h3><span style="color:grey;font-weight:lighter">Loyer des</span> maisons au m² en Charente-Maritime</h3>""", unsafe_allow_html=True)

        a, b = st.columns(2)
        with a:
            st.write("""<p style="text-align:center">Loyer moyen d’un maison non meublé</p>""", unsafe_allow_html=True)
            st.write("""<p style="text-align:center; font-weight:bold;font-size:50px">""",str(prix_mean_loc_maison[0]),""" €</p>""", unsafe_allow_html=True)
        with b:
            # Données de la table vente 
            tab_prix_m2_mean_maison = str(prix_mean_loc_maison[0])+" €/m²"
            data = {
                "Type d'appartement": ["maison"],
                "Prix vente au m² moyen ": [tab_prix_m2_mean_maison],
            }

            st.table(data)

with tb:
    if vvsloc == "Vente":        
        tba, tbb, tbc, tbd = st.columns(4)
        with tba:
            st.subheader('Ventes 2022')
            st.write("""<p style="text-align:center;color: #277DA2; font-weight:bold;font-size:50px">""",str(len(df_17)),"""</p>""", unsafe_allow_html=True)
        with tbb:
            st.subheader("Type de bien")
            a,b = st.columns(2)
            with a:
                ##### calcul des % maison / appartement
                count_maison = df_17[df_17['type_local'] == 'Maison'].shape[0]
                count_maison_if = df_17[df_17['type_local'] == 'Maison']
                if len(count_maison_if):
                    count_appartement = df_17[df_17['type_local'] == 'Appartement'].shape[0]
                    total = count_maison + count_appartement
                    percent_maison = round((count_maison / total) * 100)
                    percent_appartement = round((count_appartement / total) * 100)
                    ##### fin du calcul

                    values = [percent_appartement, percent_maison]
                    fig = go.Figure(data=[go.Pie(values=values, hole=.7,showlegend=False,hoverinfo='skip', textinfo='none')])
                    colors = ['#DEF0F8', '#277DA2']
                    fig.update_traces(marker=dict(colors=colors))
                    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=100)
                    st.plotly_chart(fig,use_container_width=True)

                    with b:
                        st.write("""<span style="margin: 0;padding:0;text-align:center;color: #277DA2; font-weight:bold;font-size:50px">""",str(percent_maison),""" %</span>""", unsafe_allow_html=True)
                    st.markdown("*de maisons*")
                    st.write("et ",str(percent_appartement)," % d'appartement")
                else:
                    st.subheader("no result")

        with tbc:
            st.subheader("Surface vente")
            if len(df_17):
                ########### calcul surface de vente
                sum_maison = df_17[df_17['type_local'] == 'Maison']['surface_reelle_bati'].sum()
                sum_appartement = df_17[df_17['type_local'] == 'Appartement']['surface_reelle_bati'].sum()
                total_surface = sum_maison + sum_appartement
                sum_0_40 = df_17[(df_17['type_local'] == 'Maison') | (df_17['type_local'] == 'Appartement')]['surface_reelle_bati'].loc[(df_17['surface_reelle_bati'] >= 0) & (df_17['surface_reelle_bati'] <= 40)].sum()
                sum_41_99 = df_17[(df_17['type_local'] == 'Maison') | (df_17['type_local'] == 'Appartement')]['surface_reelle_bati'].loc[(df_17['surface_reelle_bati'] >= 41) & (df_17['surface_reelle_bati'] <= 99)].sum()
                sum_100_plus = df_17[(df_17['type_local'] == 'Maison') | (df_17['type_local'] == 'Appartement')]['surface_reelle_bati'].loc[df_17['surface_reelle_bati'] >= 100].sum()
                # debug
                #st.write(sum_0_40)
                #st.write(sum_41_99)
                #st.write(sum_100_plus)
                # end debug
                percent_0_40 = round((sum_0_40 / total_surface) * 100)
                percent_41_99 = round((sum_41_99 / total_surface) * 100)
                percent_100_plus = round((sum_100_plus / total_surface) * 100)
                ########### fin du calcul
                
                a,b = st.columns(2)
                with a:
                    values = [100-percent_41_99, percent_41_99]
                    fig = go.Figure(data=[go.Pie(values=values, hole=.7,showlegend=False,hoverinfo='skip', textinfo='none')])
                    colors = ['#DEF0F8', '#277DA2']
                    fig.update_traces(marker=dict(colors=colors))
                    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=100)
                    st.plotly_chart(fig,use_container_width=True)
                with b:
                    st.write("""<span style="text-align:center;color: #277DA2; font-weight:bold;font-size:50px">""",str(percent_41_99),""" %</span>""", unsafe_allow_html=True)
                st.write("entre 40 et 100 m2")
                st.write("et ",str(percent_0_40)," % moins de 40m2, ",str(percent_100_plus)," % plus de 100m2")
            else:
                st.subheader("No result")

        with tbd:
            st.subheader('Logement')
            a,b = st.columns(2)
            with a:
                noR = "No result"
                #Gripperie-Saint-Symphorien
                if st.session_state.commune_selection != "Charente-Maritime":
                    vacant_tt = df.loc[df["nom_commune"] == st.session_state.commune_selection, "nombre_logements_2019"]
                    vacant_reste = df.loc[df["nom_commune"] == st.session_state.commune_selection, "nombre_logements_vacants_2019"]
                    vacant_tt = vacant_tt.iloc[0]
                    vacant_reste = vacant_reste.iloc[0]
                    if vacant_reste > 0:
                        percent_vacant = round((vacant_tt / vacant_reste))
                    else:
                        percent_vacant = 0
                else:
                    vacant_tt = df["nombre_logements_2019"].sum()
                    vacant_reste = df["nombre_logements_vacants_2019"].sum()
                    percent_vacant = round((vacant_tt / vacant_reste))

                values = [vacant_reste, vacant_tt]
                fig = go.Figure(data=[go.Pie(values=values, hole=.7,showlegend=False,hoverinfo='skip', textinfo='none')])
                colors = ['#DEF0F8', '#277DA2']
                fig.update_traces(marker=dict(colors=colors))
                fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=100)
                st.plotly_chart(fig,use_container_width=True)
            with b:
                st.write("""<span style="text-align:center;color: #277DA2; font-weight:bold;font-size:50px">""",str(percent_vacant),""" %</span>""", unsafe_allow_html=True)
            st.markdown("*Nombre de logement vacant*")

        st.divider()
        st.write("""<h3 style="text-align:center"><span style="color:grey;font-weight:lighter">Derniére </span> vente 2022</h3>""", unsafe_allow_html=True)

        if st.session_state.commune_selection != "Charente-Maritime":
            df_ventes = df_17[df_17["nom_commune"] == st.session_state.commune_selection]
            df_ventes = df_ventes.sort_values(by='date_mutation', ascending=False)
            df_ventes = df_ventes.head(6)
        else:
            df_ventes = df_17.sort_values(by='date_mutation', ascending=False)
            df_ventes = df_ventes.head(6)

        if len(df_ventes):
            a, b = st.columns(2)

            first = []
            end = []
            for i, element in enumerate(df_ventes.index):
                if i % 2 == 0:  # si c paire
                    first.append(i)
                else:
                    end.append(i)

            with a:
                bloc(df_ventes, 0, len(first))

            
            with b:
                sum_max = len(first) + len(end)
                bloc(df_ventes, len(first), sum_max)
        else:
            st.subheader("Il n'y a pas eu de ventes dans votre secteur")

    st.divider()
    st.write("""<h3 style="text-align:center"><span style="color:grey;font-weight:lighter">Données </span> démographiques</h3>""", unsafe_allow_html=True)
    
    if st.session_state.commune_selection != "Charente-Maritime":
        df_demo = df[df["nom_commune"] == st.session_state.commune_selection]
        chomage = str(df_demo.iloc[0, 12])+" %"
        revenu = str(df_demo.iloc[0, 11])+" €"
        menage = str(df_demo.iloc[0, 16])+" %"
        menage_1 = str(round(df_demo.iloc[0, 17]))+" pop"

        evo_chomage = str(round(df_demo.iloc[0, 12]-st.session_state.demo[0],1))+" %"
        evo_revenu = str(round(st.session_state.demo[1]-df_demo.iloc[0, 11]))+" €"
        evo_menage = str(round(st.session_state.demo[2]-df_demo.iloc[0, 16]))+" %"
        evo_menage_1 = str(abs(round(st.session_state.demo[3]-df_demo.iloc[0, 17])))+" personnes"

    else:
        df_demo = df.copy()
        # calcul des entier ou float pour chargement session
        chomage = round(df_demo['taux_de_chomage_des_15-64_ans_2019'].mean())
        revenu = round(df_demo['mediane_du_revenu_disponible_2020'].mean())
        menage = round(df_demo['part_des_menages_emmenage_moins_2_ans_2019'].mean())
        menage_1 = round(df_demo['taille_moyenne_menages_emmenage_moins_2_ans_2019'].mean())
        # si la session demo n'existe pas on la defini
        if "demo" not in st.session_state:
            st.session_state.demo = [chomage,revenu,menage,menage_1]
        #define var pour alimenter st.metric
        chomage = str(chomage)+" %"
        revenu = str(revenu)+" €"
        menage = str(menage)+" %"
        menage_1 = str(menage_1)+" pop"

        # define variable vide pour la suite au premier chargement ( Charente Maritime)
        evo_chomage = None
        evo_revenu = None
        evo_menage = None
        evo_menage_1 = None
        

    a, b, c, d = st.columns(4)

    a.metric("Taux de chômage",chomage, evo_chomage, delta_color="inverse")
    b.metric("Revenu médian",revenu,evo_revenu)
    c.metric("Part ménages de moins de 2 ans",menage, evo_menage)
    d.metric("Taille des nouveaux ménages",menage_1, evo_menage_1)

#st.write(df)
