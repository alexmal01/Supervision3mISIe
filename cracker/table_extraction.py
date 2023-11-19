from pdfminer.layout import LAParams, LTTextBox, LTTextLineHorizontal
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import pandas as pd
import fitz  # PyMuPDF
from collections import defaultdict



def find_pages_with_patterns(pdf_path, pattern_list):
    pdf_document = fitz.open(pdf_path)
    page_dict = {}

    for pattern in pattern_list:
        page_dict[pattern] = []

    # Iterate through all pages
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]

        # Extract text from the page
        text = page.get_text("text")

        # Check if each pattern is present on the page
        for pattern in pattern_list:
            if pattern in text:
                page_dict[pattern].append(page_number)
            else:
                # Iterate through shorten pattern
                pattern_short = '.'.join(pattern.split('.')[:-1])
                if pattern_short in text:
                    # If pattern found, add the page to the corresponding list
                    page_dict[pattern].append(page_number)

    # Close the PDF document
    pdf_document.close()

    # Create a dictionary with page numbers as keys and corresponding patterns as values
    result_dict = {}
    for pattern, page_numbers in page_dict.items():
        for page_number in page_numbers:
            if page_number not in result_dict:
                result_dict[page_number] = [pattern]
            else:
                result_dict[page_number].append(pattern)

    return result_dict


def load_interpreter_pdf():
    """
    Wczytaj pdfminer ustawienia

    Parametry:
    - Brak

    Zwrot:
    - wszystkie configs potrzebne
  """
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    return rsrcmgr, laparams, device, interpreter


def create_full(file_pdf, df_template):
  """
    Otrzymujemy końcowo DF jako odczytane wymagane tabele, korzystamy z koordynatów 
    kolumn i wierszy, funkcja jest odporna na możliwość wielu tabel obok siebie

    Parametry:
    - file_pdf - ścieżka do pdf sfcr
    - df_template - nasz plik w formacie DF, powstały na podstawie excela załącznik nr 4
  

    Zwrot:
    - df_final - końcowa DF o tabelach z danego sfcr
  """


  #read configs
  rsrcmgr,laparams,device,interpreter = load_interpreter_pdf()

  #find page for table
  unique_sheets = df_template['sheet'].unique()
  result_dict = find_pages_with_patterns(file_pdf, unique_sheets)

    # find page for table
    unique_sheets = df_template['sheet'].unique()
    result = find_pages_with_patterns(file_pdf, unique_sheets)
    grouped_dict = defaultdict(list)

    # Grouping keys by values
    for key, value in result.items():
        grouped_dict[value].append(key)

    result_dict = dict(grouped_dict)

    # -------

    fp = open(file_pdf, 'rb')
    pages = PDFPage.get_pages(fp)

  for page in pages:
      
      if not pg_number in result_dict.keys():
        pg_number+=1
        continue

    pg_number = 0
      df_sheet = df_template[df_template['sheet'].isin(result_dict[pg_number])]
      
      pg_number+=1

      try:
        
        df_found = create_final_table(page,df_sheet,interpreter,device,laparams,rsrcmgr)
        df_final = pd.concat([df_final, df_found], ignore_index=True)

        try:
  #add the one not found
  df_final['value'] = df_final['value'].str.replace(' ','')

        except Exception as e:
            continue

    # add the one not found
    df_sheet = df_template[df_template['sheet'].isin(result_dict[None])]
    df_final = pd.concat([df_final, df_sheet], ignore_index=True)
    df_final['value'] = df_final['value'].str.replace(' ', '')

    df_final['value'] = pd.to_numeric(df_final['value'], errors='coerce')

    df_final = df_final.rename(columns={"R": "WIERSZ", "C": "KOLUMNA", "value": "WARTOŚĆ", "sheet": "FORMULARZ"})

    return df_final.drop_duplicates()


def create_final_table(page,df_short,interpreter,device,laparams,rsrcmgr,THRESHOLD=4.2):
  """
    Na podstawie odczytu strony, na której znajdują się dane tabele wyekstrahuj wartości

    Parametry:
    - page - odczyt strony
    - df_short - nasz plik w formacie DF, powstały na podstawie excela załącznik nr 4,
                    przycięty tylko do nazw tabel obecnych na stronie
    -param* - configi
    -THRESHOLD - liczba pikseli odchyłki, im mniej tym dokładniej wartość w tabeli musi
                znajdować się na odpowiadających współrzędnych wymiaru,kolumny


    Zwrot:
    - df_result - DF jako informacje wiersz, kolumna, wartość, formularz z danej strony
  """
    # get coord
    data_list = []

    interpreter.process_page(page)
    layout = device.get_result()
    for lobj in layout:
        if isinstance(lobj, LTTextBox):
            for tobj in lobj:
                if isinstance(tobj, LTTextLineHorizontal):
                    x0, y0_orig, x1, y1_orig = tobj.bbox
                    # y0_orig is distance from the bottom of the page, y0 is distance from the top
                    y0 = page.mediabox[3] - y1_orig
                    y1 = page.mediabox[3] - y0_orig
                    text = tobj.get_text()
                    data_list.append({"x0": x0, "x1": x1, "y0": y0, "y1": y1, "text": text})

    # create df
    df = pd.DataFrame(data_list)
    df['text'] = df['text'].str.replace('\n', ' ')

    # get df with Columns char
    df_C = df[df['text'].str.match(r'^C\d{4}')]
    # get df with Rows char
    df_R = df[df['text'].str.match(r'^R\d{4}')]
    # wider Columns coordinates based of other columns position
    df_C = df_C.sort_values(by=['y0', 'x0'], ascending=[True, True])
    grouped_dfs = [group for _, group in df_C.groupby(['y0', 'y1'])]
    for g_df in grouped_dfs:
        if len(g_df) == 1:
            g_df['x1'] = g_df.iloc[0]['x1'] + (g_df.iloc[0]['x1'] - g_df.iloc[0]['x0'])
            continue

        dist = g_df.iloc[1]['x0'] - g_df.iloc[0]['x1']
        g_df['x1'][:-1] = g_df['x0'][1:]
        g_df['x1'][-1:] = g_df.iloc[-1]['x1'] + dist

    df_C_wider = pd.concat(grouped_dfs, ignore_index=True)

    # get values based of cooridates of Columns and Rows
    df_result = df_short

    for index, row in df_short.iterrows():
        c_code, r_code = row['C'], row['R']

        c_row = df_C_wider[df_C_wider['text'].str.contains(c_code)]
        r_row = df_R[df_R['text'].str.contains(r_code)]

        if (c_row.empty):
            continue

        c_row = c_row.iloc[0]
        # there can be multiple the same rows code on the page, so choose one under column
        r_row = r_row[(r_row['y1'] >= c_row['y0']) & (r_row['x0'] <= c_row['x0'])]

        if r_row.empty:
            continue

        r_row = r_row.sort_values(by=['y1', 'x1'], ascending=[True, False]).iloc[0]

        x0_min, x1_max = c_row['x0'], c_row['x1']
        y0_min, y1_max = r_row['y0'], r_row['y1']
        # thr is threshold what diff between coordinates and still accept as value
        thr = THRESHOLD

        # find cell
        cell_row = df[
            (df['y0'] >= y0_min - thr) & (df['y1'] <= y1_max + thr) & (df['x0'] >= x0_min - thr) & (df['x1'] <= x1_max)]

        if cell_row.empty:
            continue

        df_result.loc[(df_result['C'] == c_code) & (df_result['R'] == r_code), 'value'] = cell_row.iloc[0]['text']

    return df_result
