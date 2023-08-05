from openpyxl import load_workbook
from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime

from .frame import ColumnarFrame
from .utils import skip_footer
from .utils import make_key


def read_excel(
    filename,
    file_type='xlsx',
    sheet=None,
    skiprows=0,
    skipfooter=0,
    header=True,
    datefmt=None,
):
    if file_type == 'xls':
        return read_xls(filename, sheet, skiprows, skipfooter, header, datefmt)
    if file_type == 'xlsx':
        return read_xlsx(filename, sheet, skiprows, skipfooter, header, datefmt)
    raise RuntimeError('Unknown file type.')


def read_xlsx(filename, sheet, skiprows, skipfooter, header, datefmt):
    def convert(cell, datefmt):
        if cell is not None and cell.value is None:
            return None

        if cell.data_type == 's':
            return str(cell.value)
        if cell.data_type == 'd':
            if datefmt is None:
                return str(cell.value)
            return cell.value.strftime(datefmt)
        if cell.data_type == 'n':
            return str(cell.value)
        if cell.data_type == 'b':
            return str(cell.value)

        raise RuntimeError('Unknown data type.')

    wb = load_workbook(filename=filename)
    if sheet is None:
        ws = wb.active
    else:
        ws = wb[sheet]

    data = {}
    for idx, r in enumerate(ws.columns):
        if skiprows > 0:
            rit = iter(r[skiprows:])
        else:
            rit = iter(r)
        if header:
            key = make_key(idx, next(rit).value)
        else:
            key = str(idx)

        data[key] = [convert(c, datefmt) for c in rit]

    data = skip_footer(data, skipfooter)

    return ColumnarFrame(data)


def read_xls(filename, sheet, skiprows, skipfooter, header, datefmt):
    def convert(cell, datefmt, datemode):
        if cell is not None and cell.value is None:
            return None

        if cell.ctype == 0:  # empty
            return None
        if cell.ctype == 1:  # string
            return cell.value
        if cell.ctype == 2:  # float
            return str(cell.value)
        if cell.ctype == 3:  # date
            dt = xldate_as_datetime(cell.value, datemode)
            if datefmt is None:
                return str(dt)
            return dt.strftime(datefmt)
        if cell.ctype == 4:  # boolean
            return 'True' if cell.value == 1 else 'False'
        if cell.ctype == 5:  # error
            return str(cell.value)
        if cell.ctype == 6:  # blank
            return None

        raise RuntimeError('Unknown data type.')

    wb = open_workbook(filename)
    if sheet is None:
        ws = wb.sheets()[0]
    else:
        ws = wb.sheet_by_name(sheet)

    data = {}
    for idx in range(ws.ncols):
        columns = ws.col(idx)
        if skiprows > 0:
            rit = iter(columns[skiprows:])
        else:
            rit = iter(columns)
        if header:
            key = make_key(idx, next(rit).value)
        else:
            key = str(idx)

        data[key] = [convert(c, datefmt, wb.datemode) for c in rit]

    data = skip_footer(data, skipfooter)

    return ColumnarFrame(data)
