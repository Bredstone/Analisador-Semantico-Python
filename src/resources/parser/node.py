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

class Node:
  def __init__(self, symbol, lexeme, parent, derived_from, derives, is_terminal, line = 0, pos = 0):
    self._symbol = symbol
    self.parent = parent
    self.children = []
    self._lexeme = lexeme
    self.line = line
    self.pos = pos
    self._is_terminal = is_terminal
    self.attributes = dict()
    self.attributes["is_loop"] = False
    self.attributes["lexeme"] = self.lexeme()
    self._derived_from = derived_from
    self._derives = derives
    if parent:
      self.parent.children.append(self)

  def produces(self):
    if(self.is_terminal()):
      return None
    else:
      products = ""
      for product in self.children:
        products = products + product._symbol + " "

      products = products.strip()

      return self._symbol + " -> " + products

  def derives(self):
    return self._derives

  def derived_from(self):
    return self._derived_from

  def symbol_index(self):
    return self.parent.children.index(self)

  def do_after(self):
    if(self.derived_from() != None):
      return self.derived_from().do_when(self.symbol_index() + 1)
    return None

  def is_last(self):
    if(self.derived_from() != None):
      if(self.symbol_index() == (len(self.derived_from().products()) - 1)):
        return True
    return False

  def do_before(self):
    if(self.derived_from() != None):
        return self.derived_from().do_when(self.symbol_index())
    return None

  def symbol(self):
    return self._symbol

  def lexeme(self):
    return self._lexeme

  def is_terminal(self):
    return self._is_terminal

  def get_global_variable(self, variable):
    return self.global_variables[variable]

  def sibling(self,symbol, index):
    i = 0
    if(self.parent != None):
      if (self.parent.symbol() == symbol):
        i += 1

    for sibling_node in self.parent.children:
      if(sibling_node.symbol() == symbol):
        if(i == index):
          return sibling_node
        i += 1
    return None

  def set_global_variable(self, variable, value):
    self.global_variables[variable] = value

