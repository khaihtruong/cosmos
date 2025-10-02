import nltk
#nltk.download('punkt_tab')
#nltk.download('stopwords')
import pandas as pd
import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def main():

    # Define the text
    text = input("Text: ")

    # Clean the data set
    cleaned_text = clean_text(text)

    # Tokenise the sentences
    tokenised_sentences = tokenise_sentences(cleaned_text)

    # Create the co-occurence matrix
    co_occurrences = create_cooccurrence_matrix(tokenised_sentences)

    # Create a table of the results, substituting any missing data with N/A
    df = pd.DataFrame(co_occurrences).fillna(value="N/A")

    print(df)


def clean_text(text):
    # Remove unnecessary punctuation

    text = text.replace(",", "")
    return text


def tokenise_sentences(cleaned_text):
    # Split up sentences (this will have to be refined as at the moment only taking into account full stop). I will be using regular expressions. The issue is that sentences like "I love tennis too, but my love for football is stonger" count the two occurrences of love both for football and for tennis, while it should only be one for tennis and one for football.
    sentences = cleaned_text.lower().split(".")

    tokenised_sentences = []

    # Tokenise the words and standardise them to lower case
    for sentence in sentences:
        if sentence != "":
            words = word_tokenize(sentence)
            cleaned_words = []
            for word in words:
                if word not in set(stopwords.words("english")):
                    cleaned_words.append(word)
            tokenised_sentences.append(cleaned_words)

    return tokenised_sentences


def create_cooccurrence_matrix(tokenised_sentences):
    # Create a data structure (a dictionary of dictionaries) which stores the words that appear in the same sentence and how many times
    co_occurrences = {}

    for sentence in tokenised_sentences:
        for word in sentence:
            if word not in co_occurrences:
                co_occurrences[word] = {}
            for i in sentence:
                if not i == word:
                    if i not in co_occurrences[word]:
                        co_occurrences[word][i] = 1
                    else:
                        co_occurrences[word][i] += 1

    return co_occurrences


if __name__ == "__main__":
    main()
