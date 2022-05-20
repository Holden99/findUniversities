import pandas as pd
import numpy as np
import streamlit as st
import json

def read_faculties():
    with open('./spec_area.json', encoding='utf-16') as json_file:
        data = json.load(json_file)
        return data

def fill_color(val):
    return 'color: green' if val==1 else 'color: red'

def show_bar(data, header, x, x_title):
    plot_spot = st.empty()
    with plot_spot:
    # with st.container():
        st.header(header)
        st.vega_lite_chart(data, {
            'mark': "bar",
            'encoding': {
                'x': {'field': x, 'type': 'quantitative',
                      "title": x_title},
                'y': {'field': 'ukr_name', 'type': 'nominal', "title": ""},
                'color': {'field': 'ukr_name', 'type': 'nominal'},
            },
            'width': 700,
            'height': 400,
        })

def show_plot(data, header, x, x_title, y, y_title):
    plot_spot = st.empty()
    with plot_spot:
    # with st.container():
        st.header(header)
        st.vega_lite_chart(data, {
            'mark': {'type': 'circle', 'tooltip': True, "size": 175},
            'encoding': {
                'x': {'field': x,
                      'type': 'quantitative', "title": x_title},
                'y': {'field': y, 'type': 'quantitative', "title": y_title},
                'color': {'field': 'ukr_name', 'type': 'nominal'},
                'tooltip': [{"field": 'ukr_name', 'type': 'nominal'}],
            },
            'width': 700,
            'height': 400,
        })

