import matplotlib.pyplot as plt
import networkx as nx
import nltk
#nltk.download('punkt_tab')
#nltk.download('stopwords')
import numpy as np
import pandas as pd
from collections import Counter


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

    print(co_occurrences) 

    # Create a table of the results, substituting any missing data with 0
    df = pd.DataFrame(co_occurrences).fillna(value=0)

    print(df)

    create_graph(co_occurrences, df, tokenised_sentences)
    


def clean_text(text):
    # Remove unnecessary punctuation

    text = text.replace(",", "")
    return text


def tokenise_sentences(cleaned_text):
    # Split up sentences at the full stop
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


def create_graph(dictionary, df, tokenised_sentences):

#Create the graph - the more the words cooccur, the closer they appear in the graph    

    G = nx.Graph()
    for key in dictionary:
        for cooccurrence in dictionary[key]:
            proximity = dictionary[key][cooccurrence]**2
            G.add_edge(key, cooccurrence, weight=proximity) 
    
    all_words = [word for sentence in tokenised_sentences for word in sentence]
    word_freq = Counter(all_words)
    

    #The greater the frequency of the words in the text, the larger their visual representation in the graph
    node_sizes = [word_freq[node] * 1500 for node in G.nodes]

    pos = nx.spring_layout(G, weight="weight")
    
    nx.draw(
        G, pos, 
        with_labels=True, 
        node_size=node_sizes, 
        node_color="skyblue", 
        edge_color="gray", 
        font_size=12
        )

    plt.show()


if __name__ == "__main__":
    main()