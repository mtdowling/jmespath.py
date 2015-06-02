import string
import warnings
from json import loads

from jmespath.exceptions import LexerError, EmptyExpressionError


class Scanner(object):
    def __init__(self, expression):
        if not expression:
            raise EmptyExpressionError()
        self.expression = expression
        self.pos = 0
        self.chars = list(self.expression)
        self.len = len(self.expression)
        self.current = self.chars[self.pos]

    def next(self):
        if self.pos == self.len - 1:
            self.current = None
        else:
            self.pos += 1
            self.current = self.chars[self.pos]
        return self.current

    def in_delimiter(self, delimiter):
        start = self.pos
        buff = ''
        self.next()
        while self.current != delimiter:
            if self.current == '\\':
                buff += '\\'
                self.next()
            if self.current is None:
                raise LexerError(lexer_position=start,
                                 lexer_value=self.expression,
                                 message="Unclosed %s delimiter" % delimiter)
            buff += self.current
            self.next()
        # Skip the closing delimiter.
        self.next()
        return buff


class Lexer(object):
    VALID_NUMBER = set('-' + string.digits)
    VALID_IDENTIFIER = set(string.ascii_letters + string.digits + '_')

    def __init__(self):
        self._transitions = {
            '[': self._consume_lbracket,
            '.': lambda scanner: self._simple_token(scanner, 'dot'),
            '*': lambda scanner: self._simple_token(scanner, 'star'),
            ']': lambda scanner: self._simple_token(scanner, 'rbracket'),
            ',': lambda scanner: self._simple_token(scanner, 'comma'),
            ':': lambda scanner: self._simple_token(scanner, 'colon'),
            '@': lambda scanner: self._simple_token(scanner, 'current'),
            '&': lambda scanner: self._simple_token(scanner, 'expref'),
            '(': lambda scanner: self._simple_token(scanner, 'lparen'),
            ')': lambda scanner: self._simple_token(scanner, 'rparen'),
            '{': lambda scanner: self._simple_token(scanner, 'lbrace'),
            '}': lambda scanner: self._simple_token(scanner, 'rbrace'),
            '_': self._consume_identifier,
            'A': self._consume_identifier,
            'B': self._consume_identifier,
            'C': self._consume_identifier,
            'D': self._consume_identifier,
            'E': self._consume_identifier,
            'F': self._consume_identifier,
            'G': self._consume_identifier,
            'H': self._consume_identifier,
            'I': self._consume_identifier,
            'J': self._consume_identifier,
            'K': self._consume_identifier,
            'L': self._consume_identifier,
            'M': self._consume_identifier,
            'N': self._consume_identifier,
            'O': self._consume_identifier,
            'P': self._consume_identifier,
            'Q': self._consume_identifier,
            'R': self._consume_identifier,
            'S': self._consume_identifier,
            'T': self._consume_identifier,
            'U': self._consume_identifier,
            'V': self._consume_identifier,
            'W': self._consume_identifier,
            'X': self._consume_identifier,
            'Y': self._consume_identifier,
            'Z': self._consume_identifier,
            'a': self._consume_identifier,
            'b': self._consume_identifier,
            'c': self._consume_identifier,
            'd': self._consume_identifier,
            'e': self._consume_identifier,
            'f': self._consume_identifier,
            'g': self._consume_identifier,
            'h': self._consume_identifier,
            'i': self._consume_identifier,
            'j': self._consume_identifier,
            'k': self._consume_identifier,
            'l': self._consume_identifier,
            'm': self._consume_identifier,
            'n': self._consume_identifier,
            'o': self._consume_identifier,
            'p': self._consume_identifier,
            'q': self._consume_identifier,
            'r': self._consume_identifier,
            's': self._consume_identifier,
            't': self._consume_identifier,
            'u': self._consume_identifier,
            'v': self._consume_identifier,
            'w': self._consume_identifier,
            'x': self._consume_identifier,
            'y': self._consume_identifier,
            'z': self._consume_identifier,
            ' ': self._skip_whitespace,
            "\t": self._skip_whitespace,
            "\n": self._skip_whitespace,
            "\r": self._skip_whitespace,
            '<': lambda scanner: self._match_or_else(scanner, '=',
                                                     'lte', 'lt'),
            '>': lambda scanner: self._match_or_else(scanner, '=',
                                                     'gte', 'gt'),
            '=': lambda scanner: self._match_or_else(scanner, '=',
                                                     'eq', 'unknown'),
            '!': lambda scanner: self._match_or_else(scanner, '=',
                                                     'neq', 'unknown'),
            '|': lambda scanner: self._match_or_else(scanner, '|',
                                                     'or', 'pipe'),
            '`': self._consume_literal,
            '"': self._consume_quoted_identifier,
            "'": self._consume_raw_string_literal,
            '-': self._consume_number,
            '0': self._consume_number,
            '1': self._consume_number,
            '2': self._consume_number,
            '3': self._consume_number,
            '4': self._consume_number,
            '5': self._consume_number,
            '6': self._consume_number,
            '7': self._consume_number,
            '8': self._consume_number,
            '9': self._consume_number,
        }

    def tokenize(self, expression):
        scanner = Scanner(expression)
        while scanner.current is not None:
            if scanner.current not in self._transitions:
                raise LexerError(lexer_position=scanner.pos,
                                 lexer_value=scanner.current,
                                 message="Unknown token %s" % scanner.current)
            yield self._transitions[scanner.current](scanner)
        yield {'type': 'eof', 'value': '',
               'start': len(expression), 'end': len(expression)}

    @staticmethod
    def _skip_whitespace(scanner):
        scanner.next()

    @staticmethod
    def _simple_token(scanner, token_type):
        scanner.next()
        return {'type': token_type, 'value': token_type,
                'start': scanner.pos - 1, 'end': scanner.pos}

    @staticmethod
    def _consume_identifier(scanner):
        start = scanner.pos
        buff = scanner.current
        while scanner.next() in Lexer.VALID_IDENTIFIER:
            buff += scanner.current
        return {'type': 'unquoted_identifier', 'value': buff,
                'start': start, 'end': len(buff)}

    @staticmethod
    def _consume_number(scanner):
        start = scanner.pos
        buff = scanner.current
        while scanner.next() in Lexer.VALID_NUMBER:
            buff += scanner.current
        return {'type': 'number', 'value': int(buff),
                'start': start, 'end': len(buff)}

    @staticmethod
    def _consume_lbracket(scanner):
        start = scanner.pos
        next_char = scanner.next()
        if next_char == ']':
            scanner.next()
            return {'type': 'flatten', 'value': '[]',
                    'start': start, 'end': start + 1}
        elif next_char == '?':
            scanner.next()
            return {'type': 'filter', 'value': '[?',
                    'start': start, 'end': start + 1}
        else:
            return {'type': 'lbracket', 'value': '[',
                    'start': start, 'end': start}

    @staticmethod
    def _consume_literal(scanner):
        start = scanner.pos
        lexeme = scanner.in_delimiter('`')
        lexeme = lexeme.replace('\\`', '`')
        try:
            # Assume it is valid JSON and attempt to parse.
            parsed_json = loads(lexeme)
        except ValueError:
            try:
                # Invalid JSON values should be converted to quoted
                # JSON strings during the JEP-12 deprecation period.
                parsed_json = loads('"%s"' % lexeme.lstrip())
                warnings.warn("deprecated string literal syntax",
                              PendingDeprecationWarning)
            except ValueError:
                raise LexerError(lexer_position=start,
                                 lexer_value=lexeme,
                                 message="Bad token %s" % lexeme)
        token_len = scanner.pos - start
        return {'type': 'literal', 'value': parsed_json,
                'start': start, 'end': token_len}

    @staticmethod
    def _consume_quoted_identifier(scanner):
        start = scanner.pos
        lexeme = '"' + scanner.in_delimiter('"') + '"'
        try:
            token_len = scanner.pos - start
            return {'type': 'quoted_identifier', 'value': loads(lexeme),
                    'start': start, 'end': token_len}
        except ValueError as e:
            error_message = str(e).split(':')[0]
            raise LexerError(lexer_position=start,
                             lexer_value=lexeme,
                             message=error_message)

    @staticmethod
    def _consume_raw_string_literal(scanner):
        start = scanner.pos
        lexeme = scanner.in_delimiter("'")
        token_len = scanner.pos - start
        return {'type': 'literal', 'value': lexeme,
                'start': start, 'end': token_len}

    @staticmethod
    def _match_or_else(scanner, expected, match_type, else_type):
        start = scanner.pos
        current = scanner.current
        next_char = scanner.next()
        if next_char == expected:
            scanner.next()
            return {'type': match_type, 'value': current + next_char,
                    'start': start, 'end': start + 1}
        return {'type': else_type, 'value': current,
                'start': start, 'end': start}
