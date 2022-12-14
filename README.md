# **Analisador Semântico - *Python***
Autor: Brendon Vicente Rocha Silva | [LinkedIn][1]
<br />
<br />

## **Introdução**
- Projeto de um analisador semântico, desenvolvido em *Python*;
- O programa foi feito em conjunto com um analisador sintático e um analisador 
léxico, desenvolvido com a utilização da ferramenta *PLY* (módulo *LEX*).

Um analisador léxico é uma ferramenta capaz de converter códigos em *tokens*.
O analisador léxico lê um programa de entrada e gera um fluxo de *tokens*.

O Analisador sintático, também conhecido como *parser*, tem como tarefa 
principal determinar se o programa de entrada, representado pelo fluxo de 
*tokens*, possui as sentenças válidas para a linguagem de programação.

Análise semântica é um processo no qual são verificados os erros semânticos no 
código fonte e coletadas as informações necessárias para a próxima fase da 
compilação, que é a geração de código objeto.

<br />

**Para o projeto em questão, a linguagem empregada foi a *LCC-2022-2*.**
<br />
<br />

### ***CC-2022-2***
Abaixo encontra-se a gramática *CC-2022-2* na forma BNF:

```
PROGRAM         → (STATEMENT | FUNCLIST)?
FUNCLIST        → FUNCDEF FUNCLIST | FUNCDEF
FUNCDEF         → def ident (PARAMLIST) { STATELIST }
PARAMLIST       → ((int | float | string) ident, PARAMLIST)?
STATEMENT       → (VARDECL;    |
                   ATRIBSTAT;  |
                   PRINTSTAT;  |
                   READSTAT;   |
                   RETURNSTAT; |
                   IFSTAT;     |
                   FORSTAT     |
                   {STATELIST} |
                   break;      |
                   FUNCCALL;   |
                   ;)
VARDECL         → (int | float | string) ident ([int constant])*
ATRIBSTAT       → LVALUE = (EXPRESSION | ALLOCEXPRESSION | FUNCCALL)
FUNCCALL        → invoke ident(PARAMLISTCALL)
PARAMLISTCALL   → (ident, PARAMLISTCALL | ident | FACTOR)?
PRINTSTAT       → print EXPRESSION
READSTAT        → read LVALUE
RETURNSTAT      → return
IFSTAT          → if(EXPRESSION) STATEMENT (else STATEMENT)? endif
FORSTAT         → for(ATRIBSTAT; EXPRESSION; ATRIBSTAT)
                    STATEMENT
STATELIST       → STATEMENT (STATELIST)?
ALLOCEXPRESSION → new (int | float | string) ([NUMEXPRESSION])+
EXPRESSION      → NUMEXPRESSION ((< | > | <= | >= | == | !=) NUMEXPRESSION)?
NUMEXPRESSION   → TERM ((+ | −) TERM)∗
TERM            → UNARYEXPR((∗ | / | %) UNARYEXPR)∗
UNARYEXPR       → ((+ | −))? FACTOR
FACTOR          → (int_constant | float_constant | string_constant | null | LVALUE | (NUMEXPRESSION))
LVALUE          → ident([NUMEXPRESSION])
```
<br />
<br />

### ***ConvCC-2022-2***
Para execução do código, foi necessário a conversão da gramática para a **forma convencional**:

