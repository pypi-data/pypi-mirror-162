/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_XML_SCANNER_LIBFPLIST_XML_PARSER_H_INCLUDED
# define YY_XML_SCANNER_LIBFPLIST_XML_PARSER_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int xml_scanner_debug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    XML_ATTRIBUTE_ASSIGN = 258,    /* XML_ATTRIBUTE_ASSIGN  */
    XML_COMMENT = 259,             /* XML_COMMENT  */
    XML_DOCTYPE = 260,             /* XML_DOCTYPE  */
    XML_PROLOGUE = 261,            /* XML_PROLOGUE  */
    XML_TAG_END = 262,             /* XML_TAG_END  */
    XML_TAG_END_SINGLE = 263,      /* XML_TAG_END_SINGLE  */
    XML_UNDEFINED = 264,           /* XML_UNDEFINED  */
    XML_ATTRIBUTE_NAME = 265,      /* XML_ATTRIBUTE_NAME  */
    XML_ATTRIBUTE_VALUE = 266,     /* XML_ATTRIBUTE_VALUE  */
    XML_TAG_CLOSE = 267,           /* XML_TAG_CLOSE  */
    XML_TAG_CONTENT = 268,         /* XML_TAG_CONTENT  */
    XML_TAG_OPEN_START = 269       /* XML_TAG_OPEN_START  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif
/* Token kinds.  */
#define YYEMPTY -2
#define YYEOF 0
#define YYerror 256
#define YYUNDEF 257
#define XML_ATTRIBUTE_ASSIGN 258
#define XML_COMMENT 259
#define XML_DOCTYPE 260
#define XML_PROLOGUE 261
#define XML_TAG_END 262
#define XML_TAG_END_SINGLE 263
#define XML_UNDEFINED 264
#define XML_ATTRIBUTE_NAME 265
#define XML_ATTRIBUTE_VALUE 266
#define XML_TAG_CLOSE 267
#define XML_TAG_CONTENT 268
#define XML_TAG_OPEN_START 269

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{

        /* The numeric value
         */
        uint32_t numeric_value;

        /* The string value
         */
	struct xml_plist_string_value
	{
		/* The string data
		 */
	        const char *data;

		/* The string length
		 */
		size_t length;

	} string_value;


};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE xml_scanner_lval;


int xml_scanner_parse (void *parser_state);


#endif /* !YY_XML_SCANNER_LIBFPLIST_XML_PARSER_H_INCLUDED  */
