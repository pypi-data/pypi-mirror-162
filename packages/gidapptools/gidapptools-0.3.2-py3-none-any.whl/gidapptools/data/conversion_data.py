NANOSECONDS_IN_SECOND: int = 1_000_000_000


RAW_STRING_TRUE_VALUES = {'yes',
                          'y',
                          '1',
                          'true',
                          '+'}

RAW_STRING_FALSE_VALUES = {'no',
                           'n',
                           '0',
                           'false',
                           '-'}


STRING_TRUE_VALUES = {str(value).casefold() for value in RAW_STRING_TRUE_VALUES}

STRING_FALSE_VALUES = {str(value).casefold() for value in RAW_STRING_FALSE_VALUES}


FILE_SIZE_SYMBOL_DATA = [('K', 'Kilo'),
                         ('M', 'Mega'),
                         ('G', 'Giga'),
                         ('T', 'Tera'),
                         ('P', 'Peta'),
                         ('E', 'Exa'),
                         ('Z', 'Zetta'),
                         ('Y', 'Yotta')]


RAW_TIMEUNITS = [('nanosecond', 'ns', 1 / NANOSECONDS_IN_SECOND, []),
                 ("microsecond", "us", (1 / 1000) / 1000, ["mi", "mis", "mü", "müs", "μs"]),
                 ('millisecond', 'ms', 1 / 1000, []),
                 ('second', 's', 1, ["sec"]),
                 ('minute', 'm', 60, ["min", "mins"]),
                 ('hour', 'h', 60 * 60, []),
                 ('day', 'd', 60 * 60 * 24, []),
                 ('week', 'w', 60 * 60 * 24 * 7, []),
                 ("year", "y", (60 * 60 * 24 * 7 * 52) + (60 * 60 * 24), ["a"])]
