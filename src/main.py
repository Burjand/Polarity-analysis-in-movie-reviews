import config
from Preprocessing import Preprocessing
from collections import defaultdict
import numpy as np

if __name__ == "__main__":

    # FILES AND PATHS
    lexicon_file_medium = config.lexicon_file_medium
    lexicon_file_full = config.lexicon_file_full
    senticon_file = config.senticon_file
    corpus_folder = config.corpus_folder
    stopwords_file = config.stopwords_file
    encoding = config.encoding

    # PREPROCESSING
    # Text
    preprocessed_data = Preprocessing(corpus_folder, stopwords_file, lexicon_file_medium, lexicon_file_full, senticon_file)
    lemmatized_reviews = preprocessed_data.reviews_no_stopwords
    ranks = preprocessed_data.ranks

    # Dictionaries
    polarity_dictionary = preprocessed_data.polarity_dictionary

    # POLARITY ANALYSIS
    polarities = []

    for review in lemmatized_reviews:

        review_polarity = 0

        for word in review:

            if word in polarity_dictionary:

                review_polarity += polarity_dictionary[word]
        
        try:

            review_polarity /= len(review)

        except ZeroDivisionError:

            review_polarity = 0

        polarities.append(review_polarity)


    avg_polarity = defaultdict(list)
    
    for i in range(len(ranks)):

        avg_polarity[ranks[i]].append(polarities[i])

    for key in avg_polarity:

        avg_polarity[key] = np.average(avg_polarity[key])

    print(avg_polarity)
    



