# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#

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
        self.words = []

        with open(wordfile) as f:
            for w in f:
                w = w.strip()
                if w != "" and not self.is_word(w):
                    self.words.append(w)

    def is_word(self, w):
        '''
        Is the string a word?

        Inputs:
           w (string): the word to check

        Returns: boolean
        '''
        return (w in self.words)

    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
          prefix (string): the prefix

        Returns: int
        '''
        # IMPORTANT: When you replace this version with the trie-based
        # version, do NOT compute the number of completions simply as
        #
        #    len(self.get_completions(prefix))
        #
        # See PA writeup for more details.

        return len(self.get_completions(prefix))

    def get_completions(self, prefix):
        '''
            Get the suffixes in the dictionary of words that start with the
            specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''
        return [w[len(prefix):] for w in self.words if w.startswith(prefix)]


if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary_list")
