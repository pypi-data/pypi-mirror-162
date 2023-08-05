# -*- coding:utf-8 -*-

class EmptySerp(Exception):
    pass


class YandexParserError(Exception):
    pass


class YandexParserBadContentError(Exception):
    pass


class YandexParserContentError(YandexParserError):
    pass


class YandexParserContextError(YandexParserError):
    pass
