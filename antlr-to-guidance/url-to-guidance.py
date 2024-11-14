@guidance(stateless=True)
def url(lm):

    return lm + uri() + EOF()

@guidance(stateless=True)
def uri(lm):

    return lm + scheme() + '://' + select(['', login()]) + host() + select(['', ':' + port()]) + select(['', '/' + select(['', path()])]) + select(['', query()]) + select(['', frag()]) + select(['', WS()])

@guidance(stateless=True)
def scheme(lm):

    return lm + string()

@guidance(stateless=True)
def host(lm):

    return lm + select(['', '/']) + hostname()

@guidance(stateless=True)
def hostname(lm):

    return lm + select([
        string(), '[' + v6host() + ']'
    ])

@guidance(stateless=True)
def v6host(lm):

    return lm + select(['', '::']) + select([string(), DIGITS()]) + zero_or_more(select([':', '::']) + select([string(), DIGITS()]))

@guidance(stateless=True)
def port(lm):

    return lm + DIGITS()

@guidance(stateless=True)
def path(lm):

    return lm + string() + zero_or_more('/' + string()) + select(['', '/'])

@guidance(stateless=True)
def user(lm):

    return lm + string()

@guidance(stateless=True)
def login(lm):

    return lm + user() + select(['', ':' + password()]) + '@'

@guidance(stateless=True)
def password(lm):

    return lm + string()

@guidance(stateless=True)
def frag(lm):

    return lm + '#' + select([string(), DIGITS()])

@guidance(stateless=True)
def query(lm):

    return lm + '?' + search()

@guidance(stateless=True)
def search(lm):

    return lm + searchparameter() + zero_or_more('&' + searchparameter())

@guidance(stateless=True)
def searchparameter(lm):

    return lm + string() + select(['', '=' + select([string(), DIGITS(), HEX()])])

@guidance(stateless=True)
def string(lm):

    return lm + select([
        STRING(), DIGITS()
    ])

@guidance(stateless=True)
def DIGITS(lm):

    return lm + one_or_more(regex(r'[0-9]'))

@guidance(stateless=True)
def HEX(lm):

    return lm + one_or_more('%' + regex(r'[a-fA-F0-9]') + regex(r'[a-fA-F0-9]'))

@guidance(stateless=True)
def STRING(lm):

    return lm + select([
        regex(r'[a-zA-Z~0-9]'), HEX()
    ]) + zero_or_more(select([
        regex(r'[a-zA-Z0-9.+-]'), HEX()
    ]))

@guidance(stateless=True)
def WS(lm):

    return lm + one_or_more(regex(r'[\r\n]'))