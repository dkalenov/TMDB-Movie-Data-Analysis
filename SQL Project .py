#!/usr/bin/env python
# coding: utf-8

# 1) Устанавливаем необходимые библиотеки

# In[1]:


import sqlite3
import pandas as pd
import ydata_profiling
import matplotlib.pyplot as plt
import gdown # для скачивания файлов с гугл диска


# 2) Импортируем данные

# In[2]:


# Прописываем путь к Excel фаилу на Google Disk 
direct_link_to_file = 'https://docs.google.com/spreadsheets/d/1MfDtDtMZjPYIb2oMGGL0MXjgzhkShUi2/export?format=xlsx' 
file_name = 'movies_tmdb.xlsx'

# Скачиваем Excel фаил с Google Disk 
gdown.download(direct_link_to_file, file_name, quiet=False)

# Считываем Excel фаил в DataFrame
xlsx = pd.ExcelFile(file_name)
df = pd.read_excel(xlsx, sheet_name='1')

# Выводим первые строки для понимания структуры таблицы и визуализации
df.head(3)


# 3) Удаляем ненужные для анализа столбцы 

# In[3]:


df.drop(['Unnamed: 0','overview','tagline', 'original_language', 'popularity'], axis=1, inplace=True) 


# 4) Профилируем данные

# In[4]:


df.profile_report()


# Согласно профайлингу данных:
# 
# - Количество строк: 10 001; количество столбцов: 10;
# 
# - Общее количество пропусков 33, что составляет менее 0.1%. Большенство пропусков (23) в столбце 'release_date', в столбце 'vote_average' 1 пропуск, 'vote_count' - 1 , 'budget' - 2,'production_companies' - 2, 'revenue' - 2, 'runtime' - 2; 
# 
# - Дупликатов не обнаружено.

# 5) Форматируем датафрейм: удаляем пропуски, убираем ненужную информацию из строк, форматируем значения строк. 

# - Удаляем все строки с пропусками

# In[5]:


df.dropna(inplace=True)


# - Убираем значение времени из столбца release_date, оставляя только дату релиза

# In[6]:


#в столбце release_date значения не удавалось напрямую переделать в формат даты, поэтому пришлось использовать 
#аргумент errors='coerce' метода pd.to_datetime(), который преобразовывает неправильные значения в значение NaT (Not a Time)
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')

#извлекаем только дату из преобразованных значений
df['release_date'] = df['release_date'].dt.date


#  - приводим данные в столбце 'vote_count' к типу int

# In[7]:


df['vote_count'] = df['vote_count'].astype(int)


# In[8]:


df.head(3)


# In[9]:


df.info() # выводим информацию по датасету для проверки перед закгрузой в bd


# 6) Подключаемся к db в SQLite

# In[10]:


con = sqlite3.connect(r'E:\MathsHub\SQL\sql project\tmdb_movies', timeout=10)
cur = con.cursor() 


# 7) Добавляем таблицу в db

# In[11]:


df.to_sql(con=con, name='movies_table', index=False, if_exists='replace')


# Гипотеза 1: чем больше в год выходит фильмов, тем больше среди них «долларовых миллиардеров»
# 

# Выведем рейтинг фильмов, собравших в прокате более млрд. долларов США для понимания картины

# In[12]:


top_boxoffice = cur.execute('SELECT ROW_NUMBER() OVER(ORDER BY revenue DESC) AS rating, title, revenue                        FROM movies_table WHERE revenue >= 1000000000')
con.commit()
cur.fetchall()


# - Отсортировка фильмов-миллиардеров по годам выпуска и их количество за год

# In[13]:


top_boxoffice_count = '''
SELECT 
    COUNT(title) AS movies_count, 
    strftime("%Y", release_date) AS year,
    SUM(COUNT(title)) OVER(ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS total_amount
    FROM movies_table
    WHERE revenue >= 1000000000 GROUP BY year'''


cur.execute(top_boxoffice_count)
rows = cur.fetchall()
pd.DataFrame(rows, columns = ('movies_count', 'year', 'total_amount'))


# - Общее количество выпущенных фильмов в те года, когда выходил хотя бы один фильм-миллиардер

# In[14]:


year_movie_count = '''
    SELECT 
        strftime("%Y", release_date) AS year,
        COUNT(title) AS movies_count 
    FROM movies_table
    WHERE strftime("%Y", release_date) IN (SELECT strftime("%Y", release_date) FROM movies_table WHERE revenue >= 1000000000)
    GROUP BY year
    '''

