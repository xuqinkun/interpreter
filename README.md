# <center> 用Go自制解释器（Python版）
# 第1章：解释器基础与词法分析

第1章通常为读者奠定解释器开发的基础知识，并开始实现解释器的第一个关键组件——词法分析器（Lexer）。以下是详细内容总结：

## 1. 解释器基础概念

- **解释器与编译器的区别**：
  - 解释器直接执行源代码，边解析边执行
  - 编译器将源代码转换为机器码后再执行
  - 解释器通常更容易实现和调试

- **解释器的工作流程**：
  1. 词法分析（Lexical Analysis）
  2. 语法分析（Parsing）
  3. 语义分析（Semantic Analysis）
  4. 解释执行（Evaluation）

## 2. 词法分析器（Lexer）的作用

- 将源代码字符串转换为有意义的**词法单元（tokens）**序列
- 去除无关内容（如空白、注释）
- 识别并分类语言的基本元素（关键字、标识符、运算符等）

## 3. 使用 Go 实现基础词法分析器

## 3.1 定义 Token 类型

```go
type TokenType string

const (
    ILLEGAL = "ILLEGAL" // 未知token
    EOF     = "EOF"     // 文件结束
    
    // 标识符 + 字面量
    IDENT = "IDENT" // add, foobar, x, y...
    INT   = "INT"   // 123456
    
    // 运算符
    ASSIGN = "="
    PLUS   = "+"
    
    // 分隔符
    COMMA     = ","
    SEMICOLON = ";"
    
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    
    // 关键字
    FUNCTION = "FUNCTION"
    LET      = "LET"
)
```

## 3.2 Token 结构体

```go
type Token struct {
    Type    TokenType
    Literal string
}
```

## 3.3 Lexer 结构体

```go
type Lexer struct {
    input        string
    position     int  // 当前字符位置
    readPosition int  // 下一个字符位置
    ch           byte // 当前字符
}
```

## 3.4 核心方法实现

**初始化 Lexer**:
```go
func New(input string) *Lexer {
    l := &Lexer{input: input}
    l.readChar() // 初始化第一个字符
    return l
}
```

**读取字符**:
```go
func (l *Lexer) readChar() {
    if l.readPosition >= len(l.input) {
        l.ch = 0 // ASCII的NUL字符，表示EOF
    } else {
        l.ch = l.input[l.readPosition]
    }
    l.position = l.readPosition
    l.readPosition += 1
}
```

**核心 NextToken 方法**:
```go
func (l *Lexer) NextToken() Token {
    var tok Token
    
    l.skipWhitespace()
    
    switch l.ch {
    case '=':
        tok = newToken(ASSIGN, l.ch)
    case ';':
        tok = newToken(SEMICOLON, l.ch)
    case '(':
        tok = newToken(LPAREN, l.ch)
    case ')':
        tok = newToken(RPAREN, l.ch)
    case ',':
        tok = newToken(COMMA, l.ch)
    case '+':
        tok = newToken(PLUS, l.ch)
    case '{':
        tok = newToken(LBRACE, l.ch)
    case '}':
        tok = newToken(RBRACE, l.ch)
    case 0:
        tok.Literal = ""
        tok.Type = EOF
    default:
        if isLetter(l.ch) {
            tok.Literal = l.readIdentifier()
            tok.Type = LookupIdent(tok.Literal)
            return tok
        } else if isDigit(l.ch) {
            tok.Type = INT
            tok.Literal = l.readNumber()
            return tok
        } else {
            tok = newToken(ILLEGAL, l.ch)
        }
    }
    
    l.readChar()
    return tok
}
```

## 4. 辅助函数实现

**读取标识符**:
```go
func (l *Lexer) readIdentifier() string {
    position := l.position
    for isLetter(l.ch) {
        l.readChar()
    }
    return l.input[position:l.position]
}
```

**读取数字**:
```go
func (l *Lexer) readNumber() string {
    position := l.position
    for isDigit(l.ch) {
        l.readChar()
    }
    return l.input[position:l.position]
}
```

**跳过空白字符**:
```go
func (l *Lexer) skipWhitespace() {
    for l.ch == ' ' || l.ch == '\t' || l.ch == '\n' || l.ch == '\r' {
        l.readChar()
    }
}
```

**关键字识别**:
```go
var keywords = map[string]TokenType{
    "fn":  FUNCTION,
    "let": LET,
}

func LookupIdent(ident string) TokenType {
    if tok, ok := keywords[ident]; ok {
        return tok
    }
    return IDENT
}
```

## 5. 测试词法分析器

```go
input := `let five = 5;
let ten = 10;

let add = fn(x, y) {
    x + y;
};

let result = add(five, ten);
`

tests := []struct {
    expectedType    TokenType
    expectedLiteral string
}{
    {LET, "let"},
    {IDENT, "five"},
    {ASSIGN, "="},
    {INT, "5"},
    // ... 更多测试用例
}

l := New(input)

for i, tt := range tests {
    tok := l.NextToken()
    
    if tok.Type != tt.expectedType {
        // 错误处理
    }
    if tok.Literal != tt.expectedLiteral {
        // 错误处理
    }
}
```

