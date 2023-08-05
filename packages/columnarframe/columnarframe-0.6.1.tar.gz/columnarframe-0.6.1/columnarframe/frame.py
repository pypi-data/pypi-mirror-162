import csv

from collections import Counter

from .column import Column


class ColumnarFrame:
    def __init__(self, data=None):
        self.rows = -1
        self.data = {}
        if data is not None:
            for k, v in data.items():
                if isinstance(v, Column):
                    v = v.to_list()
                if isinstance(v, list):
                    self._check_length(v)
                self.data[k] = Column(v, self.rows)

    def _check_length(self, v):
        if self.rows == -1:
            self.rows = len(v)
        elif self.rows != len(v):
            raise RuntimeError('different row count.')

    @property
    def columns(self):
        return list(self.data.keys())

    def __getitem__(self, name):
        if isinstance(name, list):
            return ColumnarFrame({k: Column(self.data[k]) for k in name})
        return self.data[name]

    def __setitem__(self, name, value):
        if isinstance(value, Column):
            value = value.to_list()
        if isinstance(value, list):
            self._check_length(value)
        self.data[name] = Column(value, self.rows)

    def __repr__(self):
        return self.data.__repr__()

    def __len__(self):
        return self.rows if self.rows >= 0 else 0

    def rename(self, columns):
        ncf = ColumnarFrame(self.data)
        for f, t in columns.items():
            ncf.data[t] = ncf.data.pop(f)
        return ncf

    def to_csv(
            self, name, *, encoding='utf-8',
            sep=',', na_rep='', index=False, header=True,
            quoting=csv.QUOTE_MINIMAL, lineterminator='\n'):
        if isinstance(name, str):
            with open(name, 'w', encoding=encoding) as f:
                self._write_csv(f, sep, na_rep, index, header, quoting, lineterminator)
        else:
            self._write_csv(name, sep, na_rep, index, header, quoting, lineterminator)

    def _write_csv(self, stream, sep, na_rep, _, header, quoting, lineterminator):
        w = csv.writer(stream, delimiter=sep, quoting=quoting, lineterminator=lineterminator)
        if na_rep != '':
            iters = [
                map(
                    lambda x: x if x is not None else na_rep,
                    val.to_list()
                ) for val in self.data.values()]
        else:
            iters = [self.data[k] for k in self.data.keys()]

        if header:
            w.writerow(list(self.data.keys()))
        w.writerows(zip(*iters))

    def to_dict(self, orient='records'):
        columns = self.data.keys()
        data = [{c: d for c, d in zip(columns, d)} for d in zip(*self.data.values())]
        return data

    def assign(self, **kwargs):
        ncf = ColumnarFrame(self.data)
        for k, v in kwargs.items():
            ncf[k] = v
        return ncf

    def __iter__(self):
        data = iter(self.to_dict())
        return data

    def remove(self, func):
        data = {k: [] for k in self.data.keys()}
        for c in zip(*self.data.values()):
            row = {k: v for k, v in zip(self.data.keys(), c)}
            if not func(row):
                for k, v in row.items():
                    data[k].append(v)
        return ColumnarFrame(data)

    def counter(self, columns):
        cols = {c: self.data[c] for c in columns}
        return Counter(zip(*cols.values()))

    def unique(self, columns):
        cols = {c: self.data[c] for c in columns}
        return {c for c in zip(*cols.values())}

    def tree(self, keys, key_cols):
        data = {k: [] for k in keys}
        for c in self:
            key = tuple([c[col] for col in key_cols])
            data[key].append(c)
        return data

    def summary(self, keys, key_cols, **kwargs):
        data = self.tree(keys, key_cols)
        vals = {k: [] for k in [*key_cols, *kwargs.keys()]}

        for k, v in data.items():
            for kc, cv in zip(key_cols, k):
                vals[kc].append(cv)
            for kw, func in kwargs.items():
                vals[kw].append(func(v))

        return ColumnarFrame(vals)

    def build(self, keys, key_cols, cols, builder):
        data = self.tree(keys, key_cols)
        vals = {k: [] for k in [*key_cols, *cols]}

        for k, v in data.items():
            res = builder(k, v)
            for r in res:
                for kc, cv in zip(key_cols, k):
                    vals[kc].append(cv)
                for c in cols:
                    vals[c].append(r[c])

        return ColumnarFrame(vals)

    def sort(self, key):
        d = self.to_dict()
        d = sorted(d, key=key)
        d = {k: [v[k] for v in d] for k in self.data.keys()}

        return ColumnarFrame(d)
