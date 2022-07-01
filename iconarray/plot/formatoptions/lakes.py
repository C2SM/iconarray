"""Formatoption that adds lakes to mapplot, mapvector, and mapcombined plots created by psyplot."""

import psyplot.project as psy
from cartopy.feature import GSHHSFeature
from psyplot.plotter import Formatoption


class Lakes(Formatoption):
    """Add lakes to mapplot, mapvector, and mapcombined plots created by psyplot."""

    #: the default value for the formatoption
    default = True

    def validate(self, value):
        """Validate and convert the input to boolean."""  # noqa
        return bool(value)

    def update(self, value):
        """
        Update plot to add (or remove) lakes.

        Parameters
        ----------
        value: bool
            True to add lakes, False to remove.
        """
        # method to update the plot
        if value is True:
            self.lakes = self.ax.add_feature(
                GSHHSFeature(scale="high", levels=[2], alpha=0.8, linewidth=0.4)
            )
        else:
            self._remove()

    def _remove(self):
        if hasattr(self, "lakes"):
            self.lakes.remove()
            del self.lakes


psy.plot.mapplot.plotter_cls.lakes = Lakes("lakes")
psy.plot.mapvector.plotter_cls.lakes = Lakes("lakes")
psy.plot.mapcombined.plotter_cls.lakes = Lakes("lakes")
