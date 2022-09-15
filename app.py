from bs4 import BeautifulSoup
from time import sleep
import re
import streamlit as st
from collections import defaultdict
import pandas as pd
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from goose3 import Goose
from utils import remove_punctuation, tokenize, remove_stopwords, \
    count_sort_n_tokens, normalizar_candidato_felipe_avila, normalizar_candidato_lula

st.set_option('deprecation.showPyplotGlobalUse', False)
url = 'https://www.poder360.com.br/eleicoes/leia-a-transcricao-do-debate-presidencial-da-band/'

@st.cache
def load_data():
    g = Goose()
    article = g.extract(url)
    raw_text = article.cleaned_text
    raw_text = normalizar_candidato_lula(normalizar_candidato_felipe_avila(raw_text))
    regex = r'\n\n(Felipe D’Avila|Simone Tebet|Lula|Ciro Gomes|Soraya Thronicke|Soraya Thronicke|' \
            r'Jair Bolsonaro)\n\n(.*)\n\n'
    final_content = re.findall(regex, raw_text, re.MULTILINE)
    fala_candidatos=defaultdict(list)
    for item in final_content:
        if item[0] == 'Lula':
            fala_candidatos['Lula'].append(item[1])
        if item[0] == 'Soraya Thronicke':
            fala_candidatos['Soraya Thronicke'].append(item[1])
        if item[0] == 'Simone Tebet':
            fala_candidatos['Simone Tebet'].append(item[1])
        if item[0] == 'Jair Bolsonaro':
            fala_candidatos['Jair Bolsonaro'].append(item[1])
        if item[0] == 'Ciro Gomes':
            fala_candidatos['Ciro Gomes'].append(item[1])
        if item[0] == 'Felipe D’Avila':
            fala_candidatos['Felipe D’Avila'].append(item[1])
    return fala_candidatos


pipeline_full = [str.lower, remove_punctuation, tokenize, remove_stopwords, count_sort_n_tokens]
pipeline_word_cloud = [str.lower, remove_punctuation, tokenize, remove_stopwords]

text = load_data()


def prepare(text, pipeline=pipeline_full):
    tokens = ' '.join(text)
    for transform in pipeline:
        tokens = transform(tokens)
    return tokens


candidatos = ['Lula', 'Jair Bolsonaro', 'Ciro Gomes', 'Simone Tebet',
              'Soraya Thronicke', 'Felipe D’Avila']

tokens_candidatos=defaultdict(list)

for candidato in candidatos:
   tokens_candidatos[candidato] = pd.DataFrame(prepare(text[candidato]),
                                               columns=['Palavra', 'Quantidade'])

values = [tokens_candidatos[candidatos[0]]['Quantidade'].sum(),
                 tokens_candidatos[candidatos[1]]['Quantidade'].sum(),
                 tokens_candidatos[candidatos[2]]['Quantidade'].sum(),
                 tokens_candidatos[candidatos[3]]['Quantidade'].sum(),
                 tokens_candidatos[candidatos[4]]['Quantidade'].sum(),
                 tokens_candidatos[candidatos[5]]['Quantidade'].sum()]


def plot_bar_chart(candidatos, values):
    fig = go.Figure([go.Bar(x=candidatos, y=values,
                            text=values,
                            textposition='auto')])
    fig.update_layout(
        autosize=False,
        width=500,
        height=500)
    return fig


def plot_bar_chart_candidate(nome_candidato, candidato):
    fig = go.Figure([go.Bar(y=candidato['Palavra'].values, x=candidato['Quantidade'].values,
                            text=candidato['Quantidade'].values,
                            textposition='auto', orientation='h')])
    fig.update_layout(
        autosize=False, yaxis={'categoryorder': 'total ascending'},
        width=400,
        height=700,
        title_text='Palavras mais utilizadas pelo(a) candidato(a) {}'.format(nome_candidato))
    fig.update_xaxes(tickangle=-45)
    return fig

st.title('Análise Estatística sobre o Primeiro Debate Presidencial das Eleições 2022')

st.sidebar.header("Sobre o Debate")
st.sidebar.info("Ocorreu no dia 28/08 e foi organizado pelo pool de veículos de imprensa: TV Band, "
                "TV Culura, Jornal Folha de S. Paulo e Portal UOL. "
                "\n\n\n"
                "A transcrição do debate foi obtida em: "
                "https://www.poder360.com.br/eleicoes/leia-a-transcricao-do-debate-presidencial-da-band/")

st.subheader('Número de palavras utilizadas por cada candidato')
st.plotly_chart(
    plot_bar_chart(candidatos, values),
    use_container_width=True)

st.subheader('Análise por candidato')
candidato_selecionado = st.selectbox('Selecione o candidato', candidatos)



st.plotly_chart(
    plot_bar_chart_candidate(candidato_selecionado, tokens_candidatos[candidato_selecionado]),
    use_container_width=True)


# Geração das nuvens de palavras para cada candidato
tokens_candidatos_wordcloud = defaultdict(list)

for candidato in candidatos:
   tokens_candidatos_wordcloud[candidato]=' '.join(prepare(text[candidato],
                                                           pipeline=pipeline_word_cloud))

wordcloud = WordCloud(background_color="#f5f5f5", colormap='Dark2').generate(
    tokens_candidatos_wordcloud[candidato_selecionado])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()