if __name__ == '__main__':
    spec_faculties = read_faculties()
    faculties = pd.Series(data = spec_faculties.values()).unique()
    spec_faculties = pd.Series(data = spec_faculties)
    df = pd.read_csv("./last_merged.csv", encoding="utf-16")
    cities = df['місто'].unique()
    military_dep = df['воєнна кафедра'].unique()

    cities_choice = st.sidebar.multiselect("Місто:", cities, default=['Дніпро'])
    faculties_choice = st.sidebar.selectbox("Галузь:", faculties)
    specialities_choice = st.sidebar.selectbox("Спеціальність:", spec_faculties[spec_faculties.isin([faculties_choice])].index)
    price_choice = st.sidebar.slider('Ціна:', min_value=0.0, max_value=df['кінцева ціна'].max(), step=500.0, value=10000.0)
    external_evaluation_choice = st.sidebar.slider('Бал ЗНО:', min_value=100.0, max_value=200.0, step=.5, value=150.0)
    form_of_study = st.sidebar.radio(
        "Акцент на:",
        ('Бюджет', 'Контракт'))
    graduation_choice = st.sidebar.slider('Бал атестату:', min_value=0.0, max_value=12.0, step=.5, value=10.0)
    military_choise = st.sidebar.checkbox(label = "Воєнна кафедра")
    hostel_choise = st.sidebar.checkbox(label="Гуртожиток")
    preparatory_choise = st.sidebar.checkbox(label="Підготовчі курси")
    international_exchange_choise = st.sidebar.checkbox(label="Міжнародний обмін")

    df = df[df['місто'].isin(cities_choice)]
    df = df[df[specialities_choice] == 1]
    df = df[ ((price_choice >= df['начальна ціна']) & (price_choice <= df['кінцева ціна'])) | (price_choice > df['кінцева ціна']) ]
    if form_of_study == 'Бюджет':
        df = df[(external_evaluation_choice >= df[f"{specialities_choice}_бюджет"]) & (df[f"{specialities_choice}_бюджет"] != -1)]
        df = df[graduation_choice >= df[f'Середній бал атестата зарахованих на бюджет']]
    elif form_of_study == 'Контракт':
        df = df[external_evaluation_choice >= df[f"{specialities_choice}_контракт"]]
        df = df[graduation_choice >= df[f'Середній бал атестата зарахованих на контракт']]
    if military_choise:
        df = df[df['воєнна кафедра'].isin([military_choise])]
    if hostel_choise:
        df = df[df['гуртожиток'].isin([hostel_choise])]
    if preparatory_choise:
        df = df[df['підготовчі курси'].isin([preparatory_choise])]
    if international_exchange_choise:
        df = df[df['Міжнародний обмін'].isin([international_exchange_choise])]

    if (len(df) > 0):
        df_heatmap = df[['ukr_name', 'місто', 'воєнна кафедра', 'гуртожиток', 'підготовчі курси', 'Міжнародний обмін']]
        df_heatmap = df_heatmap.style.applymap(fill_color, subset=['гуртожиток', 'воєнна кафедра', 'підготовчі курси', 'Міжнародний обмін'])
        st.table(df_heatmap)

        show_bar(header = f"Середній бал ЗНО на бюджет ({specialities_choice})", data = df,
                 x =f"{specialities_choice}_бюджет",
                 x_title="Середній бал на бюджет")
        st.table(df[['ukr_name', f"{specialities_choice}_бюджет"]].rename(columns = {"ukr_name": "назва", f"{specialities_choice}_бюджет": "бали"}))

        show_bar(header=f"Середній бал ЗНО на контракт ({specialities_choice})", data=df,
                 x=f"{specialities_choice}_контракт",
                 x_title="Середній бал на контракт")

        st.table(df[['ukr_name', f"{specialities_choice}_контракт"]].rename(columns = {"ukr_name": "назва", f"{specialities_choice}_контракт": "бали"}))

        show_bar(header="Начальна ціна", data=df,
                 x='начальна ціна',
                 x_title="ціна")

        show_bar(header="Кінцева ціна", data=df,
                 x='кінцева ціна',
                 x_title="ціна")

        st.table(df[['ukr_name', f"ціна"]])

        show_bar(header="Середній бал ЗНО на бюджет (загальний)", data=df,
                 x='Середній бал ЗНО зарахованих на бюджет',
                 x_title="бал")

        st.table(df[['ukr_name', f"Середній бал ЗНО зарахованих на бюджет"]])

        show_bar(header="Середній бал ЗНО на контракт (загальний)", data=df,
                 x='Середній бал ЗНО зарахованих на контракт',
                 x_title="бал")

        st.table(df[['ukr_name', f"Середній бал ЗНО зарахованих на контракт"]])

        show_bar(header="Середній бал атестату на бюджет", data=df,
                 x='Середній бал атестата зарахованих на бюджет',
                 x_title="бал")

        st.table(df[['ukr_name', f"Середній бал атестата зарахованих на бюджет"]])

        show_bar(header = "Середній бал атестату на контракт", data = df,
                 x ='Середній бал атестата зарахованих на контракт',
                 x_title="бал")

        st.table(df[['ukr_name', f"Середній бал атестата зарахованих на контракт"]])

        show_bar(header="Конкурс на одне бюджетне місце", data=df,
                 x='Конкурс на одне бюджетне місце (всі заяви)',
                 x_title="кількість чоловік")

        st.table(df[['ukr_name', f"Конкурс на одне бюджетне місце (всі заяви)"]])

        show_bar(header="Середній пріоритет всіх заяв", data=df,
                 x='Середній пріоритет всіх заяв (від 1 до 9)',
                 x_title="пріоритет")


        st.table(df[['ukr_name', f"Середній пріоритет всіх заяв (від 1 до 9)"]])

        show_bar(header="Всього на бюджет", data=df,
                 x='Зараховано на бюджет всього',
                 x_title="всього на бюджет")

        st.table(df[['ukr_name', f"Зараховано на бюджет всього"]])

        show_bar(header="Всього на контракт", data=df,
                 x='Зараховано на контракт всього',
                 x_title="всього на контракт")

        st.table(df[['ukr_name', f"Зараховано на контракт всього"]])

        show_bar(header="Зараховано іноземців", data=df,
                 x='Зараховано іноземців на контракт',
                 x_title="всього")

        st.table(df[['ukr_name', f"Зараховано іноземців на контракт"]])

        show_plot(header="Середній бал ЗНО & Конкурс на одне бюджетне місце", data=df,
                  x=f"{specialities_choice}_бюджет",
                  x_title=f"бал ЗНО {specialities_choice}",
                  y='Конкурс на одне бюджетне місце (всі заяви)',
                  y_title='Конкурс на одне бюджетне місце')

        show_plot(header="Всього зараховано на бюджет & Всього зараховано на контракт", data=df,
                  x=f"Зараховано на бюджет всього",
                  x_title=f"Зараховано на бюджет всього",
                  y='Зараховано на контракт всього',
                  y_title='Зараховано на контракт всього')

        print(type(df['ціна'].iloc[0]))
        ukr_names = df['ukr_name']
        refs = df['сайт']
        for i, ukr_name in enumerate(ukr_names):
            st.text(f"{i + 1}) {ukr_name}")
            st.markdown("<a>" + refs.iloc[i] + "</a>", unsafe_allow_html=True)
    else:
        st.title(f"Немає результатів")
    print("done")





