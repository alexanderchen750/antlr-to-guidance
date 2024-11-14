@guidance(stateless=True)
def json(lm):

    return lm + value() + EOF()

@guidance(stateless=True)
def obj(lm):

    return lm + select([
        '{' + pair() + zero_or_more(',' + pair()) + '}', '{' + '}'
    ])

@guidance(stateless=True)
def pair(lm):

    return lm + STRING() + ':' + value()

@guidance(stateless=True)
def arr(lm):

    return lm + select([
        '[' + value() + zero_or_more(',' + value()) + ']', '[' + ']'
    ])

@guidance(stateless=True)
def value(lm):

    return lm + select([
        STRING(), NUMBER(), obj(), arr(), 'true', 'false', 'null'
    ])

@guidance(stateless=True)
def STRING(lm):

    return lm + '"' + zero_or_more(select([
        ESC(), SAFECODEPOINT()
    ])) + '"'

@guidance(stateless=True)
def ESC(lm):

    return lm + '\\' + select([
        regex(r'["\\/bfnrt]'), UNICODE()
    ])

@guidance(stateless=True)
def UNICODE(lm):

    return lm + 'u' + HEX() + HEX() + HEX() + HEX()

@guidance(stateless=True)
def HEX(lm):

    return lm + regex(r'[0-9a-fA-F]')

@guidance(stateless=True)
def SAFECODEPOINT(lm):

    return lm + regex(r'[^"\\\u0000-\u001F]')

@guidance(stateless=True)
def NUMBER(lm):

    return lm + select(['', '-']) + INT() + select(['', '.' + one_or_more(regex(r'[0-9]'))]) + select(['', EXP()])

@guidance(stateless=True)
def INT(lm):

    return lm + select([
        '0', regex(r'[1-9]') + zero_or_more(regex(r'[0-9]'))
    ])

@guidance(stateless=True)
def EXP(lm):

    return lm + regex(r'[Ee]') + select(['', regex(r'[+-]')]) + one_or_more(regex(r'[0-9]'))