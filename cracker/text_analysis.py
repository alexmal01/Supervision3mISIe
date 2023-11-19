import fitz
import nltk
import PyPDF2
import textstat
import re

def digit_percentage(text):
    # Count the number of digits in the string
    digit_count = sum(char.isdigit() for char in text)

    # Calculate the percentage of digits
    total_characters = len(text)
    percentage = (digit_count / total_characters)

    return percentage

def main():
    pdf_path = "D:\SuperVision Hack 2023\Supervision3mISIe\SFCR_TUiR_WARTA_2022-1.pdf"

    with open(pdf_path, 'rb') as f:
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text = page.get_text()
            pattern = re.compile(r'[^\w\s.]')
            cleaned_text = pattern.sub(' ', text)
            sentences = nltk.sent_tokenize(cleaned_text, language='polish')
            for sentence in sentences:
                digit_per = digit_percentage(sentence)
                sentence_len = len(sentence)
                digit_weight = 0.7  # Adjust this based on your preference
                length_weight = 0.03  # Adjust this based on your preference
                table_metric = (digit_weight * digit_per) + (length_weight * sentence_len)

    # Calculate the weighted average metric
    table_metric = (digit_weight * percentage_digits) + (length_weight * len(words))
                                                
    # pattern = re.compile(r'[^\w\s.]')
    # cleaned_text = pattern.sub(' ', text)
    # # Divide the text into sentences
    # nltk.download('punkt')
    # sentences = nltk.sent_tokenize(cleaned_text, language='polish')
    # print("EEEEE:", len(sentences))
    # # Measure the length and complexity of each sentence
    # for sentence in sentences:
    #     length = len(sentence.split())
    #     if length>100 and length<500:
    #         print(sentence)
    #     # print("TEXTSTAT",textstat.flesch_reading_ease(sentence))
    #     # print("TEXTSTAT",textstat.flesch_kincaid_grade(sentence))
    #     # print("TEXTSTAT",textstat.gunning_fog(sentence))
    #     # print("TEXTSTAT",textstat.smog_index(sentence))
    #     # print("TEXTSTAT",textstat.automated_readability_index(sentence))
    #     # print(f'Sentence: {sentence}')
    #         # print(f'Length: {length}')

if __name__ == "__main__":
    main()