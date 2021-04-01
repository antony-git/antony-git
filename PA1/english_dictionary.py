# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# Antony Awad, 21 January 2021

import os
import sys
from sys import exit

import autocorrect_shell


class EnglishDictionary(object):
    def __init__(self, wordfile):
        '''
        Constructor

        Inputs:
            wordfile (string): name of the file with the words.
        '''
        self.words = TrieNode()
        with open(wordfile) as f:
            for w in f:
                w = w.strip()
                if w != "" and not self.is_word(w):
                    self.words.add_word(w)

    def is_word(self, w):
        '''
        Is the string a word?

        Inputs:
           w (string): the word to check

        Returns: boolean
        '''
        if self.words.get_node(w) is None:
            return False
        return self.words.get_node(w).final

    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
            prefix (string): the prefix

        Returns: int
        '''
        if self.words.get_node(prefix) is not None:
            return self.words.get_node(prefix).count
        ### GRADER COMMENT
        # get_node(prefix) is called twice here. Would be better
        # to save it as a variable.
        # Penalty: -2 Style
        return 0

    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
            prefix (string): the prefix

        Returns: list of strings.
        '''
        ### GRADER COMMENT
        # .get_node(prefix) could return None and result in exception:
        # 'NoneType' object has no attribute 'get_suffixes'
        # Penalty: reflected in Test Cases rubric.
        return self.words.get_node(prefix).get_suffixes()


class TrieNode(object):
    def __init__(self, letter="", final=False):
        '''
        Constructor for the TrieNode class.

        Inputs:
            letter (string): letter correspondent with this node
            final (bool): indicates whether this node represents a full word
        '''
        ### GRADER COMMENT
        # It would be better to use read-only properties for the counter
        # and boolean, and to make the children private.
        # Penalty: No Penalty
        self.count = 0
        self.final = final
        self.letter = letter
        self.letters_to_node = {}

    def add_word(self, word):
        '''
        Method that takes a word and adds it to the trie by constructing trie
        objects and updating all of the trie attributes.

        Input:
            word (str): the word to be integrated into the trie
        '''
        self.count += 1
        if len(word) == 0:
            self.final = True
            return None
        if word[0] not in self.letters_to_node.keys():
            new_node = TrieNode(word[0]) # create destination node
            self.letters_to_node[word[0]] = new_node # create link
            new_node.add_word(word[1:])
        else:
            node = self.letters_to_node[word[0]]
            node.add_word(word[1:])

    def get_node(self, word):
        '''
        Method that takes a word and returns either the node correspondent
        to the word's final letter inside the trie, or None.

        Input:
            word (str): the word for which the node will be fetched
        Outputs:
            The correspondent node or None.
        '''
        if len(word) == 0:
            return self
        elif word[0] not in self.letters_to_node.keys():
            return None
        else:
            return self.letters_to_node[word[0]].get_node(word[1:])

    def get_suffixes(self):
        '''
        Method that acts on a node and returns all of the suffixes that
        make valid words with the letters leading up to and including the
        node's.

        Output:
            lst (list): list of suffixes
        '''
        lst = []
        if self.letters_to_node == {}:
            return ['']
        for obj in self.letters_to_node.values():
            suffixes = obj.get_suffixes()
            if obj.final is True:
                lst.append(obj.letter)
            for s in suffixes:
                suffix = obj.letter + s
                if suffix not in lst:
                    lst.append(obj.letter + s)
        return lst


if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary")
