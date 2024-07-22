"""
Lab 4
Language generation algorithm based on language profiles
"""

from typing import Tuple
import re
from lab_4.storage import Storage
from lab_4.language_profile import LanguageProfile


# 4
def tokenize_by_letters(text: str) -> Tuple or int:
    """
    Tokenizes given sequence by letters
    """
    if not isinstance(text, str):
        return -1
    text = text.lower()
    text = re.split(r'[.!?] |\n', text)
    list_text = []
    new_sentence = ''
    for sentence in text:
        for symbol in sentence:
            if symbol.isalpha() or symbol.isspace():
                new_sentence += symbol
        list_text.extend(new_sentence.split())
        new_sentence = ''
    ready_text = []
    for word in list_text:
        list_word = []
        list_word += '_'
        for letter in word:
            list_word.append(letter)
        list_word += '_'
        ready_text.append(tuple(list_word))
    return tuple(ready_text)


# 4
class LetterStorage(Storage):
    """
    Stores letters and their ids
    """

    def update(self, elements: tuple) -> int:
        """
        Fills a storage by letters from the tuple
        :param elements: a tuple of tuples of letters
        :return: 0 if succeeds, -1 if not
        """
        if not isinstance(elements, tuple):
            return -1
        super().update(elements)
        return 0

    def get_letter_count(self) -> int:
        """
        Gets the number of letters in the storage
        """
        if not self.storage:
            return -1
        return len(self.storage.keys())


# 4
def encode_corpus(storage: LetterStorage, corpus: tuple) -> tuple:
    """
    Encodes corpus by replacing letters with their ids
    :param storage: an instance of the LetterStorage class
    :param corpus: a tuple of tuples
    :return: a tuple of the encoded letters
    """
    if not (isinstance(storage, LetterStorage) and isinstance(corpus, tuple)):
        return ()
    storage.update(corpus)
    encoded_corpus = tuple(tuple(storage.storage[letter] for letter in word) for word in corpus)
    return encoded_corpus


# 4
def decode_sentence(storage: LetterStorage, sentence: tuple) -> tuple:
    """
    Decodes sentence by replacing letters with their ids
    :param storage: an instance of the LetterStorage class
    :param sentence: a tuple of tuples-encoded words
    :return: a tuple of the decoded sentence
    """
    if not (isinstance(storage, LetterStorage) and isinstance(sentence, tuple)):
        return ()
    decoded_sentence = tuple(tuple(storage.get_element(letter)
                                   for letter in word)
                             for word in sentence)
    return decoded_sentence


# 6
class NGramTextGenerator:
    """
    Language model for basic text generation
    """

    def __init__(self, language_profile: LanguageProfile):
        self.profile = language_profile
        self._used_n_grams = []

    def _generate_letter(self, context: tuple) -> int:
        """
        Generates the next letter.
            Takes the letter from the most
            frequent ngram corresponding to the context given.
        """
        if not isinstance(context, tuple):
            return -1
        dict_result = {}
        for instance in self.profile.tries:
            if instance.size - 1 == len(context):
                for key, value in instance.n_gram_frequencies.items():
                    if self._used_n_grams == list(instance.n_gram_frequencies.keys()):
                        self._used_n_grams = []
                    elif key[:len(context)] == context and key not in self._used_n_grams:
                        dict_result[key] = value
                if dict_result:
                    prediction = max(dict_result.keys(), key=dict_result.get)
                    self._used_n_grams.append(prediction)
                else:
                    prediction = max(instance.n_gram_frequencies.keys(),
                                     key=instance.n_gram_frequencies.get)
                return prediction[-1]
            return -1

    def _generate_word(self, context: tuple, word_max_length=15) -> tuple:
        """
        Generates full word for the context given.
        """
        if not isinstance(context, tuple) or \
                not isinstance(word_max_length, int):
            return ()
        word = list(context)
        if word_max_length == 1:
            word.append(self.profile.storage.get_special_token_id())
            return tuple(word)
        while len(word) != word_max_length:
            letter = self._generate_letter(context)
            word.append(letter)
            if letter == self.profile.storage.get_special_token_id():
                break
            context = tuple(word[-len(context):])
        return tuple(word)

    def generate_sentence(self, context: tuple, word_limit: int) -> tuple:
        """
        Generates full sentence with fixed number of words given.
        """
        if not (isinstance(context, tuple) \
                and isinstance(word_limit, int)):
            return ()
        sentence = []
        while len(sentence) != word_limit:
            word = self._generate_word(context, 15)
            sentence.append(word)
            context = tuple(word[-1:])
        return tuple(sentence)

    def generate_decoded_sentence(self, context: tuple, word_limit: int) -> str:
        """
        Generates full sentence and decodes it
        """
        if not (isinstance(context, tuple) and isinstance(word_limit, int)):
            return ""
        sentence = self.generate_sentence(context, word_limit)
        new_sentence = ""
        for element in sentence:
            for letter in element:
                letter = self.profile.storage.get_element(letter)
                new_sentence += letter
        decoded_sentence = new_sentence.replace('__', ' ').replace('_', '').capitalize() + '.'
        return decoded_sentence


