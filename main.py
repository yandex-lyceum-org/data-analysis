import pandas as pd
import numpy as np

df = pd.read_csv('data.csv', delimiter=',', )

df.columns = df.columns.str.lower().str.replace(' ', '_')


def f(x):
    if x == 1.0:
        return x


print(df.head(10))


# Напишем функцию для первичной проверки данных
def check_data(data_df):
    print('\033[1m" "Изучим исходные данные" "\033[em')

    print(data_df.info())

    # print(data_df.shape)

    missed_cells = data_df.isnull().sum().sum() / (data_df.shape[0] * (data_df.shape[1] - 1))
    missed_rows = sum(data_df.isnull().sum(axis=1) > 0) / data_df.shape[0]

    print('\033[1m' + '\пПроверка пропусков' + '\033[0m')
    print('Количество пропусков: {:.0f}'.format(data_df.isnull().sum().sum()))
    print('Доля пропусков: (:.1%)'.format(missed_cells) + '\033[0m')
    print('Доля строк содержащих пропуски: (:.1%)'.format(missed_rows))

    ### Проверим дубликаты

    print('\033[1m' + '\nПроверка на дубликаты' + '\033[0m')

    print('Количество полных дубликатов: ', data_df.duplicated().sum())

    ## Посмотрим на сами данные
    print('\033[1m' + "\nПервые пять строк датасета" + '\033[0m')
    display(data_df.head())

    print("\033[1m" + '\nОпописание количественных данных:' + '\033[em')

    display(data_df.describe().T)

    print("\033[1m" + '\nОписание категориальных данных: ' + '\033[em')

    display(data_df.describe(include='object').T)

    print('\033[1m' + "\nвывод уникальных значений по каждому категориальному признаку:" + "\033[0m")

    df_object = data_df.select_dtypes(include='object').columns

    for i in df_object:
        print("\033[1m" + "_" + str(1) + '\033[em')
        display(data_df[i].value_counts())
