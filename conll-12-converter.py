# encoding: utf-8

import string
import os
import re
import random
import constants
import subprocess
from pygermanet import load_germanet


class ConLL12Converter:

    def __init__(self, text, outputPath):

        self.outputPath = outputPath

        if type(text) == str or isinstance(text, unicode):
            self.text = text
        else:
            raise TypeError('self.text is not a string')

        self.tags = self.get_tags()
        self.lemmaDic = self.get_lemma_dict()

    def get_tags(self):
            """
            Generates tags from string.
            Takes a text as input and extracts nominatives using RFTagger.
            Args:
                    None
            Returns:
                    List with tags
            """

            # Create directory temp if not existent
            if not os.path.exists(constants.temp_dir):
                os.makedirs(constants.temp_dir)

            # Create random string
            rand_string = ''.join(random.choice(string.ascii_lowercase +
                                                string.digits) for _ in range(15))

            # Path for text files
            tokens = constants.temp_tokens + "_" + rand_string + ".txt"
            curr_text = constants.temp_text + "_" + rand_string + ".txt"

            # Save text to file
            f = open(curr_text, 'w')
            f.write(self.text)
            f.close()

            # Tokenize
            f = open(tokens, 'w')
            subprocess.call(
                [constants.tokenizer, curr_text], stdout=f, shell=False)
            f.close()

            # Tag Tokens from temp_tokens
            f = open(constants.temp_tags + "_" + rand_string + ".txt", 'w')
            subprocess.call([constants.rftagger, constants.german_par,
                             tokens], stdout=f, shell=False)
            f.close()

            # Read tags from file
            f = open(constants.temp_tags + "_" + rand_string + ".txt", 'r')
            tags = f.readlines()
            f.close()

            # Regular Expression
            # regex = re.compile(r'.*N.Name.*|.*N.Reg.*|.*SYM.Pun.Sent')

            # # Filtered tags
            # filtered_tags = [regex.match(tag).string for tag in tags
            #                  if regex.match(tag) is not None]

            # # Split tags in lists
            splited_tags = [str.split(tag, '\t') for tag in tags]

            # Load germanet
            g = load_germanet()

            # Build Lemmas
            splited_tags_lemma = [[g.lemmatise(tag[0].decode('utf-8'))[0], tag[0],
                                   tag[1]] for tag in splited_tags[:-1]]

            # Update self.tags
            tags = splited_tags_lemma

            # Remove files
            os.remove(curr_text)
            os.remove(tokens)
            os.remove(constants.temp_tags + "_" + rand_string + ".txt")

            return splited_tags_lemma

    def get_lemma_dict(self):

        # Build empty dictionary with lemmas as key
        lemmaDic = {key: [] for [key, value, token] in self.tags}

        # Fill the dictionary with all values
        [lemmaDic[key].append(value.decode('utf-8')) for [key, value, token] in
            self.tags if value not in lemmaDic[key]]

        return lemmaDic




if __name__ == '__main__':


    text = "Hans geht in die Schule. Dort gibt es Bäume. Dieser Baum ist aber etwas Besonderes."

    conversion = ConLL12Converter(text, 'data')

    print(conversion.lemmaDic)
