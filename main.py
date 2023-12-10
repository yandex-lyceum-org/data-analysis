from datetime import time

import pandas as pd


def f(x):
    if 0 < x["promo_code"] <= 1.0:
        return x["revenue"] * 0.9
    return x["revenue"]


def get_visit_time(x):
    if time(hour=6) <= x["session_start"].time() < time(hour=10):
        return "morning"
    if time(hour=10) <= x["session_start"].time() < time(hour=17):
        return "afternoon"
    if time(hour=17) <= x["session_start"].time() < time(hour=22):
        return "evening"
    if time(hour=0) <= x["session_start"].time() < time(hour=6) or time(hour=22) <= x["session_start"].time():
        return "night"


def payer(x):
    if x > 0:
        return 1
    return 0


df = pd.read_csv('data.csv', delimiter=',', )
df.columns = df.columns.str.lower().str.replace(' ', '_')
df = df.rename(columns={"sessiondurationsec": "session_duration_sec"})

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

df["visit_time"] = df.apply(get_visit_time, axis=1)

df["payer"] = df["revenue"].map(payer)
avg_revenue = df["total_price"].mean()  # средний чек

all_users = df["region"].count()
byers = df["order_dt"].count()
purch_by_one_user = byers / all_users  # кол-во покупок на одного пользователя
avg_time_by_channel = df.groupby("channel")[
    "session_duration_sec"].mean()  # средняя продолжительность сессии по рекламным каналам
avg_time_by_device = df.groupby("device")[
    "session_duration_sec"].mean()  # средняя продолжительность сессии по рекламным каналам
df.groupby("channel")["total_price"].mean().nlargest(3)  # топ-3 рекламных канала по среднему чеку и их значения
df.groupby("region")["total_price"].mean().nlargest(3)  # топ-3 региона по среднему чеку
df["session_start"].apply(lambda x: 2019 <= x.to_pydatetime().year < 2020).all()  # все session_start в 2019 году

df.apply(lambda x: x["session_start"].date() == x["session_date"].date(),
         axis=1).all()  # все session_start совпадают с session_date
df["session_end"].apply(lambda x: x.year == 2019 <= x.to_pydatetime().year < 2020).all()  # все session_end в 2019 году

df.apply(lambda x:
         (x["session_end"] - x["session_start"] - pd.Timedelta(
             seconds=x["session_duration_sec"])).nanoseconds > 1000,
         axis=1).any()  # все session_start + duration примерно < session_end

t = df.groupby(["region", "month"])["total_price"].mean().groupby(level="month").nlargest(3).reset_index(
    allow_duplicates=True)
# print(.drop(t.columns[0], inplace=True))
# print(t.drop(t.columns[2], axis=1))
t.columns.values[2] = 'del'
t = t.drop("del", axis=1)
# print(t.rename(columns={"month": 'Courses_Duration'}))
print(t)