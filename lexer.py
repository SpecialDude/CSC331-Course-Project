#!/usr/bin/env python3

"""
A Lexical Analyzer for python source codes

Author(s): Group 3 CSC 331 Course Project
Lecture-in-charge: Dr Joseph Akinyemi
Session: 2021/2022 Academic Session

"""

import enum
import sys
from io import StringIO


class LexicalAnalysisError(Exception):
    ...


class StateType(enum.Enum):
    START = 0
    INTERMEDIATE = 1
    FINAL = 2

class Token:
    name = ""
    value = ""
    line = 0

class Util:

    @staticmethod
    def is_whitespace(char):
        return char in (" ", "\n", "\t")

    @staticmethod
    def is_number(char):
        if len(char) != 1:
            return False
        return ord('0') <= ord(char) <= ord('9')

    @staticmethod
    def is_alphabet(char):
        return ord('a') <= ord(char) <= ord('z') or \
                ord('Z') <= ord(char) <= ord('Z')

# Definition of States for the Automaton
#   BaseState - Defines some basic properties to be inherited
#   Identifier
#   Literal
#   Indent
#   Dedent
#   Punctuator
#   Operator
#   Comment
#
#   Start
#
#   Member_Access

class BaseState:
    name = ""
    type = StateType.FINAL
    __token = []
    issingleton = False
    hasmiddle = False

    @classmethod
    def transit(cls, char):
        raise NotImplemented

    @classmethod
    def save(cls, token):
        cls.__token.append(token)

class Identifier(BaseState):
    general_name = "IDENTIFIER"
    subset_name = "KEYWORD"

    name = general_name
    is_identifier = False

    @classmethod
    def transit(cls, char):

        global token

        if char == "" or Util.is_whitespace(char):
            # End of the current token, start reading new

            import keyword

            if keyword.iskeyword(token):
                if Operator.is_member(token, True):
                    cls.name = cls.subset_name + "/OPERATOR"
                else:
                    cls.name = cls.subset_name
            else:
                cls.name = cls.general_name
            return Start


        elif char == '.':
            # Member Accessor Operation is expected
            # If next character is invalid error is raised

            return Member_Access

        elif Util.is_number(char):
            # Token is predicted to be an Identifier
            # if it contains any integer char
            cls.is_identifier = True
            return cls

        elif Util.is_alphabet(char):
                # Asci Chars is still being read
                return cls

        else:
            # Invalid token received
            # raise LexicalAnalysisError(f"Unexpected Character({char}) after token({token})")
            return Start.transit(char)

class Number(BaseState):
    name = "NUMBER"
    hasmiddle = True 

    dotis = False
    
    @classmethod
    def transit(cls, char):
        if Util.is_number(char):
            return cls
        elif char == '.':
            if not cls.dotis:
                cls.dotis = True
                return cls
            else:
                cls.dotis = False
        return Start.transit(char)

class Literal(BaseState):
    name = "LITERAL"
    close = '"'
    closing = False

    @classmethod
    def transit(cls, char):
        if char == cls.close:
            cls.closing = True
        else:
            if cls.closing:
                cls.closing = False
                return Start.transit(char)
        return cls

class Literal2(Literal):
    close = "'"

class Indent(BaseState):
    name = "INDENT"

class Dedent(BaseState):
    name = "DEDENT"

class Operator(BaseState):
    name = "Operator"

    @classmethod
    def transit(cls, char):

        if char == "":
            return EOF

        global token
        if cls.is_member(token + char):
            return cls
        return Start

    @staticmethod
    def is_member(char_s, iskeyword=False):
        if iskeyword:
            return char_s in {
                "and", "or", "not"
                }
        return char_s in {
            "+", "-", "/", "*", "%", "=", "<", ">",
            "&", "^", "~", "|",
            "+=", "-+", "/=", "*=", "%=", "==", "<=", 
            ">=", "//", "**", "!=", "&=", "^=", "~=",
            "|=", "**=", "//=", "<<=", ">>=", 
                }

class Punctuator(BaseState):
    name = "PUNCTUATOR"
    issingleton = True

    @classmethod
    def transit(cls, char):
        if cls.is_member(char):
            return cls
        return Start.transit(char)

    @staticmethod
    def is_member(char):
        return char in [
            "}", "{", "(", ")",
            ",", "[", "]"
                ]

class Comment(BaseState):
    name = "COMMENT"

    @classmethod
    def transit(cls, char):
        if char in ("\n", ""):
            return Start
        return cls

class Start(BaseState):
    name = "Start"
    type = StateType.START

    @classmethod
    def transit(cls, char):
        if char == "":
            return EOF
        if Util.is_whitespace(char):
            # Whitespace character
            return Start
        if ord('a') <= ord(char) <= ord('z') or \
            ord('A') <= ord(char) <= ord('z'):
                return Identifier
        if char == '"':
            return Literal
        if char == "'":
            return Literal2

        if char == '#':
            return Comment

        if Util.is_number(char):
            return Number
        if Operator.is_member(char):
            return Operator
        if Punctuator.is_member(char):
            return Punctuator
        return cls

class EOF(BaseState):
    name = "EOF"
    type = StateType.INTERMEDIATE

class Member_Access(BaseState):
    name = "MemberOperator"

    @classmethod
    def transit(cls, char):
        if Util.is_alphabet(char):
            return Identifier

        # An Invalid Character is read
        return Start.transit(char)
        global token
        raise LexicalAnalysisError(f"Invalid character({char}) after an Identifier token({token})")

# What happens when a State cannot Tell the next State on an input character


# The Automaton
class Automaton:

    def __init__(self):
        self.__tokens = []

    def save_token(self, token, state):
        if state.type != StateType.FINAL:
            return
        newt = Token()
        newt.name = state.name
        newt.value = token

        print(f"{newt.value} --> {newt.name}")

        self.__tokens.append(newt)

        state.save(newt)

    def recognize(self, char, current_state):

        next_state = current_state.transit(char)

        if (next_state is not current_state) or next_state.issingleton:
            global token
            self.save_token(token, current_state)
            token = ""
    
        return next_state

    def run(self, input_stream):

        state = Start
        next_state = None

        global token

        while True:
            char = input_stream.read(1)

            if not char:
                break

            next_state = self.recognize(char, state)
            state = next_state
            token += char
    
        next = self.recognize(char, state)


def main():

    global token
    token = ""
    automaton = Automaton()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename) as fd:
            automaton.run(fd)
    else:
        print("A Python Lexical Analyzer Program\n")
        print("Enter Python Instruction to analyze")
        while True:
            ins = input("(lexer): ")
            if ins == "quit":
                print("\nExiting lexer...")
                break
            automaton.run(StringIO(ins))
            print()

if __name__ == "__main__":
    main()
