#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador Semântico.

Projeto de um analisador semântico, desenvolvido em Python; em conjunto com um 
analisador sitático e um analisador léxico construído com auxílio da 
ferramenta PLY (módulo LEX).

@Author: Brendon Vicente Rocha Silva
@Email: bredstone13@gmail.com
@Date: December - 2022
"""

EPSILON = "&"

class Product():
	def __init__(self, head, products):
		self._head = head
		self._products = products
		self._actions = dict()

	def add_action(self, when, action_code):
		self._actions[when] = action_code

	def do_when(self, when):
		if(when in self._actions.keys()):
			return self._actions[when]
		else:
			return None

	def head(self):
		return self._head

	def products(self):
		return self._products

	def is_epsilon(self):
		if(len(self._products) == 1):
			if(self._products[0] == EPSILON):
				return True
		return False

	def is_direct_left_recursive(self):
		return self._products[0] == self._head

	def __str__(self):
		return str(self.__key())

	def __eq__(self, other):
		if(other != None):
			if(isinstance(other, Product)):
				return self.__key() == other.__key()
		return False

	def __ne__(self, other):
		return not(self == other)

	def __key(self):
		return (self._head, tuple(list(self._products)))

	def __hash__(self):
		return hash(self.__key())

	def __str__(self):
		string = self._head + " ->"
		for product in self._products:
			string += " "+product
		return string