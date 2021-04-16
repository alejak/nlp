/* casio.c is a calculator with the operations + - * / ^.
   The syntax is analyzed using a recursive descent parser.
   Viggo Kann viggo@nada.kth.se */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>

typedef enum /* tokens (terminals) */
{
  START, ERROR, NUMBERSYM, ENDSYM,
  ADDSYM = '+', MINUSSYM = '-',
  MULSYM = '*', DIVSYM = '/',
  EXPSYM = '^', PRINTSYM = ';',
  LEFTPARSYM = '(', RIGHTPARSYM = ')'
} TokenValue;

/* next token in the input */
TokenValue nextToken;

/* semantic value of NUMBERSYM */
double numberValue;

double error(char *s)
{
  fprintf(stderr, "%s\n", s);
  return(0.0);
}

/* Match checks that token matches the
   input and reads a new nextToken */
TokenValue Match(TokenValue token)
{ int ch;
  if (token != nextToken && token != START) {
    error("Wrong symbol.\n");
    return ERROR;
  }
  while (1) {
    ch = getchar();
    if (isdigit(ch) || ch == '.') {
      ungetc(ch, stdin);
      if (scanf("%lf", &numberValue) == 1) return (nextToken = NUMBERSYM);
      else ch = getchar();
    }
    switch (ch) {
     case EOF: return (nextToken = ENDSYM);
     case '\t':
     case ' ': break;
     case '\n':return (nextToken = PRINTSYM);
     case '^': return (nextToken = EXPSYM);
     case '*': return (nextToken = MULSYM);
     case '/': return (nextToken = DIVSYM);
     case '+': return (nextToken = ADDSYM);
     case '-': return (nextToken = MINUSSYM);
     case '(': return (nextToken = LEFTPARSYM);
     case ')': return (nextToken = RIGHTPARSYM);
     default:  fprintf(stderr, "Illegal character: %c\n", ch);
    }
  }
}

/* methods for nonterminals follows */
double prim(void);
double fact(void);
double term(void);
double expr(void);
void start(void);

double prim(void)
{ double e;
  switch (nextToken) {
   case NUMBERSYM:
    Match(NUMBERSYM);
    return numberValue;
   case MINUSSYM:
    Match(MINUSSYM);
    return -prim();
   case LEFTPARSYM:
    Match(LEFTPARSYM);
    e = expr();
    if (nextToken != RIGHTPARSYM) return error(") expected.");
    Match(RIGHTPARSYM);
    return e;
   default:
    return error("A factor was expected.");
  }
}

double fact(void)
{ double left = prim();
  if (nextToken != EXPSYM) return left;
  Match(EXPSYM);
  return pow(left, fact());
}

double term(void)
{ double d, left = fact();
  while (1)
    switch (nextToken) {
     case MULSYM:
      Match(MULSYM);
      left *= fact();
      break;
     case DIVSYM:
      Match(DIVSYM);
      d = fact();
      if (d == 0) return error("Division by 0.");
      left /= d;
      break;
     default:
      return left;
    }
}

double expr(void)
{ double left = term();
  while (1)
    switch (nextToken) {
     case ADDSYM:
      Match(ADDSYM);
      left += term();
      break;
     case MINUSSYM:
      Match(MINUSSYM);
      left -= term();
      break;
     default:
      return left;
    }
}

void start(void)
{ double value;
  while (1)
    switch (nextToken) {
     case ENDSYM:
      return;
     case PRINTSYM:
      Match(PRINTSYM);
      break;
     default:
      value = expr();
      if (nextToken != PRINTSYM) {
	error("Only one expression per line!");
	do Match(nextToken); while (nextToken != PRINTSYM);
      }
      printf("%f\n", value);
      Match(PRINTSYM);
    }
}

int main(void)
{ Match(START);
  start();
  return 0;
}
