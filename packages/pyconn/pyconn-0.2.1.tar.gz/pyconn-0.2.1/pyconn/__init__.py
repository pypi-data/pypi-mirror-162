import logging
import numpy

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s',
                              '%Y-%m-%d %H:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def to_sym(s):
    return numpy.string_(s, encoding='utf-8')


def to_sym_list(arr):
    """
    convert np.array[object] to np.array[np.string_ with utf-8]
    :param arr: df['col'].values
    :return: np.string_ with utf-8
    """
    if isinstance(arr, list):
        arr = numpy.array(arr)
    return numpy.char.encode(arr.astype(np.unicode_), encoding='utf-8')


def to_date(dt):
    return dt.astype('M8[D]')
