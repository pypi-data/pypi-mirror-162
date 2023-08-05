import pyarrow as pa


def to_str(v):
    return str(v) if v is not None else None


class Column:
    def __init__(self, value, rows=None):
        if isinstance(value, Column):
            self.value = pa.array(value.to_list())
        elif isinstance(value, pa.Array):
            self.value = pa.array(value.to_pylist())
        elif isinstance(value, list):
            self.value = pa.array(to_str(v) for v in value)
        elif rows is not None:
            self.value = pa.array([to_str(value)] * rows)
        else:
            raise RuntimeError('unknown data.')

    def __repr__(self):
        return self.value.__repr__()

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return self.value.to_pylist().__iter__()

    def to_list(self):
        return self.value.to_pylist()

    def unique(self):
        return Column(self.value.unique())

    def apply(self, *funcs):
        def call_chain(x):
            value = x
            for func in funcs:
                if isinstance(func, tuple):
                    value = func[0](value, *func[1:])
                else:
                    value = func(value)
            return value

        return Column([call_chain(d.as_py()) for d in self.value])

    def fillin(self, values, func):
        def call_func(x, val):
            if isinstance(func, tuple):
                value = func[0](x, *func[1:], val)
            else:
                value = func(x, val)
            return value

        return Column([
                call_func(x.as_py(), val)
                for x, val in zip(self.value, values)])
