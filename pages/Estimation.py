import streamlit as st
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd
from sklearn.linear_model import LinearRegression
############################################### FONCTION

############################################### CONFIG
st.set_page_config(
    page_title="Estime ton bien !",
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
# a corrigers sur le df pour les anomalie

geolocator = Nominatim(user_agent="my_app")
df_17 = df_17 = pd.read_csv('data/df_17.csv')
df_17['prix_m2'] = df_17['valeur_fonciere'] / df_17['surface_reelle_bati']
#st.write(df_17)

def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return False
    
def linearRegression(encoded_df, select_local_type, select_surface_reelle_bati, select_surface_terrain, nb_piece_prin):
    encoded_df = pd.get_dummies(df, columns=["type_local"])
    # Si la colonne Appart n'existe pas on la rajoute à la fin
    position_appartement = len(encoded_df.columns) - 1
    position_maison = len(encoded_df.columns)
    # si l'une des colonnes n'existe pas apres le get Dum
    if "type_local_Appartement" not in encoded_df.columns:
        encoded_df.insert(position_appartement, "type_local_Appartement", 0)
    if "type_local_Maison" not in encoded_df.columns:
        encoded_df.insert(position_maison, "type_local_Maison", 0)

    
    #st.write(encoded_df)
    # Préparation des données d'entraînement
    X = encoded_df.drop("valeur_fonciere", axis=1)  # Variables indépendantes
    y = encoded_df["valeur_fonciere"]  # Variable dépendante

    # Entraînement du modèle de régression linéaire
    model = LinearRegression()
    model.fit(X, y)

    # Estimation du prix pour une nouvelle maison
    if select_local_type == "Maison":
        select_local_type_maison = 0
        select_local_type_appart = 1
    else:
        select_local_type_maison = 1
        select_local_type_appart = 0
        
    nouvelle_maison = pd.DataFrame({
        "surface_reelle_bati": [select_surface_reelle_bati],
        "surface_terrain": [select_surface_terrain],
        "nombre_pieces_principales": [nb_piece_prin],
        "type_local_Appartement": [select_local_type_maison],
        "type_local_Maison": [select_local_type_appart]
    })

    prix_estime = model.predict(nouvelle_maison)
    a,b,c = st.columns(3)
    with b:
        st.header(str(round(prix_estime[0]))+" €")




def filter_coordinates(lat, lon, df):
    """
    fonctionnement du calcul

    A partir d'une localisation gps lat/lon
    on va attribuer une colonne de distance a un df provisoire de distance par rapport a ce point
    ensuite on va chercher les id qui rentre dans la condition de distance_threshold.
    Si il trouve moins de 6 resultats pour 2022
    On rentre dans une boucle while qui va 
        verifier qu'il y a moins de 6 id pour 2022 et une distance max de recherche pour garder une cohérence de prix/m2
        On applique un elargissement du cercle de recherche des resultat au fur est a messure des boucles pour eviter trop de travail
        distance_threshold = (distance_threshold + (add_meter*boucle))

    En sortie on a donc un df qui contient 
        - au mininum 6 ventes pour 2022
        - dans ce cercle de recherche les ventes des annnees precedentes
    Si un manque de donnée:
        - 0 vente pour 2022 avec un stop de la recherche aprés avoir atteint la limite imposé
        - 0 ou plus de vente pour les années precedentes.

    Pourquoi recupérer les années precedentes:
        Car meme si il n'y a pas de vente, on va essayer de proposer un prix /m2 pondérer en attribuant une hausse des prix/m2
        antécédant aux données N-1

    """
    #  on attribu le df a une variable plus parlante
    df_filtered = df
    # on recupére la lat
    reference_lat = lat
    # on recupére la lon
    reference_lon = lon
    # define une valeur de distance pour le premier test
    distance_threshold = 100 

    # recupération des colonnes au mini pour tester la rapidité d'exe
    df_filtered = df_filtered[['id_mutation', 'latitude', 'longitude', 'annee']]
    # delete val null
    df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])

    # on ajoute un colonne en calculant la distance entre les points du df
    df_filtered['distance'] = df_filtered.apply(
        lambda row: distance.distance((row['latitude'], row['longitude']), (reference_lat, reference_lon)).meters,
        axis=1
    )

    #  on instancie un df dans la variable ou on garde que les distance inf a distance_threshold
    df_filtered_p = df_filtered[df_filtered['distance'] < distance_threshold]

    # define distance max i de recupération et un seuil mini de recupération / add_meter pour la formule de radius
    seuil = 6
    max_distance = 2000
    boucle = 0
    add_meter = 25

    while (len(df_filtered_p.loc[df_filtered_p['annee'] == 2022]) < seuil) and (distance_threshold < max_distance):
        boucle +=1
        distance_threshold = (distance_threshold + (add_meter*boucle))
        
        df_filtered_p = df_filtered[df_filtered['distance'] < distance_threshold]
        #st.write('distance : ',distance_threshold, ' nb bien find : ', len(df_filtered_p.loc[df_filtered_p['annee'] == 2022]))
    
    # Réinitialiser l'index du DataFrame filtré
    df_filtered_p = df_filtered_p.reset_index(drop=True)
    df_filtered_p = df_filtered_p.sort_values('distance', ascending=True)
    # DF SMALL 
    return df_filtered_p

st.title("Estimer votre bien")

