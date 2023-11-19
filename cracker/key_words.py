import pandas as pd
import re
from stempel import StempelStemmer

def create_stemmer():
    return StempelStemmer.polimorf()


def load_key_words_requirements_csv(path:str) -> pd.DataFrame:
    requirements_df = pd.read_csv(path, sep=';')
    requirements_df.columns = ['ID_PYTANIA', 'PYTANIE', 'KLUCZ', 'ID_SEKCJA']
    return requirements_df


def load_pdf_content_csv(path:str) -> pd.DataFrame:
    content_df = pd.read_csv(path,sep=';')
    
    content_df = content_df.dropna(subset=['ID_SEKCJA', 'ID_SEKCJA NADRZĘDNA'], how='all')
    content_df['ID_SEKCJA'] = content_df['ID_SEKCJA'].fillna(content_df['ID_SEKCJA NADRZĘDNA'])
    return content_df


def has_more_than_two_uppercase_letters(word:str) -> bool:
    # helper function for count_key_phrases
    return sum(1 for char in word if char.isupper()) > 2

def count_key_phrases(text:str, key_phrases:list[str],stemmer) -> dict:
    words = text.split()
    words = [stemmer.stem(word) for word in words]
    key_phrase_counts = {} 
    for phrase in key_phrases:
        # idea: if some word has more than 2 uppercase letters, search it case-sensitive, otherwise case-insensitive
        split_phrase = phrase.split()
        split_phrase_length = len(split_phrase)
        words_length = len(words)
        try:
            if any(has_more_than_two_uppercase_letters(word) for word in split_phrase):
                count = sum(phrase == ' '.join(words[i:i + split_phrase_length])
                            for i in range(words_length - split_phrase_length + 1))
            else:
                phrase = ' '.join([stemmer.stem(word) for word in split_phrase])
                count = sum(phrase.lower() == ' '.join(words[i:i + split_phrase_length]).lower()
                            for i in range(words_length - split_phrase_length + 1))
            
            key_phrase_counts[phrase] = count
        except:
            key_phrase_counts[phrase] = 0

    return key_phrase_counts

def search_key_words(requirements_df:pd.DataFrame, content_df:pd.DataFrame, id_question:int, stemmer) -> pd.DataFrame:
    # this is the main function that returns the desired table with word counts
    key_phrases  = [phrase.strip() for  phrase in requirements_df[(requirements_df['ID_PYTANIA'] == id_question)]['KLUCZ'].values[0].split(';')]
    section_id = requirements_df[(requirements_df['ID_PYTANIA'] == id_question)]['ID_SEKCJA'].values[0]
    
    content_df = content_df[content_df['ID_SEKCJA'] == section_id]
    if len(content_df)<1:
        return None
    sfcr_date = content_df['DATA SFCR'].values[0]
    sfcr_version = content_df['WERSJA SFCR'].values[0]
    company_code = content_df['KOD ZAKŁADU'].values[0]

    result_dict = {
        # "ID_TAB" : id_tab, # jest jeden na plik wiec przy laczeniu tabel dopiero....
        'DATA SFCR' : sfcr_date,
        'WERSJA SFCR' : sfcr_version,
        'KOD ZAKŁADU' : company_code,
        'ID_PYTANIA' : id_question
    }


    # join sections content and clean it
    joined_content = ' '.join([str(x) for x in content_df['TREŚĆ']]).replace('\n', ' ')
    text = re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]', '', joined_content)
    key_phrase_counts = count_key_phrases(text, key_phrases, stemmer)
    result = sum(key_phrase_counts.values())

    result_dict['CZY WYSTĄPIŁ KLUCZ'] = 1 if result > 0 else 0
    result_dict['ILOŚĆ WYSTĄPIEŃ KLUCZY'] = result

    return result_dict


def run_question_and_save_csv(requirements_df, content_df,stemmer, csv_path='Struktura dla danych dla weryfikacji kompletności SFCR.csv'):
    question_results = []
    for question_id in list(requirements_df.ID_PYTANIA):
        result = search_key_words(requirements_df,content_df,question_id, stemmer=stemmer)
        if result:
            question_results.append(result)
    results_df = pd.DataFrame(question_results)
    return results_df


