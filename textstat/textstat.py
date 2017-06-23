# -*- coding: utf-8 -*-
from __future__ import print_function

import pkg_resources
import string
import re
import math
import operator


class TextStats(object):

    exclude = list(string.punctuation)
    easy_word_set = set([ln.strip() for ln in pkg_resources.resource_stream('textstat', 'easy_words.txt')])

    def __init__(self, text, ignore_spaces=True, rem_punct=True):
        self.text = text
        self.ignore_spaces = ignore_spaces
        self.rem_punct = rem_punct
        self.chars = self._char_count()
        if self.chars == 0:
            raise Exception('Character count is zero')
        self.lex = self._lexicon_count(self.text)
        if self.lex == 0:
            raise Exception('Word count is zero')
        self.syl = self._syllable_count(self.text)
        self.sent_count = self._sentence_count()
        if self.sent_count == 0:
            raise Exception('Sentence count is zero')
        self.asl = self._avg_sentence_length()
        self.aspw = self._avg_sentence_per_word()
        self.alpw = self._avg_letter_per_word()
        self.aspw = self._avg_sentence_per_word()
        self.diff_words = self.difficult_words()

    def _char_count(self):
        """
        Function to return total character counts in a text, pass the following parameter
        ignore_spaces = False
        to ignore whitespaces
        """
        if self.ignore_spaces:
            return len(self.text.replace(" ", ""))
        return len(self.text)

    def _lexicon_count(self, text):
        """
        Function to return total lexicon (words in lay terms) counts in a text
        """
        if self.rem_punct:
            text = ''.join(ch for ch in text if ch not in self.exclude)
            return len(text.split())
        return len(text.split())

    def _syllable_count(self, text):
        """
        Function to calculate syllable words in a text.
        I/P - a text
        O/P - number of syllable words
        """
        count = 0
        vowels = 'aeiouy'
        text = text.lower()
        text = ''.join(ch for ch in text if ch not in self.exclude)

        if text is None:
            return 0
        elif len(text) == 0:
            return 0
        else:
            if text[0] in vowels:
                count += 1
            for index in range(1, len(text)):
                if text[index] in vowels and text[index-1] not in vowels:
                    count += 1
            if text.endswith('e'):
                count -= 1
            if text.endswith('le'):
                count += 1
            if count == 0:
                count += 1
            return count - (0.1*count)

    def _sentence_count(self):
        """
        Sentence count of a text
        """
        ignoreCount = 0
        sentences = re.split(r' *[\.\?!][\'"\)\]]* *', self.text)
        for sentence in sentences:
            if self._lexicon_count(sentence) <= 2:
                ignoreCount = ignoreCount + 1
        return max(1, len(sentences) - ignoreCount)

    def _avg_sentence_length(self):
        ASL = float(self.lex/self.sent_count)
        return round(ASL, 1)

    def _avg_syllables_per_word(self):
        ASPW = float(self.syl)/float(self.lex)
        return round(ASPW, 1)

    def _avg_letter_per_word(self):
        ALPW = float(float(self.chars)/float(self.lex))
        return round(ALPW, 2)

    def _avg_sentence_per_word(self):
        ASPW = float(float(self.sent_count)/float(self.lex))
        return round(ASPW, 2)

    def _poly_syllable_count(self):
        count = 0
        for word in self.text.split():
            wrds = self._syllable_count(word)
            if wrds >= 3:
                count += 1
        return count

    # actual metrics

    def flesch_reading_ease(self):
        FRE = 206.835 - float(1.015 * self.asl) - float(84.6 * self.aspw)
        return round(FRE, 2)

    def flesch_kincaid_grade(self):
        FKRA = float(0.39 * self.asl) + float(11.8 * self.aspw) - 15.59
        return round(FKRA, 1)

    def smog_index(self):
        if self.sent_count >= 3:
            poly_syllab = self._poly_syllable_count()
            SMOG = (1.043 * (30*(poly_syllab/self.sent_count))**.5) + 3.1291
            return round(SMOG, 1)
        return 0

    def coleman_liau_index(self):
        L = round(self.alpw*100, 2)
        S = round(self.aspw*100, 2)
        CLI = float((0.058 * L) - (0.296 * S) - 15.8)
        return round(CLI, 2)

    def automated_readability_index(self):
        a = (float(self.chars)/float(self.lex))
        b = (float(self.lex)/float(self.sent_count))
        ARI = (4.71 * round(a, 2)) + (0.5*round(b, 2)) - 21.43
        return round(ARI, 1)

    def linsear_write_formula(self):
        easy_word = []
        difficult_word = []
        text_list = self.text.split()

        Number = 0
        for i, value in enumerate(text_list):
            if i <= 101:
                syl_count = self._syllable_count(value)
                if syl_count < 3:
                    easy_word.append(value)
                elif syl_count > 3:
                    difficult_word.append(value)
                text = ' '.join(text_list[:100])
                Number = float((len(easy_word)*1 + len(difficult_word)*3)/self.sent_count)
                if Number > 20:
                    Number /= 2
                else:
                    Number = (Number-2)/2
        return float(Number)

    def difficult_words(self):
        text_list = self.text.split()
        diff_words_set = set()
        for value in text_list:
            if value not in self.easy_word_set:
                if self._syllable_count(value) > 1:
                    if value not in diff_words_set:
                        diff_words_set.add(value)
        return len(diff_words_set)

    def dale_chall_readability_score(self):
        word_count = self.lex
        count = word_count - self.diff_words
        per = float(count)/float(word_count)*100

        difficult_words = 100-per
        if difficult_words > 5:
            score = (0.1579 * difficult_words) + (0.0496 * self.asl) + 3.6365
        else:
            score = (0.1579 * difficult_words) + (0.0496 * self.asl)
        return round(score, 2)

    def gunning_fog(self):
        per_diff_words = (self.diff_words/self.lex*100) + 5
        grade = 0.4*(self.asl + per_diff_words)
        return grade

    def lix(self):
    	words = self.text.split()
    	words_len = len(words)
    	long_words = len([wrd for wrd in words if len(wrd)>6])
    	per_long_words = (float(long_words) * 100)/words_len
    	return self.asl + per_long_words

    def text_standard(self, output='str'):
        grade = []

        # Appending Flesch Kincaid Grade
        lower = round(self.flesch_kincaid_grade())
        upper = math.ceil(self.flesch_kincaid_grade())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Flesch Reading Easy
        score = self.flesch_reading_ease()
        if score < 100 and score >= 90:
            grade.append(5)
        elif score < 90 and score >= 80:
            grade.append(6)
        elif score < 80 and score >= 70:
            grade.append(7)
        elif score < 70 and score >= 60:
            grade.append(8)
            grade.append(9)
        elif score < 60 and score >= 50:
            grade.append(10)
        elif score < 50 and score >= 40:
            grade.append(11)
        elif score < 40 and score >= 30:
            grade.append(12)
        else:
            grade.append(13)

        # Appending SMOG Index
        lower = round(self.smog_index())
        upper = math.ceil(self.smog_index())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Coleman_Liau_Index
        lower = round(self.coleman_liau_index())
        upper = math.ceil(self.coleman_liau_index())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Automated_Readability_Index
        lower = round(self.automated_readability_index())
        upper = math.ceil(self.automated_readability_index())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Dale_Chall_Readability_Score
        lower = round(self.dale_chall_readability_score())
        upper = math.ceil(self.dale_chall_readability_score())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Linsear_Write_Formula
        lower = round(self.linsear_write_formula())
        upper = math.ceil(self.linsear_write_formula())
        grade.append(int(lower))
        grade.append(int(upper))

        # Appending Gunning Fog Index
        lower = round(self.gunning_fog())
        upper = math.ceil(self.gunning_fog())
        grade.append(int(lower))
        grade.append(int(upper))

        # Finding the Readability Consensus based upon all the above tests
        d = dict([(x, grade.count(x)) for x in grade])
        sorted_x = sorted(d.items(), key=operator.itemgetter(1))
        final_grade = str((sorted_x)[len(sorted_x)-1])
        score = final_grade.split(',')[0].strip('(')
        if output.lower() == 'str':
            return str(int(score)-1) + "th " + "and " + str(int(score)) + "th grade"
        else:
            return (int(score)-1, int(score))
