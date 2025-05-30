from enum import Enum
from typing import Optional, Dict, Callable

from monkey_lexer import lexer
from monkey_lexer.lexer import Lexer
from monkey_ast.ast import *
from monkey_token.token import *


class Precedence(Enum):
    BLANK = 0
    LOWEST = 1
    LOGIC = 2
    BITWISE = 3
    EQUALS = 4  # ==
    LESS_GREATER = 5  # > or <
    SUM = 6  # +
    PRODUCT = 7  # *
    PREFIX = 8  # -X or !X
    CALL = 9  # func(X)
    INDEX = 10


precedences = {
    LOGIC_AND: Precedence.LOGIC,
    LOGIC_OR: Precedence.LOGIC,
    BITWISE_AND: Precedence.BITWISE,
    BITWISE_OR: Precedence.BITWISE,
    EQ: Precedence.EQUALS,
    NOT_EQ: Precedence.EQUALS,
    LT: Precedence.LESS_GREATER,
    GT: Precedence.LESS_GREATER,
    PLUS: Precedence.SUM,
    MINUS: Precedence.SUM,
    SLASH: Precedence.PRODUCT,
    ASTERISK: Precedence.PRODUCT,
    LPAREN: Precedence.CALL,
    LBRACKET: Precedence.INDEX,
}


