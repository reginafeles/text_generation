# pylint: skip-file
"""
Module with storage functionality
"""

from typing import Union


class Storage:
    """
    Stores and manages elements
    """

    def __init__(self):
        self.storage = {}

    def _put(self, element: str) -> int:
        """
        Puts an element into the storage, assigns a unique id to it
        :param element: an element
        :return: 0 if succeeds, -1 if not
        """
        if not isinstance(element, str) or not len(element) <= 1:
            return -1
        if element not in self.storage:
            self.storage[element] = len(self.storage) + 1
        return 0

    def get_id(self, element: str) -> int:
        """
        Gets a unique id by an element
        :param element: an element to find
        :return: the id of the element given
            or -1 if there is no such element
            in the storage
        """
        if not isinstance(element, str) or element not in self.storage or not 0 < len(element) <= 1:
            return -1
        return self.storage[element]

    def get_element(self, element_id: int) -> Union[str, int]:
        """
        Gets an element by a unique id
        :param element_id: a unique id
        :return: the element for the id given
            or -1 if there is no such element
        """
        if not isinstance(element_id, int):
            return -1

        for letter, idx in self.storage.items():
            if idx == element_id:
                return letter

        return -1

    def update(self, elements: tuple) -> int:
        """
        Fills a storage by elements from the iterable
        :param elements: a tuple of elements
        :return: 0 if succeeds, -1 if not
        """
        if not isinstance(elements, tuple):
            return -1
        for sentence in elements:
            for token in sentence:
                for letter in token:
                    self._put(letter)
        return 0

    def get_special_token_id(self):
        """
        Returns the id of the '_' special token
            or None if there is no such token
        """
        try:
            return self.storage['_']
        except KeyError:
            return None
