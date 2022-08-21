import streamlit as st
import streamlit.components.v1 as stc
from streamlit_option_menu import option_menu
from database import drop_create_table, create_table, insert_data, show_data, retrieve_task, delete_data, view_tasks, update_task
import pandas as pd
import numpy as np
from datetime import date
import sqlite3
from sqlite3 import Connection

@st.cache(hash_funcs={Connection: id})
def get_connection(path: str):
    """Put the connection in cache to reuse if path does not change between Streamlit reruns.
    NB : https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
    """
    return sqlite3.connect(path, check_same_thread=False)

def drop_create_table(conn: Connection):
    conn.execute('DROP TABLE IF EXISTS TODO_TABLE;')
    conn.execute('CREATE TABLE IF NOT EXISTS TODO_TABLE(task_ TEXT NOT NULL UNIQUE, status_ NOT NULL, date_ DATE NOT NULL, PRIMARY KEY (task_))')
    conn.commit()

def create_table(conn: Connection):
    # cursor.execute('DROP TABLE IF EXISTS TODO_TABLE;')
    conn.execute('CREATE TABLE IF NOT EXISTS TODO_TABLE(task_ TEXT NOT NULL UNIQUE, status_ NOT NULL, date_ DATE NOT NULL, PRIMARY KEY (task_))')
    conn.commit()
    
def insert_data(task_: str, status_: str, date_: str, conn: Connection):
    conn.execute("INSERT INTO TODO_TABLE(task_, status_, date_) VALUES (?, ?, ?)", (task_, status_, date_)) # Always use the format YYYY-MM-DD to insert the date into database.
    conn.commit()
    
def show_data(conn: Connection):
    records = pd.read_sql(sql = 'SELECT * FROM TODO_TABLE', con=conn)
    return records

def retrieve_task(task_, conn: Connection):
    query = f'SELECT * FROM TODO_TABLE WHERE task_ = "{task_}"'
    records = pd.read_sql(sql = query, con=conn)
    return records

def delete_data(task_, conn: Connection):
    conn.execute('DELETE FROM TODO_TABLE WHERE task_ = "{}"'.format(task_))
    conn.commit()
    
def view_tasks(conn: Connection):
    records = pd.read_sql(sql = "SELECT DISTINCT task_ FROM TODO_TABLE", con=conn)
    return records

def update_task(new_task_, new_status_, new_date_, task_, status_, date_, conn: Connection):
    conn.execute('UPDATE TODO_TABLE SET task_ = ?, status_ = ?, date_ = ?  WHERE task_ = ? and status_ = ? and date_ = ?', (new_task_, new_status_, new_date_, task_, status_, date_))
    conn.commit()
    records = conn.fetchall()
    return records

st.set_page_config(page_title="Takvim Uygulaması")

