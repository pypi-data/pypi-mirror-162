import csv

from itertools import zip_longest

from .frame import ColumnarFrame
from .utils import skip_footer
from .utils import make_key


def read_csv(
        filename,
        encoding='utf-8',
        delimiter=',',
        skiprows=0,
        skipfooter=0,
        header=True,
        quotechar='"',
        doublequote=True,
        escapechar=None,
        ):

    with open(filename, 'r', encoding=encoding) as f:
        csvdata = csv.reader(
            f,
            delimiter=delimiter,
            quotechar=quotechar,
            doublequote=doublequote,
            escapechar=escapechar)

        rit = iter(csvdata)
        if skiprows > 0:
            for _ in range(skiprows):
                next(rit)

        data = None
        if header:
            row = next(rit)
            head = [make_key(idx, key) for idx, key in enumerate(row)]
            data = {key: [] for key in head}

        for row in rit:
            if data is None:
                head = [str(i) for i in range(len(row))]
                data = {key: [] for key in head}

            for key, value in zip_longest(head, row):
                if key is None:
                    continue
                if value is not None and len(value) == 0:
                    value = None
                data[key].append(value)

    data = skip_footer(data, skipfooter)

    return ColumnarFrame(data)
