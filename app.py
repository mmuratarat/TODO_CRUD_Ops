import streamlit as st
import streamlit.components.v1 as stc
from streamlit_option_menu import option_menu
from database import *
import pandas as pd
import numpy as np
from datetime import date

st.set_page_config(
     page_title="Takvim Uygulaması"
 )

html_temp = """
<div style="background-color:#831302;padding:1.5px">
<h1 style="color:white;text-align:center;">YAPILACAKLAR LİSTESİ </h1>
</div><br>"""
st.markdown(html_temp,unsafe_allow_html=True)
st.markdown('<style>h1{color: red;}</style>', unsafe_allow_html=True)

with st.sidebar:
    options = option_menu(menu_title = "MENÜ", options = ["Yarat (CREATE)", "Oku (READ)", "Güncelle (UPDATE)", "Sil (DELETE)"],
                         icons=['calendar-plus', 'book', 'wrench', 'x-square'],
                         menu_icon="house", default_index=0, orientation="vertical",
                         styles={
        "container": {"padding": "5!important", "background-color": "#d9d7d7"},
        "icon": {"color": "black", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#9c9a9a"},
        "nav-link-selected": {"background-color": "#831302"},
    }
    )

create_table()

if options == 'Yarat (CREATE)':
    st.subheader("Görevlerinizi Ekleyiniz:")
    
    col1, col2 = st.columns(2)
    with col1:
        task_ = st.text_area("Gerçekleştireceğiniz görevin ismini giriniz:")
        
    with col2:
        status_ =st.selectbox("Durum", ["Yapılacak", "Devam Ediyor", "Tamamlandı"])
        date_ =st.date_input("Bitiş Tarihi")
    
    if st.button("Görevi Ekleyin!"):
        if (task_ == ''):
            st.warning('Önce görevinizi giriniz!')
        elif (len(retrieve_task(task_ = task_))):
            st.error('Görev zaten mevcut!')
        else:
            insert_data(task_, status_, date_)
            st.success("Göreviniz başarıyla eklendi: '{}'".format(task_))

if options == 'Oku (READ)':
    data = show_data()
    data_df = pd.DataFrame(data, columns = ["Görev", "Durum", "Bitiş Tarihi"])

    with st.expander("Bütün görevleri inceleyiniz:"):
        st.dataframe(data_df)
    with st.expander("Görevlerin Son Durumu"):
        tasks_df = data_df["Durum"].value_counts().to_frame()
        print(tasks_df)
        tasks_df.reset_index()
        st.dataframe(tasks_df)

if options == 'Güncelle (UPDATE)':
    st.subheader("Görevleri Düzenleyiniz / Güncelleyiniz:")
    data = show_data()
    data_df = pd.DataFrame(data, columns = ["Görev", "Durum", "Bitiş Tarihi"])
    with st.expander("Güncel görevleriniz:"):
        st.dataframe(data_df)

    list_of_tasks = [i[0] for i in view_tasks()]
    selected_task = st.selectbox("Görev",list_of_tasks)
    task_result = retrieve_task(selected_task)

    if task_result:
        task_name, task_status, task_to_date =  task_result[0]
        date_val = [int(x) for x in task_to_date.split('-')]
        task_to_date = date(date_val[0], date_val[1], date_val[2])
        
        task_list =  ["Yapılacak", "Devam Ediyor", "Tamamlandı"]
        task_index = task_list.index(task_status)
        
        col1,col2 = st.columns(2)
        with col1:
            new_task = st.text_area("Yapılacak Görev", task_name)
        
        with col2:
            new_task_status = st.selectbox("Durum", task_list, index = task_index)
            new_task_to_date = st.date_input("Bitiş Tarihi", task_to_date)
            
        if st.button("Görevi Güncelle"):

            if(new_task == ''):
                st.error('Önce görevinizi giriniz!')

            elif(len(retrieve_task(new_task)) and task_status == new_task_status and task_to_date == new_task_to_date):
                st.error('Görev zaten mevcut!')

            else:
                update_task(new_task, new_task_status, new_task_to_date, task_name, task_status, task_to_date)
                st.success("Güncellenmiş Görev: '{}'".format(task_name))
                
                with st.expander("Güncellenmiş görevleri gör:"):
                    result = show_data()
                    clean_df = pd.DataFrame(result, columns = ["Görev", "Durum", "Bitiş Tarihi"])
                    st.dataframe(clean_df)

if options == 'Sil (DELETE)':
    st.subheader("Görevleri Silebilirsiniz!")
    data = show_data()
    data_df = pd.DataFrame(data, columns = ["Görev", "Durum", "Bitiş Tarihi"])
    with st.expander("Güncel görevleriniz:"):
        st.dataframe(data_df)

    list_of_tasks = [i[0] for i in view_tasks()]
    list_of_tasks.append('Bütün görevleri sil')
    selected_task = st.selectbox("Görev",list_of_tasks)

    if st.button("Delete"):
        if selected_task == 'Bütün görevleri sil':
            drop_create_table()
            st.success("Bütün görevler başarı ile silindi!")
        else:
            delete_data(selected_task)
            st.success("Deleted Task: '{}'".format(selected_task))

        with st.expander("Güncellenmiş görevleri gör:"):
            result = show_data()
            clean_df = pd.DataFrame(result, columns = ["Görev", "Durum", "Bitiş Tarihi"])
            st.dataframe(clean_df)

# Hide the footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)