cur.execute(year_movie_count)
rows = cur.fetchall()
pd.DataFrame(rows, columns = ('year', 'movies_count'))


# Вывод: 
# С 1997 года по 2009 наблюдается двукратное увеличение количества выходящих фильмов в год, при этом количество «фильмов-миллиардеров» не увеличивается.
# С 2009 года по 2012 каждый год увеличивалось количество «фильмов-миллиардеров» на единицу, общее количество фильмов при этом выросло  незначительно. В 2012 вышло 4 «фильма-миллиардера», однако по сравнению с 2011 годом в 2012 вышло на 14 меньше. 
# В 2013 и 2014 на фоне роста общего числа вышедших фильмов наблюдается снижение количества фильмов, собравших миллиард и более. 
# С 2015 по 2019 года наблюдаются резкое количество увеличение «фильмов-миллиардеров», достигнув своего максимума в 9 фильмов за всю историю. Общее количество фильмов также постепенно росло.
# После пандемийного периода в 2021 сохраняется тенденция увеличения общего количества фильмов, однако «фильмов-миллиардеров» среди них всего 1. 
# В 2022 вышло в общем вышло рекордное количество фильмов – 825 фильмов, «фильмов-миллиардеров» среди них 3, как и в 2011 году, когда общее количество фильмов было в 3 раза меньше, всего 261.
# 
# Таким образом, количество выпускаемых фильмов не является фактором увеличения количества выходящих «фильмов-миллионеров». Наоборот статистика за 2013, 2014, 2021, 2022 годы демонстрирует обратную зависимость.

# Вывод графиков для визуализации данных 

# In[15]:


get_ipython().run_line_magic('matplotlib', 'inline')

# создаём копию таблицы
df_top_movies = df.copy()

# Код для первого графика
df_top_movies['release_date'] = pd.to_datetime(df['release_date']) # приводим release_date к формату даты
df_top_movies['year'] = df_top_movies['release_date'].dt.year # оставляем только год, создаём колонку year

revenue_max = df_top_movies[df_top_movies['revenue'] > 1000000000] # выбираем фильмы со сборами выше 1000000000
movies_count = revenue_max.groupby('year').size() # группируем по столбцу year


# Первый график
plt.subplot(2, 1, 1) # выведет график сверху
movies_count.plot(kind='bar', color='blue', figsize=(7.5, 6))
plt.xlabel('Year')
plt.ylabel('Number of Movies')
plt.title('Number of Movies with Revenue > 1 Billion by Year')
plt.grid(False) # убирается сетка с графика

# Код для второго графика
filtered_year = df_top_movies[df_top_movies['year'].isin(revenue_max['year'].unique())]
movies_count_filtered = filtered_year.groupby('year').size()

# Второй график
plt.subplot(2, 1, 2)# выведет график снизу
movies_count_filtered.plot(kind='bar', color='red')
plt.xlabel('Year')
plt.ylabel('Number of Movies')
plt.title('Number of Movies Released by Year (Years with Revenue > 1 Billion)')
plt.grid(False) 


# Изменяем расстояние между графиками
plt.subplots_adjust(hspace=0.5)

# Показать все графики
plt.show()


# Гипотеза 2: Самую большую прибыль в количественном и процентном соотношении приносят фильмы жанра «экшен»

# Создаём таблицу с разбивкой по жанрам

# In[16]:


df_genre = df.copy() #создаём копию таблицы


# In[17]:


#удаляем столбицы где хотя бы одно из значений бюджета или сборов = 0
df_genre = df_genre[~(df_genre == 0).any(axis=1)]


# In[18]:


# удаляем ненужные столбцы для анализа
df_genre.drop(['release_date','production_companies', 'runtime'], axis=1, inplace=True) 


# In[19]:


df_genre.head(3)


# Разбиваем жанры по отдельным строкам для точного расчёта кассовых сборов по жанрам.

# In[20]:


df_genre['genres'] = df_genre['genres'].str.split(', ') # разделяем значения по запятым
df_genre = df_genre.explode('genres')# разделяем компании на разные строки
df_genre = df_genre.rename(columns={'genres': 'genre'})# переименовываем столбец


# In[21]:


df_genre['genre'] = df_genre['genre'].str.extract(r"'([^']+)") # убираем ненужные символы


# In[22]:


df_genre.head(3)


# Добавляем новую таблицу в bd

# In[23]:


df_genre.to_sql(con=con, name='movies_genre', index=False, if_exists='replace')


# - Выводим общую информацию по таблице: количество фильмов в каждом жанре; средний бюджет и сборы фильмов каждого жанра; общий бюджет и сборы фильмов по жанрам

# In[24]:


genre_info = '''SELECT genre,
                                COUNT(*) AS movies_count,
                                AVG(budget) AS avg_budget,
                                AVG(revenue) AS avg_revenue,
                                SUM(budget) AS total_budget,
                                SUM(revenue) AS total_revenue
                        FROM movies_genre 
                        GROUP BY genre 
                        ORDER BY genre'''

cur.execute(genre_info)
rows = cur.fetchall()
pd.DataFrame(rows, columns = ('genre', 'movies_count', 'avg_budget', 'avg_revenue', 'total_budget', 'total_revenue'))


# Вывод графика через pandas

# In[25]:


fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(8, 20))

df_genre_movies = pd.DataFrame(rows, columns=['genre', 'movies_count', 'avg_budget', 'avg_revenue', 'total_budget', 
                                              'total_revenue'])

# График movies_count
axes[0].barh(df_genre_movies['genre'], df_genre_movies['movies_count'], color='blue')
axes[0].set_xlabel('Number of Movies')
axes[0].set_ylabel('Genre')
axes[0].set_title('Number of Movies by Genre')
plt.grid(False) # убирается сетка с графика

# График avg_budget
axes[1].barh(df_genre_movies['genre'], df_genre_movies['avg_budget'], color='green')
axes[1].set_xlabel('Average Budget')
axes[1].set_ylabel('Genre')
axes[1].set_title('Average Budget by Genre')
plt.grid(False) # убирается сетка с графика

# График avg_revenue
axes[2].barh(df_genre_movies['genre'], df_genre_movies['avg_revenue'], color='red')
axes[2].set_xlabel('Average Revenue')
axes[2].set_ylabel('Genre')
axes[2].set_title('Average Revenue by Genre')
plt.grid(False) # убирается сетка с графика

# График total_budget
axes[3].barh(df_genre_movies['genre'], df_genre_movies['total_budget'], color='purple')
axes[3].set_xlabel('Total Budget')
axes[3].set_ylabel('Genre')
axes[3].set_title('Total Budget by Genre')
plt.grid(False) # убирается сетка с графика

# График total_revenue
axes[4].barh(df_genre_movies['genre'], df_genre_movies['total_revenue'], color='orange')
axes[4].set_xlabel('Total Revenue')
axes[4].set_ylabel('Genre')
axes[4].set_title('Total Revenue by Genre')
plt.grid(False) # убирается сетка с графика

# Изменяем расстояние между графиками
plt.subplots_adjust(hspace=0.5)

plt.show()


# - Сортировка фильмов по жанрам; абсолютная и относительня средняя прибыль по жанрам

# In[26]:


top_boxoffice_genre = '''SELECT genre,
                                COUNT(*) AS movies_count,
                                AVG(revenue - budget) AS avg_profit,
                                AVG(revenue / budget * 100) AS ag_percent_profit
                        FROM movies_genre 
                        GROUP BY genre 
                        ORDER BY ag_percent_profit DESC'''
cur.execute(top_boxoffice_genre)

rows = cur.fetchall()
pd.DataFrame(rows, columns = ('genre', 'movies_count', 'avg_profit', 'avg_percent_profit'))


# Выыод графика 

# In[27]:


fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 20))

df_genre_profit = pd.DataFrame(rows, columns=['genre', 'movies_count', 'avg_profit', 'avg_percent_profit'])

# График avg_profit
axes[0].barh(df_genre_profit['genre'], df_genre_profit['avg_profit'], color='blue')
axes[0].set_xlabel('Average Profit')
axes[0].set_ylabel('Genre')
axes[0].set_title('Average Profit by Genre')
plt.grid(False) # убирается сетка с графика

# График avg_percent_profit
axes[1].barh(df_genre_profit['genre'], df_genre_profit['avg_percent_profit'], color='green')
axes[1].set_xlabel('Average Profit Percent')
axes[1].set_ylabel('Genre')
axes[1].set_title('Average Profit Percent by Genre')

