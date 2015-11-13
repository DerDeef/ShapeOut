#!/usr/bin/python
# -*- coding: utf-8 -*-
""" ShapeOut - wx and chaco plot components

"""
from __future__ import division, print_function

import chaco.api as ca
import cv2
import enable.api as ea

import numpy as np
import os
import platform
import wx
import wx.lib.agw.flatnotebook as fnb

from .. import tlabwrap


class PlotNotebook(fnb.FlatNotebook):
    """
    Flatnotebook class
    """
    def __init__(self, parent):
        """Constructor"""
        style = fnb.FNB_RIBBON_TABS|\
                fnb.FNB_TABS_BORDER_SIMPLE|fnb.FNB_NO_X_BUTTON|\
                fnb.FNB_NO_NAV_BUTTONS|fnb.FNB_NODRAG
        # Bugfix for Mac
        if platform.system().lower() in ["windows", "linux"]:
            style = style|fnb.FNB_HIDE_ON_SINGLE_TAB
        self.fnb = fnb.FlatNotebook.__init__(self, parent, wx.ID_ANY,
                                             agwStyle=style)


class PlotPanel(wx.Panel):
    """"""
    def __init__(self, parent, frame):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        
        self.frame = frame
        self.config = frame.config
        self.notebook = PlotNotebook(self) 

        self.mainplot = MainPlotArea(self.notebook, frame)
        self.AddPanel(self.mainplot, "Main Plot")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
    
    def AddPanel(self, panel, name):
        self.notebook.AddPage(panel, _(name))

    def Plot(self, anal=None):
        """
        convenience function that calls MainPlotArea.Plot
        """
        self.mainplot.Plot(anal)


