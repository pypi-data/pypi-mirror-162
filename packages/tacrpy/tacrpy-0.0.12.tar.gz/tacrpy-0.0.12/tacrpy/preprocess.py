import pandas as pd
import re
import string


def create_corpus(df, id_col, text_cols=[]):
    """
    Ze vstupních dat vytvoří corpus (sloučené texty, pro textovou analýzu).

    Např. v rámci projektů corpus tvoří Název projektu, Cíle projektu případně i Klíčová slova.

    Parameters
    ----------
    df (DataFrame): vstupní DataFrame se surovými daty, ze kterých má vziknout corpus
    id_col (str): název sloupce, který slouží jako id (např. Kód projektu, ID dotazu)
    text_cols (list): název textových sloupců, ze kterých má vziknout corpus

    Returns
    -------
    df_corpus (DataFrame):

    """

    cols = [id_col] + text_cols
    df = df[cols]
    df = df.fillna('')  # agg a join nefunguje pokud jsou NA hodnoty
    df['corpus'] = df[df.columns[1:]].agg('; '.join, axis=1)
    df_corpus = df[[df.columns[0], df.columns[-1]]]
    df_corpus.columns = ['id', 'corpus']

    return df_corpus


def text_lemma(text, model):
    """
    Lemmatizuje text na základní tvar. Např. lepší -> dobrý, projektový -> projekt.

    Je potřeba mít stažený a načtený model - nejlépe czech-pdt-ud-2.5-191206.udpipe, dostupný na:
    https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3131

    Parameters
    ----------
    text (str): corpus (text) jednoho projektu, dotazu atd. => 1 buňka
    model (model): je potřeba mít nahraný předtrénovaný model (např. czech-pdt-ud-2.5-191206.udpipe)

    Returns
    -------
    lemma (str): lemmatizovaný text => 1 buňka

    """
    sentence = []

    for s in model.process(text):  # rozdělí text na věty
        for w in s.words:  # rozdělí text na slova
            if '<root>' not in w.lemma:  # <roo> je v podstatě začátek věty
                sentence.append(w.lemma)

    # složí zpátky celou větu z lemmatizovaných slov, resp. celý text.
    lemma = ' '.join(sentence)

    return lemma


def df_lemma(df_corpus, entity_name, model, df_lemma=None):
    """
    Vytvoří lemmatizovaný DataFrame a aktualizuje (nebo vytvoří) soubor (pickle) s lemmatizovanými texty.

    Nejdříve zkontroluje, jestli existují texty, které nebyly lemmatizované.
    Pro texty, které nebyly lemmatizované provede lemmatizaci.
    Aktualizuje původní soubor s lemmatizovanými texty o nově lemmatizované texty.

    !!!POZOR!!! Pro velké množství texu může zabrat nějakou dobu (cca 0.5 sec na text => 10 000 textů za 48 minut)

    Parameters
    ----------
    df_corpus (DataFrame): dataframe se všemi texty (corpus)
    entity_name (str): entita, které se lemmatizace týká (např. projekty), slouží pro pojmenování souboru
    model (model): je potřeba mít nahraný předtrénovaný model (např. czech-pdt-ud-2.5-191206.udpipe)
    df_lemma (DataFrame): nepovinný parametr, dataframe s lemmatizovanými texty (původní soubor pickle)

    Returns
    -------
    df_lemma (DataFrame): aktualizovaný dataframe lemmatizovaných textů

    """

    # pokud df_lemma neexistuje, pak lemmatizuje všechny texty a vytvoří pickle soubor
    if df_lemma is None:
        df_corpus['lemma'] = df_corpus['corpus'].apply(lambda x: text_lemma(x, model))
        df_lemma = df_corpus[[df_corpus.columns[0], 'lemma']]
        df_lemma.to_pickle(entity_name + '_lemma.pkl')

    # pokud existuje, tak lemmatizuje pouze nové texty a 'aktualizuje' pickle soubor
    else:
        # zjištění, které texty jsou nové
        id_set = set(df_corpus[df_corpus.columns[0]]) - set(df_lemma[df_lemma.columns[0]])

        # vyfiltruje pouze nové texty a provede lemmatizaci funkce cz_lemma
        df = df_corpus[df_corpus[df_corpus.columns[0]].isin(id_set)]
        df['lemma'] = df['corpus'].apply(lambda x: text_lemma(x, model))

        # rozšíří df původních lemmatizovaných textů a vytvoří nový soubor se stejným jménem
        df = df[[df.columns[0], 'lemma']]
        df_lemma = pd.concat([df_lemma, df], ignore_index=True)
        df_lemma.to_pickle(entity_name + '_lemma.pkl')

    return df_lemma

def text_cleaning(text):
    """ Preprocessing textu, odstranění netextových znaků."""

    # TODO: Zamyslet se, jestli se nedá čistit komplexněji v rámci jednoho regex

    text = text.lower()  # převední na malá písmena
    text = re.sub(';', ' ; ', text)
    text = re.sub(',', ' , ', text)
    text = re.sub('-', ' - ', text)
    text = re.sub('\d', '', text)  # odstranění čísel
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)

    return text

def df_cleaning(df_lemma):
    """
    Na vybraných projektech, dle filtru provede text preprocessing

    Parameters
    ----------
    df_lemma (DataFrame): lemmatizované texty projektů

    Returns
    -------
    df_cleaned (DataFrame): DataFrame připravený na další kroky analýzy podobností

    """
    # TODO: zapojit již do funkce lemmatizace a provádět text preprocessing jako celek
    # TODO: obecněji zdokumentovat na vstupu nemusí být jen lemmatizované texty
    # zde nechat jen výběr podle filtru VS

    #     df = df_lemma[(df_lemma['kod'].str.slice(0,4).isin(filtr_vs))]
    df_lemma['lemma'] = pd.DataFrame(df_lemma['lemma'].apply(lambda x: text_cleaning(x)))

    df_cleaned = df_lemma[['id', 'lemma']].reset_index(drop=True)

    return df_cleaned