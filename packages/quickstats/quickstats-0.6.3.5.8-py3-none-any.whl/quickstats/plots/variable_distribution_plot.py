from typing import Optional, Union, Dict, List

import pandas as pd
import numpy as np

from matplotlib import colors
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

from quickstats.plots import AbstractPlot
from quickstats.plots.template import single_frame, parse_styles, create_transform
from quickstats.utils.common_utils import combine_dict


class VariableDistributionPlot(AbstractPlot):
    
    def __init__(self, data_map:Dict[str, pd.DataFrame], plot_options:Dict[str, Dict],
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None,
                 config:Optional[Dict]=None):
        """
        Arguments:
            plot_options: dicionary
                A dictionary containing plot options for various group of samples.
                Format: { <sample_group>: {
                            "samples": <list of sample names>,
                            "style": <options in mpl.hist>},
                            "type": "hist" or "errorbar"
                          ...}
             
        """
        self.data_map = data_map
        self.plot_options = plot_options
        super().__init__(styles=styles,
                         analysis_label_options=analysis_label_options,
                         config=config)
    
    def draw(self, column_name:str, weight_name:Optional[str]="weight",
             xlabel:str="", ylabel:str="Fraction of Events / {bin_width:.2f}",
             nbins:int=25, xmin:Optional[float]=None, xmax:Optional[float]=None,
             ypad:float=0.4,  rescale_by:Optional[float]=None):
        """
        
        Arguments:
            column_name: string, default = "score"
                Name of the variable in the dataframe.
            weight_name: (optional) string, default = "weight"
                If specified, normalize the histogram by the "weight_name" variable
                in the dataframe.
            xlabel: string, default = "Score"
                Label of x-axis.
            ylabel: string, default = "Fraction of Events / {bin_width}"
                Label of y-axis.
            boundaries: (optional) list of float
                If specified, draw score boundaries at given values.
            nbins: int, default = 25
                Number of histogram bins.
            xmin: (optional) float
                Minimum value of x-axis.
            xmax: (optional) float
                Maximum value of x-axis.
            rescale_by: (optional) float
                Rescale variable values by a factor.
        """
        ax = self.draw_frame()
        data_xmin = None
        data_xmax = None
        for key in self.plot_options:
            samples = self.plot_options[key]["samples"]
            plot_style  = self.plot_options[key].get("style", {})
            df = pd.concat([self.data_map[sample] for sample in samples], ignore_index = True)
            if weight_name is not None:
                norm_weights = df[weight_name] / df[weight_name].sum()
            else:
                norm_weights = None
            plot_type = self.plot_options[key].get("type", "hist")
            x = df[column_name].values
            if rescale_by is not None:
                x = x * rescale_by
            if data_xmin is None:
                data_xmin = np.min(x)
            else:
                data_xmin = min(data_xmin, np.min(x))
            if data_xmax is None:
                data_xmax = np.max(x)
            else:
                data_xmax = max(data_xmax, np.max(x))
            if plot_type == "hist":
                y, x, _ = ax.hist(x, nbins, range=(xmin, xmax),
                                  weights=norm_weights, **plot_style, zorder=-5)
            elif plot_type == "errorbar":
                n_data = len(x)
                norm_weights = np.ones((n_data,)) / n_data
                y, bins = np.histogram(x, nbins, weights=norm_weights)
                bin_centers  = 0.5*(bins[1:] + bins[:-1])
                from quickstats.maths.statistics import get_poisson_interval
                yerr = get_poisson_interval(y * n_data)
                ax.errorbar(bin_centers, y, 
                            yerr=(yerr["lo"] / n_data, yerr["hi"] / n_data),
                            **plot_style)
            else:
                raise RuntimeError(f'unknown plot type: {plot_type}')
        if xmin is None:
            xmin = data_xmin
        if xmax is None:
            xmax = data_xmax
        bin_width = (xmax - xmin) / nbins
        ylabel = ylabel.format(bin_width=bin_width)
        
        self.draw_axis_components(ax, xlabel=xlabel, ylabel=ylabel)
        self.set_axis_range(ax, xmin=xmin, xmax=xmax, ypad=ypad)

        handles, labels = ax.get_legend_handles_labels()
        new_handles = [Line2D([], [], c=h.get_edgecolor(), linestyle=h.get_linestyle(),
                       **self.styles['legend_Line2D']) if isinstance(h, Polygon) else h for h in handles]
        ax.legend(handles=new_handles, labels=labels, **self.styles['legend'])
        return ax