@dataclass
class Parser:
    # 定义函数类型别名
    PrefixParseFn = Callable[[], Expression]
    InfixParseFn = Callable[[Expression], Expression]

    lexer: Lexer = None
    line: int = 0
    errors: list[str] = None
    curr: Token = ''
    peek: Token = ''
    prefix_parse_fns: Dict[str, PrefixParseFn] = None
    infix_parse_fns: Dict[str, InfixParseFn] = None

    def __repr__(self):
        curr = self.curr.literal
        peek = self.peek.literal
        code = self.lexer.code
        return f"curr={curr},peek={peek} \ncode:{code}"

    def next_token(self):
        self.curr = self.peek
        self.peek = self.lexer.next_token()

    def parse_program(self) -> Program:
        statements = []
        program = Program(statements)
        while self.curr.token_type != EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self) -> Optional[Statement]:
        if self.curr.token_type == LET:
            return self.parse_let_statement()
        elif self.curr.token_type == RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> Optional[LetStatement]:
        stmt = LetStatement(self.curr)
        if not self.expect_peek(IDENT):
            return None
        stmt.name = Identifier(self.curr, self.curr.literal)
        if not self.expect_peek(ASSIGN):
            return None
        self.next_token()
        stmt.value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_return_statement(self):
        stmt = ReturnStatement(self.curr)
        self.next_token()
        stmt.return_value = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(token=self.curr)
        stmt.expression = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_expression(self, precedence: Precedence):
        token_type = self.curr.token_type
        prefix = self.prefix_parse_fns.get(token_type, None)
        if prefix is None:
            err_msg = f"no prefix parse function for '{token_type}' found"
            self.append_error(err_msg)
            return None
        left_exp = prefix()
        while not self.peek_token_is(SEMICOLON) and precedence.value < self.peek_precedence().value:
            infix = self.infix_parse_fns.get(self.peek.token_type, None)
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)
        return left_exp

    def append_error(self, err_msg: str):
        if self.errors is None:
            self.errors = []
        self.errors.append(err_msg)

    def peek_error(self, token_type):
        err_msg = f"line:{self.lexer.lino}: expected next token to be {token_type}, got {self.peek.token_type} instead"
        self.append_error(err_msg)

    def curr_token_is(self, token_type: str):
        return self.curr.token_type == token_type

    def peek_token_is(self, token_type: str):
        return self.peek.token_type == token_type

    def expect_peek(self, token_type: str):
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        else:
            self.peek_error(token_type)
            return False

    def peek_precedence(self):
        return precedences.get(self.peek.token_type, Precedence.LOWEST)

    def curr_precedence(self):
        return precedences.get(self.curr.token_type, Precedence.LOWEST)

    def register_prefix(self, token_type: str, fn: PrefixParseFn):
        """注册前缀解析函数"""
        self.prefix_parse_fns[token_type] = fn

    def register_infix(self, token_type: str, fn: InfixParseFn):
        """注册中缀解析函数"""
        self.infix_parse_fns[token_type] = fn

    def parse_identifier(self) -> Optional[Expression]:
        return Identifier(token=self.curr, value=self.curr.literal)

    def parse_integer_literal(self) -> Optional[Expression]:
        lit = IntegerLiteral(token=self.curr)
        literal = lit.literal()
        if not literal.isdigit():
            self.append_error(f'Could not parse {literal} as integer')
            return None
        lit.value = int(literal)
        return lit

    def parse_prefix_expression(self):
        exp = PrefixExpression(token=self.curr, operator=self.curr.literal)
        self.next_token()
        exp.right = self.parse_expression(Precedence.PREFIX)
        return exp

    def parse_infix_expression(self, left: Expression):
        exp = InfixExpression(token=self.curr,
                              operator=self.curr.literal,
                              left=left)
        precedence = self.curr_precedence()
        self.next_token()
        exp.right = self.parse_expression(precedence)
        return exp

    def parse_bool_literal(self) -> Expression:
        return Boolean(self.curr, self.curr_token_is(TRUE))

    def parse_string_literal(self) -> Expression:
        return StringLiteral(self.curr, self.curr.literal)

    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(RPAREN):
            return None
        return exp

    def parse_if_expression(self):
        exp = IFExpression(token=self.curr)
        if not self.expect_peek(LPAREN):
            return None
        self.next_token()
        exp.condition = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(RPAREN):
            return None
        if not self.expect_peek(LBRACE):
            return None
        exp.consequence = self.parse_block_statement()
        if self.peek_token_is(ELSE):
            self.next_token()
            if not self.expect_peek(LBRACE):
                return None
            exp.alternative = self.parse_block_statement()
        return exp

    def parse_block_statement(self):
        block = BlockStatement(token=self.curr)
        block.statements = []
        self.next_token()
        while not self.curr_token_is(RBRACE) and not self.curr_token_is(EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()
        return block

    def parse_function_literal(self):
        lit = FunctionLiteral(self.curr)
        if not self.expect_peek(LPAREN):
            return None
        lit.parameters = self.parse_function_parameters()
        if not self.expect_peek(LBRACE):
            return None
        lit.body = self.parse_block_statement()
        return lit

    def parse_function_parameters(self):
        identifiers = []
        if self.peek_token_is(RPAREN):
            self.next_token()
            return identifiers
        self.next_token()
        identifiers.append(Identifier(self.curr, self.curr.literal))
        while self.peek_token_is(COMMA):
            self.next_token()
            self.next_token()
            identifiers.append(Identifier(self.curr, self.curr.literal))
        if not self.expect_peek(RPAREN):
            return None
        return identifiers

    def parse_call_expression(self, function: Expression):
        exp = CallExpression(self.curr, function)
        exp.arguments = self.parse_expression_list(RPAREN)
        return exp

    def parse_call_arguments(self):
        args = []
        if self.peek_token_is(RPAREN):
            self.next_token()
            return args
        self.next_token()
        args.append(self.parse_expression(Precedence.LOWEST))
        while self.peek_token_is(COMMA):
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(Precedence.LOWEST))
        if not self.expect_peek(RPAREN):
            return None
        return args

    def parse_array_literal(self):
        arr = ArrayLiteral(self.curr)
        arr.elements = self.parse_expression_list(RBRACKET)
        return arr

    def parse_expression_list(self, end: str):
        expressions = []
        if self.peek_token_is(end):
            self.next_token()
            return expressions
        self.next_token()
        expressions.append(self.parse_expression(Precedence.LOWEST))
        while self.peek_token_is(COMMA):
            self.next_token()
            self.next_token()
            expressions.append(self.parse_expression(Precedence.LOWEST))
        if not self.expect_peek(end):
            return None
        return expressions

    def parse_index_expression(self, left: Expression):
        exp = IndexExpression(self.curr, left=left)
        self.next_token()
        exp.index = self.parse_expression(Precedence.LOWEST)
        if not self.expect_peek(RBRACKET):
            return True
        return exp

    def parse_hash_literal(self):
        hs = HashLiteral(self.curr)
        hs.pairs = {}
        while not self.peek_token_is(RBRACE):
            self.next_token()
            key = self.parse_expression(Precedence.LOWEST)
            if not self.expect_peek(COLON):
                return None
            self.next_token()
            val = self.parse_expression(Precedence.LOWEST)
            hs.pairs[key] = val
            if not self.peek_token_is(RBRACE) and not self.expect_peek(COMMA):
                return None
        if not self.expect_peek(RBRACE):
            return None
        return hs

    def parse_macro_literal(self):
        lit = MacroLiteral(self.curr)
        if not self.expect_peek(LPAREN):
            return None
        lit.parameters = self.parse_function_parameters()
        if not self.expect_peek(LBRACE):
            return None
        lit.body = self.parse_block_statement()
        return lit

    @staticmethod
    def get_parser(lex: Lexer):
        p = Parser()
        p.lexer = lex
        p.errors = []
        p.prefix_parse_fns = {}
        p.infix_parse_fns = {}
        # IDENT
        p.register_prefix(IDENT, p.parse_identifier)
        # ()
        p.register_prefix(LPAREN, p.parse_grouped_expression)
        # Array
        p.register_prefix(LBRACKET, p.parse_array_literal)
        # Integer
        p.register_prefix(INT, p.parse_integer_literal)
        # Boolean
        p.register_prefix(TRUE, p.parse_bool_literal)
        p.register_prefix(FALSE, p.parse_bool_literal)
        # String
        p.register_prefix(STRING, p.parse_string_literal)
        # !
        p.register_prefix(BANG, p.parse_prefix_expression)
        # +-*/
        p.register_prefix(MINUS, p.parse_prefix_expression)
        p.register_infix(PLUS, p.parse_infix_expression)
        p.register_infix(MINUS, p.parse_infix_expression)
        p.register_infix(SLASH, p.parse_infix_expression)
        p.register_infix(ASTERISK, p.parse_infix_expression)
        p.register_infix(LOGIC_AND, p.parse_infix_expression)
        p.register_infix(LOGIC_OR, p.parse_infix_expression)
        p.register_infix(BITWISE_AND, p.parse_infix_expression)
        p.register_infix(BITWISE_OR, p.parse_infix_expression)
        # =,!=,<,>
        p.register_infix(EQ, p.parse_infix_expression)
        p.register_infix(NOT_EQ, p.parse_infix_expression)
        p.register_infix(LT, p.parse_infix_expression)
        p.register_infix(GT, p.parse_infix_expression)
        # []
        p.register_infix(LBRACKET, p.parse_index_expression)
        # if
        p.register_prefix(IF, p.parse_if_expression)
        # function
        p.register_prefix(FUNCTION, p.parse_function_literal)
        # 调用表达式
        p.register_infix(LPAREN, p.parse_call_expression)
        # 哈希
        p.register_prefix(LBRACE, p.parse_hash_literal)
        # 宏
        p.register_prefix(MACRO, p.parse_macro_literal)
        # 将curr指向第一个token
        p.next_token()
        p.next_token()
        return p


def check_parser_errors(p: Parser):
    errors = p.errors
    if not errors:
        return False
    print(f'parser has {len(errors)} errors')
    for err in errors:
        print(f'parse error:{err}')
    return True


def parse(code):
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    return program
