from .frame import ColumnarFrame


def concat(cf1, cf2):
    if cf1.columns != cf2.columns:
        raise RuntimeError('different columns')

    data = {k: v.to_list() + cf2[k].to_list() for k, v in cf1.data.items()}
    return ColumnarFrame(data)