class MainPlotArea(wx.Panel):
    def __init__(self, parent, frame):
        self.frame = frame
        wx.Panel.__init__(self, parent, -1)

        self.plot_window = ea.Window(self)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)

        #self.mainplot=self

    def Plot(self, anal=None):
        self._lastplot = -1
        self._lastselect = -1
        self._lasthover = -1
        
        if anal is not None:
            self.analysis = anal
        
        anal = self.analysis
        
        xax, yax = anal.GetPlotAxes()
        
        rows, cols, lcc, lll = anal.GetPlotGeometry()
        
        numplots = rows * cols

        container = ca.GridPlotContainer(
                                      shape = (rows,cols),
                                      spacing = (0,0),
                                      padding = (0,0,0,0),
                                      valign = 'top',
                                      bgcolor = 'white',
                                      fill_padding = True,
                                      use_backbuffer = True)
                                      

        maxplots = min(len(anal.measurements), numplots)

        self.index_datasources = list()

        # dictionary mapping plot objects to data for scatter plots
        scatter2measure = {}

        c_plot = 0
        legend_plotted = False
        range_joined = list()
        for j in range(rows):
            for i in range(cols):
                #k = i + j*rows
                if (i == cols-1 and j == 0 and lcc == 1):
                    # Contour plot in upper right corner
                    aplot = tlabwrap.CreateContourPlot(anal.measurements,
                                               xax=xax, yax=yax,
                                               levels=[0.5,0.95])
                    range_joined.append(aplot)
                elif (i == cols-1 and j == 1 and lll == 1):
                    # Legend plot below contour plot
                    aplot = tlabwrap.CreateLegendPlot(anal.measurements)
                    legend_plotted = True
                elif c_plot < maxplots:
                    # Scatter Plot
                    aplot = tlabwrap.CreateScatterPlot(anal.measurements[c_plot],
                                               xax=xax, yax=yax)
                    scatter2measure[aplot] = anal.measurements[c_plot]
                    range_joined.append(aplot)
                    c_plot += 1
                    # Retrieve the plot hooked to selection tool
                    my_plot = aplot.plots["my_plot"][0]
                    # Set up the trait handler for the selection
                    id_ds = my_plot.index

                    id_ds.on_trait_change(self.OnMouseScatter,
                                          "metadata_changed")
                    self.index_datasources.append((aplot, id_ds))
                elif (not legend_plotted and lll == 1 and rows == 1) :
                    # Legend plot in next free window
                    aplot = tlabwrap.CreateLegendPlot(anal.measurements)
                    legend_plotted = True
                else:
                    # dummy plot
                    aplot = ca.Plot()
                    aplot.aspect_ratio = 1
                    aplot.range2d.low = (0,0)
                    aplot.range2d.high = (1,1)
                    aplot.y_axis = None
                    aplot.x_axis = None
                    aplot.x_grid = None
                    aplot.y_grid = None
                
                container.add(aplot)

        # connect all plots' panning and zooming
        comp = None
        for comp in range_joined[1:]:
            comp.range2d = container.components[0].range2d
            comp.components[-1].marker_size = container.components[0].components[-1].marker_size
        
        # Connect range with displayed range
        if comp is not None:
            comp.range2d.on_trait_change(self.OnPlotRangeChanged)

        container.padding = 10
        container.padding_left = 30
        container.padding_right = 5

        (bx, by) = container.outer_bounds
        container.set_outer_bounds(0, bx)
        container.set_outer_bounds(1, by)
        self.container = container
        self.scatter2measure = scatter2measure

        self.plot_window.component = container

        self.plot_window.redraw()


    def OnPlotRangeChanged(self, obj, name, new):
        """ Is called by traits on_trait_change for plots
            
        Updates the data in panel top
        """
        ctrls = self.frame.PanelTop.page_plot.GetChildren()
        #samdict = self.analysis.measurements[0].\
        #                               Configuration["Plotting"].copy()
        newfilt = dict()
 
        xax, yax = self.analysis.GetPlotAxes()
 
        # identify controls via their name correspondence in the cfg
        for c in ctrls:
            name = c.GetName()
            if   name == xax+" Min":
                ol0 = float("{:.4e}".format(obj.low[0]))
                newfilt[name] = ol0
                c.SetValue(unicode(ol0))
            elif name == xax+" Max":
                oh0 = float("{:.4e}".format(obj.high[0]))
                newfilt[name] = oh0
                c.SetValue(unicode(oh0))
            elif name == yax+" Min":
                ol1 = float("{:.4e}".format(obj.low[1]))
                newfilt[name] =ol1
                c.SetValue(unicode(ol1))
            elif name == yax+" Max":
                oh1 = float("{:.4e}".format(obj.high[1]))
                newfilt[name] = oh1
                c.SetValue(unicode(oh1))
                

        cfg = { "Plotting" : newfilt }
        self.analysis.SetParameters(cfg)

    def OnMouseScatter(self):
        # TODO:
        # - detect when hover is stuck
        # - display additional information in plot
        
        if not hasattr(self, "_lasthover"):
            self._lasthover = False
        if not hasattr(self, "_lastselect"):
            self._lastselect = False
        if not hasattr(self, "_lastplothover"):
            self._lastplothover = False
        if not hasattr(self, "_lastplotselect"):
            self._lastplotselect = False
        
        thisplothover = None
        thisplotselect = None
        thissel = None
        thishov = None
        for (aplot, id_ds) in self.index_datasources:
            hov = id_ds.metadata.get("hover", [])
            sel = id_ds.metadata.get("selections", [])
            # Get hover data
            if len(hov) > 0:
                thisplothover = aplot
                thishov = hov[0]
                # Get select data
                if len(sel) != 0:
                    thisplotselect = aplot
                    thissel = sel[0]
        
        if thishov is None:        
            for (aplot, id_ds) in self.index_datasources:
                if self._lastplothover is aplot:
                    thisplothover = aplot

        for (aplot, id_ds) in self.index_datasources:
            my_plot = aplot.plots["my_plot"][0]
            # Show or hide overlays:
            if thisplothover is aplot:
                my_plot.overlays[0].visible = True
            else:
                my_plot.overlays[0].visible = False

        action = False

        if thisplotselect is not None:
            if self._lastplotselect is thisplotselect:
                # We are in the same plot
                if self._lastselect != thissel:
                    # We have a different cell
                    action = True
            else:
                # We have a new plot
                action = True


        if action:
            # Get the cell and plot it
            dataset = self.scatter2measure[thisplotselect]
            # these are all cells that were plotted
            plotfilterid = np.where(dataset._plot_filter)[0]
            # this is the plot selection
            plot_sel = plotfilterid[thissel]
            # these are all the filtered cells
            filterid = np.where(dataset._filter)[0]
            actual_sel = filterid[plot_sel]
            
            #vfile = os.path.join(dataset.fdir, dataset.video)
            os.chdir(dataset.fdir)
            video = cv2.VideoCapture(dataset.video)
            totframes = video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
            
            video.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, actual_sel-1)
            
            flag, cellimg = video.read()

            if flag:
                # add contour in red
                if len(cellimg.shape) == 2:
                    # convert grayscale to color
                    cellimg = np.tile(cellimg, [3,1,1]).transpose(1,2,0)
                
                
                r = cellimg[:,:,0]
                b = cellimg[:,:,1]
                g = cellimg[:,:,2]
                
                # only do this if there was a contour file loaded
                if len(dataset.contours) > 0:
                    contours = dataset.contours[dataset.frame[actual_sel]]
                    
                    r[contours[:,1], contours[:,0]] = 255
                    b[contours[:,1], contours[:,0]] = 0
                    g[contours[:,1], contours[:,0]] = 0
                
                self.frame.PanelImage.ShowImage(cellimg)
            
            video.release()
            print("Frame {} / {}".format(actual_sel, totframes))


        if not thisplothover is None:
            self._lastplothover = thisplothover
        if not thisplotselect is None:
            self._lastplotselect = thisplotselect
        self._lasthover = thishov
        self._lastselect = thissel

    def CheckTightLayout(self):
        """ Determine whether a call to tight_layout is necessary and
            (do not) do it.
        """
        if not self.tight_layout:
            self.figure.tight_layout()
            self.tight_layout = True
        #self.figure.tight_layout(pad=0.5, h_pad=0, w_pad=0)