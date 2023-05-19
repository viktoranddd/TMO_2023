import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.datasets import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt


@st.cache
def preprocess_data(data_in):
    '''
    Масштабирование признаков, функция возвращает X и y для кросс-валидации
    '''
    data_out = data_in.copy()
    # Числовые колонки для масштабирования
    scale_cols = ['alcohol', 'malic_acid', 'ash', 'alcalinity_of_ash', 'magnesium',
       'total_phenols', 'flavanoids', 'nonflavanoid_phenols',
       'proanthocyanins', 'color_intensity', 'hue',
       'od280/od315_of_diluted_wines', 'proline']
    new_cols = []
    sc1 = MinMaxScaler()
    sc1_data = sc1.fit_transform(data_out[scale_cols])
    for i in range(len(scale_cols)):
        col = scale_cols[i]
        new_col_name = col + '_scaled'
        new_cols.append(new_col_name)
        data_out[new_col_name] = sc1_data[:,i]
    return data_out[new_cols], data_out['target']

st.sidebar.header('Метод ближайших соседей')

def make_dataframe(ds_function):
    ds = ds_function()
    df = pd.DataFrame(data= np.c_[ds['data'], ds['target']],
                     columns= list(ds['feature_names']) + ['target'])
    return df

wine = load_wine()

data = make_dataframe(load_wine)

cv_slider = st.sidebar.slider('Количество фолдов:', min_value=3, max_value=10, value=3, step=1)
step_slider = st.sidebar.slider('Шаг для соседей:', min_value=1, max_value=50, value=10, step=1)

if st.checkbox('Показать корреляционную матрицу'):
    fig1, ax = plt.subplots(figsize=(10,5))
    sns.heatmap(data.corr(), annot=True, fmt='.2f')
    st.pyplot(fig1)

#Количество записей
data_len = data.shape[0]
#Вычислим количество возможных ближайших соседей
rows_in_one_fold = int(data_len / cv_slider)
allowed_knn = int(rows_in_one_fold * (cv_slider-1))
st.write('Количество строк в наборе данных - {}'.format(data_len))
st.write('Максимальное допустимое количество ближайших соседей с учетом выбранного количества фолдов - {}'.format(allowed_knn))

# Подбор гиперпараметра
n_range_list = list(range(1,allowed_knn,step_slider))
n_range = np.array(n_range_list)
st.write('Возможные значения соседей - {}'.format(n_range))
tuned_parameters = [{'n_neighbors': n_range}]

data_X, data_y = preprocess_data(data)
clf_gs = GridSearchCV(KNeighborsClassifier(), tuned_parameters, cv=cv_slider, scoring='accuracy')
clf_gs.fit(data_X, data_y)

st.subheader('Оценка качества модели')

st.write('Лучшее значение параметров - {}'.format(clf_gs.best_params_))

# Изменение качества на тестовой выборке в зависимости от К-соседей
fig1 = plt.figure(figsize=(7,5))
ax = plt.plot(n_range, clf_gs.cv_results_['mean_test_score'])
st.pyplot(fig1)
