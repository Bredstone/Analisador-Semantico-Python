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

import resources.lexical_analyzer.ply.lex as lex
from resources.lexical_analyzer.symtable import LexemeTable

class LexicalException(Exception):
  def __init__(self, symbol, lineno, pos):
    self.args = (f"Símbolo inesperado {symbol} na posição {pos}, linha {lineno}", )
    self.symbol = symbol
    self.line = lineno
    self.pos = pos

class LexicalAnalyzer:
  def __init__(self):
    self.token_regex = []
    self.literals = None
    self.ignore = None
    self.lexeme_table = None
    self.lexer = None
    self.ident = None

  global t_newline
  global t_error

  def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

  def t_error(t):
    pass

  def token_creator(self):
    global literals
    global tokens
    global t_ignore

    if(self.literals != None):
        literals = self.literals
    if(self.ignore != None):
        t_ignore = self.ignore

    token_list = [token for (token, regex) in self.token_regex]

    tokens = tuple(token_list)

    for (token, regex)  in self.token_regex:
      regex_func='def t_'+token+'(token):\n\tr\''+regex+'\'\n\treturn token'
      code=compile(regex_func,token,'exec')
      exec(code,globals())

  def input(self, data):
    self.token_creator()
    self.lexer = lex.lex()
    self.lexer.input(data)
    self.lexeme_table = LexemeTable(self.ident)

  def token(self):
    try:
      token = self.lexer.token()
      if token: 
        self.lexeme_table.add_token(token.type, token.value, token.lineno, token.lexpos)
        return self.lexeme_table.last()
      else:
        return None
    except Exception as e:
      raise LexicalException(self.lexer.lexdata[self.lexer.lexpos],self.lexer.lineno, self.lexer.lexpos)

  def destroy(self):
    global tokens
    global literals
    global t_ignore
    for (token, regex)  in self.token_regex:
      del globals()["t_"+token]

    if 'tokens' in globals():
      del tokens
    if 'literals' in globals():
      del literals
    if 't_ignore' in globals():
      del t_ignore

  def line_to_token_regex(line):
    (token_name, regex) = line.split(" ",1)
    return (token_name, regex) 

  def file_to_token_list(self, file_path):
    token_regex = []

    f = open(file_path, "r")
    data = f.read().splitlines()
    token_regex = [LexicalAnalyzer.line_to_token_regex(token) for token in data]
    f.close()

    self.token_regex = token_regex
    literals_filter = list(filter(lambda t: t[0] == "literals", token_regex))
    for lit in literals_filter:
      token_regex.remove(lit)
    if(len(literals_filter) > 0):
      self.literals = literals_filter[0][1]

    idents_filter = list(filter(lambda t: t[0] == "IDENT", token_regex))
    for ident in idents_filter:
      token_regex.remove(ident)

    self.ident = idents_filter[0][1].split(" ")

    ignore_filter = list(filter(lambda t: t[0] == "ignore", token_regex))
    for ign in ignore_filter:
      token_regex.remove(ign)
    if(len(ignore_filter) > 0):
      self.ignore = ignore_filter[0][1]

  def set_token_list(self, token_regex):
    self.destroy()
    self.token_regex = token_regex

  def from_file(self, file_path):
    self.destroy()
    self.file_to_token_list(file_path)