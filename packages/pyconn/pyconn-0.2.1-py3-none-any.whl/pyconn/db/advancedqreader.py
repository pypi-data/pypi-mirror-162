import copy
import numpy
import pandas

from qpython import MetaData
from qpython._pandas import PandasQReader, Mapper
from qpython.qtype import QSYMBOL_LIST, QSYMBOL
from qpython.qcollection import qlist


class AdvancedQReader(PandasQReader):
    _reader_map = copy.copy(PandasQReader._reader_map)
    parse = Mapper(_reader_map)

    def _read_list(self, qtype):
        if qtype == QSYMBOL_LIST and self._options.pandas:
            self._buffer.skip()
            length = self._buffer.get_int()
            symbols = self._buffer.get_symbols(length)
            series = pandas.Series([s.decode('utf-8') for s in symbols], dtype=str)
            series.meta = MetaData(qtype=qtype)
            return series
        else:
            return PandasQReader._read_list(self, qtype)

    @parse(QSYMBOL)
    def _read_symbol(self, qtype=QSYMBOL):
        if self._options.pandas:
            return numpy.string_(self._buffer.get_symbol()).decode('utf-8')
        return PandasQReader._read_symbol(self, qtype)
