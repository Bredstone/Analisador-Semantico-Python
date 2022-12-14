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

import sys

from resources.parser.grammar import Grammar
from resources.lexical_analyzer.lexical_analyzer import LexicalAnalyzer, LexicalException
from resources.parser.parser import Parser, SyntaxException
from resources.semantic_analyzer.semantic import SemanticAnalyzer, SemanticException

def p_symbol_tables(symbol_tables):
  if(not symbol_tables.is_empty()):
    print("\n" + symbol_tables.to_text())
  for child in symbol_tables.children:
    p_symbol_tables(child)

def analyze(token_file, grammar_text, data):
  MAX = 1000000
  grammar = Grammar(grammar_text)
  la = LexicalAnalyzer()
  ll1_parser = Parser(grammar)
  sema = SemanticAnalyzer()

  la.from_file(token_file)
  la.input(data)
  while True:
    token = la.token()
    if (not (token is None)):
      i = 0
      while((i < MAX) and (1 < len(ll1_parser.stack))):
        (must_break, node) = ll1_parser.parse(token)

        if(node != None):
          sema.put(node)
        if(must_break):
          break

        i += 1
    else:
      while(len(ll1_parser.parents) > 0):
        (must_break, node) = ll1_parser.parse()
        if(node != None):
          sema.put(node)

      break

  symbol_table = sema.get_symbol_table()

  p_symbol_tables(symbol_table)
  
  print()
  print("Todas as expressões são válidas")
  print("Todas as declarações de variáveis por escopo são válidas")
  print("Toda quebra de loop (break) é válida")

if __name__ == '__main__':
  try:
    if len(sys.argv) != 2:
      raise Exception('Número de argumentos inválido!')

    _, data_file_path = sys.argv

    with open('./src/resources/grammar.txt') as grammar_text:
      with open(data_file_path) as data:
        analyze("./src/resources/tokens.txt", grammar_text.read(), data.read())
  except LexicalException as le:
    print(f"\nErro léxico: {le}")
  except SyntaxException as se:
    print(f"\nErro sintático: {se}")
  except SemanticException as se:
    print(f"\nErro semântico: {se}")
  except Exception as e:
    print(e)