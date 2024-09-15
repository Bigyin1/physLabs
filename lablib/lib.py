import matplotlib.pyplot as plt
import numpy as np

import pint
import pint_pandas

import pandas as pd

pd.options.mode.copy_on_write = True


class LabCtx:
    _ureg = pint.UnitRegistry()
    _Q = _ureg.Quantity
    pint_pandas.PintType.ureg = _ureg

    _ureg.enable_contexts("Gaussian")

    def __init__(self, exelPath: str) -> None:
        self._labData = pd.read_excel(exelPath, sheet_name=None, header=[0, 1])

    def _getTable(self, name: str) -> pd.DataFrame:
        return self._labData[name].pint.quantify(level=-1)

    def _toLatexFormat(self):
        self._ureg.default_format = "Lx"

    def _toDefaultFormat(self):
        self._ureg.default_format = "P"


Q = LabCtx._Q

UR = LabCtx._ureg


def q_for_eval(magnitude, unit=None):
    return Q(magnitude, unit)


class LabTable:
    def __init__(
        self, ctx: LabCtx, name: str = "", table: pd.DataFrame = pd.DataFrame(data={})
    ) -> None:

        self.ctx = ctx

        if not table.empty:
            self._table = table
            return

        self._table = self.ctx._getTable(name)

    def toLatex(
        self, file: str, columnsRen={}, caption="", float_format="%.2f", toStdout=False
    ) -> None:
        self.ctx._toLatexFormat()

        self._table.rename(columns=columnsRen).pint.dequantify().to_latex(
            file,
            index=False,
            caption=caption,
            position="H",
            float_format=float_format,
        )

        self.ctx._toDefaultFormat()

        if toStdout:
            print(self._table.rename(columns=columnsRen).pint.dequantify())

    def setColUnits(self, col: str, u: pint.Unit | str):
        self._table[col] = self._table[col].pint.to(u)
        return self

    def getColUnits(self, col: str) -> pint.Unit:
        return self._table[col].pint.units

    def addCol(self, col: str, data: pd.Series) -> None:
        self._table[col] = data

    def col(self, col: str) -> pd.Series:
        return self._table[col]

    def colQuantity(self, col: str) -> pint.Quantity:
        return self._table[col].values.quantity

    def colRaw(self, col: str) -> list[float]:
        return self._table[col].values.quantity.magnitude

    def query(self, q: str):
        return LabTable(self.ctx, table=self._table.query(q))

    def printPretty(self):
        print(self._table)


class LabPlot:
    def __init__(self, file: str, xlbl: str, ylbl: str) -> None:
        self.file = file

        self.xlbl = xlbl
        self.ylbl = ylbl

    def __enter__(self):
        self.fig, self.axis = plt.subplots(figsize=(12, 10), dpi=100)
        self.axis.grid(True)

        self.axis.set_xlabel(self.xlbl, fontsize=20)
        self.axis.set_ylabel(self.ylbl, fontsize=20)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.axis.legend()
        self.fig.savefig(self.file)


def plotMNK(ax: plt.Axes, x_units, y_units, name, scatter=False, prec=5) -> list:
    x = x_units
    y = y_units

    fit, pcov = np.polyfit(x, y, 1, full=False, cov=True)
    perr = np.sqrt(np.diag(pcov))
    poly = np.poly1d(fit)

    x = np.linspace(min(x), max(x), 50)
    ax.plot(
        x,
        poly(x),
        label=f"{name}: ${fit[0]:.{prec}f}\\pm{perr[0]:.{prec}f}$",
    )

    if scatter:
        ax.scatter(x_units, y_units)

    return fit
