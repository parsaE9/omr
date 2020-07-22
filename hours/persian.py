# coding: utf-8

from __future__ import unicode_literals

maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))
en_numbers = maketrans( '1234567890','۱۲۳۴۵۶۷۸۹۰')
numbers = maketrans('۱۲۳۴۵۶۷۸۹۰', '1234567890')
normalize_digits = lambda text: text.translate(numbers)
persian_numbers = lambda text: text.translate(en_numbers)