# 6
def translate_sentence_to_plain_text(decoded_corpus: tuple) -> str:
    """
    Converts decoded sentence into the string sequence
    """
    if not isinstance(decoded_corpus, tuple) or not decoded_corpus:
        return ''
    sentence = ''
    for word in decoded_corpus:
        for letter in word:
            sentence += letter
    string_sequence = sentence.replace('__', ' ').replace('_', '').capitalize() + '.'
    return string_sequence


# 8
class LikelihoodBasedTextGenerator(NGramTextGenerator):
    """
    Language model for likelihood based text generation
    """

    def _calculate_maximum_likelihood(self, letter: int, context: tuple) -> float:
        """
        Calculates maximum likelihood for a given letter
        :param letter: a letter given
        :param context: a context for the letter given
        :return: float number, that indicates maximum likelihood
        """
        if not isinstance(letter, int) or not isinstance(context, tuple) or not context:
            return -1
        freq_dict = {}
        summary = 0
        for trie in self.profile.tries:
            if trie.size == len(context) + 1:
                for key, value in trie.n_gram_frequencies.items():
                    if context == key[:-1]:
                        freq_dict[key] = value
                        if letter == key[-1]:
                            summary += value
        if not sum(freq_dict.values()):
            return 0.0
        return summary / sum(freq_dict.values())

    def _generate_letter(self, context: tuple) -> int:
        """
        Generates the next letter.
            Takes the letter with highest
            maximum likelihood frequency.
        """
        if not isinstance(context, tuple) or not context:
            return -1
        probability = {}
        for instance in self.profile.tries:
            if instance.size - 1 == len(context):
                for key in instance.n_gram_frequencies:
                    if key[:len(context)] == context:
                        probability[key] = self._calculate_maximum_likelihood(key[-1], context)
        if not probability:
            for instance in self.profile.tries:
                if instance.size == 1:
                    return max(instance.n_gram_frequencies, key=instance.n_gram_frequencies.get)[0]
        return max(probability.keys(), key=probability.get)[-1]


# 10
class BackOffGenerator(NGramTextGenerator):
    """
    Language model for back-off based text generation
    """

    def _generate_letter(self, context: tuple) -> int:
        """
        Generates the next letter.
            Takes the letter with highest
            available frequency for the corresponding context.
            if no context can be found, reduces the context size by 1.
        """
        pass


# 10
class PublicLanguageProfile(LanguageProfile):
    """
    Language Profile to work with public language profiles
    """

    def open(self, file_name: str) -> int:
        """
        Opens public profile and adapts it.
        :return: o if succeeds, 1 otherwise
        """
        pass
