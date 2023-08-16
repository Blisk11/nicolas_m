import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np
from datetime import datetime, date
from math import floor
import plotly.express as px
from PIL import Image
from pathlib import Path
import openpyxl
import xml.etree.ElementTree as ET
import requests
import json


# streamlit options
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title='Dashboard cabinet Nicolas MASSABUAU', layout = 'wide', initial_sidebar_state = 'auto')


hide_streamlit_style = """<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
pwd1, pwd2= st.columns((0.5 ,1,))
pwd = pwd1.text_input("Password:", value="")

pwd = st.text_input("Mot de Passe:", value="")

domain = "cloud.leviia.com";
auth=('boina-oisif_pro', 'Heokepide01!'); # admin user
url = "http://"+domain+"/remote.php/dav/files/"+auth[0];
headers = {"OCS-APIRequest": "true"}

if pwd != 'n_MASSABUAU_capucine':
    st.title('Entrez votre mot de passe SVP et appuyer sur entrée')
else:
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    with st.spinner('Mise à jour des informations, un instant SVP.'):
    #t1, t2 = st.columns((0.25,1)) 
        path = "/Oisif-Pro/operation/DATA/dashboard_data";
        df_list = []
        r = requests.request('PROPFIND', url+path, data=None, auth=auth);
        data = ET.fromstring(r.text);
        list = [el[0].text for el in data];
        for i in list:
            if 'Nicolas_MASSABUAU_Osteo' in i:
                path = i
                print(i)
                r = requests.request('GET', "http://"+domain+path, auth=auth)
                temp_df = pd.read_excel(r.content, )
                df_list.append(temp_df)
    
        df = pd.concat(df_list)
        df = df.reset_index()
        min_date = df['date_de_debut'].min().strftime('%d-%m-%Y')
        max_date = df['date_de_debut'].max().strftime('%d-%m-%Y')
        df['1 visite'] = df['1 visite'].astype(str)
        df['année'] = df['année'].astype(str)

        st.title("Votre activité du: " + min_date + ' au ' + max_date)
    
        category_list = [ 'ostéo', 'jour_de_la_semaine', 'nouveau_patient', 'statut', 'année_mois', 'trimestre', 'nom_du_mois', 'année', 'debut', '1 visite', 'age_sex', 'age_bin', 'motif_du_rdv', 'civilite', 'distance_bin', 'nbs_rdv_bin', ]
     
        #Metrics setting and rendering
                
        f1, f2= st.columns((1,1))        
        DF_legend = f1.selectbox('Choisir la légende du tableau ci-dessous', category_list , help = 'La légende du sous groupe à analyser')              
     
        g1, g2 = st.columns((2,1))
        # bar chart

        groupby_df_list = [DF_legend, 'année', 'month_number', 'année_mois']
        data = df.groupby(groupby_df_list)['index'].count().reset_index()
        data.sort_values(['année', 'month_number'], ascending = [True, True], inplace=True)
        #data['month'] = data['month'].astype(str).str.replace('-', '_')
        data.rename(columns = {'index':'nbs rdv'}, inplace=True)

        fig = px.bar(data, x="année_mois", y="nbs rdv", color= DF_legend, title="Nombre de rdv par mois", barmode='group')   
  
        g1.plotly_chart(fig, use_container_width=True)
        #Metrics setting and rendering

        #f22, f33, fempty = st.columns((1,1,1))
        f11, f22, f33empty = st.columns((1, 1, 1))
            
        nom_du_mois = f11.multiselect("Choisir les trimestres que vous souhaitez analyser", df.sort_values('month_number')['nom_du_mois'].drop_duplicates().to_list(), df.sort_values('month_number')['nom_du_mois'].drop_duplicates().to_list(),)
        feature = f22.selectbox("Choisir une caractéristique à analyser", category_list , help = "Choisir l'axe des X du tableau de gauche")
        df_data = df[(df['nom_du_mois'].isin(nom_du_mois))]
        
        f111, f222empty, f333empty = st.columns((1, 1, 1))
        category_list_for_legend_g22 = sorted(set(category_list) - set([feature]))
        legend_g22 = f111.selectbox("Choisir la légendu du graphique à bar ci-dessous", category_list_for_legend_g22 , help = "légende = couleurs",
                                    index = category_list_for_legend_g22.index('1 visite'))
        
        
        g22, g_empty, g33 = st.columns((1, 0.2, 1))


        # Here we use a column with categorical data
        groupby_df_list = [feature, legend_g22, ]
        g22_data = df_data.groupby(groupby_df_list)['index'].count().reset_index()
        
        #data['month'] = data['month'].astype(str).str.replace('-', '_')
        g22_data.rename(columns = {'index':'nbs rdv'}, inplace=True)

        fig = px.bar(g22_data, x=feature, y="nbs rdv", color= legend_g22, title="Nombre de rdv par " + feature, barmode='group')   
        
        #fig = px.histogram(df_data.sort_values(feature), x=feature, color = legend_g22, title=feature)    
        g22.plotly_chart(fig, use_container_width=True)
        
        fig = px.pie(df_data.sort_values(feature), values='rdv_compte', names= feature, title = feature)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        g33.plotly_chart(fig,)

        #st.caption('Pour le tableau ci-dessous, les colonnes est la caractéristique sélectionné ci-haut, veuillez choisir une autre caratéristique pour les rangées.')
        
        f1111, f2222, f3333empty = st.columns((1,1,1))
        feature1111 = f1111.selectbox("Choisir les colonnes du rangées ci-dessous", category_list )
        category_list_for_table = sorted(set(category_list) - set([feature1111]))
        feature2222 = f2222.selectbox("Choisir les colonnes", category_list_for_table,  ) 
        if feature1111 == feature2222:
            st.caption("Si vous voyez une erreur, c'est parce que la caractéristique sélectionné pour les colonnes et rangées sont la même", )
        
        px_table = df_data.groupby([feature1111,feature2222 ])['rdv_compte'].sum().reset_index().sort_values('rdv_compte',ascending=False)
        px_table = px_table.pivot(index = feature1111, columns = feature2222, values = 'rdv_compte')
        px_table1 = px_table.copy()
        px_table.loc["Total"] = px_table.sum()
        
        px_table1 = (px_table1.div(px_table1.sum(), axis=1).round(2)*100).fillna(0).astype(int).astype(str) + '%'        
        # sort columns
        px_table = px_table[px_table.sum().sort_values(ascending=False).index.to_list()].fillna(' ')
        px_table1 = px_table1[px_table1.sum().sort_values(ascending=False).index.to_list()].fillna(' ')
        #st.dataframe(px_table)
        px_table.reset_index(inplace= True)
        fig = go.Figure(
            data = [go.Table (
                header = dict(
                values = px_table.columns,
                font=dict(size=12, color = 'white'),
                fill_color = '#264653',
                line_color = 'rgba(255,255,255,0.2)',
                align = ['left','center'],
                #text wrapping
                height=20
                )
            , cells = dict(
                values = [px_table[K].tolist() for K in px_table.columns], 
                font=dict(size=12),
                align = ['left','center'],
                #fill_color = colourcode,
                line_color = 'rgba(255,255,255,0.2)',
                height=20))],)
        "Nombre de consultation par " + feature1111 + ' et ' + feature2222
        fig.update_layout(
        width=1400,
        height=450,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
            )
        )
        st.plotly_chart(fig,)
        
        st.caption('Les valeurs du tableau ci-haut, mais en % du total (par colonne)')
        px_table1.reset_index(inplace= True)
        fig = go.Figure(
            data = [go.Table (
                header = dict(
                values = px_table1.columns,
                font=dict(size=12, color = 'white'),
                fill_color = '#264653',
                line_color = 'rgba(255,255,255,0.2)',
                align = ['left','center'],
                #text wrapping
                height=20
                )
            , cells = dict(
                values = [px_table1[K].tolist() for K in px_table1.columns], 
                font=dict(size=12),
                align = ['left','center'],
                #fill_color = colourcode,
                line_color = 'rgba(255,255,255,0.2)',
                height=20))],)
        fig.update_layout(
        width=1400,
        height=450,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
            )
        )
        st.plotly_chart(fig,)
