# CS122: Auto-completing keyboard
# User interface implementation
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#


########################################
###                                  ###
###   DO NOT MODIFY THIS FILE        ###
###                                  ###
########################################

import os
import sys
import tty
import termios
import fcntl
import string
import importlib

module = None


def load_trie_module(name):
    global module
    module = importlib.import_module(name)


def getch():
    '''
    Get a character from stdin
    '''
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
        while True:
            try:
                c = sys.stdin.read(1)
                if c != "":
                    break
            except IOError:
                pass

    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    return c

nearby_dict = {"q": ["w", "a"],
               "w": ["q", "e", "s"],
               "e": ["w", "r", "d"],
               "r": ["e", "t", "f"],
               "t": ["r", "y", "g"],
               "y": ["t", "u", "h"],
               "u": ["y", "i", "j"],
               "i": ["u", "o", "k"],
               "o": ["i", "p", "l"],
               "p": ["o"],
               "a": ["q", "s", "z"],
               "s": ["w", "a", "d", "z", "x"],
               "d": ["e", "s", "f", "x", "c"],
               "f": ["r", "d", "g", "c", "v"],
               "g": ["t", "f", "h", "v", "b"],
               "h": ["y", "g", "j", "b", "n"],
               "j": ["u", "h", "k", "n", "m"],
               "k": ["i", "j", "l", "m"],
               "l": ["o", "k"],
               "z": ["s", "x"],
               "x": ["z", "s", "d", "c"],
               "c": ["x", "v", "f"],
               "v": ["c", "b", "f", "g"],
               "b": ["v", "n", "g", "h"],
               "n": ["b", "m", "h", "j"],
               "m": ["n", "j", "k"]}


def nearby_keys(c):
    '''
    Return a list of the letters near c on the keyboard
    '''
    rv = nearby_dict.get(c, [])
    rv = rv[:]
    return rv


def did_you_mean(eng_dict, word):
    '''
    Return a list of possible correct words that are "near" to the
    current word.
    '''
    fv = []  # trie.fuzzy_versions(t, word)
    if len(fv) == 0:
        return
    if len(fv) <= 20:
        print("Did you mean one of these?")
        for maybe in fv:
            for c in maybe:
                sys.stdout.write(c)
            sys.stdout.write(" ")
        print("")


def misspelled_prompt(message, eng_dict, word):
    print("\nThere are no words that start with '%s'" % word)
    did_you_mean(eng_dict, word)
    prompt(message, word)


def prompt(message, word):
    '''
    Write the shell's prompt to stdout
    '''
    if len(message) == 0:
        pre = ""
    else:
        pre = "|%s| " % message
    sys.stdout.write(pre + "> " + word)
    sys.stdout.flush()


def process_completions(eng_dict, message, word, print_candidates):
    '''
    Process the current "word" and generate a new message and prompt,
    information about possible completions, an error message, or
    information about possible corrections to the word.
    '''
    n = eng_dict.num_completions(word)
    misspelled = False

    if n == 0:
        # If there are no possible completions, this is a misspelled
        # word. We want nothing to do with it.

        misspelled = True
        misspelled_prompt(message, eng_dict, word)
    elif n == 1:
        # If there is only one possible completion, go ahead and add
        # the word to the message.
        word += eng_dict.get_completions(word)[0]
        if len(message) > 0:
            message += " "
        message += word
        word = ""
        print()
        prompt(message, word)
    else:
        if print_candidates:
            if n > 10:
                print("\n(" + str(n) + " completions)")
            else:
                print()
                for com in eng_dict.get_completions(word):
                    print(word + com)
            prompt(message, word)

    return message, word, misspelled


def shell(eng_dict):
    '''
    Gather characters from stdin and handle requests for auto
    completion, reset, etc.

    Type Control-C to get out of this shell.
    '''
    message = ""
    word = ""
    misspelled = False
    prompt(message, word)
    while True:
        # Get a character
        c = getch()

        # Control-D resets the message
        if ord(c) == 4:
            message = ""
            word = ""
            misspelled = False
            print()
            prompt(message, word)
            continue

        # Possible end of word
        if (c == " ") or (c == "\n"):
            if misspelled:
                misspelled_prompt(message, eng_dict, word)
            else:
                if not eng_dict.is_word(word):
                    print("\nWord '%s' does not exist" % word)
                    did_you_mean(eng_dict, word)
                    prompt(message, word)
                else:
                    if len(message) > 0:
                        message += " "
                    message += word
                    word = ""
                    print()
                    prompt(message, word)

            continue

        # Autocomplete
        if c == "\t":
            if word != "":
                message, word, misspelled = process_completions(eng_dict, message, word, print_candidates=True)
            continue

        # Backspace
        if ord(c) == 127:
            if len(word) == 0:
                print("cannot change previous word once accepted")
                continue
            word = word[:len(word) - 1]
            sys.stdout.write('\r')
            sys.stdout.flush()
            prompt(message, word + " ")
            sys.stdout.write('\b')
            sys.stdout.flush()
        else:
            # If the character is not a letter, we're not interested
            # in it.
            if c not in string.ascii_letters:
                message = "5:" + message
                continue

            # Update prompt and letter
            sys.stdout.write(c)
            sys.stdout.flush()
            word = word + c

        message, word, misspelled = process_completions(eng_dict, message, word, print_candidates=False)


def go(module_name=None):
    '''
    Process the arguments and fire up the shell.
    '''

    global module

    # set modules to the desired module
    if module_name:
        module = __import__(module_name)

    if(len(sys.argv) != 2):
        print("Usage: python3 english_dictionary.py WORD_FILE")
        exit(1)

    wordfile = sys.argv[1]

    if not os.path.exists(wordfile):
        print("Error: %s does not exist")
        exit(1)

    print("Loading words into trie...",)
    eng_dict = module.EnglishDictionary(wordfile)
    print(" done")
    print("===================================================")
    print("      Welcome to the auto-completing shell!")
    print()
    print(" Start typing a word and press Tab to autocomplete")
    print()
    print("      Press Control-D to reset the message")
    print("             Press Control-C to exit")
    print("===================================================")
    print()

    try:
        shell(eng_dict)
    except KeyboardInterrupt as ki:
        print()
        exit(0)

if __name__ == "__main__":
    go(sys.argv[0])
