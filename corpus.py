import dhlab_v2 as d2 
import pandas as pd
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import base64

@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(word, period):
    return d2.ngram_book(word, years = period)

@st.cache(suppress_st_warning = True, show_spinner = False)
def get_corpus():
    corpus = pd.read_csv('helenes_korpusdata.csv', index_col = 0)
    fem = corpus[corpus.gender == 'fem']
    masc = corpus[corpus.gender == 'masc']
    return fem, masc


@st.cache(suppress_st_warning = True, allow_output_mutation = True, show_spinner = False)
def make_combo():
    fem_agg = nb.frame(nb.aggregate_urns(list(fem.index)), 'fem')
    masc_agg = nb.frame(nb.aggregate_urns(list(masc.index)), 'masc')
    combo = pd.concat([masc_agg, fem_agg], axis = 1)
    return combo, combo.sum()

def show_data(data):
    fontsize = 12

    fig, ax = plt.subplots() #nrows=2, ncols=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_color("grey")
    ax.spines["left"].set_color("grey")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_linewidth(0.3)
    ax.legend(loc='upper left', frameon=False)
    ax.spines["left"].set_visible(False)

    plt.rcParams.update({'font.size': 12,
                        'font.family': 'monospace',
                        'font.monospace':'Courier'})

    plt.legend(loc = 2, prop = {
        'size': fontsize})
    #plt.xlabel('Ordliste', fontsize= fontsize*0.8)
    #plt.ylabel('Frekvensvekt', fontsize= fontsize*0.8)
    data.plot(ax=ax, figsize = (8,4), kind='bar', rot=20)

    st.pyplot(fig)

    st.write('som tabell')
    st.write(data.style.background_gradient())


#### Display NB logo ##########################

pd.set_option('display.max_colwidth', -1)

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://www.nb.no/dh-lab), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')




fem, masc = get_corpus()



st.markdown('## Helenes korpus')
st.text("Sjekk frekvens av ord i korpuset, og konkordonans i korpuset")

ordliste_input = st.text_input("Angi ordene som en kommaseparert liste - for å ta med komma, legg inn ett mot slutten eller to etter hverandre", "rød, grønn")

st.text("Frekvens av ordene fordelt på korpusene ")

combo, tot = make_combo()

nb.normalize_corpus_dataframe(combo)

normalize = st.radio('normaliser i prosent', ['ja', 'nei'])
if normalize == 'ja':
    combo = combo*100
else:
    combo.fem = (combo.fem * tot.fem)/100
    combo.masc = (combo.masc * tot.masc)/100
    
ordliste = [x.strip() for x in ordliste_input.split(',')]
if '' in ordliste:
    ordliste = [','] + [y for y in ordliste if y != '']
data = combo.loc[[x for x in ordliste if x in combo.index]].sort_values(by='fem', ascending=False)

show_data(data.drop_duplicates())

### undersøk en enkelt forfatter #### eller subcorpus?
both = pd.concat([fem, masc])
vals = st.multiselect('vel en noen bøker', list(both.author + ' - ' + both.title))

st.write(vals)
with open('korpus.csv', 'w') as f:
    f.write(", ".join([x for x in vals]))

def save_frame(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)
    return 

save_frame(both)
    
    
    #st.area_chart(data)

#st.bar_chart(data)


##### Set up sidebar ############3
st.sidebar.header('Parametre for konkordanser')

corpus = st.sidebar.selectbox('corpus', ['fem', 'masc', 'both'])


if corpus == 'fem':
    urns = list(fem.index)
elif corpus == 'masc':
    urns = list(masc.index)
else:
    urns = list(fem.index)
    urns += list(masc.index)
    
c_before = st.sidebar.number_input('antall ord foran', 0, 30, 10, key = 'conc_before')
c_after = st.sidebar.number_input('antall ord bak', 0, 30, 10, key = 'conc_after')
c_resultat_antall = st.sidebar.number_input('antall ord i resultatet', 5, 300, 50, key ='conc_antall')


conc_word = st.text_input('Lag en konkordans for', "hallo")

if conc_word != "":
    conc = nb.get_urnkonk(
        conc_word, 
        {

            'urns' : urns,
            'before':c_before,
            'after':c_after
        }, 
        html = False)

    st.write(conc)