address = st.text_input("Entrez une adresse")
az, er, ty,ui = st.columns(4)
with az:
    select_local_type = st.selectbox("Type de bien", options=["Maison", "Appartement"])
with er:
    select_surface_reelle_bati = st.number_input("Surface habitable en m2", step=1, min_value=0)
with ty:
    select_surface_terrain = st.number_input("Surface terrain en m2", step=1, min_value=0)
with ui:
    select_piece_principale = st.number_input("Nombre Pièces Principales", step=1, min_value=0)

a,b,c,d,e = st.columns(5)
with c:
    btn = st.button("Estimer")

if btn:
    # gestion de l'erreur surface_bati
    if select_surface_reelle_bati <= 0:
        st.info('Précisez une surface habitable', icon="ℹ️")
        st.stop()

    coordinates = get_coordinates(address)
    if coordinates == False:
        st.info('Adresse introuvable', icon="ℹ️")
        st.stop()

    latitude, longitude = coordinates
    df_filtered = filter_coordinates(latitude, longitude, df_17)
    ##### CALCUL
    df_filtered = df_17[df_17['id_mutation'].isin(df_filtered['id_mutation'])]
   
    liste_maison_vendus_2022 = df_filtered[(df_filtered["annee"] == 2022) & (df_filtered["type_local"] == "Maison")]
    nombre_maison_vendus_2022 = len(df_filtered[(df_filtered["annee"] == 2022) & (df_filtered["type_local"] == "Maison")])
    nombre_maison_vendus_allDate= len(df_filtered[df_filtered["type_local"]== "Maison" ])

    liste_appartement_vendus_2022 = df_filtered[(df_filtered["annee"] == 2022) & (df_filtered["type_local"] == "Appartement")]
    nombre_appartement_vendus_2022 = len(df_filtered[(df_filtered["annee"] == 2022) & (df_filtered["type_local"] == "Appartement")])
    nombre_appartement_vendus_allDate= len(df_filtered[df_filtered["type_local"]== "Appartement" ])
    #### CALCUL

    if coordinates:

        donnee2022secteur = df_filtered[(df_filtered["annee"] == 2022)][['type_local', 'valeur_fonciere', 'surface_reelle_bati', 'surface_terrain', 'nombre_pieces_principales']]
        donnee2022secteur['surface_terrain'] = donnee2022secteur['surface_terrain'].fillna(0)

        if len(donnee2022secteur) > 5:
            df = pd.DataFrame(donnee2022secteur)
            linearRegression(df,select_local_type,select_surface_reelle_bati, select_surface_terrain,select_piece_principale )
        elif len(donnee2022secteur) < 5:
            donnee2022et2021secteur = df_filtered[(df_filtered["annee"] == 2022) & (df_filtered["annee"] == 2021)][['type_local', 'valeur_fonciere', 'surface_reelle_bati', 'surface_terrain', 'nombre_pieces_principales']]
            donnee2022et2021secteur['surface_terrain'] = donnee2022et2021secteur['surface_terrain'].fillna(0)
            if len(donnee2022et2021secteur) > 1:
                df = pd.DataFrame(donnee2022et2021secteur)
                linearRegression(df,select_local_type,select_surface_reelle_bati, select_surface_terrain,select_piece_principale )
            else:
                st.header("Pas assez de données pour estimer.")
        else:
            st.header("Pas assez de données pour estimer.")
            


        # CREATION DU DICT POUR PLOLTY
        data = dict(
            lat=[latitude],
            lon=[longitude]
        )
        # AFFICHE LA MAP
        fig = px.scatter_mapbox(data, lat="lat", lon="lon", zoom=12)
        fig.update_traces(marker=dict(color="red", size=20))
        fig.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig)
        
        st.subheader("Proche de chez vous ...")
        st.divider()
        a, b = st.columns(2)
        with a:
            st.header("MAISON")
            
            # calcul price
            if len(liste_maison_vendus_2022):
                st.write(liste_maison_vendus_2022)
                prix_m2_2022_maison = round(liste_maison_vendus_2022['prix_m2'].sum() / nombre_maison_vendus_2022)
                ###### END CALCUL

                col1,col2 = st.columns(2)
                with col1:
                    st.write('nb vente 2022') 
                    st.subheader(str(nombre_maison_vendus_2022))
                with col2:
                    st.write("2018 a 2022 ")
                    st.subheader(str(nombre_maison_vendus_allDate) )
                st.subheader(str(prix_m2_2022_maison)+" €/m2")
        with b:
            st.header("APPARTEMENT")
            
            # calcul price
            if len(liste_appartement_vendus_2022):
                prix_m2_2022_appart = round(liste_appartement_vendus_2022['prix_m2'].sum() / nombre_appartement_vendus_2022)
                ###### END CALCUL

                col3,col4 = st.columns(2)
                with col3:
                    st.write('Nnb vente 2022')
                    st.subheader(str(nombre_appartement_vendus_2022))
                with col4:
                    st.write("2018 a 2022")
                    st.subheader(str(nombre_appartement_vendus_allDate) )

                st.subheader(str(prix_m2_2022_appart)+" €/m2")

        # affiche le data frame des ventes pour la curiosité
        st.write('Données pour 2022')
        donnee2022secteur['prix/m2'] = round(donnee2022secteur['valeur_fonciere'] / donnee2022secteur['surface_reelle_bati'])

        st.dataframe(donnee2022secteur)

    else:
        st.error("Adresse invalide")
