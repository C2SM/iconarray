"""Formatoption that adds rivers to mapplot, mapvector, and mapcombined plots created by psyplot."""

import psyplot.project as psy
from cartopy.feature import NaturalEarthFeature
from psyplot.plotter import BEFOREPLOTTING, Formatoption


class Rivers(Formatoption):
    """Add rivers to mapplot, mapvector, and mapcombined plots created by psyplot."""

    #: the default value for the formatoption
    default = None
    priority = BEFOREPLOTTING
    name = "Display Rivers"

    def validate(self, value):
        """Validate and convert the input to boolean."""  # noqa
        if not isinstance(value, bool):
            return bool(value)
        return value

    def initialize_plot(self, value):
        """Initialize the plot with or without rivers."""  # noqa
        rivers10m = NaturalEarthFeature("physical", "rivers_lake_centerlines", "10m")
        self.rivers = None
        if value is True and self.rivers is None:
            self.rivers = self.ax.add_feature(
                rivers10m, linewidth=0.5, edgecolors="black", facecolors="none"
            )
        elif value is False:
            self._remove()

    def update(self, value):
        """
        Update plot to add (or remove) rivers.

        Parameters
        ----------
        value: bool
            True to add rivers, and False to remove.
        """
        rivers10m = NaturalEarthFeature("physical", "rivers_lake_centerlines", "10m")
        if value is True:
            self.rivers = self.ax.add_feature(
                rivers10m, linewidth=0.1, edgecolors="black", facecolors="none"
            )
        elif value is False or value is None:
            self._remove()

    def _remove(self):
        if self.rivers is None:
            return
        self.rivers.remove()
        del self.rivers


psy.plot.mapplot.plotter_cls.rivers = Rivers("rivers")
psy.plot.mapvector.plotter_cls.rivers = Rivers("rivers")
psy.plot.mapcombined.plotter_cls.rivers = Rivers("rivers")
