import pandas as pd
import json
from urllib.parse import quote

def ciselnikJSON(df, file_name):
    """
    Na základě vstupních dat vygeneruje JSON strukturu číselníku pro Otevřená data (OD).

    Z vloženého textu vytvoří název pro výstupní soubor (ve formátu - malá písmena, s diakritikou, spojená pomlčkou).
    Propisuje se také do iri datové sady i jendotlivých položek.
    Dále vytvoří prázdný dict s přednastavenou hlavičkou a částí "položky", která se iterativně naplní daty ze zdrojového souboru.

    Podle otevřené formální normy musí číselník obsahovat minimálně:
    @context - vazba v rámci propojených dat (pouze v JSON)
    iri číselníku
    název číselníku v češtině
    položky číselníku

    Podle otevřené formální normy musí položky číselníku obsahovat minimálně:
    iri položky
    kód položky
    název položky v češtině
    popis položky v češtině

    Parameters
    ----------
    df (DataFrame): DataFrame o struktuře - Kód, Název, Popis.
    file_name (str): název výstupního souboru, který se převede do správného formátu

    Returns
    -------
    JSON file (file): výstupní soubor číselníku ve formátu JSON
    ciselnik_dict (dict): dict se strukturou číselníku, slouží hlavně k zobrazení výsledku

    """

    formatted_file_name = '-'.join(file_name.lower().split(' ')) # název spojený pomlčkami, malá písmena
    json_file_name = formatted_file_name + '.json'

    iri = 'https://www.tacr.cz/opendata/číselníky/' + formatted_file_name

    # základní struktura dict
    # předvyplněná hlavička
    ciselnik_dict = {
        "@context": "https://ofn.gov.cz/číselníky/2022-02-08/kontexty/číselník.jsonld",
        "typ": "Číselník",
        "iri": iri,
        "název": {
            "cs": file_name
        },
        "položky": []
    }

    # naplnění části dict "položky"
    for i in range(len(df)):
        # data k naplnění
        kod = df.iloc[i, 0]
        nazev = df.iloc[i, 1]
        popis = df.iloc[i, 2]

        # naplnění dat
        child_dict = {
            "typ": "Položka",
            "iri": iri + '/položka/' + str(kod),
            "kód": str(kod),
            "název": {
                "cs": nazev
            },
            "popis": {
                "cs": popis
            }
        }

        ciselnik_dict['položky'].append(child_dict)

    # vytvoření JSON souboru
    with open(json_file_name, 'w', encoding='utf-8') as f:
        json.dump(ciselnik_dict, f, ensure_ascii=False)

    return ciselnik_dict

def ciselnikCSV(df, file_name):
    """
    Na základě vstupních dat vygeneruje CSV strukturu číselníku pro Otevřená data (OD).

    Z vloženého textu vytvoří název pro výstupní soubor (ve formátu - malá písmena, s diakritikou, spojená pomlčkou).
    Propisuje se také do iri datové sady i jendotlivých položek.
    Dále vytvoří DataFrame s přednastavenou hlavičkou a částmi, které se iterativně naplní daty ze zdrojového souboru.

    Podle otevřené formální normy musí číselník obsahovat minimálně:
    @context - vazba v rámci propojených dat (pouze v JSON)
    iri číselníku
    název číselníku v češtině
    položky číselníku

    Podle otevřené formální normy musí položky číselníku obsahovat minimálně:
    iri položky
    kód položky
    název položky v češtině
    popis položky v češtině

    Parameters
    ----------
    df (DataFrame): DataFrame o struktuře - Kód, Název, Popis.
    file_name (str): název výstupního souboru, který se převede do správného formátu

    Returns
    -------
    CSV file (file): výstupní soubor číselníku ve formátu CSV
    ciselnik_df (DataFrame): DataFrame se strukturou číselníku, slouží hlavně k zobrazení výsledku

    """

    formatted_file_name = '-'.join(file_name.lower().split(' ')) # název spojený pomlčkami, malá písmena
    csv_file_name = formatted_file_name + '.csv'

    iri = 'https://www.tacr.cz/opendata/číselníky/' + formatted_file_name

    # standardizované názvy sloupců
    cols = ['číselník', 'číselník_název_cs', 'číselník_položka'
        , 'číselník_položka_kód', 'číselník_položka_název_cs', 'číselník_položka_popis_cs']

    ciselnik_list = []

    for i in range(len(df)):
        kod = str(df.iloc[i, 0])
        nazev = df.iloc[i, 1]
        popis = df.iloc[i, 2]

        iri_polozka = iri + '/položka/' + str(kod)

        ciselnik_list.append([iri, file_name, iri_polozka, kod, nazev, popis])

    ciselnik_df = pd.DataFrame(ciselnik_list, columns=cols)
    ciselnik_df.to_csv(csv_file_name, encoding='utf-8', index=False)

    return ciselnik_df

def schemaJSON(df, file_name, key=[]):
    """
    Vytvoří do formátu JSON schéma metadat datové sady v CSV pro Otevřená data (OD).

    Z vloženého textu vytvoří název pro výstupní soubor (ve formátu - malá písmena, s diakritikou, spojená pomlčkou).
    Propisuje se také do url schématu.
    Dále vytvoří dict, kde pro každý sloupec doplní metadata ze zdrojového souboru.

    Parameters
    ----------
    df (DataFrame): DataFrame o struktuře:
        name - název proměnné,
        titles - název sloupce, případně sloupců, pokud je v různých datových sadách pojmenován jinak
        dc:description - popis významu sloupce
        required - True/False, specifikuje, zda je hodnota ve sloupci povinná
        datatype - datový typ hodnot ve sloupci

    file_name (str): název výstupního souboru, který se převede do správného formátu
    key (str, list): názvy sloupců, které slouží jako klíč, může být samostatný sloupec nebo více sloupců jako list

    Returns
    -------
    JSON file (file): výstupní soubor metadat datové sady ve formátu JSON
    schema_dict (dict): dict se strukturou metadat datové sady, slouží hlavně k zobrazení výsledku

    """
    # kontrola, jestli vyplněné hodnoty klíče odpovídají názvům sloupců
    # porovná počet uvedených klíčů s počtem stejných hodnot v názvech sloupců (tady řádků)
    cols = df.iloc[:,1]

    if type(key) is list:
        set1 = set(key)
    else:
        set1 = set([key])

    set2 = set(cols)
    if len(set1.intersection(set2)) != len(set1):
        raise ValueError('Hodnota klíče není mezi názvy sloupců.')

    json_file_name = '-'.join(file_name.lower().split(' ')) + '.csv-metadata.json'

    url = 'https://www.tacr.cz/opendata/' + json_file_name

    schema_dict = {
        "@context": ["http://www.w3.org/ns/csvw", {"@language": "cs"}],
        "url": url,
        "tableSchema": {
            "columns": [],
            "primaryKey": key
        }
    }

    for i in range(len(df)):
        name = quote(df.iloc[i, 0])  # zakóduje název do URI, tj. diakritika je zakódovaná procenty
        titles = df.iloc[i, 1]
        desc = df.iloc[i, 2]
        required = bool(df.iloc[i, 3])
        datatype = df.iloc[i, 4]

        child_dict = {
            "name": name,
            "titles": titles,
            "dc:description": desc,
            "required": required,
            "datatype": datatype
        }

        schema_dict['tableSchema']['columns'].append(child_dict)

    with open(json_file_name, 'w', encoding='utf-8') as f:
        json.dump(schema_dict, f, ensure_ascii=False)

    return schema_dict
