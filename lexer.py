#!/usr/bin/env python3

"""A Lexical Analyzer for python source codes"""

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

# Definition of States for the Automaton
#   BaseState - Defines some basic properties to be inherited
#   Identifier
#   Keyword
#   Literal
#   Indent
#   Dedent
#   Punctuator
#   Comment
#
#   Start
#
#   Member_Access

class BaseState:
    name = ""
    type = StateType.FINAL
    __token = []

    @classmethod
    def transit(cls, char):
        raise NotImplemented

    @classmethod
    def save(cls, token):
        cls.__token.append(token)

class Identifier(BaseState):
    name = "IDENTIFIER"
    is_identifier = False

    @classmethod
    def transit(cls, char):
        if char == '.':
            # Member Accessor Operation is expected
            # If next character is invalid error is raised

            return Member_Access

        if ord('0') <= ord(char) <= ord('9'):
            # Token is predicted to be an Identifier
            # if it contains any integer char
            cls.is_identifier = True
            return cls

        if ord('a') <= ord(char) <= ord('z') or \
            ord('A') <= ord(char) <= ord('Z'):
                # Asci Chars is still being read
                return cls
        
        global token

        if Util.is_whitespace(char):
            # End of the current token, start reading new
            print(token)
            print(cls.is_identifier)

            if not cls.is_identifier and Keyword.is_member(token):
                cls.is_identifier = False
                return Keyword
            else:
                return Start
        
        else:
            # Invalid token received
            raise LexicalAnalysisError(f"Unexpected Character({char}) after token({token})")

    @staticmethod
    def is_member(char):
        ...

class Keyword(BaseState):
    name = "KEYWORD"

    @classmethod
    def transit(cls, char):
        return cls

    @staticmethod
    def is_member(token):
        import keyword
        
        return keyword.iskeyword(token)

class Literal(BaseState):
    name = "LITERAL"

class Indent(BaseState):
    name = "INDENT"

class Dedent(BaseState):
    name = "DEDENT"

class Punctuator(BaseState):
    name = "PUNCTUATOR"

    @classmethod
    def transit(cls, char):
        ...

    @staticmethod
    def is_member(char):
        return char in [
            "}", "{", "(", ")",
            ",", "[", "]"
                ]

class Comment(BaseState):
    name = "COMMENT"

class Start(BaseState):
    name = "Start"
    type = StateType.START

    @classmethod
    def transit(cls, char):
        if Util.is_whitespace(char):
            # Whitespace character
            return Start
        if ord('a') <= ord(char) <= ord('z') or \
            ord('A') <= ord(char) <= ord('z'):
                return Identifier

        if ord('0') <= ord(char) <= ord("1"):
            return Literal

class Member_Access(BaseState):
    name = "MemberOperator"

    @classmethod
    def transit(cls, char):
        if ord('a') <= ord(char) <= ord('z') or \
            ord('A') <= ord(char) <= ord('Z'):
            return Identifier

        # An Invalid Character is read
        global token
        raise LexicalAnalysisError(f"Invalid character({char}) after an Identifier token({token})")

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

    def recognize(self, char, current_state, next_state):
        next_state = current_state.transit(char)
        return next_state

    def run(self, input_stream):

        state = Start
        next_state = None

        global token

        while True:
            char = input_stream.read(1)

            if not char:
                break

            next_state = self.recognize(char, state, next_state)
            if next_state != state:
                self.save_token(token, state)
                token = ""
            state = next_state
            token += char


def main():

    global token
    token = ""
    automaton = Automaton()

    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename) as fd:
            automaton.run(fd)
    else:
        print("Enter Python Instruction to parse")
        while True:
            ins = input("(lexer): ")
            if ins == "quit":
                print("\nExiting lexer...")
                break
            automaton.run(StringIO(ins))

if __name__ == "__main__":
    main()
