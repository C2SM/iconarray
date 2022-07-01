"""Formatoption that adds a title to mapplot, mapvector, and mapcombined plots created by psyplot."""

import psyplot.project as psy
from psy_simple.base import TextBase
from psyplot.plotter import Formatoption


class StandardTitle(TextBase, Formatoption):
    """
    Add title to mapplot, mapvector, and mapcombined plots created by psyplot.

    The title includes information on variable plotted, and time/date of data.
    This was created as an example custom formatoption, and could be improved.
    """

    default = True

    @property
    def enhanced_attrs(self):  # noqa
        return self.get_fig_data_attrs()

    def validate(self, s):
        """Validate and convert the plot attributes to required format for update function."""  # noqa
        if s:
            try:
                zname = self.get_enhanced_attrs(self.data)["zname"]
                zvalue = self.get_enhanced_attrs(self.data)["z"]
                zdata = " on " + str(zname) + " " + str(zvalue)
            except Exception:
                zdata = ""
            return {
                "time": "%A %e %b %Y\n %d.%m.%Y %H:%M:%S",
                "details": (f"%(long_name)s" f"{zdata}"),
            }
        else:
            return False

    def update(self, s):
        r"""
        Update plot to add (or remove) title.

        Parameters
        ----------
        s: Dict
            eg { "time": "%A %e %b %Y\n %d.%m.%Y %H:%M:%S", "details": 2m Temperature on Height level 10") }
        """
        if type(s) is dict:
            self.standardtitle = [
                self.ax.set_title(
                    self.replace(s["time"], self.plotter.data, self.enhanced_attrs),
                    loc="right",
                ),
                self.ax.set_title(
                    self.replace(s["details"], self.plotter.data, self.enhanced_attrs),
                    loc="left",
                ),
            ]
            self._clear_other_texts()
        else:
            self.standardtitle = [
                self.ax.set_title("", loc="right"),
                self.ax.set_title("", loc="left"),
            ]

    def _clear_other_texts(self, remove=False):
        fig = self.ax.get_figure()
        # don't do anything if our figtitle is the only Text instance
        if len(fig.texts) == 1:
            return
        for i, text in enumerate(fig.texts):
            if text == self._text:
                continue
            if text.get_position() == self._text.get_position():
                if not remove:
                    text.set_text("")
                else:
                    del fig[i]


psy.plot.mapplot.plotter_cls.standardtitle = StandardTitle("standardtitle")
psy.plot.mapvector.plotter_cls.standardtitle = StandardTitle("standardtitle")
psy.plot.mapcombined.plotter_cls.standardtitle = StandardTitle("standardtitle")
