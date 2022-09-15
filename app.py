import re
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from goose3 import Goose
from wordcloud import WordCloud

from utils import remove_punctuation, tokenize, remove_stopwords, \
    count_sort_n_tokens, normalize_candidate_felipe_avila, normalize_candidate_lula

st.set_option('deprecation.showPyplotGlobalUse', False)
url = 'https://www.poder360.com.br/eleicoes/leia-a-transcricao-do-debate-presidencial-da-band/'


@st.cache
def load_data():
    g = Goose()
    article = g.extract(url)
    raw_text = article.cleaned_text
    raw_text = normalize_candidate_lula(normalize_candidate_felipe_avila(raw_text))
    regex = r'(Felipe D’Avila|Simone Tebet|Lula|Ciro Gomes|Soraya Thronicke|Jair Bolsonaro)\n\n(.*)\n\n'
    final_content = re.findall(regex, raw_text, re.MULTILINE)
    candidates_speeches = defaultdict(list)
    for item in final_content:
        if item[0] == 'Lula':
            candidates_speeches['Lula'].append(item[1])
        if item[0] == 'Soraya Thronicke':
            candidates_speeches['Soraya Thronicke'].append(item[1])
        if item[0] == 'Simone Tebet':
            candidates_speeches['Simone Tebet'].append(item[1])
        if item[0] == 'Jair Bolsonaro':
            candidates_speeches['Jair Bolsonaro'].append(item[1])
        if item[0] == 'Ciro Gomes':
            candidates_speeches['Ciro Gomes'].append(item[1])
        if item[0] == 'Felipe D’Avila':
            candidates_speeches['Felipe D’Avila'].append(item[1])
    return candidates_speeches


def join_speechs(candidates_speeches):
    all_candidates = []
    for item in candidates_speeches.values():
        all_candidates.extend(item)
    dict_all_candidates = {'Todos candidatos': all_candidates}
    return dict_all_candidates


pipeline_full = [str.lower, remove_punctuation, tokenize, remove_stopwords, count_sort_n_tokens]
pipeline_word_cloud = [str.lower, remove_punctuation, tokenize, remove_stopwords]

speeches = load_data()


def prepare(text_, pipeline=None):
    if pipeline is None:
        pipeline = pipeline_full
    tokens = ' '.join(text_)
    for transform in pipeline:
        tokens = transform(tokens)
    return tokens


candidates = ['Lula', 'Jair Bolsonaro', 'Ciro Gomes', 'Simone Tebet',
              'Soraya Thronicke', 'Felipe D’Avila']

tokens_per_candidate = defaultdict(list)

for candidato in candidates:
    tokens_per_candidate[candidato] = pd.DataFrame(prepare(speeches[candidato]),
                                                   columns=['Palavra', 'Quantidade'])

tokens_all_candidates = join_speechs(speeches)


geral = pd.DataFrame(prepare(tokens_all_candidates['Todos candidatos']),
                     columns=['Palavra', 'Quantidade'])

values = [tokens_per_candidate[candidates[0]]['Quantidade'].sum(),
          tokens_per_candidate[candidates[1]]['Quantidade'].sum(),
          tokens_per_candidate[candidates[2]]['Quantidade'].sum(),
          tokens_per_candidate[candidates[3]]['Quantidade'].sum(),
          tokens_per_candidate[candidates[4]]['Quantidade'].sum(),
          tokens_per_candidate[candidates[5]]['Quantidade'].sum()]


def plot_bar_chart(candidates, values):
    fig = go.Figure([go.Bar(x=candidates, y=values,
                            text=values,
                            textposition='auto')])
    fig.update_layout(
        autosize=False,
        width=500,
        height=500)
    return fig


def plot_bar_chart_candidate(candidate):
    fig = go.Figure([go.Bar(y=candidate['Palavra'].values, x=candidate['Quantidade'].values,
                            text=candidate['Quantidade'].values,
                            textposition='outside', orientation='h')])
    fig.update_layout(
        autosize=False, yaxis={'categoryorder': 'total ascending'},
        width=400,
        height=700)
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
    plot_bar_chart(candidates, values),
    use_container_width=True)

st.subheader('30 palavras mais citadas por todos os candidatos')
st.plotly_chart(
    plot_bar_chart_candidate(geral),
    use_container_width=True)

st.subheader('Nuvem de palavras mais citadas por todos os candidatos')

content_wordcloud_general = ' '.join(prepare(tokens_all_candidates['Todos candidatos'], pipeline=pipeline_word_cloud))

wordcloud = WordCloud(background_color="#f5f5f5", colormap='Dark2').generate(content_wordcloud_general)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()

st.subheader('Análise por candidato')
candidato_selecionado = st.selectbox('Selecione o candidato', candidates)


st.plotly_chart(
    plot_bar_chart_candidate(tokens_per_candidate[candidato_selecionado]),
    use_container_width=True)


# Geração das nuvens de palavras para cada candidato
tokens_candidatos_wordcloud = defaultdict(list)

for candidato in candidates:
    tokens_candidatos_wordcloud[candidato] = ' '.join(prepare(speeches[candidato], pipeline=pipeline_word_cloud))

wordcloud = WordCloud(background_color="#f5f5f5", colormap='Dark2').generate(
    tokens_candidatos_wordcloud[candidato_selecionado])
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()