plt.grid(False) # убирается сетка с графика

# Изменяем расстояние между графиками
plt.subplots_adjust(hspace=0.1)

plt.show()


# Вывод: в результате запроса видно, что на первом месте по средней прибыли среди всех жанров занимают фильмы в жанре 'приключения'; по средней прибыли фильмы в жанре "экшен" занмают 6-ое место, в среднеем получая прибыль в 120 617 200 $.
# В процентом соотношению большую прибыль зарабатывают фильмы в жанре 'комедия', в среднем фильмы этого жанра окупаются в 15 раз; фильмы жанра 'экшен' в среднем приносят прибыль в 407 \%, что соответсвует 16-му месту среди рассматриваемых 19-ти жанров. 

# - Сортировка фильмов по жанрам и вывод общей прибыли

# In[28]:


top_boxoffice_genre = '''SELECT 
                            ROW_NUMBER() OVER(ORDER BY SUM(revenue - budget) DESC) AS rating,
                            genre, 
                            COUNT(*) AS movies_count,
                            SUM(revenue - budget) AS total_profit
                        FROM movies_genre 
                        GROUP BY genre 
                        ORDER BY total_profit DESC'''
cur.execute(top_boxoffice_genre)

rows = cur.fetchall()
pd.DataFrame(rows, columns = ('rating', 'genre', 'movies_count','total_profit'))


# Строим график для визуализации данных

# In[29]:


df_genre_sum = pd.DataFrame(rows, columns=['rating', 'genre', 'movies_count', 'total_profit'])

# Plotting the graph
fig, axes = plt.subplots(figsize=(8, 6))
axes.barh(df_genre_sum['genre'], df_genre_sum['total_profit'], color='blue')
axes.set_xlabel('Total Profit')
axes.set_ylabel('Genre')
axes.set_title('Top Box Office Genre')

# Displaying the graph
plt.show()


# Вывод: На первом месте по общим сборам фильмов различных жанров занимают фильмы жанра "приключения", филмы жанра 'экшен' располагаются на втором месте, уступая по общим сборам 'приключениям' 12.475.500.000$.

# Гипотеза 3: Ремейки фильмов, имеющие одинаковое название с оригиналом, приносят больше прибыли в обсолютных и относительных показателях, чем сам оригинал. 

# In[30]:


df_remake = df.copy() #создаём копию таблицы


# In[31]:


df_remake = df_remake[~(df_remake == 0).any(axis=1)]#удаляем столбицы где хотя бы одно из значений бюджета или сборов = 0


# In[32]:


# Оставляем только строки с дублирующимися названиями, но разными датами выхода
df_remake = df_remake[df_remake['title'].isin(df_remake['title'][df_remake['title'].duplicated()])].sort_values('title')


# Добавляем новый столбец в таблицу для проверки оригинальности фильма (под оригинальным подразумевается фильм, который вышел первым, остальные - римейки)

# In[33]:


# приводим release_date к формату времени
df_remake['release_date'] = pd.to_datetime(df_remake['release_date']).dt.date

# Добавляем новый столбец "orig_rem"
df_remake['orig_check'] = None

# Группируем по названию фильма и находим минимальную и максимальную дату выхода
grouped = df_remake.groupby('title')['release_date'].agg(['min'])

# Обновляем столбец "orig_rem" согласно условиям
for index, row in grouped.iterrows():
    df_remake.loc[(df['title'] == index) & (df_remake['release_date'] == row['min']), 'orig_check'] = 'orig'
    df_remake.loc[(df['title'] == index) & (df_remake['release_date'] != row['min']), 'orig_check'] = 'rem'


# In[34]:


df_remake.head()


# In[35]:


# Добавляем новую таблицу в bd
df_remake.to_sql(con=con, name='remake', index=False, if_exists='replace')


# Выводим информацию о фильмах с одинаковыми названиями и считаем прибыль

# In[36]:


remakes = '''
SELECT
    id,
    title, 
    release_date, 
    genres, 
    vote_average, 
    vote_count, 
    revenue - budget AS profit, 
    revenue / budget * 100 AS percent_profit, 
    runtime
FROM remake
ORDER BY title, release_date 
'''

cur.execute(remakes)
rows = cur.fetchall()

