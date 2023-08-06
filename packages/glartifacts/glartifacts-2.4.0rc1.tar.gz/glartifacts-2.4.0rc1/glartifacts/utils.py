import functools
from datetime import datetime

class OutputSettings():
    def __init__(self, humanize, delimiter):
        self.humanize = humanize
        self.delimiter = delimiter

        # Use machine format when a custom delimiter is specified
        if self.delimiter:
            self.humanize = False

    @classmethod
    def from_args(cls, args):
        return cls(
            not args.machine_readable,
            args.delimiter,
            )

def indent(val, amount=2):
    if not val:
        return val
    space = " "*amount
    return val.strip().replace("\n", "\n"+space)

def tabulate(heading, rows, display_transforms=None, totals=None, sortby=None, settings=None):
    total_row = []
    if settings.humanize and totals:
        for i, aggregate in enumerate(totals):
            if not aggregate:
                total_row.append('')
                continue

            total_row.append(aggregate(r[i] for r in rows))

    if 'key' in sortby:
        sortby = [sortby]
    for term in sortby:
        rows.sort(key=term['key'], reverse=term.get('reverse', False))

    if not settings.humanize:
        heading = [h.upper() for h in heading]

    text_totals = transform_row(total_row, display_transforms)
    text_rows = [transform_row(r, display_transforms) for r in rows]
    col_sizes = autosize([heading]+text_rows+[text_totals])

    print_row(heading, col_sizes, settings.delimiter)
    if settings.humanize:
        print_spacer(col_sizes)

    for r in text_rows:
        print_row(r, col_sizes, settings.delimiter)

    if settings.humanize and totals:
        print_spacer(col_sizes)
        print_row(text_totals, col_sizes, settings.delimiter)

def transform_row(row, transforms):
    text_row = []
    for i, col in enumerate(row):
        transform = (transforms[i] if transforms else None) or str
        text_row.append(transform(col))

    return text_row

def print_row(row, col_sizes, delimiter=None):
    if delimiter:
        print(delimiter.join(row))
        return

    for i, col in enumerate(row):
        print(col.ljust(col_sizes[i]), end="")
    print("")

def print_spacer(col_sizes):
    spacer = []
    for c in col_sizes:
        spacer.append("-"*(c-1))
    print_row(spacer, col_sizes)

def autosize(rows):
    sizes = []
    for r in rows:
        col_count = len(r) - len(sizes)
        if col_count > 0:
            sizes.extend([0]*col_count)

        for i, col in enumerate(r):
            col = str(col)
            if len(col) >= sizes[i]:
                sizes[i] = len(col)+1

    return sizes

def humanize_id(value):
    return '#'+str(value) if value else ''

def machine_id(value):
    return str(value) if value else ''

def humanize_size(size):
    if size is None:
        return ''

    size_format = '{:.2f} {}'
    for unit in ['B', 'KiB', 'MiB']:
        if size < 1024:
            return size_format.format(size, unit)

        size = size / 1024

    return size_format.format(size, "GiB")

def machine_size(size):
    return str(size) if size is not None else ""

def humanize_datetime(ts):
    if not isinstance(ts, datetime):
        return ''

    return ts.date().isoformat() + " " + ts.strftime('%X')

def machine_datetime(ts):
    return str(int(ts.timestamp())) if isinstance(ts, datetime) else ""

def memoize(key=None):
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def cacheable(*args):
            # reduce arguments using cache key callable
            cache_args = key(args) if key else args

            cache_key = '|'.join([str(a) for a in cache_args])
            if cache_key in cache:
                return cache[cache_key]

            result = func(*args)
            cache[cache_key] = result
            return result

        return cacheable

    return decorator
