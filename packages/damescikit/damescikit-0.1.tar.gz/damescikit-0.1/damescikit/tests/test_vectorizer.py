#  Copyright (C) 2020 David Arroyo Menéndez

#  Author: David Arroyo Menéndez <davidam@gmail.com>
#  Maintainer: David Arroyo Menéndez <davidam@gmail.com>
#  This file is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3, or (at your option)
#  any later version.
#
#  This file is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with damescikit; see the file LICENSE.  If not, write to
#  the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#  Boston, MA 02110-1301 USA,


import unittest
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from numpy import array
from scipy.sparse import csr_matrix
from pprint import pprint


class TddInPythonExample(unittest.TestCase):

    def test_vectorizer_method_returns_correct_result(self):
        # this test allows create the vector with the words of the text
        corpus = [
            'This is the first document.',
            'This document is the second document.',
            'And this is the third one.',
            'Is this the first document?',
        ]
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpus)
        self.assertEqual(['and', 'document', 'first', 'is',
                          'one', 'second', 'the', 'third', 'this'],
                         vectorizer.get_feature_names())

    def test_vectorizer2_method_returns_correct_result(self):
        # this test allows create the dictionary with the words of the text
        # list of text documents
        text = ["The quick brown fox jumped over the lazy dog."]
        # create the transform
        vectorizer = CountVectorizer()
        # tokenize and build vocab
        vectorizer.fit(text)
        # summarize: the word and the position in the array
        self.assertEqual({'the': 7, 'quick': 6, 'brown': 0,
                          'fox': 2, 'jumped': 3, 'over': 5,
                          'lazy': 4, 'dog': 1}, vectorizer.vocabulary_)
