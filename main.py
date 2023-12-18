from datetime import time

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


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


def remove_outlier(df_in, col_name):
    q1 = df_in[col_name].quantile(0.05)
    q3 = df_in[col_name].quantile(0.95)
    df_out = df_in.loc[(df_in[col_name] >= q1) & (df_in[col_name] <= q3) | (df_in[col_name].isna())]
    return df_out


df = pd.read_csv('data.csv', delimiter=',', )
df.columns = df.columns.str.lower().str.replace(' ', '_')
df = df.rename(columns={"sessiondurationsec": "session_duration_sec"})


date_col_names = ["session_start", "session_end", "session_date", "order_dt"]
df[date_col_names] = df[date_col_names].apply(pd.to_datetime)  # перевод

a = ["user_id", "region", "device", "channel", "session_start", "session_end", "session_date", "month",
     "day", "hour_of_day"]

df = df.drop(df[df[a].isnull().any(axis=1)].index.tolist())  # удаление 13 строк с пропущенными важными данными

df = df.drop(df[df.duplicated(["user_id", "session_start"])].index.tolist())  # удаление 2 полных дубликатов

df["total_price"] = df.apply(f, axis=1)  # новый столбец итоговой цены с учетом промокода

df = remove_outlier(df, "total_price")

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

t = df.groupby("month")["total_price"].mean().nlargest(3).reset_index()["month"].tolist()  # топ 3 месяца по чеку

t2 = df[df["month"].isin(t)].groupby(["month", "region"])["total_price"].mean()  # с разбивкой на регионы

d = df.groupby(["month", "channel"])["user_id"].count().reset_index()

top3_channels = d.groupby('month').apply(lambda x: x.nlargest(3, 'user_id')).reset_index(drop=True)

len(df["user_id"].unique()), df["user_id"].count()  # все пользователи уникальные

k = pd.DataFrame()
grouped = df.groupby("channel")
k["users_amount"] = grouped["user_id"].count()
k["unique_users_amount"] = grouped["user_id"].apply(lambda x: len(x.unique()))
k["amount_of_payers"] = grouped["payer"].sum()
k["total_sum"] = grouped["total_price"].sum()
k.nlargest(1, "total_sum")  # большая сумма продаж
k.nlargest(1, "users_amount")  # больше всего пользователей

# TODO: подписать оси на всех графиках

# pie = df["region"].value_counts() / df["region"].count() * 100
# pie.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()
#
# pie2 = df["channel"].value_counts() / df["channel"].count() * 100
# pie2.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()
#
# pie3 = df["device"].value_counts() / df["device"].count() * 100
# pie3.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()

# pie4 = df.groupby("region")["payer"].value_counts()
# pie4.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()

# pie5 = df.groupby("device")["payer"].value_counts()
# pie5.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()

# pie6 = df.groupby("channel")["payer"].value_counts()
# pie6.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()

# hist = df[df["payer"] == 1].value_counts("month", sort=False)
# hist.plot.bar(grid=True)
# plt.show()

# hist2 = df[df["payer"] == 1].value_counts("day", sort=False)
# hist2.plot.bar(grid=True)
# plt.show()

# hist3 = df[df["payer"] == 1].value_counts("hour_of_day", sort=False)
# hist3.plot.bar(grid=True)
# plt.show()

# ночью покупали больше всего? Это связано с тем, что основные покупатели из Америки, где во время покупок ночь.
# hist = df[df["payer"] == 1].value_counts("visit_time", sort=False)
# hist.plot.bar(grid=True)
# plt.subplots_adjust(bottom=.2)
# plt.xlabel("")
# plt.show()

# pie7 = df[df["payer"] == 1].groupby("payment_type").sum("payer")["payer"]
# pie7.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show()

# print(df["device"].unique())

# print(df[df["payer"] == 1].groupby(["region", "device"])["session_date"].value_counts())
# df['num_session_date'] = df['session_date'].apply(mpl_dates.date2num)
#
# shapiro_test_stat, shapiro_p_value = shapiro(df['num_session_date'])
# print(f"Тест Шапиро-Уилка для session_date: статистика={shapiro_test_stat}, p-значение={shapiro_p_value}")

# Первая и вторая гипотеза через ANOVA (не интересно)

