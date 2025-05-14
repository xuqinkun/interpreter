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
## Chapter2 语法分析