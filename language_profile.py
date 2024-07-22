# pylint: skip-file
"""
Implements language profile class and supported functionality
"""


import json
from lab_4.storage import Storage


class NGramTrie:
    """
    Stores and manages ngrams
    """

    def __init__(self, n: int, letter_storage: Storage):
        self.size = n
        self._storage = letter_storage
        self.n_grams = []
        self.n_gram_frequencies = {}

    def extract_n_grams(self, encoded_corpus: tuple) -> int:
        """
        Extracts n-grams from the given sentence, fills the field n_grams
        :return: 0 if succeeds, 1 if not
        e.g.
        encoded_corpus = (
            ((1, 2, 3, 4, 1), (1, 5, 2, 1)),
            ((1, 3, 4, 1), (1, 5, 2, 1))
        )
        self.size = 2
        --> (
            (
                ((1, 2), (2, 3), (3, 4), (4, 1)), ((1, 5), (5, 2), (2, 1))),
                (((1, 3), (3, 4), (4, 1)), ((1, 5), (5, 2), (2, 1))
            )
        )
        """
        if not isinstance(encoded_corpus, tuple):
            return 1

        list_n_grams = []
        encoded_corpus = [encoded_corpus]
        for sentence in encoded_corpus:
            n_grams_sentence = []
            for token in sentence:
                n_grams_token = []
                for ind in range(len(token) - self.size + 1):
                    n_grams_token.append(tuple(token[ind:ind + self.size]))
                if not n_grams_token:
                    continue
                n_grams_sentence.append(tuple(n_grams_token))
            list_n_grams.append(tuple(n_grams_sentence))
        self.n_grams = tuple(list_n_grams)
        return 0

    def get_n_grams_frequencies(self) -> int:
        """
        Fills in the n-gram storage from a sentence, fills the field n_gram_frequencies
        :return: 0 if succeeds, 1 if not
        e.g.
        self.n_grams = (
            (
                ((1, 2), (2, 3), (3, 4), (4, 1)), ((1, 5), (5, 2), (2, 1))),
                (((1, 3), (3, 4), (4, 1)), ((1, 5), (5, 2), (2, 1))
            )
        )
        --> {
            (1, 2): 1, (2, 3): 1, (3, 4): 2, (4, 1): 2,
            (1, 5): 2, (5, 2): 2, (2, 1): 2, (1, 3): 1
        }
        """
        if not self.n_grams:
            return 1

        for sentence in self.n_grams:
            for word in sentence:
                for n_gram in word:
                    self.n_gram_frequencies[n_gram] = self.n_gram_frequencies.get(n_gram, 0) + 1
        return 0

    def extract_n_grams_frequencies(self, n_grams_dictionary: dict) -> int:
        """
        Extracts n_grams frequencies from given dictionary.
        Fills self.n_gram_frequency field.
        """
        if not isinstance(n_grams_dictionary, dict):
            return 1

        for ngram, frequency in n_grams_dictionary.items():
            if isinstance(ngram, tuple) and isinstance(frequency, int):
                self.n_gram_frequencies[ngram] = frequency
        return 0


class LanguageProfile:
    """
    Stores and manages language profile information
    """

    def __init__(self, letter_storage: Storage, language_name: str):
        self.storage = letter_storage
        self.language = language_name
        self.tries = []
        self.n_words = []

    def create_from_tokens(self, encoded_corpus: tuple, ngram_sizes: tuple) -> int:
        """
        Creates a language profile
        :param encoded_corpus: a tuple of encoded letters
        :param ngram_sizes: a tuple of ngram sizes,
            e.g. (1, 2, 3) will indicate the function to create 1,2,3-grams
        :return: 0 if succeeds, 1 if not
        e.g.
        encoded_corpus = (((1, 2, 3, 1), (1, 4, 5, 1), (1, 2, 6, 7, 7, 8, 1)),)
        ngram_sizes = (2, 3)
        self.tries --> [
            <__main__.NGramTrie object at 0x09DB9BB0>,
            <__main__.NGramTrie object at 0x09DB9A48>
        ]
        self.n_words --> [11, 9]
        self.tries[0].n_grams --> (
            (((1, 2), (2, 3), (3, 1)), ((1, 4), (4, 5), (5, 1)),
            ((1, 2), (2, 6), (6, 7), (7, 7), (7, 8), (8, 1))),
        )
        """
        if not isinstance(encoded_corpus, tuple) or not isinstance(ngram_sizes, tuple):
            return 1

        for size in ngram_sizes:
            ngram_storage = NGramTrie(size, self.storage)
            ngram_storage.extract_n_grams(encoded_corpus)
            ngram_storage.get_n_grams_frequencies()
            self.tries.append(ngram_storage)
            self.n_words.append(len(ngram_storage.n_gram_frequencies))
        return 0

    def save(self, name: str) -> int:
        """
        Saves language profile into json file
        :param name: name of the json file with .json format
        :return: 0 if profile saves, 1 if any errors occurred
        """
        if not isinstance(name, str):
            return 1

        profile_to_save = {}

        # name
        profile_to_save['name'] = self.language

        # build all frequencies
        profile_to_save['freq'] = {}
        for trie in self.tries:
            profile_to_save['freq'].update(trie.n_gram_frequencies)

        # n_words
        profile_to_save['n_words'] = self.n_words

        # decode frequencies and merge them
        profile_to_save['freq'] = dict(
            ("".join([self.storage.get_element(id_letter) for id_letter in k]), v)
            for k, v in profile_to_save['freq'].items())

        # save result
        with open(name, 'w', encoding='utf-8') as profile_file:
            json_string = json.dumps(
                profile_to_save, sort_keys=True, indent=2, ensure_ascii=False)
            profile_file.write(json_string)
        return 0

    def open(self, file_name: str) -> int:
        """
        Opens language profile from json file and writes output to
            self.language,
            self.tries,
            self.n_words fields.
        :param file_name: name of the json file with .json format
        :return: 0 if profile is opened, 1 if any errors occurred
        """
        if not isinstance(file_name, str):
            return 1

        with open(file_name, 'r', encoding='utf-8') as file:
            profile = json.load(file)

            # update storage with letters in case there are non existing letters
            self.storage.update(
                tuple(tuple(letter for letter in key) for key in profile['freq'].keys()))

            # replace letters with ids
            profile['encoded_freqs'] = {}
            for key, value in profile['freq'].items():
                encoded_ngram = tuple(self.storage.get_id(letter) for letter in key)
                profile['encoded_freqs'][encoded_ngram] = value
            profile['freq'] = profile['encoded_freqs']

            # language and nwords
            self.language = profile['name']
            self.n_words = profile['n_words']

            # initialize tries with ngram frequencies
            self._initialize_and_fill_tries(profile)
        return 0

    def _initialize_and_fill_tries(self, freq_dictionary: dict) -> int:
        """
        Helping method for initialization and filling
            NGramTrie objects with ngrams given

        freq_dict sample: {
            1: {(2,): 234, (1,): 2345},
            2: {(1, 2): 23456, (2, 1): 123}
        }
        """
        if not isinstance(freq_dictionary, dict):
            return -1

        unique_sizes = {}
        for ngram, frequency in freq_dictionary['freq'].items():
            if len(ngram) not in unique_sizes:
                unique_sizes[len(ngram)] = {}
            unique_sizes[len(ngram)].update({ngram: frequency})

        for unique_size, dictionary in unique_sizes.items():
            ngram_storage = NGramTrie(unique_size, self.storage)
            ngram_storage.extract_n_grams_frequencies(dictionary)
            self.tries.append(ngram_storage)
        return 0
