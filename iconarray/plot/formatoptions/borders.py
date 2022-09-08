"""Formatoption that adds internal land borders on mapplot, mapvector, and mapcombined plots created by psyplot."""

import cartopy.feature as cf
import psyplot.project as psy
from psyplot.plotter import Formatoption


class Borders(Formatoption):
    """Add internal land borders on mapplot, mapvector, and mapcombined plots created by psyplot."""

    children = ["lsm"]
    default = {"color": "black", "linewidth": 1.0}

    def validate(self, value):
        """Validate and convert the input to boolean or dictionary."""  # noqa
        if type(value) is dict:
            return value
        else:
            return bool(value)

    def update(self, value):
        """
        Update plot to add (or remove) borders.

        Parameters
        ----------
        value: bool or Dict
            True to add black borders, False to remove, or Dict with color and linewidth properties eg. {"color": "black", "linewidth": 1.0}
        """
        if type(value) is dict:
            self.borders = self.ax.add_feature(
                cf.BORDERS, edgecolor=value["color"], linewidth=value["linewidth"]
            )
            self.lsm.update(
                {"res": "10m", "linewidth": value["linewidth"], "coast": value["color"]}
            )
        elif value is True:
            self.borders = self.ax.add_feature(
                cf.BORDERS, edgecolor="black", linewidth=1.0
            )
            self.lsm.update({"res": "10m", "linewidth": 1.0, "coast": "black"})
        else:
            if hasattr(self, "borders"):
                self.borders.remove()
                del self.borders
            if hasattr(self, "lsm"):
                self.lsm.update(None)


psy.plot.mapplot.plotter_cls.borders = Borders("borders")
psy.plot.mapvector.plotter_cls.borders = Borders("borders")
psy.plot.mapcombined.plotter_cls.borders = Borders("borders")
