"""Formatoption that adds customized text to mapplot, mapvector, and mapcombined plots created by psyplot."""

import psyplot.project as psy
from psyplot.plotter import Formatoption


class CustomText(Formatoption):
    """
    Add customized text to mapplot, mapvector, and mapcombined plots created by psyplot.

    This was created as an example custom formatoption, and serves not much use. Can be improved.
    """

    #: the default value for the formatoption
    default = False

    def update(self, value):
        """Update the plot with text."""  # noqa
        if type(value) is str:
            if hasattr(self, "text"):
                self._remove()
            self.text = self.ax.text(
                0.0,
                -0.15,
                value,
                fontsize="xx-large",
                # ha='right', va='top',   # text alignment,
                transform=self.ax.transAxes,  # coordinate system transformation)
            )
        elif value in [False, None] and hasattr(self, "text"):
            self._remove()

    def _remove(self):
        if self.text is None:
            return
        self.text.remove()
        del self.text


psy.plot.mapplot.plotter_cls.customtext = CustomText("customtext")
psy.plot.mapvector.plotter_cls.customtext = CustomText("customtext")
psy.plot.mapcombined.plotter_cls.customtext = CustomText("customtext")
