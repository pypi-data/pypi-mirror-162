#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Damescikit; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
import numpy as np
import pickle
import os.path

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import SGDClassifier
from sklearn.kernel_approximation import RBFSampler
from sklearn import svm
from sklearn.svm import SVR
from sklearn.linear_model import Perceptron


class TddInPythonExample(unittest.TestCase):

    def test_models_lda(self):
        X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
        y = np.array([1, 1, 1, 2, 2, 2])
        clf = LinearDiscriminantAnalysis()
        clf.fit(X, y)
        self.assertEqual(clf.predict([[-1, -1]]), 1)

    def test_models_mlp(self):
        X = [[0., 0.], [1., 1.]]
        y = [0, 1]
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(5, 2), random_state=1)

        clf.fit(X, y)
        n = np.array([1, 0])
        self.assertTrue(np.array_equal(clf.predict([[2., 2.], [-1., -2.]]), n))

    def test_models_svc(self):
        X = np.array([[0, 0], [1, 1]])
        y = np.array([0, 1])
        clf = svm.SVC()
        clf.fit(X, y)
        self.assertTrue(np.array_equal(clf.predict(np.array([[0, 0]])),
                                       np.array([0])))

    def test_models_perceptron(self):
        X = np.array([[0, 0], [1, 1]])
        y = np.array([0, 1])
        clf = Perceptron(tol=1e-3, random_state=0)
        clf.fit(X, y)
        self.assertEqual(1.0, clf.score(X, y))

    def test_models_gaussiannb(self):
        # assigning predictor and target variables
        x = np.array([[-3, 7], [1, 5], [1, 2], [-2, 0], [2, 3],
                      [-4, 0], [-1, 1], [1, 1], [-2, 2], [2, 7],
                      [-4, 1], [-2, 7]])
        y = np.array([3, 3, 3, 3, 4, 3, 3, 4, 3, 4, 4, 4])
        # Create a Gaussian Classifier
        model = GaussianNB()
        # Train the model using the training sets
        model.fit(x, y)
        # Predict Output
        predicted = model.predict([[1, 2], [3, 4]])
        self.assertTrue(np.array_equal(predicted, np.array([3, 4])))

    def test_models_bernoullinb(self):
        X = np.random.randint(5, size=(6, 100))
        y = np.array([1, 2, 3, 4, 5, 6])
        clf = BernoulliNB()
        clf.fit(X, y)
        self.assertTrue(np.array_equal([3], clf.predict(X[2:3])))

    def test_models_tree(self):
        from sklearn import tree
        X = [[0, 0], [1, 1]]
        Y = [0, 1]
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(X, Y)
        self.assertTrue(np.array(1), clf.predict([[2., 2.]]))

    def test_models_kernel_approximation(self):
        X = [[0, 0], [1, 1], [1, 0], [0, 1]]
        y = [0, 0, 1, 1]
        rbf_feature = RBFSampler(gamma=1, random_state=1)
        X_features = rbf_feature.fit_transform(X)
        clf = SGDClassifier()
        clf.fit(X_features, y)
        self.assertEqual(clf.score(X_features, y), 1)