pd.DataFrame(rows, columns=('id', 'title', 'release_date', 'genres', 'vote_average', 'vote_count', 'profit', 
                            'percent_profit', 'runtime'))


# - Выводим среднюю прибыль и процент прибыли среди всех оригинальных фильмов и ремейков

# In[37]:


remakes = '''
SELECT 
    orig_check,
    COUNT(orig_check) AS count,
    ROUND(AVG(vote_average), 2) AS avg_vote, 
    ROUND(AVG(vote_count)) AS avg_vote_count, 
    AVG(revenue - budget) AS avg_profit, 
    ROUND(AVG(revenue / budget * 100)) AS avg_percent_profit, 
    ROUND(AVG(runtime)) AS avg_runtime
FROM remake
GROUP BY orig_check
'''

cur.execute(remakes)
rows = cur.fetchall()

pd.DataFrame(rows, columns=('originality_check', 'count','avg_vote', 'avg_vote_count', 'avg_profit', 
                            'avg_percent_profit', 'avg_runtime'))


# Строим график для визуализации данных

# In[38]:


df_remake_avg = pd.DataFrame(rows, columns=['originality_check', 'count', 'avg_vote', 'avg_vote_count', 
                                        'avg_profit', 'avg_percent_profit', 'avg_runtime'])

fig, axes = plt.subplots(3, 2, figsize=(12, 8))

# Изменяем расстояние между графиками
plt.subplots_adjust(hspace=0.5)
fig.suptitle('Originals & Remakes')

# Диаграмма для count
axes[0, 0].bar(df_remake_avg['originality_check'], df_remake_avg['count'], color = 'purple')
axes[0, 0].set_xlabel('Originality')
axes[0, 0].set_ylabel('Amount')
axes[0, 0].set_title('Total Amount of Movies')


# Диаграмма для avg_vote
axes[0, 1].bar(df_remake_avg['originality_check'], df_remake_avg['avg_vote'], color = 'black')
axes[0, 1].set_xlabel('Originality')
axes[0, 1].set_ylabel('Average Rating')
axes[0, 1].set_title('Average Vote')

# Диаграмма для avg_vote_count
axes[1, 0].bar(df_remake_avg['originality_check'], df_remake_avg['avg_vote_count'], color = 'navy')
axes[1, 0].set_xlabel('Originality')
axes[1, 0].set_ylabel('Amount')
axes[1, 0].set_title('Average Vote Amount')

# Диаграмма для avg_profit
axes[1, 1].bar(df_remake_avg['originality_check'], df_remake_avg['avg_profit'], color = 'brown')
axes[1, 1].set_xlabel('Originality')
axes[1, 1].set_ylabel('Profit')
axes[1, 1].set_title('Average Profit')


# Диаграмма для avg_percent_profit
axes[2, 0].bar(df_remake_avg['originality_check'], df_remake_avg['avg_percent_profit'], color = 'blue')
axes[2, 0].set_xlabel('Originality')
axes[2, 0].set_ylabel('Profit Percent')
axes[2, 0].set_title('Average Profit Percent')


# Диаграмма для avg_runtime
axes[2, 1].bar(df_remake_avg['originality_check'], df_remake_avg['avg_runtime'], color = 'grey')
axes[2, 1].set_xlabel('Originality')
axes[2, 1].set_ylabel('Runtime in Min.')
axes[2, 1].set_title('Average Runtime')


# Изменяем расстояние между графиками
plt.subplots_adjust(hspace=0.5)

# Displaying the pie charts
plt.show()


# Вывод: В среднем оригинальные фильмы получают выше оценки от зрителей на 0.64 балла, однако среднее количество оценок у оригинальных фильмов меньше на 1150. 
# Средняя сумма сборов «ремейков» более чем в 2 раза больше, чем у оригиналов, однако в процентом соотношении оригинальные фильмы приносили почти в 5 раз больше прибыли, чем сиквелы. 
# И, наконец, средняя продолжительность ремейков увеличилась на 7 минут по сравнению с оригиналами. 
# Таким образом, ремейки фильмов, имеющие одинаковое название с оригиналами, приносят более чем в 2 раза большую прибыль по сравнению с оригиналами. Однако, в процентом соотношении прибыль ремейков значительно уступает оригиналам, поэтому для большей объективности в дальнейшем стоит рассмотреть прибыль оригиналов и ремейков с учётом инфляции.