## 6. 本章关键点总结

1. **词法分析器的作用**：将原始代码分解为有意义的token序列
2. **Token设计**：每个token包含类型和字面值
3. **逐字符分析**：通过逐个读取字符来识别token
4. **状态管理**：Lexer需要跟踪当前读取位置和状态
5. **关键字识别**：通过预定义关键字表区分标识符和关键字
6. **错误处理**：对无法识别的字符标记为ILLEGAL

这一章为解释器开发奠定了重要基础，下一章通常会在此基础上构建解析器（Parser）来处理这些token并构建抽象语法树（AST）。


# 第2章：解析器与抽象语法树（AST）

第2章通常在第1章词法分析器的基础上，介绍如何构建解析器（Parser）和抽象语法树（AST），这是解释器/编译器工作的核心组成部分。

## 1. 解析器基础

- **解析器的职责**：
  - 接收词法分析器产生的token流
  - 验证语法是否符合语言规范
  - 构建抽象语法树（AST）表示程序结构

- **两种主要解析策略**：
  - 自顶向下解析（递归下降）
  - 自底向上解析（本书采用递归下降方法）

## 2. 抽象语法树（AST）

- **AST的作用**：
  - 以树状结构表示源代码的语法
  - 省略不必要的细节（如分号、括号等）
  - 便于后续分析和执行

- **AST与具体语法树（CST）的区别**：
  - CST包含所有语法细节
  - AST只保留语义关键信息

## 3. 解析器实现

## 3.1 定义AST节点接口

```go
type Node interface {
    TokenLiteral() string
    String() string
}

type Statement interface {
    Node
    statementNode()
}

type Expression interface {
    Node
    expressionNode()
}
```

## 3.2 基本AST节点结构

**程序根节点**：
```go
type Program struct {
    Statements []Statement
}

func (p *Program) TokenLiteral() string {
    if len(p.Statements) > 0 {
        return p.Statements[0].TokenLiteral()
    }
    return ""
}
```

**Let语句**：
```go
type LetStatement struct {
    Token token.Token // token.LET
    Name  *Identifier
    Value Expression
}

func (ls *LetStatement) statementNode() {}
func (ls *LetStatement) TokenLiteral() string { return ls.Token.Literal }
```

**Return语句**：
```go
type ReturnStatement struct {
    Token       token.Token // token.RETURN
    ReturnValue Expression
}

func (rs *ReturnStatement) statementNode() {}
func (rs *ReturnStatement) TokenLiteral() string { return rs.Token.Literal }
```

**表达式语句**：
```go
type ExpressionStatement struct {
    Token      token.Token // 表达式的第一个token
    Expression Expression
}

func (es *ExpressionStatement) statementNode() {}
func (es *ExpressionStatement) TokenLiteral() string { return es.Token.Literal }
```

**标识符表达式**：
```go
type Identifier struct {
    Token token.Token // token.IDENT
    Value string
}

func (i *Identifier) expressionNode() {}
func (i *Identifier) TokenLiteral() string { return i.Token.Literal }
```

## 3.3 解析器结构

```go
type Parser struct {
    l      *lexer.Lexer
    errors []string

    curToken  token.Token
    peekToken token.Token
}
```

## 3.4 解析器初始化

```go
func New(l *lexer.Lexer) *Parser {
    p := &Parser{
        l:      l,
        errors: []string{},
    }

    // 读取两个token，初始化curToken和peekToken
    p.nextToken()
    p.nextToken()

    return p
}

func (p *Parser) nextToken() {
    p.curToken = p.peekToken
    p.peekToken = p.l.NextToken()
}
```

## 3.5 解析程序入口

```go
func (p *Parser) ParseProgram() *ast.Program {
    program := &ast.Program{}
    program.Statements = []ast.Statement{}

    for p.curToken.Type != token.EOF {
        stmt := p.parseStatement()
        if stmt != nil {
            program.Statements = append(program.Statements, stmt)
        }
        p.nextToken()
    }

    return program
}
```

## 3.6 解析语句

```go
func (p *Parser) parseStatement() ast.Statement {
    switch p.curToken.Type {
    case token.LET:
        return p.parseLetStatement()
    case token.RETURN:
        return p.parseReturnStatement()
    default:
        return p.parseExpressionStatement()
    }
}
```

**解析Let语句**：
```go
func (p *Parser) parseLetStatement() *ast.LetStatement {
    stmt := &ast.LetStatement{Token: p.curToken}

    if !p.expectPeek(token.IDENT) {
        return nil
    }

    stmt.Name = &ast.Identifier{Token: p.curToken, Value: p.curToken.Literal}

    if !p.expectPeek(token.ASSIGN) {
        return nil
    }

    p.nextToken()

    stmt.Value = p.parseExpression(LOWEST)

    if p.peekTokenIs(token.SEMICOLON) {
        p.nextToken()
    }

    return stmt
}
```

