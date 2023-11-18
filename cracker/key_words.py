import pandas as pd
import re



def load_key_words_requirements_csv(path:str) -> pd.DataFrame:
    requirements_df = pd.read_csv('key_words_requirements.csv', sep=';')
    requirements_df.columns = ['ID_PYTANIA', 'PYTANIE', 'KLUCZ', 'ID_SEKCJA']
    return requirements_df


def load_pdf_content_csv(path:str) -> pd.DataFrame:
    content_df = pd.read_csv('key_words_sample.csv',sep=';')
    content_df.columns = ['ID_TAB', 'DATA SFCR', 'WERSJA SFCR', 'KOD ZAKŁADU', 'ID_SEKCJA NADRZĘDNA', 'ID_SEKCJA', 'NAZWA_SECKJI', 'TREŚĆ']

    columns_to_fill = ['ID_TAB']
    content_df[columns_to_fill] = content_df[columns_to_fill].ffill()
    return content_df


def has_more_than_two_uppercase_letters(word:str) -> bool:
    # helper function for count_key_phrases
    return sum(1 for char in word if char.isupper()) > 2

def count_key_phrases(text:str, key_phrases:list[str]) -> dict:
    words = text.split()
    key_phrase_counts = {} 
    for phrase in key_phrases:
        # idea: if some word has more than 2 uppercase letters, search it case-sensitive, otherwise case-insensitive
        split_phrase = phrase.split()
        split_phrase_length = len(split_phrase)
        words_length = len(words)

        if any(has_more_than_two_uppercase_letters(word) for word in split_phrase):
            count = sum(phrase == ' '.join(words[i:i + split_phrase_length])
                        for i in range(words_length - split_phrase_length + 1))
        else:
            count = sum(phrase.lower() == ' '.join(words[i:i + split_phrase_length]).lower()
                        for i in range(words_length - split_phrase_length + 1))
        
        key_phrase_counts[phrase] = count

    return key_phrase_counts

def search_key_words(requirements_df:pd.DataFrame, content_df:pd.DataFrame, id_question:int, id_tab:int) -> pd.DataFrame:
    # this is the main function that returns the desired table with word counts
    key_phrases  = [phrase.strip() for  phrase in requirements_df[(requirements_df['ID_PYTANIA'] == id_question)]['KLUCZ'].values[0].split(';')]
    content_df = content_df[content_df['ID_TAB'] == id_tab] 
    sfcr_date = content_df['DATA SFCR'].values[0]
    sfcr_version = content_df['WERSJA SFCR'].values[0]
    company_code = content_df['KOD ZAKŁADU'].values[0]

    result_dict = {
        "ID_TAB" : id_tab,
        'DATA SFCR' : sfcr_date,
        'WERSJA SFCR' : sfcr_version,
        'KOD ZAKŁADU' : company_code,
        'ID_PYTANIA' : id_question
    }

    section_id = requirements_df[(requirements_df['ID_PYTANIA'] == id_question)]['ID_SEKCJA'].values[0]
    content = content_df[(content_df['ID_SEKCJA'] == section_id)]['TREŚĆ']
    # join sections content and clean it
    joined_content = ' '.join(list(content)).replace('\n', ' ')
    text = re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]', '', joined_content)
    key_phrase_counts = count_key_phrases(text, key_phrases)
    result = sum(key_phrase_counts.values())

    result_dict['CZY WYSTĄPIŁ KLUCZ'] = 1 if result > 0 else 0
    result_dict['ILOŚĆ WYSTĄPIEŃ KLUCZY'] = result

    return result_dict



