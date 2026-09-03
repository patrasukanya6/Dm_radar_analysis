
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
import calendar
import xarray as xr
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import pandas as pd
import math
import os
import datetime
#from suntime import Sun, SunTimeException
import matplotlib as mpl
from HTI_plot_config import get_plot_config
from hti_plot_layout import create_plot_axes
from hti_plot_sun import plot_sunrise_sunset
from hti_plot_colorbar import create_plot_colorbar
from hti_plot_axes import format_plot_axes
from hti_plot_time import prepare_time_plot_data
from hti_plot_metadata import configure_plot_metadata


### -----creating the ideal time axis with one hour interval for the x-axis--------------------------------
TIME_i = [f"{hour:02d}:00" for hour in range(24)]	




def HTI_plot(fn,Input,**args):	
	"""Generate and save a time-height quicklook plot.

	The function opens the input NetCDF file, prepares the time and height
	coordinates, applies the configured plot style, and creates the main
	data plot with annotations and a colorbar. Figure layout, time handling,
	axis formatting, sunrise/sunset markers, metadata, and colorbar placement
	are delegated to the dedicated helper modules.

	Parameters
	----------
	fn : str
		Path to the input NetCDF file.
	Input : xarray.DataArray
		Variable to display in the time-height plot.
	**args
		Optional plot settings and layout flags. Configuration values such as
		``pathOutputPlots``, ``colormap``, ``Vmin``, and ``Vmax`` may be
		overridden here.

	Returns
	-------
	None
		The generated figure is saved to the configured output directory.
	"""

	
	# Open the input NetCDF dataset and derive its product title.
	#Vmin,Vmax,colormap=inspect.getargspec(func)
	dataset=xr.open_dataset(fn)
	title=fn.split('/')[-1].split('.')[0]

	# Load colormap, color limits, output path, and colorbar label.
	plot_config = get_plot_config(Input.name, title, args)
	pathOutputPlots = plot_config.output_path
	colormap = plot_config.colormap
	Vmin = plot_config.vmin
	Vmax = plot_config.vmax
	ColorbarLabel = plot_config.colorbar_label	

	time_notation, input1, TIME, xtick, xticklabels, date = prepare_time_plot_data(
		fn, dataset, Input, title, args, TIME_i
	)


	# Build the two-dimensional time-coordinate grid required by pcolor.
	time = np.broadcast_to(
    np.arange(input1.shape[0]),
    (input1.shape[1], input1.shape[0]),
)


	# Select the vertical coordinate: radar range or instrument height.

	if 'range' in dataset.coords:ht='range'
	else:ht='height'

	# Convert vertical coordinates from metres to kilometres.
	height=np.ones((input1.shape[0],input1.shape[1]))*dataset[ht].values/1000



	# Create the figure and axes according to the requested layout.
	fig, ax, row, col, subplot_pos = create_plot_axes(args)
	
	# Calculate and draw sunrise/sunset markers.
	ind1, ind2 = plot_sunrise_sunset(date, TIME, height, title, args)
	##------Main pcolor plot------------
	#print(input1.name)


	# Draw the main time-height plot.
	plot_config = get_plot_config(input1.name, title, args)
	colormap = plot_config.colormap
	Vmin = plot_config.vmin
	Vmax = plot_config.vmax
	ColorbarLabel = plot_config.colorbar_label
	pc=ax.pcolor(time.transpose(),height,input1,vmin=Vmin,vmax=Vmax,cmap=colormap)

	# Apply grid, ticks, limits, and missing-data shading.
	format_plot_axes(ax, dataset, input1, xtick, args, height)

	##--setting the axis linewidth and tick length and width			
	for axis in ['top','bottom','left','right']:ax.spines[axis].set_linewidth(1.5)
	ax.minorticks_on()
	ax.tick_params('both', length=7, width=1.2, which='major')
	ax.tick_params('both', length=5, width=.8, which='minor')
	box_text = "Kamacs= -1\nWmacs=-1.5\nxmacs=-5"
	if args.get('offset_corrected') or args.get('offset_corrected_zoom'):
		if subplot_pos==1:
			ax.text(
			0.98, 0.98, box_text,
			transform=ax.transAxes,
			fontsize=14,
			verticalalignment='top',
			horizontalalignment='right',
			bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
	
	# Add titles, labels, annotations, and determine the output filename.
	my_file = configure_plot_metadata(
		ax,
		fn,
		title,
		input1,
		date,
		time_notation,
		args,
		row,
		subplot_pos,
		xticklabels,
		ind1,
		ind2,
		locals().get("TITLE"),
	)
	cbaxes1, cb1 = create_plot_colorbar(
		fig, pc, args, row, subplot_pos, ColorbarLabel
	)
	