# regions = df['region'].unique()
# for region in regions:
#     region_data = df[(df['region'] == region) & (df["payer"] == 1)]
#     reg = region_data.groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#
#     devices = region_data['device'].unique()
#
#     devices_res = []
#
#     for device in devices:
#         dev = region_data[region_data["device"] == device].groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#         devices_res.append(dev)
#
#     stats, pvalue = f_oneway(*devices_res)
#     print(region, stats, pvalue)
#
# regions = df['region'].unique()
# for region in regions:
#     region_data = df[(df['region'] == region) & (df["payer"] == 1)]
#     reg = region_data.groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#
#     channels = region_data['channel'].unique()
#
#     channels_res = []
#
#     for channel in channels:
#         dev = region_data[region_data["channel"] == channel].groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#         channels_res.append(dev)
#
#     stats, pvalue = f_oneway(*channels_res)
#     print(region, stats, pvalue)

# Первая и вторая гипотеза через t-test (интересно для девайсов по usa)


# regions = df['region'].unique()
# for region in regions:
#     region_data = df[(df['region'] == region) & (df["payer"] == 1)]
#     reg = region_data.groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#
#     devices = region_data['device'].unique()
#     for device in devices:
#         dev = region_data[region_data["device"] != device].groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#         stats, pvalue = ttest_ind(reg, dev)
#         if pvalue < 0.05:
#             print("влияет", region, device, stats, pvalue)
#         else:
#             print("Не влияет", region, device, stats, pvalue)
#     print()

# regions = df['region'].unique()
# for region in regions:
#     region_data = df[(df['region'] == region) & (df["payer"] == 1)]
#     reg = region_data.groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#
#     channels = region_data['channel'].unique()
#     for channel in channels:
#         dev = region_data[region_data["channel"] != channel].groupby("session_date")["payer"].count().reset_index(name="count")["count"]
#         stats, pvalue = ttest_ind(reg, dev)
#         if pvalue < 0.05:
#             print("влияет", region, channel, stats, pvalue)
#         else:
#             print("Не влияет", region, channel, stats, pvalue)
#     print()


df[df["payer"] == 1].groupby("region")["total_price"].mean()
df[df["payer"] == 1].groupby("channel")["total_price"].mean()
df[df["payer"] == 1].groupby("visit_time")["total_price"].mean()

df[df["payer"] == 1][["session_duration_sec", "total_price"]].corr("spearman")  # корреляции очень слабая

# Гипотеза 1: Влияет ли регион на тип оплаты продукта?
# cont_table = pd.crosstab(df["region"], df["payment_type"])
# p_val_payment_type = chi2_contingency(cont_table).pvalue # p = 0.9724 - данные между регионом и типом оплаты независимы

# Гипотеза 2: Влияет ли день недели на кол-во покупок?

# bh = df[df["payer"] == 1]
# bh = bh.groupby("day")["payer"].count()
# bh.plot.pie(autopct='%.1f%%')
# plt.ylabel("")
# plt.show() # Из диаграммы видно, что особых различий между кол-вом покупок нет. Вывод: день недели не зависит от покупок

# X = df[["region", "channel"]]
#
# # print(X)
#
# columnTransformer = ColumnTransformer([('encoder', OneHotEncoder(sparse_output=False), ["region", "channel"])],
#                                       remainder='passthrough')
# X = columnTransformer.fit_transform(X)
# # X = pd.DataFrame()
# # print(X)
# # X = pd.DataFrame(X)
# # print(X)
#
# y = df["total_price"].fillna(0)
#
# # print(y)
# # print(X)
#
# # Разделение на обучающий и тестовый наборы
# X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False)
#
# # Построение модели линейной регрессии
# model = LinearRegression()
# model.fit(X_train, y_train)
#
# # Предсказание на тестовом наборе
# y_pred = model.predict(X_test)
#
# # Оценка качества модели
# mse = mean_squared_error(y_test, y_pred)
# r2 = r2_score(y_test, y_pred)
#
# print(f'Средняя квадратичная ошибка: {mse}')
# print(f'R^2: {r2}')

X = df[['region', 'channel', 'payment_type']]

y = pd.DataFrame()

y["total_price"] = df['total_price'].fillna(0)
y["payer"] = df["payer"]
print(df.shape)
print(y.shape, X.shape)

# Разделение на обучающий и тестовый наборы
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, shuffle=False)

# Создание пайплайна для предобработки данных
categorical_cols = ['region', 'channel', 'payment_type']
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, categorical_cols)
    ])

# Создание модели линейной регрессии вместе с предобработкой данных
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', LinearRegression())
])

# Обучение модели
model.fit(X_train, y_train)

# Предсказание на тестовом наборе
y_pred = model.predict(X_test)

# Оценка качества модели
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Средняя квадратичная ошибка: {mse}')
print(f'R^2: {r2}')