**辅助函数**：
```go
func (p *Parser) curTokenIs(t token.TokenType) bool {
    return p.curToken.Type == t
}

func (p *Parser) peekTokenIs(t token.TokenType) bool {
    return p.peekToken.Type == t
}

func (p *Parser) expectPeek(t token.TokenType) bool {
    if p.peekTokenIs(t) {
        p.nextToken()
        return true
    } else {
        p.peekError(t)
        return false
    }
}
```

## 4. 表达式解析

## 4.1 表达式优先级

```go
const (
    _ int = iota
    LOWEST
    EQUALS      // ==
    LESSGREATER // > or <
    SUM        // +
    PRODUCT     // *
    PREFIX      // -X or !X
    CALL        // myFunction(X)
)
```

## 4.2 前缀表达式

```go
type PrefixExpression struct {
    Token    token.Token // 前缀token，如!
    Operator string
    Right    Expression
}

func (pe *PrefixExpression) expressionNode() {}
func (pe *PrefixExpression) TokenLiteral() string { return pe.Token.Literal }
```

**解析前缀表达式**：
```go
func (p *Parser) parsePrefixExpression() ast.Expression {
    expression := &ast.PrefixExpression{
        Token:    p.curToken,
        Operator: p.curToken.Literal,
    }

    p.nextToken()

    expression.Right = p.parseExpression(PREFIX)

    return expression
}
```

## 4.3 中缀表达式

```go
type InfixExpression struct {
    Token    token.Token // 运算符token，如+
    Left     Expression
    Operator string
    Right    Expression
}

func (ie *InfixExpression) expressionNode() {}
func (ie *InfixExpression) TokenLiteral() string { return ie.Token.Literal }
```

**解析中缀表达式**：
```go
func (p *Parser) parseInfixExpression(left ast.Expression) ast.Expression {
    expression := &ast.InfixExpression{
        Token:    p.curToken,
        Operator: p.curToken.Literal,
        Left:     left,
    }

    precedence := p.curPrecedence()
    p.nextToken()
    expression.Right = p.parseExpression(precedence)

    return expression
}
```

## 5. Pratt解析器核心

```go
func (p *Parser) parseExpression(precedence int) ast.Expression {
    prefix := p.prefixParseFns[p.curToken.Type]
    if prefix == nil {
        p.noPrefixParseFnError(p.curToken.Type)
        return nil
    }
    leftExp := prefix()

    for !p.peekTokenIs(token.SEMICOLON) && precedence < p.peekPrecedence() {
        infix := p.infixParseFns[p.peekToken.Type]
        if infix == nil {
            return leftExp
        }

        p.nextToken()

        leftExp = infix(leftExp)
    }

    return leftExp
}
```

## 6. 注册解析函数

```go
func New(l *lexer.Lexer) *Parser {
    p := &Parser{
        l:      l,
        errors: []string{},
    }

    // 注册前缀解析函数
    p.prefixParseFns = make(map[token.TokenType]prefixParseFn)
    p.registerPrefix(token.IDENT, p.parseIdentifier)
    p.registerPrefix(token.INT, p.parseIntegerLiteral)
    p.registerPrefix(token.BANG, p.parsePrefixExpression)
    p.registerPrefix(token.MINUS, p.parsePrefixExpression)

    // 注册中缀解析函数
    p.infixParseFns = make(map[token.TokenType]infixParseFn)
    p.registerInfix(token.PLUS, p.parseInfixExpression)
    p.registerInfix(token.MINUS, p.parseInfixExpression)
    p.registerInfix(token.SLASH, p.parseInfixExpression)
    p.registerInfix(token.ASTERISK, p.parseInfixExpression)
    p.registerInfix(token.EQ, p.parseInfixExpression)
    p.registerInfix(token.NOT_EQ, p.parseInfixExpression)
    p.registerInfix(token.LT, p.parseInfixExpression)
    p.registerInfix(token.GT, p.parseInfixExpression)

    // 读取两个token初始化curToken和peekToken
    p.nextToken()
    p.nextToken()

    return p
}
```

## 7. 测试解析器

```go
input := `
let x = 5;
let y = 10;
let foobar = 838383;
`

l := lexer.New(input)
p := New(l)
program := p.ParseProgram()

if program == nil {
    t.Fatalf("ParseProgram() returned nil")
}
if len(program.Statements) != 3 {
    t.Fatalf("program.Statements does not contain 3 statements. got=%d",
        len(program.Statements))
}

tests := []struct {
    expectedIdentifier string
}{
    {"x"},
    {"y"},
    {"foobar"},
}

for i, tt := range tests {
    stmt := program.Statements[i]
    if !testLetStatement(t, stmt, tt.expectedIdentifier) {
        return
    }
}
```

## 8. 本章关键点总结

1. **解析器架构**：采用递归下降的Pratt解析方法
2. **AST设计**：明确定义语句和表达式接口
3. **节点类型**：实现了Let、Return、表达式语句等基本节点
4. **表达式解析**：处理前缀和中缀表达式，考虑优先级
5. **错误处理**：完善的错误收集和报告机制
6. **测试验证**：确保解析器正确构建AST

第2章完成了从token流到AST的转换过程，为后续的求值器（Evaluator）实现奠定了基础。下一章通常会介绍如何遍历AST并执行程序。

