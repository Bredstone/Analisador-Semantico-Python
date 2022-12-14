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

from texttable import Texttable

class SemanticException(Exception):
  def __init__(self, symbol, lineno, pos):
    self.args = (f"Símbolo inesperado {symbol} na posição {pos}, linha {lineno}", )
    self.symbol = symbol
    self.line = lineno
    self.pos = pos

class NoLoopBreakException(SemanticException):
  def __init__(self, lineno, pos):
    super().__init__("break", lineno, pos)
    self.args = (f"Quebra de loop (break) inesperado na posição {pos}, linha {lineno}", )

class RedeclarationException(SemanticException):
  def __init__(self, symbol, lineno, pos, last_lineno, last_pos):
    super().__init__(symbol, lineno, pos)
    self.args = (f"Declaração de {symbol} duplicado, na posição {pos}, linha {lineno} - Já declarado na posição {last_pos}, linha {last_lineno}", )

class IncompatibleOperandsException(SemanticException):
  def __init__(self, next_lexeme, lineno, pos):
    super().__init__(next_lexeme, lineno, pos)
    self.args = (f"Operandos com tipos incompatíveis na posição {pos}, linha {lineno}", )

class SymTable:
  def __init__(self, node, parent, is_loop):
    if(node == None):
      self.lexeme = "GLOBAL"
      self.line = 0
      self.pos = 0
    else:
      self.lexeme = node.lexeme()
      self.line = node.line
      self.pos = node.pos

    self.parent = parent
    self.children = []

    if(self.parent != None):
      self.parent.children.append(self)

    self.is_loop = is_loop
    self.symbols = list()

  def get_type(self, lexeme):
    for symbol in self.symbols:
      if(symbol[1] == lexeme):
        return symbol[4]
    return None

  def add_func(self, node, param_count):
    self.assert_unique(node)
    self.symbols.append([node.symbol(), node.lexeme(), node.line, node.pos, "function", param_count])

  def add_var(self, var_type, node):
    self.assert_unique(node)
    self.symbols.append([node.symbol(), node.lexeme(), node.line, node.pos, var_type, 0])

  def assert_unique(self, node):
    for symbol in self.symbols:
      if(node.lexeme() == symbol[1]):
        raise RedeclarationException(node.symbol(), node.line, node.pos, symbol[2], symbol[3])

  def to_text(self):
    table = Texttable()
    rows = [["TOKEN", "VALOR", "LINHA", "POSIÇÃO", "TIPO", "Nº PARÂMETROS"]] + self.symbols
    table.add_rows(rows)
    inicio = f"Início: (Valor = {self.lexeme}, Linha = {self.line}, Posição = {self.pos})"
    parent = self.parent
    parent = f"Pai Imediato: (Valor = {parent.lexeme}, Linha = {parent.line}, Posição = {parent.pos}]"
    return inicio+"\n"+parent+"\n"+table.draw()

  def is_empty(self):
    return len(self.symbols)==0

class ExpressionNode:
  def __init__(self, value, value_type, left, right):
    self.value = value
    self.value_type = value_type
    self.signal = None
    self.children = []
    self.parent = None
    if(left != None):
      self.children.append(left)
      left.parent = self
    if(right != None):
      self.children.append(right)
      right.parent = self

  def set_signal(self, signal):
    self.signal = signal

class SemanticAnalyzer:
  def __init__(self):
    pass

  def get_symbol_table(self):
    global curr_table
    table = curr_table
    while(table.parent != None):
      table = table.parent

    return table

  def put(self,node):
    if(not (node.do_before() is None)):
      self.do(node, node.do_before())

    if(node.is_last() and node.is_terminal()):
      if(not (node.do_after() is None)):
        self.do(node, node.do_after())

      parent = node.parent
      while(parent.is_last()):
        if(not (parent.do_after() is None)):
          self.do(parent, parent.do_after())

        parent = parent.parent

  def do(self, node, commands):
    if(commands != None):
      command = ""
      for symbol in commands.split(" "):
        if(symbol.startswith("#") and symbol.endswith("#")):
          symbol_attribute = symbol[1:-1]
          attribute = None
          if(len(symbol_attribute.split(".")) > 1):
            (symbol, attribute) = symbol_attribute.split(".")
          else:
            symbol = symbol_attribute

          (symbol,index) = symbol.rsplit("_",1)
          index = int(index)
          target = None
          if(symbol == node.derived_from().head() and index == 0):
            target = "node.parent"
          else:
            target = "node.sibling(\""+symbol+"\","+str(index)+")"

          if(attribute != None):
            symbol = target+".attributes[\""+ attribute +"\"]"
          else:
            symbol = target

        command = command + symbol + " "
      exec(command)

curr_table = None

def scope(node = None, is_loop = False):
  global curr_table
  curr_table = SymTable(node, curr_table, is_loop)

def unscope():
  global curr_table
  curr_table = curr_table.parent


def add_func(node, param_count):
  curr_table.add_func(node, param_count)

def add_var(var_type, node):
  curr_table.add_var(var_type, node)

def assertLoop(node):
  global curr_table
  table = curr_table 
  while(table != None):
    if(table.is_loop):
      return True
    table = table.parent

  raise NoLoopBreakException(node.line, node.pos)

def get_ident_type(lexeme):
  global curr_table
  table = curr_table

  while(table != None):
    ident_type = table.get_type(lexeme)
    if(ident_type != None):
      return ident_type

    table = table.parent

  return None


def exp_node(value, value_type, left=None, right=None, indexes=None):
  return ExpressionNode(value, value_type, left, right)

def exp_ptree(tree, indent_width=1):
  def _exp_ptree(start, parent, tree, grandpa=None, indent=""):
    if parent != start:
      if parent.parent is None:
        if(parent.signal != None):
          print(" "+str(parent.signal) +str(parent.value), end="")
        else:
          print(" "+str(parent.value), end="")
      else:
        if(parent.signal != None):
          print(" "+str(parent.signal) +str(parent.value))
        else:
          print(" "+str(parent.value))

    if parent == None:
      return
    if(len(parent.children)>0):
      for child in parent.children[:-1]:
        print(indent + "├" + "─" * indent_width, end="")
        _exp_ptree(start, child, tree, parent, indent + "│" + " " * 4)
          
      child = parent.children[-1]
      print(indent + "└" + "─" * indent_width, end="")
      _exp_ptree(start, child, tree, parent, indent + " " * 5)
  
  if(tree.signal != None):
    print(str(tree.signal) +str(tree.value))
  else:
    print(str(tree.value))

  _exp_ptree(tree, tree, tree)

def set_signal(exp_node, signal):
  exp_node.set_signal(signal)

def append(atribute, value):
  atribute.append(value)

def assert_expression(exp_root, terminal_associated=None):
  stack = [exp_root]

  value_type = None
  while(len(stack)>0):
    node = stack.pop()
    if(node.value_type == "op"):
      for child in node.children:
        stack.append(child)
    else:
      if(value_type == None):
        value_type = node.value_type
      else:
        if(value_type != node.value_type):
          raise IncompatibleOperandsException(terminal_associated.lexeme(), terminal_associated.line, terminal_associated.pos)

  print()
  print(f"Árvore de expressão, a seguir de '{terminal_associated.lexeme()}' (linha {terminal_associated.line}, posição {terminal_associated.pos})")
  exp_ptree(exp_root)