def main():
    html_temp = """
    <div style="background-color:#831302;padding:1.5px">
        <h1 style="color:white;text-align:center;">YAPILACAKLAR LİSTESİ </h1>
</div><br>"""
    st.markdown(html_temp, unsafe_allow_html=True)
    st.markdown('<style>h1{color: red;}</style>', unsafe_allow_html=True)

    with st.sidebar:
      options = option_menu(menu_title="MENÜ", options=["Yarat (CREATE)", "Oku (READ)", "Güncelle (UPDATE)", "Sil (DELETE)"],
                            icons=['calendar-plus', 'book',
                                   'wrench', 'x-square'],
                            menu_icon="house", default_index=0, orientation="vertical",
                           styles={
          "container": {"padding": "5!important", "background-color": "#d9d7d7"},
          "icon": {"color": "black", "font-size": "25px"},
          "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#9c9a9a"},
          "nav-link-selected": {"background-color": "#831302"},
        }
        )

    db_file = "myDatabase_TODO.db"
    conn = get_connection(db_file)
    create_table(conn)
    
    if options == 'Yarat (CREATE)':
        st.subheader("Görevlerinizi Ekleyiniz:")

        col1, col2 = st.columns(2)
        with col1:
            task_ = st.text_area("Gerçekleştireceğiniz görevin ismini giriniz:")

        with col2:
            status_ = st.selectbox("Durum", ["Yapılacak", "Devam Ediyor", "Tamamlandı"])
            date_ = st.date_input("Bitiş Tarihi")

        if st.button("Görevi Ekleyin!"):
            if (task_ == ''):
                st.warning('Önce görevinizi giriniz!')
            elif (len(retrieve_task(task_=task_, conn=conn))):
                st.error('Görev zaten mevcut!')
            else:
                insert_data(task_, status_, date_, conn=conn)
                st.success("Göreviniz başarıyla eklendi: '{}'".format(task_))

    if options == 'Oku (READ)':
        data_df = show_data(conn=conn)
        data_df.columns = ["Görev", "Durum", "Bitiş Tarihi"]

        with st.expander("Bütün görevleri inceleyiniz:"):
            st.dataframe(data_df)
        with st.expander("Görevlerin Son Durumu"):
            tasks_df = data_df["Durum"].value_counts().to_frame()
            print(tasks_df)
            tasks_df.reset_index()
            st.dataframe(tasks_df)

    if options == 'Güncelle (UPDATE)':
        st.subheader("Görevleri Düzenleyiniz / Güncelleyiniz:")
        data_df = show_data(conn=conn)
        data_df.columns = ["Görev", "Durum", "Bitiş Tarihi"]

        with st.expander("Güncel görevleriniz:"):
            st.dataframe(data_df)

        list_of_tasks = list(view_tasks(conn = conn)['task_'])
        selected_task = st.selectbox("Görev", list_of_tasks)
        task_result = retrieve_task(selected_task, conn=conn)

        if task_result:
            task_name, task_status, task_to_date = task_result[0]
            date_val = [int(x) for x in task_to_date.split('-')]
            task_to_date = date(date_val[0], date_val[1], date_val[2])

            task_list = ["Yapılacak", "Devam Ediyor", "Tamamlandı"]
            task_index = task_list.index(task_status)

            col1, col2 = st.columns(2)
            with col1:
                new_task = st.text_area("Yapılacak Görev", task_name)

            with col2:
                new_task_status = st.selectbox(
                    "Durum", task_list, index=task_index)
                new_task_to_date = st.date_input("Bitiş Tarihi", task_to_date)

            if st.button("Görevi Güncelle"):

                if (new_task == ''):
                    st.error('Önce görevinizi giriniz!')

                elif (len(retrieve_task(new_task,)) and task_status == new_task_status and task_to_date == new_task_to_date):
                    st.error('Görev zaten mevcut!')

                else:
                    update_task(new_task, new_task_status, new_task_to_date,
                                task_name, task_status, task_to_date)
                    st.success("Güncellenmiş Görev: '{}'".format(task_name))

                    with st.expander("Güncellenmiş görevleri gör:"):
                        result = show_data(conn=conn)
                        clean_df = pd.DataFrame(
                            result, columns=["Görev", "Durum", "Bitiş Tarihi"])
                        st.dataframe(clean_df)

    if options == 'Sil (DELETE)':
        st.subheader("Görevleri Silebilirsiniz!")
        data_df = show_data(conn=conn)
        data_df.columns = ["Görev", "Durum", "Bitiş Tarihi"]

        with st.expander("Güncel görevleriniz:"):
            st.dataframe(data_df)

        list_of_tasks = list(view_tasks(conn = conn)['task_'])
        list_of_tasks.append('Bütün görevleri sil')
        selected_task = st.selectbox("Görev", list_of_tasks)

        if st.button("Delete"):
            if selected_task == 'Bütün görevleri sil':
                drop_create_table(conn=conn)
                st.success("Bütün görevler başarı ile silindi!")
            else:
                delete_data(selected_task, conn = conn)
                st.success("Deleted Task: '{}'".format(selected_task))

            with st.expander("Güncellenmiş görevleri gör:"):
                result = show_data(conn=conn)
                result.columns = ["Görev", "Durum", "Bitiş Tarihi"]
                st.dataframe(result)

    # Hide the footer
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()