```
PROGRAM         -> STATEMENT | FUNCLIST | &
FUNCLIST        -> FUNCDEF FUNCLIST | FUNCDEF
FUNCDEF         -> def ident ( PARAMLIST ) { STATELIST }
PARAMLIST       -> & | TYPE ident , PARAMLIST | TYPE ident
TYPE            -> int | float | string
STATEMENT       -> VARDECL ; | ATRIBSTAT ; | PRINTSTAT ; | READSTAT ; | RETURNSTAT ; | IFSTAT ; | FORSTAT | { STATELIST } | break ; | FUNCCALL ; | ;
VARDECL         -> TYPE ident INT_INDEX
INT_INDEX       -> [ int_constant ] INT_INDEX | &
ATRIBSTAT       -> LVALUE = ATRIBSTAT'
ATRIBSTAT'      -> EXPRESSION | ALLOCEXPRESSION
FUNCCALL        -> invoke ident ( PARAMLISTCALL )
PARAMLISTCALL   -> ident , PARAMLISTCALL | ident | FACTOR | &
PRINTSTAT       -> print EXPRESSION
READSTAT        -> read LVALUE
RETURNSTAT      -> return
IFSTAT          -> if ( EXPRESSION ) STATEMENT IFSTAT'
IFSTAT'         -> endif | else STATEMENT endif
FORSTAT         -> for ( ATRIBSTAT ; EXPRESSION ; ATRIBSTAT ) STATEMENT
STATELIST       -> STATEMENT STATELIST'
STATELIST'      -> & | STATELIST
ALLOCEXPRESSION -> new TYPE ALLOC_SIZE
ALLOC_SIZE      -> [ NUMEXPRESSION ] ALLOC_SIZE'
ALLOC_SIZE'     -> ALLOC_SIZE | &
EXPRESSION      -> NUMEXPRESSION EXPRESSION'
EXPRESSION'     -> & | RELOP NUMEXPRESSION
RELOP           -> < | > | < OREQ | > OREQ | = = | ! =
OREQ            -> = | &
NUMEXPRESSION   -> TERM NUMEXPRESSION'
NUMEXPRESSION'  -> SUM TERM NUMEXPRESSION' | &
SUM             -> + | -
TERM            -> UNARYEXPR TERM'
TERM'           -> & | MULTI UNARYEXPR TERM'
MULTI           -> * | / | %
UNARYEXPR       -> SUM FACTOR | FACTOR
FACTOR          -> int_constant | float_constant | string_constant | null | LVALUE | ( NUMEXPRESSION )
LVALUE          -> ident NUM_INDEX
NUM_INDEX       -> [ NUMEXPRESSION ] NUM_INDEX | &
```
<br />
<br />

### ***Tokens* utilizados**
Um *token* é um segmento de texto ou símbolo que pode ser manipulado por um 
analisador sintático, que fornece um significado ao texto.

Dentro da linguagem *LCC-2022-2*, foram utilizados os seguintes:
<br />
<br />

**Palavras Reservadas**
- def  
- int  
- float
- string
- break
- print
- read 
- return
- if
- else
- endif
- for  
- new  
- null
- invoke
<br />
<br />

***Tokens* Literais**
- `( ) { } [ ] = < > ! + - * / % , ;`
<br />
<br />

***Tokens* não triviais**
- int_constant (`[\+-]?[0-9]+(E[\+-]?[0-9]+)?`)
  - *Strings* formadas por um ou mais algarismos, podendo conter sinal ou 
  indicador de exponencial (caractere *E*) | **Ex:** -1234E+123
- float_constant (`[\+-]?[0-9]+\.[0-9]+(E[\+-]?[0-9]+(\.[0-9]+)?)?`)
  - *Strings* formadas por um ou mais algarismos, com separador decimal 
  (caractere *.*), podendo conter sinal ou indicador de exponencial
  (caractere *E*) | **Ex:** -1.234E+1.23
- string_constant (`(".*"|\'.*\')`)
  - *Strings* quaisquer, cercadas por aspas ou aspas duplas (incluindo strings 
  vazias) | **Ex:** 'teste'
- ident (`[a-zA-Z_][a-zA-Z_0-9]*`)
  - *Strings* iniciadas por uma letra (de A à Z, ignorando capitalização) 
  ou *underline* (caractere *_*), seguido por *N* letras, números ou 
  underlines | **Ex:** multiplicar_matrizes
<br />
<br />

## Execução
### Entrada e Saída de Dados
Deve ser fornecido o caminho de um arquivo no formato *.lcc* escrito na linguagem
*LCC-2022-2* derivada por *CC-2022-2*.

As seguintes saídas são esperadas:
- **se não houver erros léxicos, sintáticos ou semânticos -** árvores de 
expressões aritméticas, tabelas de símbolos e mensagens indicando que a 
entrada é válida;
- **se houver erros léxicos -** uma mensagem simples de erro léxico indicando a 
posição léxica e a linha do arquivo de entrada onde ele ocorre;
- **se houver erros sintáticos -** uma mensagem simples de erro sintático 
indicando a posição léxica e a linha do arquivo de entrada onde ele ocorre;
- **se houver erros semânticos -** uma mensagem de erro semântico, indicando 
qual o erro encontrado, assim como sua posição léxica e a linha do arquivo 
de entrada onde ele ocorre;
<br />
<br />

### *Makefile*
Para executar o programa, através do *Makefile*, execute:
```
make run INPUT_FILE
```

- **INPUT_FILE -** deve ser o arquivo de entrada do programa, contendo o código 
fonte a ser analisado, em linguagem *LC-2022-2*;
<br />
<br />

### Executando da Fonte
Para executar o programa, através do código fonte, execute:
```
pip install -r requirements.txt
python src/main.py INPUT_FILE
```

As mesmas regras se mantêm para **INPUT_FILE**.

[1]: https://www.linkedin.com/in/brendon-vicente-rocha/