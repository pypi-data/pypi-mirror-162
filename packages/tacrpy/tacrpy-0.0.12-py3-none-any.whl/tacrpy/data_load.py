import pandas as pd
import re
import os


def multiload(path, filename):
    """
    Načte a spojí všechny soubory se stejným jménem a strukturou v dané složce.

    Vhodné využít pro soubory, které jsou strukturou stejné a název se liší jen příponou.
    (Např. Export_projekty.xlsx, Export_projekty_MV.xlsx, Export_projekty_MPO.xlsx).

    Obsahuje i ztlumení varování "Workbook contains no default style, apply openpyxl's default".
    Pokud se podaří odstranit na straně pandas, tak odstranit i zde.

    Parameters
    ----------
    path (str): cesta, kde se dané soubory nachází
    filename (str): textový řetezec, který se nachází v názvu souborů

    Returns
    -------
    df_concat (DataFrame): DataFrame spojený z jednotlivých souborů

    """
    import warnings

    with warnings.catch_warnings(record=True):
        warnings.simplefilter('always')

        # vytvoří seznam všech souboru s daným názvem
        files = [file for file in os.listdir(path) if re.match(filename, file)]

        df_concat = pd.DataFrame()

        # postupně načte a spojí všechny soubory ze seznamu výše
        for file in files:
            df = pd.read_excel(os.path.join(path, file))
            df_concat = pd.concat([df_concat, df])

        return df_concat