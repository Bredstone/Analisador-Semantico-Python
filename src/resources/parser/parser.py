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

from resources.parser.node import Node
from resources.parser.product import EPSILON
from resources.lexical_analyzer.symtable import Token

class ParsingResult():
  def __init__(self):
    self._stack = []
    self._input = []
    self._rule = []
    self.tree = None
    self.accepted = False
    self.fs = None
    self.unmatched_token = None

  def add_entry(self, _stack, _input, _rule):
    self._stack.append(_stack)
    self._input.append(_input)
    self._rule.append(_rule)

  def check(self):
    try:
      self.accepted = (len(self._stack[-1]) == 1) and (self._stack[0][0] == "$")
      self.accepted = self.accepted and (len(self._input[-1]) == 0)
    except IndexError as e:
      self.accepted = False

    if(self.accepted == False):
      try:
        self.load_error()
      except Exception as e:
        self.fs = None
    else:
      self.fs = None

  def load_error(self):
    self.fs = (self._input[0][:-(len(self._input[-1]))])+list(reversed(self._stack[-1][1:]))
    self.unmatched_token = self._input[-1][0]

class SyntaxException(Exception):
  def __init__(self, symbol, lineno, pos):
    self.args = (f"Símbolo inesperado {symbol} na posição {pos}, linha {lineno}", )
    self.symbol = symbol
    self.line = lineno
    self.pos = pos

class g_set(set):
  def __init__(self):
    super().__init__()

  def add(self,item):
    added = not (item in self)
    super().add(item)
    return added

class Parser():
  def __init__(self, grammar):
    self.grammar = grammar
    self.first_pos = dict()
    self.follow_pos = dict()
    self.parsing_table = dict()

    for non_terminal in self.grammar.non_terminals:
      self.follow_pos[non_terminal] = g_set()
      self.first_pos[non_terminal] = g_set()
      self.parsing_table[non_terminal] = dict()
      
      for terminal in self.grammar.terminals:
        self.parsing_table[non_terminal][terminal] = g_set()
      
      self.parsing_table[non_terminal]["$"] = g_set()
      self.parsing_table[non_terminal]["&"] = g_set()

    self.load_first_pos()
    self.load_follow_pos()
    self.load_parsing_table()

    self.stack = ["$", self.grammar.non_terminals[0]]
    self.result = ParsingResult()
    self.tree = Node("ROOT", None, None, None, None, None)
    self.parents = [self.tree]
    self.epsilon_in_products = False
    self.global_variables = dict()

  def load_first_pos(self):
    collected = True

    while(collected):
      collected = False
      for production in self.grammar.productions:
        if (production.is_epsilon()):
          collected =  collected or self.first_pos[production.head()].add(EPSILON)
        else:
          collected = collected or self.collect_firsts(production)

  def collect_firsts(self, production):
    products = production.products()
    firsts = self.first_pos[production.head()]
    added = False
    epsilon_in_firsts = True

    for symbol in products:
      epsilon_in_firsts = False

      if(symbol in self.grammar.terminals):
        added = added or firsts.add(symbol)
        break

      for first in self.first_pos[symbol]:
        epsilon_in_firsts = epsilon_in_firsts or (first == EPSILON)
        added = added or firsts.add(first)
        
      if(not epsilon_in_firsts):
        break

    if(epsilon_in_firsts):
      added = added or firsts.add(EPSILON)

    return added

  def load_follow_pos(self):
    collected = True

    while(collected):
      collected = False

      first_production = True
      for production in self.grammar.productions:
        head = production.head()
        if(first_production):
          collected = collected or self.follow_pos[head].add("$")
          first_production = False

        for i in range(0,len(production.products())):
          symbol = production.products()[i]

          if symbol in self.grammar.non_terminals:
            after_symbols = production.products()[i+1:]
            after_firsts = self.collect_terminals_and_firsts(after_symbols)

            for first in after_firsts:
              if(first == EPSILON):
                for follow in self.follow_pos[head]:
                  collected = collected or self.follow_pos[symbol].add(follow)
              else:
                collected = collected or self.follow_pos[symbol].add(first)

  def collect_terminals_and_firsts(self, symbols):
    firsts = []

    has_epsilon = True
    for symbol in symbols:
      has_epsilon = False

      if((symbol in self.grammar.terminals) and not (symbol in firsts)):
        firsts.append(symbol)
        break
      
      for first in self.first_pos[symbol]:
        has_epsilon = has_epsilon or first == EPSILON
        if(not (first in firsts)):
          firsts.append(first)

      has_epsilon = has_epsilon or (len(self.first_pos[symbol]) == 0)
      if(not has_epsilon):
        break

    if(has_epsilon):
      if(not (EPSILON in firsts)):
        firsts.append(EPSILON)

    return firsts

  def load_parsing_table(self):
    for production in self.grammar.productions:
      products = production.products().copy()
      if(EPSILON in products):
        products.remove(EPSILON)

      products_firsts = self.collect_terminals_and_firsts(products)
      for symbol in products_firsts:
        if(symbol != EPSILON):
          self.parsing_table[production.head()][symbol].add(production)
        else:
          follows = self.follow_pos[production.head()]
          for follow in follows:
            self.parsing_table[production.head()][follow].add(production)

  def parse(self, token = Token("$","$", 0, 0)):
    symbol = token.token
    lexeme = token.lexeme
    top = self.stack[-1]
    rule = None

    if(self.epsilon_in_products):
      curr_node = Node(EPSILON, EPSILON, self.parents[-1], self.parents[-1].derives(), None, True)
      del self.parents[-1]
      self.epsilon_in_products = False
      return (False, curr_node)

    if(top == symbol):
      del self.stack[-1]
      curr_node = Node(symbol, lexeme, self.parents[-1], self.parents[-1].derives(), None, True, token.line, token.pos)
      del self.parents[-1]

      return (True, curr_node)

    elif(top in self.grammar.non_terminals):
      rule = self.parsing_table[top][symbol]
      if not rule:
        raise SyntaxException(token.token, token.line, token.pos)
      top_node = Node(top, None, self.parents[-1], self.parents[-1].derives(), list(rule)[0], False)
      curr_node = top_node

      del self.parents[-1]
      del self.stack[-1]
      products = list(reversed(list(rule)[0].products()))

      for _ in products:
        self.parents.append(top_node)

      if(not(EPSILON in products)):
        self.stack += products
      else:
        self.epsilon_in_products = True

      return (False, curr_node)
      
    else:
      return (True, None)