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

from resources.parser.product import Product, EPSILON

class Grammar():
  def __init__(self, grammar):
    self.alphabet = set()
    self.terminals = set()
    self.non_terminals = []
    self.productions = []
    self.actions = dict()

    lines = grammar.split("\n")

    for line in lines:
      productions = line.split("->")
      if(len(productions) != 2):
        continue

      head = productions[0].strip()
      tail = productions[1].split()

      self.alphabet.add(head)
      if(not(head in self.non_terminals)):
        self.non_terminals.append(head)

      action = False
      symbols_tail = list()
      for symbol in tail:
        if(symbol == "§"):
          action = not action
        if(not action and symbol != "§"):
          symbols_tail.append(symbol)

      production = Product(head, symbols_tail)
      self.productions.append(production)

      for symbol in symbols_tail:
        if(symbol != EPSILON):
          self.alphabet.add(symbol)

      action = False
      action_code = ""
      i = 0
      for symbol in tail:
        if(symbol == "§"):
          if(action):
            production.add_action(i, action_code)
          action = not action
          action_code = ""
        elif(action):
          symbol = symbol.strip()
          action_code =  action_code + symbol + " "
        else:
          i+=1

    self.terminals = self.alphabet - set(self.non_terminals)

  def get_productions(self, non_terminal):
    return [production for production in self.productions if production.head == non_terminal]
  
  def find_direct_left_recursion(self,productions):
    for production in productions:
      if(production.is_direct_left_recursive()):
        return production
    return None

  def remove_direct_left_recursion(self, non_terminal):
    productions = self.get_productions(non_terminal)

    left_recursion = self.find_direct_left_recursion(productions)

    if(left_recursion != None):
      self.productions.remove(left_recursion)

      for production in productions:
        production.products.append(production.head+"'")

      left_recursion.head += "'"
      left_recursion.products = left_recursion.products[1:]

      left_recursion_epsilon = Product(left_recursion.head, EPSILON)

      self.productions.append(left_recursion)
      self.productions.append(left_recursion_epsilon)
      self.non_terminals.append(left_recursion.head)

      return True

    return False


  def remove_left_recusion(self):
    left_recursion_found = False

    for i in range(len(self.non_terminals)):
      a_i = self.non_terminals[i]
      for j in range(i):
        a_j = self.non_terminals[j]

        for a_i_production in self.get_productions(a_i):
          if(a_i_production.products[0] == a_j):
            self.productions.remove(a_i_production)
            gamma = a_i_production.products[1:]

            for a_j_production in self.get_productions(a_j):
              delta = a_j_production.products
              self.productions.append(Product(a_i, delta + gamma))
        left_recursion_found = left_recursion_found or self.remove_direct_left_recursion(a_i)

    return left_recursion_found