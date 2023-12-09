import pandas as pd
from IPython.display import display


def f(x):
    if 0 < x["promo_code"] <= 1.0:
        return x["revenue"] * 0.9
    return x["revenue"]


# Напишем функцию для первичной проверки данных
def check_data(data_df):
    print('\033[1m" "Изучим исходные данные" "\033[em')

    print(data_df.info())

    # print(data_df.shape)

    missed_cells = data_df.isnull().sum().sum() / (data_df.shape[0] * (data_df.shape[1] - 1))
    missed_rows = sum(data_df.isnull().sum(axis=1) > 0) / data_df.shape[0]

    print('\033[1m' + '\nПроверка пропусков' + '\033[0m')
    print('Количество пропусков: {:.0f}'.format(data_df.isnull().sum().sum()))
    print('Доля пропусков: {:.1%}'.format(missed_cells) + '\033[0m')
    print('Доля строк содержащих пропуски: {:.1%}'.format(missed_rows))

    print('\033[1m' + '\nПроверка на дубликаты' + '\033[0m')

    print('Количество полных дубликатов: ', data_df.duplicated().sum())

    print('\033[1m' + "\nПервые пять строк датасета" + '\033[0m')
    display(data_df.head(10))

    print("\033[1m" + '\nОпописание количественных данных:' + '\033[0m')

    display(data_df.describe().T)

    print("\033[1m" + '\nОписание категориальных данных: ' + '\033[0m')

    display(data_df.describe(include='object').T)

    print('\033[1m' + "\nвывод уникальных значений по каждому категориальному признаку:" + "\033[0m")

    df_object = data_df.select_dtypes(include='object').columns

    for i in df_object:
        print("\033[1m" + "_" + str(i) + '\033[0m')
        display(data_df[i].value_counts())


df = pd.read_csv('data.csv', delimiter=',', )
df.columns = df.columns.str.lower().str.replace(' ', '_')
# check_data(df)

df["total_price"] = df.apply(f, axis=1)  # новый столбец итоговой цены с учетом промокода

date_col_names = ["session_start", "session_end", "session_date", "order_dt"]
df[date_col_names] = df[date_col_names].apply(pd.to_datetime)  # перевод

a = ["user_id", "region", "device", "channel", "session_start", "session_end", "session_date", "month",
     "day", "hour_of_day"]

df = df.drop(df[df[a].isnull().any(axis=1)].index.tolist())  # удаление 13 строк с пропущенными важными данными

df = df.drop(df[df.duplicated(["user_id", "session_start"])].index.tolist())  # удаление 2 дубликатов

df["region"] = (df["region"].replace("United States", "United States")
                .replace("Frаnce", "France")
                .replace("Unjted States", "United States")
                .replace("Germany", "Germany")
                .replace("UK", "UK")
                .replace("France", "France")
                .replace("Frаncе", "France")
                .replace("Franсe", "France")
                .replace("germany", "Germany")
                .replace("UК", "UK"))

df["device"] = df["device"].replace("android", "Android")

df["channel"] = df["channel"].replace("контексная реклама", "контекстная реклама")

print(df.iloc[487])