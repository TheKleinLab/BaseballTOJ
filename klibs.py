#TODO: 1) App.query() is intermittently using accepted_list; look into & fix
import abc
import math
import sys
import os
import random
import time
import datetime
import traceback
import sqlite3
import hashlib
import re
import shutil
from copy import copy
import numpy
import thread
from functools import wraps
import OpenGL.GL as gl
from PIL import Image
from PIL import ImageFont
from PIL import ImageOps
import sdl2
import sdl2.ext

PYLINK_AVAILABLE = False
PARRALELL_AVAILABLE = False
try:
	import pylink
	PYLINK_AVAILABLE = True
except:
	print "Warning: Pylink library not found; eyetracking will not be available."
try:
	import parallel
	PARRALELL_AVAILABLE = True
except:
	print "Warning: Parallel library not found; eeg messaging will not be available."

#Allowable eye drift from mandatory fixation in degrees of visual angle
MAX_DRIFT_DEG = 3
#Minimum distance moved in degrees before eye movement counts as an initial saccade for response direction detection
INIT_SAC_DIST = 3

# lists of sdl2 key representations needed by klibs
MOD_KEYS = {"Left Shift": 1, "Right Shift": 2, "Left Ctrl": 64, "Rigth Ctrl": 128,  # todo: make __mod_keysyms
			"Left Alt": 256, "Right Alt": 512, "Left Command": 1024, "Right Command": 2048}
UI_METHOD_KEYSYMS = [sdl2.SDLK_q, sdl2.SDLK_c, sdl2.SDLK_p]

SCREEN_FLAGS = ["sdl_window_opengl", "sdl_window_shown", "sdl_window_fullscreen_desktop", "sdl_renderer_accelerated",
				"sdl_renderer_presentvsync"]

# string constants, included for tidyness below basically
DB = ".db"
EDF = "EDF"
BACK = ".backup"
LOG = "_log.txt"
SCHEMA = "_schema.sql"
INCH = "in"
CM = "cm"
NS_FOREGROUND = 1  # NumpySurface foreground layer
NS_BACKGROUND = 0  # NumpySurface background layer
MAX_WAIT = 9999999
TIMEOUT = "TIMEOUT"
NO_RESPONSE = "NO_RESPONSE"


class AppParams(object):
	initialized = False

	key_maps = dict()  # todo: create a class, KeyMapper, to manage key maps
	id_field_name = "participant_id"
	__random_seed = None
	collect_demographics = True
	__eye_tracking = False
	__exp_factors = None
	__instructions = False  # todo: instructions file
	__practicing = False
	__paused = False
	testing = False
	__default_alert_duration = 1
	default_alert_duration = 3  # seconds
	default_fill_color = (255, 255, 255)

	__project_name = None
	__database_filename = None
	__schema_filename = None
	__log_filename = None

	__asset_path = None
	__database_path = None
	__database_backup_path = None
	__edf_path = None
	__log_file_path = None
	__schema_file_path = None

	__monitor_x = None
	__monitor_y = None
	__diagonal_px = None
	__ppi = 96  # pixels-per-inch, varies between CRT & LCD screens
	__pixels_per_degree = None  # pixels-per-degree, ie. degree of visual angle
	__ppd = None  # pixels-per-degree, ie. degree of visual angle
	__screen_c = (None, None)
	__screen_ratio = None
	__screen_x = None
	__screen_y = None
	__screen_x_y = (None, None)
	__view_unit = "in"  # inch, not the preposition
	__view_distance = 56  # in centimeters, 56cm = in 1deg of visual angle per horizontal cm of screen

	__saccadic_velocity_threshold = 20
	__saccadic_acceleration_threshold = 5000
	__saccadic_motion_threshold = 0.15
	__default_font_size = 28

	__fixation_size = 1  # deg of visual angle
	__box_size = 1  # deg of visual angle
	__cue_size = 1  # deg of visual angle
	__cue_back_size = 1  # deg of visual angle
	__verbosity = 10  # Should hold a value between 0-10, with 0 being no errors and 10 being all errors

	__trials = 0
	__trials_per_block = 0
	__trials_per_practice_block = 0
	__blocks = 0
	__blocks_per_experiment = 0
	__practice_blocks_per_experiment = 0
	# tar_dur = 300   # todo: ask ross wtf this is
	# negative = 0   # todo: ask ross wtf this is
	# positive = 1   # todo: ask ross wtf this is
	# duration = 10000  # todo: ask ross wtf this is

	def __init__(self):
		pass

	def init_project(self):
		# todo: write checks in these setters to not overwrite paths that don't include asset_paths (ie. arbitrarily set)
		self.database_filename = self.project_name
		self.schema_filename = self.project_name
		self.log_filename = self.project_name
		self.edf_path = os.path.join(self.asset_path, EDF)  # todo: write edf management
		self.log_file_path = os.path.join(self.asset_path, self.log_filename)
		self.schema_file_path = os.path.join(self.asset_path, self.schema_filename)
		self.database_path = os.path.join(self.asset_path, self.database_filename)
		self.database_backup_path = self.database_path + BACK
		self.data_path = os.path.join(self.asset_path, "Data")
		self.incomplete_data_path = os.path.join(self.data_path, "incomplete")
		self.initialized = True
		return True

	def setup(self, project_name, asset_path):
		self.project_name = project_name
		self.asset_path = asset_path
		return self.init_project()

	@property
	def project_name(self):
		return self.__project_name

	@project_name.setter
	def project_name(self, project_name):
		if type(project_name) is str:
			self.__project_name = project_name
		else:
			raise TypeError("Argument 'project_name' must be a string.")

	@property
	def asset_path(self):
		return self.__asset_path

	@asset_path.setter
	def asset_path(self, asset_path):
		if type(asset_path) is str:
			if os.path.exists(asset_path):
				if os.path.isdir(asset_path):
					self.__asset_path = asset_path
				else:
					raise IOError("Argument 'asset_path' does not point to a directory.")
			else:
				raise IOError("Argument 'asset_path' does not point to valid  location on the file system.")
		else:
			raise TypeError("Argument 'asset_path' must be string indicating a the path to a writeable directory..")

	@property
	def database_filename(self):
		return self.__database_filename

	@database_filename.setter
	def database_filename(self, database_filename):
		if type(database_filename) is str:
			database_filename.rstrip(DB)
			self.__database_filename = database_filename + DB
		else:
			raise TypeError("Argument 'database_filename' must be a string.")

	@property
	def database_path(self):
		return self.__database_path

	@database_path.setter
	def database_path(self, database_path):
		if type(database_path) is str:
			self.__database_path = database_path  # eventually, check if the parent directory exists if the file doesn't
		# 	if os.path.exists(database_path):
		# 		if os.path.isdir(database_path):
		# 			raise IOError("Argument 'database_path' is a directory.")
		# 		else:
		# 	else:  # todo: try to create it
		# 		pass  # it may be created by the Database class initialization process
		# else:
		# 	raise TypeError("Argument 'database_path' must be a string and a valid file system location..")

	@property
	def database_backup_path(self):
		return self.__database_backup_path

	@database_backup_path.setter
	def database_backup_path(self, database_backup_path):
		if type(database_backup_path) is str:
			self.__database_backup_path = database_backup_path
		# 	if os.path.exists(database_backup_path):
		# 		if os.path.isdir(database_backup_path):
		# 			raise IOError("Argument 'database_backup_path' is a directory.")
		# 		else:
		# 	else:  # todo: try to create it
		# 		pass  # it may be created by the Database class initialization process
		# else:
		# 	raise TypeError("Argument 'database_backup_path' must be a string and a valid file system location..")

	@property
	def edf_path(self):
		return self.__edf_path

	@edf_path.setter
	def edf_path(self, edf_path):
		if type(edf_path) is str:
			if os.path.exists(edf_path):
				if os.path.isdir(edf_path):
					self.__edf_path = edf_path
				else:
					raise IOError("Argument 'edf_path' does not point to a directory.")
			else:
				raise IOError("Argument 'edf_path' does not point to valid  location on the file system.")
		else:
			raise TypeError("Argument 'edf_path' must be string indicating a the path to a writeable directory..")

	@property
	def data_path(self):
		return self.__data_path

	@data_path.setter
	def data_path(self, data_path):
		if type(data_path) is str:
			if os.path.exists(data_path):
				if os.path.isdir(data_path):
					self.__data_path = data_path
				else:
					raise IOError("Argument 'data_path' does not point to a directory.")
			else:
				raise IOError("Argument 'data_path' does not point to valid  location on the file system.")
		else:
			raise TypeError("Argument 'data_path' must be string indicating a the path to a writeable directory..")

	@property
	def incomplete_data_path(self):
		return self.__incomplete_data_path

	@incomplete_data_path.setter
	def incomplete_data_path(self, incomplete_data_path):
		if type(incomplete_data_path) is str:
			if os.path.exists(incomplete_data_path):
				if os.path.isdir(incomplete_data_path):
					self.__incomplete_data_path = incomplete_data_path
				else:
					raise IOError("Argument 'incomplete_data_path' does not point to a directory.")
			else:
				raise IOError("Argument 'incomplete_data_path' does not point to valid  location on the file system.")
		else:
			raise TypeError("Argument 'incomplete_data_path' must be string indicating a the path to a writeable directory..")


	@property
	def exp_factors(self):
		return self.__exp_factors


	@exp_factors.setter
	def exp_factors(self, factors):
		if type(factors) == dict:
			self.__exp_factors = factors
		elif factors is None:
			self.__exp_factors = None
		else:
			raise ValueError("Argument 'factors' must be a dict.")


	@property
	def log_filename(self):
		return self.__log_filename

	@log_filename.setter
	def log_filename(self, log_filename):
		if type(log_filename) is str:
			log_filename.rstrip(LOG)
			self.__log_filename = log_filename + LOG
		else:
			raise TypeError("Argument 'log_filename' must be a string.")

	@property
	def log_file_path(self):
		return self.__log_file_path

	@log_file_path.setter
	def log_file_path(self, log_file_path):
		if type(log_file_path) is str:
			if os.path.exists(log_file_path):
				if os.path.isdir(log_file_path):
					raise IOError("Argument 'log_file_path' is a directory.")
				else:
					self.__log_file_path = log_file_path
			else:  # todo: try to create it
				raise IOError("Argument 'log_file_path' does not point to a valid location on the file system.")
		else:
			raise TypeError(
				"Argument 'log_file_path' must be a string and a valid file system location..")

	@property
	def schema_filename(self):
		return self.__schema_filename
	
	@schema_filename.setter
	def schema_filename(self, schema_filename):
		if type(schema_filename) is str:
			schema_filename.rstrip(SCHEMA)
			self.__schema_filename = schema_filename + SCHEMA
		else:
			raise TypeError("Argument 'schema_filename' must be a string.")

	@property
	def schema_file_path(self):
		return self.__schema_file_path

	@schema_file_path.setter
	def schema_file_path(self, schema_file_path):
		if type(schema_file_path) is str:
			if os.path.exists(schema_file_path):
				if os.path.isdir(schema_file_path):
					raise IOError("Argument 'schema_file_path' is a directory.")
				else:
					self.__schema_file_path = schema_file_path
			else:  # todo: try to create it
				raise IOError("Argument 'schema_file_path' does not point to a valid location on the file system.")
		else:
			raise TypeError(
				"Argument 'schema_file_path' must be a string and a valid file system location..")

	@property
	def view_unit(self):
		return self.__view_unit
	
	@view_unit.setter
	def view_unit(self, unit):
		if type(unit) is str and unit in (INCH, CM):
			self.__view_unit = unit
		else:
			err_str = "Argument 'unit' must be one two strings, klibs.INCH ('{0}') or klibs.CM ('{1}')."
			raise TypeError(err_str.format(INCH, CM))
	
	@property
	def view_distance(self):
		return self.__view_distance
	
	@view_distance.setter
	def view_distance(self, distance):
		if type(distance) in (int, float) and distance > 0:
			self.__view_distance = distance
		else:
			raise TypeError("Argument 'distance' must be a positive number .")
	
	@property
	def monitor_x(self):
		return self.__monitor_x
	
	@monitor_x.setter
	def monitor_x(self, monitor_x):
		if type(monitor_x) in (int, float) > 0:
			self.__monitor_x = monitor_x
		else:
			raise TypeError("Argument 'monitor_x' must be a positive number.")
	
	@property
	def monitor_y(self):
		return self.__monitor_y

	
	@monitor_y.setter
	def monitor_y(self, monitor_y):
		if type(monitor_y) in (int, float) > 0:
			self.__monitor_y = monitor_y
		else:
			raise TypeError("Argument 'monitor_y' must be a positive number.")

	@property
	def screen_ratio(self):
		return self.__screen_ratio

	
	@screen_ratio.setter
	def screen_ratio(self, screen_ratio):
		if type(screen_ratio) is tuple and len(screen_ratio) == 2 and all(type(val) is int > 0 for val in screen_ratio):
			self.__screen_ratio = screen_ratio
		elif type(screen_ratio) is str:
			pass  # todo: keep a dict of common screen ratios and look this up rather than doing string manipulation
		else:
			raise TypeError("Argument 'screen_ratio' must be a tuple of two positive integers.")

	@property
	def blocks_per_experiment(self):
		return self.__blocks_per_experiment

	@blocks_per_experiment.setter
	def blocks_per_experiment(self, blocks_per_experiment):
		if type(blocks_per_experiment) is int and blocks_per_experiment >= 0:
			self.__blocks_per_experiment = blocks_per_experiment
		else:
			raise TypeError("Argument 'blocks_per_experiment' must be a positive integer.")


	@property
	def block_number(self):
		return self.__block_number

	@block_number.setter
	def block_number(self, block_number):
		if type(block_number) is int and block_number >= 0:
			self.__block_number = block_number
		else:
			raise TypeError("Argument 'block_number' must be a positive integer.")


	@property
	def practice_blocks_per_experiment(self):
		return self.__practice_blocks_per_experiment

	@practice_blocks_per_experiment.setter
	def practice_blocks_per_experiment(self, practice_blocks_per_experiment):
		if type(practice_blocks_per_experiment) is int and practice_blocks_per_experiment >= 0:
			self.__practice_blocks_per_experiment = practice_blocks_per_experiment
		else:
			raise TypeError("Argument 'practice_blocks_per_experiment' must be a positive integer.")


	@property
	def trials_per_block(self):
		return self.__trials_per_block

	@trials_per_block.setter
	def trials_per_block(self, trials_per_block):
		if type(trials_per_block) is int and trials_per_block >= 0:
			self.__trials_per_block = trials_per_block
		else:
			raise TypeError("Argument 'trials_per_block' must be a positive integer.")


	@property
	def total_trials(self):
		return self.__total_trials

	@total_trials.setter
	def total_trials(self, total_trials):
		if type(total_trials) is int and total_trials >= 0:
			self.__total_trials = total_trials
		else:
			raise TypeError("Argument 'total_trials' must be a positive integer.")


	@property
	def trials_per_practice_block(self):
		return self.__trials_per_practice_block

	@trials_per_practice_block.setter
	def trials_per_practice_block(self, trials_per_practice_block):
		if type(trials_per_practice_block) is int and trials_per_practice_block >= 0:
			self.__trials_per_practice_block = trials_per_practice_block
		else:
			raise TypeError("Argument 'trials_per_practice_block' must be a positive integer.")


	@property
	def trials(self):
		return self.__trials


	@trials.setter
	def trials(self, trials):
		if type(trials) is int and trials >= 0:
			self.__trials = trials
		else:
			raise TypeError("Argument 'trials' must be a positive integer.")

	@property
	def blocks(self):
		return self.__blocks


	@blocks.setter
	def blocks(self, blocks):
		if type(blocks) is int and blocks >= 0:
			self.__blocks = blocks
		else:
			raise TypeError("Argument 'blocks' must be a positive integer.")


	@property
	def diagonal_px(self):
		return self.__diagonal_px

	@diagonal_px.setter
	def diagonal_px(self, diagonal_px):
		if type(diagonal_px) in (int, float)  > 0:
			self.__diagonal_px = diagonal_px
		else:
			raise TypeError("Argument 'diagonal_px' must be a positive number.")
	
	@property
	def screen_c(self):
		return self.__screen_c
	
	@screen_c.setter
	def screen_c(self, screen_c):
		if type(screen_c) is tuple and len(screen_c) == 2 and all(type(val) is int > 0 for val in screen_c):
			self.__screen_c = screen_c
		else:
			raise TypeError("Argument 'screen_c' must be a tuple of two positive integers.")
	
	@property
	def screen_x(self):
		return self.__screen_x

	@screen_x.setter
	def screen_x(self, screen_x):
		if type(screen_x) in (int, float) > 0:
			self.__screen_x = screen_x
		else:
			raise TypeError("Argument 'screen_x' must be a positive number.")
	
	@property
	def screen_y(self):
		return self.__screen_y
	
	@screen_y.setter
	def screen_y(self, screen_y):
		if type(screen_y) in (int, float) > 0:
			self.__screen_y = screen_y
		else:
			raise TypeError("Argument 'screen_y' must be a positive number.")
	
	@property
	def screen_x_y(self):
		return self.__screen_x_y
	
	@screen_x_y.setter
	def screen_x_y(self, screen_x_y):
		if type(screen_x_y) is tuple and len(screen_x_y) == 2 and all(type(val) is int > 0 for val in screen_x_y):
			self.__screen_x_y = screen_x_y
		else:
			raise TypeError("Argument 'screen_x_y' must be a tuple of two positive integers.")
	
	@property
	def ppi(self):
		return self.__ppi
	
	@ppi.setter
	def ppi(self, ppi):
		if type(ppi) is int > 0:
			self.__ppi = ppi
		else:
			raise TypeError("Argument 'ppi' must be a positive integer.")


	@property
	def pixels_per_degree(self):
		return self.__pixels_per_degree

	@pixels_per_degree.setter
	def pixels_per_degree(self, pixels_per_degree):
		if type(pixels_per_degree) is int > 0:
			self.__pixels_per_degree = pixels_per_degree
		else:
			raise TypeError("Argument 'pixels_per_degree' must be a positive integer.")
	
	
	@property
	def ppd(self):
		return self.__ppd
	
	@ppd.setter
	def ppd(self, ppd):
		if type(ppd) is int > 0:
			self.__ppd = ppd
		else:
			raise TypeError("Argument 'ppd' must be a positive integer.")

	
	@property
	def saccadic_velocity_threshold(self):
		return self.__saccadic_velocity_threshold
	
	@saccadic_velocity_threshold.setter
	def saccadic_velocity_threshold(self, value):
		if type(value) is int > 0:
			self.__saccadic_velocity_threshold = value
		else:
			raise TypeError("Argument 'value' must be a positive integer.")

	
	@property
	def saccadic_acceleration_threshold(self):
		return self.__saccadic_acceleration_threshold
	
	@saccadic_acceleration_threshold.setter
	def saccadic_acceleration_threshold(self, value):
		if type(value) is int > 0:
			self.__saccadic_acceleration_threshold = value
		else:
			raise TypeError("Argument 'value' must be a positive integer.")

	
	@property
	def saccadic_motion_threshold(self):
		return self.__saccadic_motion_threshold
	
	@saccadic_motion_threshold.setter
	def saccadic_motion_threshold(self, value):
		if type(value) is int > 0:
			self.__saccadic_motion_threshold = value
		else:
			raise TypeError("Argument 'value' must be a positive integer.")

	
	@property
	def default_font_size(self):
		return self.__default_font_size
	
	@default_font_size.setter
	def default_font_size(self, font_size):
		if type(font_size) is str:
			self.__default_font_size = pt_to_px(font_size)
		elif type(font_size) is int:
			self.__default_font_size = font_size
		else:
			raise TypeError("Argument 'font_size' must be either an integer (px) or a point-value string (ie. '8pt').")


	#todo: look into whether these next 4 params should be included by default (especially without a drawing API)
	
	@property
	def fixation_size(self):
		return self.__fixation_size
	
	@fixation_size.setter
	def fixation_size(self, fixation_size):
		if type(fixation_size) is int > 0:
			self.__fixation_size = fixation_size
		else:
			raise TypeError("Argument 'fixation_size' must be a positive integer.")

	
	@property
	def box_size(self):
		return self.__box_size
	
	@box_size.setter
	def box_size(self, box_size):
		if type(box_size) is int > 0:
			self.__box_size = box_size
		else:
			raise TypeError("Argument 'box_size ' must be a positive integer.")

	
	@property
	def cue_size(self):
		return self.__cue_size
	
	@cue_size.setter
	def cue_size(self, cue_size):
		if type(cue_size) is int > 0:
			self.__cue_size = cue_size
		else:
			raise TypeError("Argument 'cue_size ' must be a positive integer.")

	
	@property
	def cue_back_size(self):
		return self.__cue_back_size
	
	@cue_back_size.setter
	def cue_back_size(self, cue_back_size):
		if type(cue_back_size) is int > 0:
			self.__cue_back_size = cue_back_size
		else:
			raise TypeError("Argument 'cue_back_size ' must be a positive integer.")

	
	@property
	def verbosity(self):
		return self.__verbosity

	# todo: make use of this or delete it
	@verbosity.setter
	def verbosity(self, verbosity):
		if type(verbosity) is int in range(1, 10):
			self.__verbosity = verbosity
		else:
			raise TypeError("Argument 'verbosity' must be an integer between 1 and 10.")


class NumpySurface(object):
	# todo: save states! save diffs between operations! so cool and unnecessary!
	# todo: default alpha value for render

	def __init__(self, foreground=None, background=None, fg_position=None, bg_position=None, width=None, height=None):
		self.__foreground = None
		self.__foreground_position = None
		self.__foreground_mask = None
		self.__foreground_unmask = None
		self.__fg_mask_position = None
		self.__background = None
		self.__background_position = None
		self.__background_mask = None
		self.__background_unmask = None
		self.__bg_mask_position = None
		self.__height = None
		self.__width = None
		self.__bg_color = None
		self.__prerender = None
		self.bg = None
		self.fg = None
		self.bg_xy = None
		self.fg_xy = None

		if width:
			self.width = width
		if height:
			self.height = height

		# do positions first in case a resize is required during bg & fg processing
		if fg_position is not None:
			if type(fg_position) is tuple:
				if len(fg_position) == 2 and all(type(i) is int for i in fg_position):
					self.__foreground_position = fg_position
				else:
					raise ValueError("Both indices of argument 'fg_position' must be positive integers.")
			else:
				raise TypeError("Argument 'fg_position' must be a tuple of length 2 or NoneType.")
		else:
			self.__foreground_position = (0, 0)

		if bg_position is not None:
			if type(bg_position) is tuple:
				if len(bg_position) == 2 and all(type(i) is int for i in bg_position):
					self.__background_position = bg_position
				else:
					raise ValueError("Both indices of argument 'bg_position' must be positive integers.")
			else:
				raise TypeError("Argument 'bg_position' must be a tuple of length 2 or NoneType.")
		else:
			self.__background_position = (0, 0)

		# just some aliases to shorten lines later (render, resize, etc.)
		self.bg = self.__background
		self.fg = self.__foreground
		self.bg_xy = self.__background_position
		self.fg_xy = self.__foreground_position

		if background is not None:  # process bg first to cut down on resizing since bg is probably > fg
			if type(background) is numpy.ndarray:
				self.background = self.__ensure_alpha_channel(background)
			elif type(background) is str:  # assume it's a path to an image file
				self.layer_from_file(background, False, bg_position)
			else:
				raise TypeError("Argument 'background' must be either a string (path to image) or a numpy.ndarray.")

		if foreground is not None:
			if type(foreground) is numpy.ndarray:
				self.foreground = self.__ensure_alpha_channel(foreground)
			elif type(foreground) is str:  # assume it's a path to an image file
				self.layer_from_file(foreground, True, fg_position)
			else:
				raise TypeError("Argument 'foreground' must be either a string (path to image) or a numpy.ndarray.")

	def __str__(self):
		return "klibs.NumpySurface, ({0} x {1}) at {2}".format(self.width, self.height, hex(id(self)))

	def blit(self, source, layer=NS_FOREGROUND, registration=7, position=(0, 0)):
		# todo: implement layer logic here
		source_array = None
		source_height = None
		source_width = None

		if type(source) is numpy.ndarray:
			source_array = self.__ensure_alpha_channel(source)
		elif type(source) is NumpySurface:
			source_array = source.render()
		else:
			raise TypeError("Argument 'source' must be either of klibs.NumpySurface or numpy.ndarray.")

		source_height = source.shape[0]
		source_width = source.shape[1]

		# convert english location strings to x,y coordinates of destination surface
		if type(position) is str:
			position = absolute_position(position, self)

		registrations = build_registrations(source_height, source_width)
		position = (position[0] + registration[0], position[1] + registration[1])

		# don't attempt the blit if source can't fit
		if source_height > self.height or source_width > self.width:
			raise ValueError("Source is larger than destination in one or more dimensions.")
		elif source_height + position[1] > self.height or source_width + position[0] > self.width:
			raise ValueError("Source cannot be blit to position; destination bounds exceeded.")

		self.__foreground[position[0]:position[0] + source_width, position[1]:position[1] + source_height] = source_array

	def __ensure_alpha_channel(self, numpy_array, alpha_value=255):
		if len(numpy_array[2][0]) == 3:
			return numpy.insert(numpy_array, 3, alpha_value, 2)
		else:
			return numpy_array

	def layer_from_file(self, image, layer=NS_FOREGROUND, position=None):
		# todo: better error handling; check if the file has a valid image extension, make sure path is a valid type
		image_content = None
		if type(image) is str:
			image_content = self.__import_image_file(image)
		elif isinstance(image, Image.Image):
			image_content = self.__ensure_alpha_channel(numpy.array(Image.open(image)))
		else:
			raise TypeError("Argument 'image' must be either a path to an image file or a PIL Image object.")

		if layer == NS_FOREGROUND:
			self.foreground = image_content
		elif layer == NS_BACKGROUND:
			self.background = image_content
		else:
			TypeError("Argument 'layer' must be either NS_FOREGROUND (ie. 1) or NS_BACKGROUND (ie. 0).")

		self.__update_shape()  # only needed if resize not called; __update_shape called at the end of resize

		return True

	def __import_image_file(self, path):
		if os.path.exists(path):
			return self.__ensure_alpha_channel(numpy.array(Image.open(path)))
		else:
			ValueError("Argument 'path' was not a valid path on the current file system.")

	def position_in_layer_bounds(self, position, layer=None):
		layer = NS_FOREGROUND if type(layer) is None else layer
		target = self.__fetch_layer(layer)
		try:
			position_iter = iter(position)
			if layer == NS_FOREGROUND:
				target = self.foreground
			elif layer == NS_BACKGROUND:
				target = self.background
			else:
				raise TypeError("Argument 'layer' must be either NS_FOREGROUND (ie. 1) or NS_BACKGROUND (ie. 0).")
		except:
			raise ValueError("Argument 'position' must be an iterable representation of  x, y coordinates.")

		return position[0] < target.shape[1] and position[1] < target.shape[0]

	def region_in_layer_bounds(self, region, offset=0, layer=NS_FOREGROUND):
		bounding_coords = [0, 0, 0, 0]  # ie. x1, y1, x2, y2
		target = self.__fetch_layer(layer)
		if type(offset) is int:
			offset = (offset, offset)
		elif type(offset) in (tuple, list) and len(offset) == 2 and all(type(i) is int and i > 0 for i in offset):
			bounding_coords[0] = offset[0]
			bounding_coords[1] = offset[1]

		if type(region) is NumpySurface:
			bounding_coords[2] = region.width + offset[0]
			bounding_coords[3] = region.height + offset[1]
		elif type(region) is numpy.ndarray:
			bounding_coords[2] = region.shape[1] + offset[0]
			bounding_coords[3] = region.shape[0] + offset[1]
		else:
			raise TypeError("Argument 'region' must be either a numpy.ndarray or a klibs.NumpySurface object.")
		in_bounds = True
		for coord in bounding_coords:
			in_bounds = self.position_in_layer_bounds(coord)

		return in_bounds

	def __fetch_layer(self, layer):
		if layer == NS_FOREGROUND:
			if self.foreground is not None:
				return self.foreground
			else:
				raise ValueError("klibs.NS_FOREGROUND given for 'layer' argument, but foreground attribute is not set.")
		elif layer == NS_BACKGROUND:
			if self.background is not None:
				return self.background
			else:
				raise ValueError("klibs.NS_BACKGROUND given for 'layer' argument, but background attribute is not set.")
		else:
			raise TypeError("Argument 'layer' must be either NS_FOREGROUND (ie. 1) or NS_BACKGROUND (ie. 0).")

	def get_pixel_value(self, location, layer=NS_FOREGROUND):
		if self.position_in_layer_bounds(location, layer):
			return self.__fetch_layer(layer)[location[1]][location[0]]
		else:
			return False

	# def __truncate(self, surface, position, layer=NS_FOREGROUND):
	# 	width = 0
	# 	height = 0
		#
		# destination[position]

	def mask(self, mask, position, layer=NS_FOREGROUND, auto_truncate=True):  # YOU ALLOW NEGATIVE POSITIONING HERE
		if type(mask) is NumpySurface:
			mask = mask.render()
		elif type(mask) is str:
			mask = self.__import_image_file(mask)
		elif type(mask) is not numpy.ndarray:
			raise TypeError("Argument 'mask' must be a NumpySurface, numpy.ndarray or a path string of an image file.")

		if layer == NS_FOREGROUND:
			self.__foreground_unmask = copy(self.foreground)
			self.__foreground_mask = mask
			if auto_truncate:
				position = [position[0], position[1]]  # todo: use duck typing properly so this can arrive as a list
				# layer_yx = self.foreground.shape
				# mask_height = self.foreground.shape[0] - mask.shape[0] + -1 * position[1]
				# mask_width = self.foreground.shape[1] - mask.shape[1] + -1 * position[0]

				new_pos = [0, 0]
				mask_x1 = 0
				mask_x2 = 0
				mask_y1 = 0
				mask_y2 = 0

				# make sure position isn't impossible (ie. not off right-hand or bottom edge)
				if position[0] >= 0:
					mask_x1 = position[0]
					if mask.shape[1] + position[0] > self.foreground.shape[1]:
						mask_x2 = self.foreground.shape[1] - position[0]
					else:
						mask_x2 = mask.shape[1] + position[0]
					new_pos[0] = position[0]
				else:
					mask_x1 = abs(position[0])
					if abs(position[0]) + mask.shape[1] > self.foreground.shape[1]:
						mask_x2 = self.foreground.shape[1] + abs(position[0])
					else:
						mask_x2 = self.foreground.shape[1] - (abs(position[0]) + mask.shape[1])
					new_pos[0] = 0

				if position[1] >= 0:
					mask_y1 = position[1]
					if mask.shape[0] + position[1] > self.foreground.shape[0]:
						mask_y2 = self.foreground.shape[0] - position[1]
					else:
						mask_y2 = mask.shape[0] + position[1]
					new_pos[1] = position[1]
				else:
					mask_y1 = abs(position[1])
					if abs(position[1]) + mask.shape[0] > self.foreground.shape[0]:
						mask_y2 = self.foreground.shape[0] + abs(position[1])
					else:
						mask_y2 = self.foreground.shape[0] - (abs(position[1]) + mask.shape[0])
					new_pos[1] = 0
				mask = mask[mask_y1: mask_y2, mask_x1: mask_x2]
				position = new_pos
				# print "Mask Shape: {0}, Position: {1}, FG Shape: {2}".format(mask.shape, position, self.foreground.shape)

			elif self.region_in_layer_bounds(mask, position, NS_FOREGROUND):
				self.__fg_mask_position = position
			else:
				raise ValueError("Mask falls outside of layer bounds; reduce size or reposition.")

			alpha_map = numpy.ones(mask.shape[:-1]) * 255 - mask[..., 3]
			fg_x1 = position[0]
			fg_x2 = alpha_map.shape[1] + position[0]
			fg_y1 = position[1]
			fg_y2 = alpha_map.shape[0] + position[1]

			self.foreground[fg_y1: fg_y2, fg_x1: fg_x2, 3] = alpha_map

	def prerender(self):
		return self.render(True)

	def resize(self, dimensions, fill=(0, 0, 0, 0)):
		# todo: add "extend" function, which wraps this
		"""

		:param dimension:
		:param fill: Transparent by default, can be any rgba value
		:return:
		"""
		print "Resize[dimensions]: {0}".format(dimensions)
		if type(fill) is tuple:
			if len(fill) in (3, 4) and all(type(color) is int for color in fill):
				if len(fill) == 3:
					fill = rgb_to_rgba(fill)
			else:
				raise ValueError("All indices of argument 'fill' must be integers between 0 and 255.")
		else:
			raise TypeError("Argument 'fill' must be a tuple of either length 3 or 4.")
		if type(dimensions) is tuple and len(dimensions) == 2:
			if int in (type(dimensions[0]), type(dimensions[1])):
				if type(dimensions[0]) is True:
					dimensions[0] = dimensions[1]
				if type(dimensions[0]) is False:
					dimensions[0] = self.width
				if type(dimensions[1]) is True:
					dimensions[1] = dimensions[0]
				if type(dimensions[1]) is False:
					dimensions[1] = self.height
			else:
				raise ValueError("Both indices of argument 'dimensions' cannot be boolean; at least 1 integer required.")
		else:
			raise ValueError("Argument 'dimensions' must be a tuple of length 2. ")

		# create some empty arrays of the new dimensions
		nfg = numpy.zeros((dimensions[0], dimensions[1], 4))  # ie. new foreground
		nbg = numpy.zeros((dimensions[0], dimensions[1], 4))

		# if resize is called during __init__ (b/c both bg & fg != None), bg or fg dims.  may be missing, so use (0,0)
		# positions, though (ie. bg_xy and fg_xy) are set before surfaces are loaded in __init__ so will be ok
		ofg_wh = None  # ie. old foreground width & height
		obg_wh = None
		if self.background is None:
			obg_wh = nbg.shape
		else:
			obg_wh = self.background.shape
		if self.foreground is None:
			ofg_wh = nfg.shape
		else:
			ofg_wh = self.background.shape

		# insert old background and foreground into their positions on new arrays
		if self.background is None:
			self.background = nbg
		print self.bg_xy
		print obg_wh
		nbg[self.bg_xy[0]: self.bg_xy[0] + obg_wh[0], self.bg_xy[1]: self.bg_xy[1] + obg_wh[1]] = self.background
		self.background = nbg

		if self.fg is None:
			self.foreground = nfg
		nfg[self.fg_xy[1]: self.fg_xy[1] + ofg_wh[0], self.fg_xy[1]: self.fg_xy[1] + ofg_wh[1]] = self.foreground
		self.foreground = nfg

		self.__update_shape()

	def render(self, prerendering=False):
		# todo: add functionality for not using a copy, ie. permanently render
		if self.__prerender is not None and prerendering is False:
			return self.__prerender
		render_surface = None
		if self.background is None and self.foreground is None:
			raise ValueError('Nothing to render; NumpySurface has been initialized but not content has been added.')
		if self.background is None:
			render_surface = copy(self.foreground)
		else:  # flatten background and foreground together
			render_surface = numpy.zeros((self.height, self.width, 4))
			bg_x1 = self.__background_position[0]
			bg_x2 = bg_x1 + self.background.shape[1]
			bg_y1 = self.__background_position[1]
			bg_y2 = bg_y1 + self.background.shape[0]

			fg_x1 = self.__foreground_position[0]
			fg_x2 = fg_x1 + self.foreground.shape[1]
			fg_y1 = self.__foreground_position[1]
			fg_y2 = fg_y1 + self.foreground.shape[0]
			print self.foreground
			render_surface[bg_y1: bg_y2, bg_x1: bg_x2] = self.background
			render_surface[fg_y1: fg_y2, fg_x1: fg_x2] = self.foreground

		if prerendering:
			self.__prerender = render_surface
			return True
		else:
			return render_surface

	def __update_shape(self):
		if type(self.foreground) is numpy.ndarray:
			if type(self.background) is numpy.ndarray:
				if self.foreground.shape[1] > self.background.shape[1]:
					self.width = self.foreground.shape[1]
				else:
					self.width = self.background.shape[1]
				if self.foreground.shape[0] > self.background.shape[0]:
					self.height = self.foreground.shape[0]
				else:
					self.height = self.background.shape[0]
			else:
				self.width = self.foreground.shape[1]
				self.height = self.foreground.shape[0]
		elif type(self.background) is numpy.ndarray:
			self.width = self.background.shape[1]
			self.height = self.background.shape[0]
		else:
			self.width = 0
			self.height = 0

		return True

	@property
	def height(self):
		return self.__height

	@height.setter
	def height(self, height_value):
		if type(height_value) is int > 0:
			self.__height = height_value
		else:
			raise TypeError("NumpySurface.height must be a positive integer.")

	@property
	def width(self):
		return self.__width

	@width.setter
	def width(self, width_value):
		if type(width_value) is int > 0:
			self.__width = width_value  # todo: extend a numpy array with empty pixels?
		else:
			raise TypeError("NumpySurface.width must be a positive integer.")

	@property
	def foreground(self):
		return self.__foreground

	@foreground.setter
	def foreground(self, foreground_content):
		if type(foreground_content) is numpy.ndarray:
			if foreground_content.shape[1] > self.width:
				self.width = foreground_content.shape[1]
			if foreground_content.shape[0] > self.height:
				self.height = foreground_content.shape[0]
			self.__foreground = foreground_content
		else:
			raise TypeError("NumpySurface.foreground must be a numpy.ndarray.")

	@property
	def background(self):
		return self.__background

	@background.setter
	def background(self, background_content):
		if type(background_content) is numpy.ndarray:
			# todo: foreground needs to be resized to background size if this happens
			if background_content.shape[1] > self.width:
				self.width = background_content.shape[1]
			if background_content.shape[0] > self.height:
				self.height = background_content.shape[0]
			self.__background = background_content
		elif type(background_content) is tuple and len(background_content) in (3, 4):
			raise TypeError("NumpySurface.background must be a numpy.ndarray; set color with NumpySurface.background_color")
		else:
			raise TypeError("NumpySurface.background must be a numpy.ndarray.")

	@property
	def background_color(self):
		return self.__bg_color

	@background_color.setter
	def background_color(self, color):
		if type(color) is tuple and len(color) in (3, 4):
			if len(color) == 3:
				color[3] = 255
			self.__bg_color = color
		else:
			raise TypeError("NumpySurface.background_color must be a tuple of integers (ie. rgb or rgba color value).")



Params = AppParams()


def absolute_position(position, destination):
	locations = ['center', 'topLeft', 'topRight', 'bottomLeft', 'bottomRight', 'top', 'left', 'right', 'bottom']
	if position not in locations:
		raise ValueError("Argument 'position'  was not a key in the locations dict.")
	if type(destination) is numpy.ndarray:
		height = destination.shape[0]
		width = destination.shape[1]
	elif type(destination) is NumpySurface:
		height = destination.height
		width = destination.width
	elif type(destination) is tuple and len(destination) == 2 and all(type(i) is int for i in destination):
		height = destination[1]
		width = destination[0]
	elif type(destination) is sdl2.ext.window.Window:
		height = Params.screen_y
		width = Params.screen_x
	else:
		raise TypeError("Argument 'destination' invalid; must be (x,y) tuple, numpy.ndarray or klibs.NumpySurface.")

	locations = {
		'center': [width // 2, height // 2],
		'topLeft': [0, 0],
		'top': [width // 2, 0],
		'topRight': [width, 0],
		'left': [0, height // 2],
		'right': [0, height],
		'bottomLeft': [0, height],
		'bottom': [width // 2, height],
		'bottomRight': [width, height]
	}
	return locations[position]


def arg_error_str(arg_name, given, expected, kw=True):
	if kw:
		err_string = "The keyword argument, '{0}', was expected to be of type '{1}' but '{2}' was given."
	else:
		err_string = "The argument, '{0}', was expected to be of type '{1}' but '{2}' was given."
	return err_string.format(arg_name, type(given), type(expected))


def build_registrations(source_height, source_width):
	return ((),
		(0, -1.0 * source_height),
		(-1.0 * source_width / 2.0, source_height),
		(-1.0 * source_width, -1.0 * source_height),
		(0, -1.0 * source_height / 2.0),
		(-1.0 * source_width / 2.0, -1.0 * source_height / 2.0),
		(-1.0 * source_width, -1.0 * source_height / 2.0),
		(0, 0),
		(-1.0 * source_width / 2.0, 0),
		(-1.0 * source_width, 0))


def deg_to_px(deg):
	return deg * Params.ppd  # todo: error checking?


def equiv(comparator, canonical):
	equivalencies = {
					"inch": ["in", "inch"],
					"inches": ["ins", "inches"],
					"cm": ["centimeter", "cm"],
					"cms": ["centimeters", "cms"],
					"CRT": ["crt", "CRT"],
					"LCD": ["lcd", "LCD"]
	}

	if canonical in equivalencies:
		return comparator in equivalencies[canonical]
	else:
		return False


def log(msg, priority):
	"""Log an event
	:param msg: - a string to log
	:param priority: - 	an integer from 1-10 specifying how important the event is,
						1 being most critical and 10 being routine. If set to 0 it
						will always be printed, regardless of what the user sets
						verbosity to. You probably shouldn't do that.
	"""
	if priority <= Params.verbosity:
		with open(Params.log_file_path, 'a') as log:
			log.write(str(priority) + ": " + msg)
	return True


def peak(v1, v2):
	if v1 > v2:
		return v1
	else:
		return v2


def pretty_join(array, whitespace=1, delimiter="'", delimit_behavior=None, prepend=None, before_last=None, each_n=None,
				after_first=None, append=None):
	"""Automates string combination. Parameters:
	:param array: - a list of strings to be joined
	:param config: - a dict with any of the following keys:
		'prepend':
		'afterFirst':
		'beforeLast':
		'eachN':
		'whitespace':	Whitespace to place between elements. Should be a positive integer, but can be a string if the number
						is smaller than three and greater than zero. May also be the string None or False, but you should probably
						just not set it if that's what you want.
		'append':
		'delimiter':
		'delimitBehavior':
		'delimitBehaviour':
	"""
	msg = "Trying to use  a .join() call instead." # gets repeated in several 'raise' statements, easier to reuse
	config = None
	ws = ''
	for n in range(whitespace):
		ws += ' '
	whitespace = ws

	output = ''
	if prepend is not None:
		output = prepend
	for n in range(len(array)):
		#if after first iteration, print whitespace
		if n > 1:
			output = output + whitespace
		#if beforeLast is set, print it and add whitespace
		if (n == (len(array) - 1)) and before_last is not None:
			output = output + before_last + whitespace
		# if eachN is set and the iterator is divisible by N, print an eachN and add whitespace
		if each_n is tuple:
			if len(each_n) == 2:
				if type(each_n[0]) is int:
					if n % each_n == 0:
						output = output + str(each_n[1]) + whitespace
				else:
					log_str = "Klib.prettyJoin() config parameter 'eachN[0]' must be an int, '{0}' {1} passed. {2}"
					log(log_str.format(each_n, type(each_n, 10)))
			else:
				raise ValueError("Argument 'each_n' must have length 2.")
		elif each_n is not None:
			raise TypeError("Argument 'each_n' must be a tuple of length 2.")
		# if delimiter is set to default or wrap, print a delimiter before the array item
		if delimit_behavior in ('wrap', None):
			output = output + delimiter
		# finally print the array item
		output = output + str(array[n]) + delimiter + whitespace
		# if afterFirst is set, print it and add whitespace
		if (n == 0) and (after_first is not None):
			output = output + after_first + whitespace
	if append is not None:
		output = output + append

	return output


def pt_to_px(pt_size):
	if type(pt_size) is not int:
		raise TypeError("Argument 'pt_size' must be an integer.")
	if 512 < pt_size < 2:
		raise ValueError("Argument 'pt_size' must be between 2 and 512.")
	dpi = None
	if Params.dpi is not None:
		dpi = Params.dpi
	else:
		dpi = 96  # CRT default
	return int(math.floor(1.0 / 72 * dpi * pt_size))


def px_to_deg(length):  # length = px
	return length / Params.ppd    # todo: error checking?


def rgb_to_rgba(rgb):
	return rgb[0], rgb[1], rgb[2], 1  # todo: error checking?


def safe_flag_string(flags, prefix=None, uc=True):
	if prefix and type(prefix) is not str:
		e = "The keyword argument, 'prefix', must be of type 'str' but '{0}' was passed.".format(type(prefix))
		raise TypeError(e)

	if type(flags) is list:
		for i in range(0, len(flags)):
			if uc:
				flags[i] = flags[i].upper()
			else:
				flags[i] = flags[i]
			if prefix:
				flags[i] = prefix + "." + flags[i]
		flag_string = " | ".join(flags)

	else:
		e = "The 'flags' argument must be of type 'list' but '{0}' was passed.".format(type(flags))
		raise TypeError(e)

	return eval(flag_string)


def quit(msg=None):
	if msg:
		print msg
	print "Exiting..."
	sdl2.SDL_Quit()
	sys.exit()



# class EEG(KlibBase):
#
# 	def __init__(self):
# 		KlibBase.__init__(self)
# 		#self.P =  parallel.Parallel()
#
# 	def threaded(self, func):
# 		@wraps(func)
# 		def wrapper(*args, **kwargs):
# 			thread.start_new_thread(func, *args, **kwargs)
# 			return wrapper
#
# 	@threaded
# 	def send_code(self, code):
# 			self.P.setData(code)  # send the event code
# 			time.sleep(0.006)  # sleep 6 ms
# 			self.P.setData(0)  # send a code to clear the register
# 			time.sleep(0.01)  # sleep 10 ms
#

#############
#  CLASSES
#############

class TrialIterator(object):
	def __init__(self, l):
		self.l = l
		self.length = len(l)
		self.i = 0

	def __iter__(self):
		return self

	def __len__(self):
		return self.length

	def __getitem__(self, i):
		return self.l[i]

	def __setitem__(self, i, x):
		self.l[i] = x

	def next(self):
		if self.i >= self.length:
			raise StopIteration
		else:
			self.i += 1
			return self.l[self.i - 1]

	def recycle(self):
		self.l.append(self.l[self.i - 1])
		temp = self.l[self.i:]
		random.shuffle(temp)
		self.l[self.i:] = temp
		self.length += 1


class App(object):
	__completion_message = "thanks for participating; please have the researcher return to the room."
	__collecting_demographics = False
	__default_font_size = 28
	__exp_factors = None
	trial_number = 0
	block_number = 0
	__wrong_key_msg = None

	logged_fields = list()

	testing = True
	paused = False
	execute = True

	wrong_key_message = None

	def __init__(self, project_name, el=None, asset_path="ExpAssets"):
		if not Params.setup(project_name, asset_path):
			raise EnvironmentError("Fatal error; Params object was not able to be initialized for unknown reasons.")

		Params.key_maps["*"] = KeyMap("*", (), (), ())

		# this is silly but it makes importing from the params file work smoothly with rest of App
		self.event_code_generator = None

		#initialize the database instance
		self.__db_init()

		# initialize screen surface and screen parameters
		self.__display_init(Params.view_distance, flags=SCREEN_FLAGS)

		# Type(self.window) = sdl2.ext.window.Window

		# initialize the text layer for the app
		self.text = TextLayer(Params.screen_x_y, Params.screen_x_y, Params.ppi)
		if Params.default_font_size:
			self.text.default_font_size = Params.default_font_size

		# initialize eyelink
		# if el:
		# 	self.el = el
		# else:
		# 	self.el = EyeLink()
		# self.no_tracker = self.el.dummy_mode
		# self.el.screen_size = Params.screen_x_y

	def __trial_func(self, *args, **kwargs):
		"""
		Manages a trial.
		"""
		# try:
		self.trial_number += 1
		self.trial_prep(*args, **kwargs)
		trial_data = self.trial(*args, **kwargs)
		# except:
		# 	raise
		# finally:
		self.__log_trial(trial_data)
		self.trial_clean_up()

	def __experiment_manager(self, *args, **kwargs):
		"""
		Manages an experiment using the schema and factors.
		"""
		self.setup()
		for i in range(Params.practice_blocks_per_experiment):
			self.__generate_trials(practice=True, event_code_generator=self.__event_code_function, **Params.exp_factors)
			if Params.trials_per_practice_block % len(self.trials):
				if Params.trials_per_practice_block < len(self.trials):
					self.trials = self.trials[:Params.trials_per_practice_block]
				else:
					e_str = "The desired number of trials in the practice block, \
							{0}, is not a multiple of the minimum number of trials, {1}."
					raise ValueError(e_str.format(Params.trials_per_practice_block, len(self.trials)))
			else:
				self.trials *= (Params.trials_per_practice_block / len(self.trials))
			self.__trial_func(*args, **kwargs)
		for i in range(Params.blocks_per_experiment):
			Params.block_number = i + 1  # added this for data-out aesthetics more than use in program logic
			self.block(Params.block_number)
			self.__generate_trials(practice=False, event_code_generator=self.__event_code_function, **Params.exp_factors)
			if Params.trials_per_block % len(self.trials):
				e = "The desired number of trials in the block, {0}, is not a multiple of the minimum number of trials, {1}."
				raise ValueError(e.format(Params.trials_per_block, len(self.trials)))
			else:
				self.trials *= (Params.trials_per_block / len(self.trials))
				random.shuffle(self.trials)
			for trial_factors in self.trials:
				self.__trial_func(trial_factors, self.trial_number)
			self.block_break()
		self.clean_up()
		self.db.db.commit()
		self.db.db.close()

	def __db_init(self):
		self.db = Database()

	def __generate_trials(self, practice=False, event_code_generator=None, **kwargs):
		"""
		Example usage:
		Jono: event_code_gen: literally creates an event code, as per some rule, that will be in the trial_factors list
		passed to trial() for use with EEG bidnis
		event_code_generator = self.event_code_generator, cue=['right', 'left'], target=['right', 'left'], type=['word', 'nonword'], cued_bool='cue==target'
		To create an expression, simply pass a named string ending in _bool with a logical expression inside:
		cued_bool='peripheral==cue'
		Do not include other expression variables in an expression.
		They are evaluated in arbitrary order and may not yet exist.
		:param practice:
		:param event_code_generator:
		:return:
		"""
		trials = [[practice]]
		factors = ['practice']
		eval_queue = list()
		for k, f in kwargs.iteritems():
			temp = list()
			if k[-5:] == '_bool':
				eval_queue.append([k, f])
			else:
				factors.append(k)
				for e in trials:
					if e:
						for v in f:
							te = e[:]
							te.append(v)
							temp.append(te)
				trials = temp[:]
		for e in eval_queue:
			factors.append(e[0][:-5])
			print "e: " + e[1]
			operands = re.split('[=>!<]+', str(e[1]).strip())
			operator = re.search('[=<!>]+', str(e[1])).group()
			for t in trials:
				t.append(eval('t[factors.index(\'' + operands[0] + '\')]' + operator + 't[factors.index(\'' + operands[
					1] + '\')]'))
		if event_code_generator is not None and type(event_code_generator).__name__ == 'function':
			factors.append('code')
			for t in trials:
				t.append(event_code_generator(t))
		self.trials = trials
		self.factors = factors

	def __log_trial(self, trial_data, auto_id=True):
		#  todo: move this to a DB function.... :/
		if auto_id:
			if Params.testing or not Params.collect_demographics:
				self.participant_id = -1
			trial_data[Params.id_field_name] = self.participant_id
		for attr in trial_data:
			self.db.log(attr, trial_data[attr])
		self.db.insert()

	def __set_stroke(self):
		stroke = int(1 * math.floor(Params.screen_y / 500.0))
		if (stroke < 1):
			stroke = 1
		return stroke

	def __display_init(self, view_distance, flags=None, ppi="crt"):
		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
		sdl2.mouse.SDL_ShowCursor(sdl2.SDL_DISABLE)
		Params.screen_x_y = (Params.screen_x, Params.screen_y)
		window_flags = False
		if flags:
			window_flags = safe_flag_string(flags, 'sdl2')
		if window_flags:
			self.window = sdl2.ext.Window(Params.project_name, Params.screen_x_y, (0, 0), window_flags)
		else:
			self.window = sdl2.ext.Window(Params.project_name, Params.screen_x_y, (0, 0))
		# self.window.show()
		Params.screen_c = (Params.screen_x / 2, Params.screen_y / 2)
		Params.diagonal_px = int(math.sqrt(Params.screen_x * Params.screen_x + Params.screen_y * Params.screen_y))

		# these next six lines essentially assert a 2d, pixel-based rendering context; copied-and-pasted from Mike!
		gl_context = sdl2.SDL_GL_CreateContext(self.window.window)
		gl.glMatrixMode(gl.GL_PROJECTION)
		gl.glLoadIdentity()
		gl.glOrtho(0, Params.screen_x, Params.screen_y, 0, 0, 1)
		gl.glMatrixMode(gl.GL_MODELVIEW)
		gl.glDisable(gl.GL_DEPTH_TEST)
		self.clear()
		sdl2.SDL_PumpEvents()
		self.fill()
		self.blit(self.numpy_surface("splash.png"), 5, 'center')
		self.flip(1)

		# this error message can be used in three places below, it's easier set it here

		# interpret view_distance
		if type(view_distance) is tuple and type(view_distance[0]) is int:
			if equiv('inch', view_distance[1]):
				Params.view_distance = view_distance[0]
				Params.view_unit = 'inch'
			elif equiv('cm', view_distance[1]):
				Params.view_distance = view_distance[0]
				Params.view_unit = 'cm'
				#convert physical screen measurements to cm
				Params.monitor_x *= 2.55
				Params.monitor_y *= 2.55
			else:
				raise TypeError("view_distance must be int (inches) or a tuple containing (int, str).")
		elif type(view_distance) is int:
			Params.view_distance = view_distance
			Params.view_unit = INCH
		else:
			raise TypeError("view_distance must be int (inches) or a tuple containing (int,str).")

		# TODO: THIS IS BROKEN. PPI needs to be calculated diagonally, this is using horizontal math only.
		# http://en.wikipedia.org/wiki/Pixel_density
		if equiv(ppi, "CRT"):
			Params.ppi = 72
		elif equiv(ppi, "LCD"):
			Params.ppi = 96
		elif type(ppi) is int:
			Params.ppi = ppi
		else:
			raise TypeError("ppi must be either an integer or a string representing monitor type (CRT/LCD).")
		# Params.monitor_x = Params.screen_x / Params.ppi
		# Params.monitor_y = Params.screen_y / Params.ppi
		Params.monitor_x = 23.3
		Params.monitor_y = Params.screen_y / Params.ppi
		Params.screen_degrees_x = math.degrees(math.atan((Params.monitor_x / 2.0) / Params.view_distance) * 2)
		Params.pixels_per_degree = int(Params.screen_x / Params.screen_degrees_x)
		Params.ppd = Params.pixels_per_degree  # alias for convenience

	def alert(self, alert_string, urgent=False, display_for=0):
		# TODO: address the absence of default colors
		# todo: instead hard-fill, "separate screen" flag; copy current surface, blit over it, reblit surf or fresh surf
		"""
		Display an alert

		:param alert_string: - Message to display
		:param urgent: - Boolean, returns alert surface for manual handling rather waiting for 'any key' response
		"""
		# if urgent:
		# 	return self.message(alert_string, color=(255, 0, 0, 255), location='topRight', registration=9,
		# 						font_size=self.text.default_font_size * 2, blit=True, flip=True)
		self.clear()
		self.fill(Params.default_fill_color)
		self.message(alert_string, color=(255, 0, 0, 255), location='center', registration=5,
							font_size=self.text.default_font_size * 2, blit=True)
		if display_for > 0:
			start = time.time()
			self.flip()
			while (time.time() - start) < display_for:
				pass
			return
		else:
			self.listen()  # remember that listen calls flip() be default

	def blit(self, source, registration=7, position=(0, 0)):
		height = None
		width = None
		content = None
		if type(source) is NumpySurface:
			height = source.height
			width = source.width
			content = source.render()
		elif type(source) is numpy.ndarray:
			height = source.shape[0]
			width = source.shape[1]
			content = source
		else:
			raise TypeError("Argument 'source' must be either of type numpy.ndarray or klibs.NumpySurface.")

		# configure OpenGL for blit
		gl.glEnable(gl.GL_BLEND)
		gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		id = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, id)
		gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_REPLACE)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, content)
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, id)
		gl.glBegin(gl.GL_QUADS)

		# convert english location strings to x,y coordinates of destination surface
		if type(position) is str:
			position = absolute_position(position, Params.screen_x_y)

		# define boundaries coordinates of region being blit to
		x_bounds = [position[0], position[0] + width]
		y_bounds = [position[1], position[1] + height]

		# shift boundary mappings to reflect registration
		#
		# 1--2--3  Default assumes registration = 5, but if registration = 3 (top-right), X/Y would be shifted
		# 4--5--6  by the distance from the object's top-left  to it's top-right corner
		# 7--8--9  ie. Given an object of width = 3, height = 3, with registration 9 being blit to (5,5) of some
		#          surface, the default blit behavior (placing the  top-left coordinate at 5,5) would result in
		#          the top-left corner being blit to (2,2), such that the bottom-right corner would be at (5,5)
		registrations = build_registrations(height, width)

		if 0 < registration & registration < 10:
			x_bounds[0] += int(registrations[registration][0])
			x_bounds[1] += int(registrations[registration][0])
			y_bounds[0] += int(registrations[registration][1])
			y_bounds[1] += int(registrations[registration][1])
		else:
			x_bounds[0] += int(registrations[7][0])
			x_bounds[1] += int(registrations[7][0])
			y_bounds[0] += int(registrations[7][1])
			y_bounds[1] += int(registrations[7][1])

		gl.glTexCoord2f(0, 0)
		gl.glVertex2f(x_bounds[0], y_bounds[0])
		gl.glTexCoord2f(1, 0)
		gl.glVertex2f(x_bounds[1], y_bounds[0])
		gl.glTexCoord2f(1, 1)
		gl.glVertex2f(x_bounds[1], y_bounds[1])
		gl.glTexCoord2f(0, 1)
		gl.glVertex2f(x_bounds[0], y_bounds[1])
		gl.glEnd()
		gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
		gl.glDeleteTextures([id])
		del id
		gl.glDisable(gl.GL_TEXTURE_2D)

	@abc.abstractmethod
	def block(self, block_num):
		pass

	def block_break(self, message=None, is_path=False):
		"""
		Display a break message between blocks

		:param message: A message string or path to a file containing a message string
		:param is_path:
		:raise:
		"""
		default = "You've completed block {0} of {1}. When you're ready to continue, press any key.".format(
			Params.block_number, Params.blocks)
		if is_path:
			try:
				path_exists = os.path.exists(message)
				if path_exists:
					with open(message, "r") as f:
						message = f.read().replace("\n", '')
				else:
					e = "'isPath' parameter was True but '{0}' was not a valid path. Using default message".format(
						message)
					raise IOError(e)
			except IOError as e:
				self.warn(e, 'App', 'blockBreak')
				message = default
		if self.testing:
			pass
		else:
			if type(message) is str:
				if message is None:
					message = default
				self.message(message, location='center', registration=5)
				self.listen()

	def bounded_by(self, pos, left, right, top, bottom):
		xpos = int(pos[0])
		ypos = int(pos[1])
		# todo: tighten up that series of ifs into one statement
		if all(type(val) is int for val in (left, right, top, bottom)) and type(pos) is tuple:
			if xpos > left:
				if xpos < right:
					if ypos > top:
						if ypos < bottom:
							return True
						else:
							return False
					else:
						return False
				else:
					return False
			else:
				return False
		else:
			e ="Argument 'pos' must be a tuple, others must be integers."
			raise TypeError()

	def collect_demographics(self):
		"""
		Gather participant demographic information and enter it into the database

		"""
		# TODO: this function should have default questions/answers but should also be able to read from a
		# CSV or array for custom Q&A
		self.db.init_entry('participants', instance_name='ptcp', set_current=True)
		name_query_string = self.query(
			"What is your full name, banner number or e-mail address? Your answer will be encrypted and cannot be read later.",
			as_password=True)
		name_hash = hashlib.sha1(name_query_string)
		name = name_hash.hexdigest()
		self.db.log('userhash', name)

		# names must be unique; returns True if unique, False otherwise
		if self.db.is_unique(name, 'userhash', 'participants'):
			gender = "What is your gender? Answer with:  (m)ale,(f)emale or (o)ther)"
			handedness = "Are right-handed, left-handed or ambidextrous? Answer with (r)ight, (l)eft or (a)mbidextrous."
			self.db.log('gender', self.query(gender, accepted=('m', 'M', 'f', 'F', 'o', 'O')))
			self.db.log('handedness', self.query(handedness, accepted=('r', 'R', 'l', 'L', 'a', 'A')))
			self.db.log('age', self.query('What is  your age?', return_type='int'))
			self.db.log('created', self.now())
			if not self.db.insert():
				raise DatabaseException("Database.insert(), which failed for unknown reasons.")
			self.db.cursor.execute("SELECT `id` FROM `participants` WHERE `userhash` = '{0}'".format(name))
			result = self.db.cursor.fetchall()
			self.participant_id = result[0][0]
			if not self.participant_id:
				raise ValueError("For unknown reasons, 'participant_id' couldn't be retrieved from database.")
		else:
			retry = self.query('That participant identifier has already been used. Do you wish to try another? (y/n) ')
			if retry == 'y':
				self.collect_demographics()
			else:
				self.fill()
				self.message("Thanks for participating!", location=Params.screen_c)
				self.window.refresh()
				time.sleep(2)
				self.quit()

	def exempt(self, index, state=True):
		if index in self.exemptions.keys():
			if state == 'on' or True:
				self.exemptions[index] = True
			if state == 'off' or False:
				self.exemptions[index] = False

	def flip(self, duration=0):
		"""
		Flip the window and wait for an optional duration
		:param duration: The duration to wait in ms
		:return: :raise: AttributeError, TypeError, GenError
		"""
		sdl2.SDL_GL_SwapWindow(self.window.window)
		if duration == 0:
			return
		if type(duration) is int:
			if duration > 0:
				start = time.time()
				while time.time() - start < duration:
					self.over_watch()
			else:
				raise AttributeError("Duration must be a positive number, '{0}' was passed".format(duration))
		else:
			raise TypeError("Duration must be expressed as an integer, '{0}' was passed.".format(type(duration)))

	def key_mapper(self, name, key_names=None, key_codes=None, key_vals=None):
		if type(name) is not str:
			raise TypeError("Argument 'name' must be a string.")

		# register the keymap if one is being passed in and set keyMap = name of the newly registered map
		if all(type(key_param) in [tuple, str] for key_param in [key_names, key_codes, key_vals]):
			Params.key_maps[name] = KeyMap(name, key_names, key_codes, key_vals)

		#retrieve registered keymap(s) by name
		if name in Params.key_maps:
			return Params.key_maps[name]
		else:
			return False

	def instructions(self, text, is_path=False):
		#  todo: remove arguments and use Params.instructions_file after you create it
		if is_path:
			if type(text) is str:
				if os.path.exists(text):
					f = open(text, 'rt')
					text = f.read()
				else:
					raise IOError("Argument 'is_path' was true but path to instruction text does not exist.")
			else:
				raise TypeError("Argument 'text' must be of type 'str' but '{0}' was passed.".format(type(text)))
		self.fill()
		self.message(text, location="center", flip=True)
		self.listen()

	def ui_request(self, request, execute=False):
		if request[1] in (MOD_KEYS["Left Command"], MOD_KEYS["Right Command"]):
			if request[0] in UI_METHOD_KEYSYMS:
				if request[0] == sdl2.SDLK_q:
					quit()
				elif request[0] == sdl2.SDLK_c:
					# self.calibrate()  # todo: uhh... write... this?
					return True
				elif request[0] == sdl2.SDLK_p:
					if not self.paused:
						self.paused = True
						self.pause()
						return True
					if self.paused:
						self.paused = False
						return False
		return False

	# todo: listen is not a method; it should be a class, "listener", that gets configured
	def listen(self, max_wait=MAX_WAIT, key_map_name="*", wait_callback=None, wait_cb_args=None, wait_cb_kwargs=None,
			el_args=None, null_response=None, time_out_message=None, response_count=None, response_map=None,
			interrupt=True, quick_return=False, flip=True):
		# TODO: have customizable wrong key & time-out behaviors
		# TODO: make RT & Response part of a customizable ResponseMap object
		# TODO: start_time should be optionally predefined and/or else add a latency param to be added onto starTime
		# TODO: make it possible to pass the parameters of a new KeyMap directly to listen()
		# TODO: add functionality for wait_callback() to exit the loop
		# establish an interval for which to listen for responding
		key_map = None

		if type(max_wait) not in (int, float):
			raise TypeError("Argument 'max_wait' must be an integer.")
		try:
			if key_map_name in Params.key_maps:
				key_map = Params.key_maps[key_map_name]
			else:
				raise ValueError("Argument 'key_map_name' did not match any registered KeyMap.")
		except:
			raise TypeError("Argument 'key_map_name' must be a string corresponding to a registered KeyMap.")
		response = None
		rt = -1

		start_time = time.time()
		waiting = True

		# enter with a clean event queue
		sdl2.SDL_PumpEvents()
		sdl2.SDL_FlushEvents(sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)  # upper/lower bounds of event queue,ie. flush all
		if flip:
			self.flip()  # executed as close to wait loop as possible for minimum delay between timing and presentation

		key = None
		sdl_keysym = None
		key_name = None
		wrong_key = False
		# then = time.time()
		while waiting:
			# now = time.time()
			# if print_interval:  # todo: this was once an argument; should be a component of verbosity once implemented
			# 	print str(int((now - then) * 1000)) + "ms"
			# 	# print "%f" % (now - then)
			# then = now

			if el_args:
				if type(el_args) is dict:
					self.eyelink_response = self.el.listen(**el_args)
				else:
					raise TypeError("Argument 'el_args' must be a dict.")
			if wait_callback is not None and type(wait_callback).__name__ == 'instancemethod':  # todo: fix second cond.
				if wait_cb_args is None:
					wait_callback()
				elif type(wait_cb_args) is dict:
					# abstract method, allows for blits, flips and other changes during a listen() call
					wait_callback(*wait_cb_args, **wait_cb_kwargs)
				else:
					raise TypeError("Argument 'wait_cb_args' must be a dict.")
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type == sdl2.SDL_KEYDOWN:
					rt = time.time() - start_time
					if not response:  # only record a response once per call to listen()
						key = event.key  # keyboard button event object (https://wiki.libsdl.org/SDL_KeyboardEvent)
						sdl_keysym = key.keysym.sym
						key_name = sdl2.keyboard.SDL_GetKeyName(sdl_keysym)
						valid = key_map.validate(sdl_keysym)
						if valid:  # a KeyMap with name "*" (ie. any key) returns self.ANY_KEY
							response = key_map.read(sdl_keysym, "data")
							if interrupt:  # ONLY for TIME SENSITIVE reactions to participant response; this flag voids overwatch()
								return [response, rt]
						else:
							wrong_key = True
					if key_name not in MOD_KEYS and key_name is not None:
						self.over_watch(event)  # ensure the 'wrong key' wasn't a call to quit or pause
						if interrupt:    # returns response immediately; else waits for maxWait to elapse
							if response:
								return [response, rt]
							elif key_map.any_key:
								return [key_map.any_key_string, rt]
						if wrong_key is True:  # flash an error for an actual wrong key
							pass
							# todo: make wrong key message modifable; figure out how to turn off to not fuck with RTs
							# wrong_key_message = "Please respond using '{0}'.".format(key_map.valid_keys())
							# self.alert(wrong_key_message)
							# wrong_key = False
			if (time.time() - start_time) > max_wait:
				waiting = False
				if time_out_message:
					self.alert(time_out_message, display_for=Params.default_alert_duration)
					return [TIMEOUT, -1]
		if not response:
			if null_response:
				return [null_response, rt]
			else:
				return [NO_RESPONSE, rt]
		else:
			return [response, rt]

	def message(self, message, font=None, font_size=None, color=None, bg_color=None, location=None, registration=None,
				wrap=None, wrap_width=None, delimiter=None, blit=True, flip=False, padding=None):
		# todo: padding should be implemented as a call to resize() on message surface; but you have to fix wrap first
		render_config = {}
		message_surface = None  # unless wrap is true, will remain empty

		if font is None:
			font = self.text.default_font

		if font_size is None:
			font_size = self.text.default_font_size

		if color is None:
			if self.text.default_color:
				color = self.text.default_color

		if bg_color is None:
			bg_color = self.text.default_bg_color

		if wrap:
			print "Wrapped text is not currently implemented. This feature is pending."
			exit()
			message = self.text.wrapped_text(message, delimiter, font_size, font, wrap_width)
			line_surfaces = []
			message_height = 0
			message_width = 0
			for line in message:
				line_surface = self.text.render_text(line, render_config)
				line_surfaces.append((line_surface, [0, message_height]))
				message_width = peak(line_surface.get_width(), message_width)
				message_height = message_height + line_surface.get_height()
			message_surface = pygame.Surface((message_width, message_height))
			message_surface.fill(bg_color)
			for ls in line_surfaces:
				self.blit(ls[0], 7, ls[1], message_surface)

		#process blit registration
		if location == "center" and registration is None:  # an exception case for perfect centering
			registration = 5
		if registration is None:
			if wrap:
				registration = 5
			else:
				registration = 7

		# process location, infer if need be; failure here is considered fatal
		if location is None:
			# By Default: wrapped text blits to screen center; single-lines blit to topLeft with a padding = fontSize
			if wrap:
				location = Params.screen_c
			else:
				x_offset = (Params.screen_x - Params.screen_x) // 2 + font_size
				y_offset = (Params.screen_y - Params.screen_y) // 2 + font_size
				location = (x_offset, y_offset)
		elif type(location) is str:
			location = absolute_position(location, self.window)
		else:
			try:
				iter(location)
				if len(location) != 2:
					raise ValueError()
			except:
				raise ValueError("Argument 'location' invalid; must be a location string, coordinate tuple, or NoneType")


		if not blit:
			if wrap:
				return message_surface
			else:
				message_surface = self.text.render_text(message, render_config)
				#check for single lines that extend beyond the app area and wrap if need be
				# if message_surface.shape[1] > self.screen_x:
				# 	return self.message(message, wrap=True)
				# else:
				# 	return message_surface
				return message_surface
		else:
			if wrap:
				self.blit(message_surface, registration, Params.screen_c)
			else:
				message_surface = self.text.render_text(message, font, font_size, color, bg_color)
				# if message_surface.shape[1] > self.screen_x:
				# 	wrap = True
				# 	return self.message(message, font, font_size, color, bg_color, location, registration,
				# 						wrap, wrap_width, delimiter, blit, flip)
				self.blit(message_surface, registration, location)
			if flip:
				self.flip()
		return True

	def now(self):
		today = datetime.datetime
		return today.now().strftime("%Y-%m-%d %H:%M:%S")

	def numpy_surface(self, foreground=None, background=None, fg_position=None, bg_position=None, width=None, height=None):
			"""
			Factory method for klibs.NumpySurface
			:param foreground:
			:param background:
			:param width:
			:param height:
			:return:
			"""
			return NumpySurface(foreground, background, fg_position, bg_position, width, height)

	def over_watch(self, event=None):
		"""
		Inspects keyboard events for app-wide functions calls like 'quit', 'calibrate', 'pause', etc.
		When event argument is passed only that event in inspected.
		When called without event argument, pumps and inspects the entire event queue.
		:param event:
		:return:
		"""
		input_collected = False
		repumping = False  # only repump once else holding a modifier key down can keep overwatch running forever
		keysym = None
		mod_name = None
		key_name = None
		event_stack = None
		if event is None:
			event_stack = sdl2.SDL_PumpEvents()
			if type(event_stack) is list:
				event_stack.reverse()
			else:
				return False  # ie. app is in a passive context and no input is happening
		else:
			event_stack = [event]
		while not input_collected:
			event = event_stack.pop()
			if event.type in [sdl2.SDL_KEYUP, sdl2.SDL_KEYDOWN]:
				keysym = event.key.keysym.sym  # keyboard button event object (https://wiki.libsdl.org/SDL_KeyboardEvent)
				key_name = sdl2.keyboard.SDL_GetKeyName(keysym)
				if event.type == sdl2.SDL_KEYUP:  # modifier or no, a key up event implies user decision; exit loop
					input_collected = True
				if key_name not in MOD_KEYS:  # if event key isn't a modifier: get key info & exit loop
					mod_name = sdl2.keyboard.SDL_GetModState()
					input_collected = True
				elif repumping and event.repeat != 0:  # user holding mod key; return control to calling method calling
					return False
				elif len(event_stack) == 0:
					sdl2.SDL_PumpEvents()
					event_stack = sdl2.ext.get_events()
					event_stack.reverse()
					if len(event_stack) > 0:
						repumping = True
					else:
						return False
				else:
					pass
			else:
				return False   # event argument was no good; just bail

		self.ui_request((keysym, mod_name))
		return False

	def pause(self):
		time.sleep(0.2)  # to prevent unpausing immediately due to a key(still)down event
		while self.paused:
			self.message('PAUSED', fullscreen=True, location='center', font_size=96, color=(255, 0, 0, 255),
						registration=5, blit=False)
			self.over_watch()
			self.flip_callback()

	def pre_blit(self, source, start_time, end_time, registration=7, pos=(0, 0), destination=None, flags=None, area=None,
				interim_action=None):
		"""
		Blit to the screen buffer, wait until endTime to flip. Check func often if set.
		:type start_time: float
		:param source:
		:param start_time: Time trial began (from time.time())
		:param end_time: The time post trial after which the screen should be flipped.
		:param registration:
		:param pos:
		:param destination:
		:param flags:
		:param area:
		:param interim_action: A function called repeatedly until the duration has passed. Don't make it long.
		"""
		self.blit(source, registration, pos, destination, flags, area)
		now = time.time()
		while now < start_time + end_time:
			if interim_action is not None:
				interim_action()
			now = time.time()
		self.flip_callback()
		return now - start_time + end_time

	def pre_bug(self):
		#todo: will be a screen that's shown before anything happens in the program to quickly tweak debug settings
		pass

	def query(self, query=None, as_password=False, font=None, font_size=None, color=None,
				locations=None, registration=5, return_type=None, accepted=None):
		input_config = [None, None, None, None]  # font, font_size, color, bg_color
		query_config = [None, None, None, None]
		vertical_padding = None
		input_location = None
		query_location = None
		query_registration = 8
		input_registration = 2

		# build config argument(s) for __render_text()
		# process the possibility of different query/input font sizes
		if font_size is not None:
			if type(font_size) is (tuple or list):
				if len(font_size) == 2:
					input_config[1] = self.text.font_sizes[font_size[0]]
					query_config[1] = self.text.font_sizes[font_size[1]]
					vertical_padding = query_config[1]
					if input_config[1] < query_config[1]:  # smallest  size =  vertical padding from midline
						vertical_padding = input_config[1]
			else:
				input_config[1] = self.text.font_sizes[font_size]
				query_config[1] = self.text.font_sizes[font_size]
				vertical_padding = self.text.font_sizes[font_size]
		else:
			input_config[1] = self.text.default_font_size
			query_config[1] = self.text.default_font_size
			vertical_padding = self.text.default_font_size

		if registration is not None:
			if type(registration) is (tuple or list):
				input_registration = registration[0]
				query_registration = registration[1]
			else:
				input_registration = registration
				query_registration = registration

		# process the (unlikely) possibility of different query/input fonts
		if type(font) is tuple and len(font) == 2:
			input_config[0] = font[0]
			query_config[0] = font[1]
		elif type(font) is str:
			input_config[0] = font
			query_config[0] = font
		else:
			input_config[0] = self.text.default_font
			query_config[0] = self.text.default_font

		# process the possibility of different query/input colors
		if color is not None:
			if len(color) == 2 and all(isinstance(col, tuple) for col in color):
				input_config[2] = color[0]
				query_config[2] = color[1]
			else:
				input_config[2] = color
				query_config[2] = color
		else:
			input_config[2] = self.text.default_input_color
			query_config[2] = self.text.default_color

		# process locations
		generate_locations = False
		if locations is not None:
			if None in (locations.get('query'), locations.get('input')):
				query_location = self.text.fetch_print_location('query')
				input_location = self.text.fetch_print_location('response')
			else:
				query_location = locations['query']
				input_location = locations['input']
		else:
			generate_locations = True
		# infer locations if not provided (ie. center y, pad x from screen midline) create/ render query_surface
		# Note: input_surface not declared until user input received, see while loop below
		query_surface = None
		if query is None:
			query = self.text.fetch_string('query')

		if query:
			query_surface = self.text.render_text(query, *query_config)
		else:
			raise ValueError("A default query string was not set and argument 'query' was not provided")

		query_baseline = (Params.screen_y // 2) - vertical_padding
		input_baseline = (Params.screen_y // 2) + vertical_padding
		horizontal_center = Params.screen_x // 2
		if generate_locations:
			query_location = [horizontal_center, query_baseline]
			input_location = [horizontal_center, input_baseline]

		self.fill((255, 255, 255))
		self.blit(query_surface, query_registration, query_location)
		self.flip()

		# todo: split this into query_draw() [above code] and query_listen() [remaining code]
		input_string = ''  # populated in loop below
		user_finished = False  # True when enter or return are pressed
		no_answer_string = 'Please provide an answer.'
		invalid_answer_string = None

		if accepted is not None:
			try:
				accepted_iter = iter(accepted)
				accepted_str = pretty_join(accepted, delimiter=",", before_last='or', prepend='[ ', append=']')
				invalid_answer_string = 'Your answer must be one of the following: {0}'.format(accepted_str)
			except:
				raise TypeError("Argument 'accepted' must be iterable.")
		while not user_finished:
			sdl2.SDL_PumpEvents()
			for event in sdl2.ext.get_events():
				if event.type == sdl2.SDL_KEYDOWN:
					if input_string == no_answer_string:
						input_string = ''
					key = event.key  # keyboard button event object (https://wiki.libsdl.org/SDL_KeyboardEvent)
					sdl_keysym = key.keysym.sym
					key_name = sdl2.keyboard.SDL_GetKeyName(sdl_keysym)
					shift_key = False
					self.over_watch(event)

					if sdl2.keyboard.SDL_GetModState() in (sdl2.KMOD_LSHIFT, sdl2.KMOD_RSHIFT, sdl2.KMOD_CAPS):
						shift_key = True
					if sdl_keysym == sdl2.SDLK_BACKSPACE:  # ie. backspace
						if input_string:
							input_string = input_string[0:(len(input_string) - 1)]
							render_string = None
							if as_password is True and len(input_string) != 0:
								render_string = len(input_string) * '*'
							else:
								render_string = input_string

							if len(render_string) > 0:
								input_surface = self.text.render_text(render_string, *input_config)
								self.fill()
								self.blit(query_surface, query_registration, query_location)
								self.blit(input_surface, input_registration, input_location)
								self.flip()
							else:
								self.fill()
								self.blit(query_surface, query_registration, query_location)
								self.flip()
					elif sdl_keysym in (sdl2.SDLK_RETURN, sdl2.SDLK_RETURN):  # ie. if enter or return
						invalid_answer = False
						empty_answer = False
						if len(input_string) > 0:
							if accepted:   # to make the accepted list work, there's a lot of checking yet to do
								if input_string in accepted:
									user_finished = True
								else:
									invalid_answer = True
							else:
								user_finished = True
						else:
							empty_answer = True
						if invalid_answer or empty_answer:
							error_string = ""
							if invalid_answer:
								error_string = invalid_answer_string
							else:
								error_string = no_answer_string
							error_config = copy(input_config)
							error_config[2] = self.text.alert_color
							input_surface = self.text.render_text(error_string, *error_config)
							self.fill()
							self.blit(query_surface, query_registration, query_location)
							self.blit(input_surface, input_registration, input_location)
							self.flip()
							input_string = ""
					elif sdl_keysym == sdl2.SDLK_ESCAPE:  # if escape, erase the string
						input_string = ''
						input_surface = self.text.render_text(input_string, *input_config)
						self.fill()
						self.blit(query_surface, query_registration, query_location)
						self.blit(input_surface, input_registration, input_location)
						self.flip()
					else:
						if key_name not in (MOD_KEYS):  # TODO: probably use sdl keysyms as keys instead of key_names
							if shift_key:
								input_string += key_name
							else:
								input_string += key_name.lower()
							input_surface = None
							if as_password:
								if as_password is True and len(input_string) != 0:
									password_string = '' + len(input_string) * '*'
									input_surface = self.text.render_text(password_string, *input_config)
								else:
									input_surface = self.text.render_text(input_string, *input_config)
							else:
								input_surface = self.text.render_text(input_string, *input_config)
							self.fill()
							self.blit(query_surface, query_registration, query_location)
							self.blit(input_surface, input_registration, input_location)
							self.flip()
						# else:
						# 	pass  # until a key-up event occurs, could be a ui request (ie. quit, pause, calibrate)
				elif event.type is sdl2.SDL_KEYUP:
					self.over_watch(event)
		self.fill()
		self.flip()
		if return_type in (int, str):
			if return_type is int:
				return int(input_string)
			if return_type is str:
				return str(input_string)
		else:
			return input_string

	def quit(self):
		try:
			self.db.db.commit()
		except:  # TODO: Determine exception type
			print "Commit() to database failed."
			pass
		try:
			self.db.db.close()
		except:  # TODO: Determine exception tpye
			print "Database close() unsuccessful."
			pass
		if not self.no_tracker:
			if self.el.el.isRecording():
				self.el.el.stopRecording()
		sdl2.SDL_Quit()
		sys.exit()

	def run(self, *args, **kwargs):
		self.__experiment_manager(*args, **kwargs)

	def start(self):
		self.start_time = time.time()

	def fill(self, color=(255, 255, 255), context=None):
		# todo: consider adding sdl2's "area" argument, to fill a subset of the surface
		if len(color) == 3:
			color = rgb_to_rgba(color)
		try:
			context.fill(color)
			# todo need a registry of all NumpySurfaces so they can be erased by name
		except:
			gl.glClearColor(color[0], color[1], color[2], color[3])
			gl.glClear(gl.GL_COLOR_BUFFER_BIT)

	def clear(self, color=(255, 255, 255)):
		self.fill(color)
		self.flip()
		self.fill(color)
		self.flip()

	@property
	def db_name(self):
		return self.__db_name

	@db_name.setter
	def db_name(self, db_name):
		self.__db_name = db_name

	@property
	def event_code_generator(self):
		return self.__event_code_function

	@event_code_generator.setter
	def event_code_generator(self, event_code_function):
		if type(event_code_function).__name__ == 'function':
			self.__event_code_function = event_code_function
		elif event_code_function is None:
			self.__event_code_function = None
		else:
			raise ValueError('App.codeFunc must be set to a function.')

	@property
	def no_tracker(self):
		return self.__no_tracker

	@no_tracker.setter
	def no_tracker(self, no_tracker):
		if type(no_tracker) is bool:
			self.__no_tracker = no_tracker
		else:
			raise ValueError('App.noTracker must be a boolean value.')

	@property
	def screen_ratio(self):
		dividend = round(float(self.screen_x) / float(self.screen_y), 3)
		if dividend == 1.333:
			return "4:3"
		elif dividend == 1.778:
			return "16:9"
		elif dividend == 1.6:
			return "16:10"
		else:
			return "X:Y"

	@property
	def collecting_demographics(self):
		return self.__collecting_demographics

	@collecting_demographics.setter
	def collecting_demographics(self, state):
		if type(state) is bool:
			self.__collecting_demographics = state
		else:
			raise TypeError("collect_demographics must be boolean.")

	@property
	def participant_instructions(self):
		pass

	@participant_instructions.getter
	def participant_instructions(self):
		return self.participant_instructions

	@participant_instructions.setter
	def participant_instructions(self, instructions_file):
		with open("ExpAssets/participant_instructions.txt", "r") as ins_file:
			self.participant_instructions = ins_file.read()

	@abc.abstractmethod
	def clean_up(self):
		return

	@abc.abstractmethod
	def setup(self):
		pass

	@abc.abstractmethod
	def trial(self, trial_factors, trial_num):
		pass

	@abc.abstractmethod
	def trial_prep(self):
		pass

	@abc.abstractmethod
	def trial_clean_up(self):
		pass

	@abc.abstractmethod
	def flip_callback(self, **kwargs):
		pass


class Palette(object):
	def __init__(self):
		
		self.black = (0, 0, 0)
		self.white = (255, 255, 255)
		self.grey1 = (50, 50, 50)
		self.grey2 = (100, 100, 100)
		self.grey3 = (150, 150, 150)
		self.grey4 = (200, 200, 200)
		self.grey5 = (250, 250, 250)
		self.alert = (255, 0, 0)

	def hsl(self, index):
		print("to be defined later")


class Database(object):
	__default_table = None
	__open_entries = {}
	__current_entry = None
	db = None
	cursor = None
	schema = None
	db_backup_path = None
	table_schemas = {}

	def __init__(self):
		self.__init_db()
		self.build_table_schemas()

	def __catch_db_not_found(self):
		self.db = None
		self.cursor = None
		self.schema = None
		err_string = "No database file was present at '{0}'. \nYou can (c)reate it, (s)upply a different path or (q)uit."
		user_action = raw_input(err_string.format(Params.database_path))
		if user_action == "s":
			Params.database_path = raw_input("Great. Where might it be?")
			self.__init_db()
		elif user_action == "c":
			f = open(Params.database_path, "a").close()
			self.__init_db()
		else:
			quit()

	def __init_db(self):
		if os.path.exists(Params.database_path):
			shutil.copy(Params.database_path, Params.database_backup_path)
			self.db = sqlite3.connect(Params.database_path)
			self.cursor = self.db.cursor()
			table_list = self.__tables()
			if len(table_list) == 0:
				if os.path.exists(Params.schema_file_path):
					self.__deploy_schema(Params.schema_file_path)
					return True
				else:
					raise RuntimeError("Database exists but no tables were found and no table schema were provided.")
		else:
			self.__catch_db_not_found()

	def __tables(self):
		#TODO: I changed tableCount to tableList and made it an attribute as it seems to be used in rebuild. Verify this.
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		self.table_list = self.cursor.fetchall()
		return self.table_list

	def __drop_tables(self, table_list=None, kill_app=False):
		if table_list is None:
			table_list = self.__tables()
		for n in table_list:
			if str(n[0]) != "sqlite_sequence":
				self.cursor.execute("DROP TABLE `{0}`".format(str(n[0])))
		self.db.commit()
		if kill_app:
			self.db.close()
			self.__restore()
			quit()

	def __restore(self):
		# restores database file from the back-up of it
		os.remove(Params.database_path)
		os.rename(Params.database_backup_path, Params.database_path)

	def __deploy_schema(self, schema):
		f = open(schema, 'rt')
		self.cursor.executescript(f.read())
		return True

	def build_table_schemas(self):
		self.cursor.execute("SELECT `name` FROM `sqlite_master` WHERE `type` = 'table'")
		tables = {}
		for table in self.cursor.fetchall():
			table = str(table[0])  # unicode value
			if table != "sqlite_sequence":  # a table internal to the database structure
				table_cols = {}
				self.cursor.execute("PRAGMA table_info(" + table + ")")
				columns = self.cursor.fetchall()

				# convert sqlite3 types to python types
				for col in columns:
					if col[2] == 'text':
						col_type = 'str'
					elif col[2] == 'blob':
						col_type = 'binary'
					elif col[2] in ('integer', 'integer key'):
						col_type = 'int'
					elif col[2] in ('float', 'real'):
						col_type = 'float'
					else:
						col_type = 'unknown'
						e_str = "column '{0}' of table '{1}' has type '{2}' on the database but was assigned a type of \
								'unknown' during schema building'"
						self.warn(e_str.format(col[1], table, col[2]), "Database", "build_table_schemas")
					allow_null = False
					if col[3] == 0:
						allow_null = True
					table_cols[str(col[1])] = {'order': int(col[0]), 'type': col_type, 'allow_null': allow_null}
				tables[table] = table_cols
		self.table_schemas = tables

		return True

	def flush(self):
		self.cursor.execute("SELECT `name` FROM `sqlite_master` WHERE `type` = 'table'")
		for tableTuple in self.cursor.fetchall():
			table = str(tableTuple[0]) #str() necessary b/c tableTuple[0] is in unicode
			if table == "sqlite_sequence":
				pass
			else:
				self.cursor.execute("DELETE from `{0}`".format(table))
		self.db.commit()

	def rebuild(self):
		#todo: make this optionally handle the backup database too
		self.__drop_tables()
		e = "Error: Database schema could not be deployed; there is a syntax error in the SQL file."
		if self.schema is not None:
			if self.__deploy_schema(self.schema, False):
				initialized = True
			else:
				self.__drop_tables(self.table_list, True)
				raise IOError(e)
		elif Params.schema_file_path is not None:
			if self.__deploy_schema(Params.schema_file_path):
				initialized = True
			else:
				self.__drop_tables(self.table_list)
				raise IOError(e)

		if self.build_table_schemas():
			self.__open_entries = {}
			self.__current_entry = 'None'
			print  "Database successfully rebuilt; exiting program. Be sure to disable the call to Database.rebuild() before relaunching."
			# TODO: Make this call App.message() somehow so as to be clearer.Or better, relaunch the app somehow!!
			# m = "Database successfully rebuilt; exiting program. Be sure to disable the call to Database.rebuild() before relaunching."
			# App.message(m, location="center", fullscreen=True, fontSize=48, color=(0,255,0))
			quit()

	def entry(self, instance=None):
		if instance is None:
			try:
				return self.__open_entries[self.__current_entry]
			except:
				print self.err() + "Database\n\tentry(): A specific instance name was not provided and there is no current entry set.\n"
		else:
			try:
				return self.__open_entries[instance]
			except:
				print self.err() + "Database\n\tentry(): No currently open entries named '" + instance + "' exist."

	def init_entry(self, table_name, instance_name=None, set_current=True):
		if type(table_name) is str:
			if self.table_schemas[table_name]:
				if instance_name is None:
					instance_name = table_name
				self.__open_entries[instance_name] = EntryTemplate(table_name, self.table_schemas[table_name], instance_name)
				if set_current:
					self.current(instance_name)
			else:
				print "No table with the name '" + table_name + "' was found in the Database.tableSchemas."
		else:
			raise ValueError("tableName must be a string.")

	def empty(self, table):
		pass

	def log(self, field, value, instance=None):
		if instance is not None and self.__open_entries[instance]:
			self.__current_entry = instance
		elif instance is None and self.__current_entry != 'None':
			instance = self.__current_entry
		else:
			raise ValueError("No default entry is set and no instance was passed.")
		self.__open_entries[instance].log(field, value)

	def current(self, verbose=False):
		if verbose == (0 or None or 'None' or False):
			self.__current_entry = 'None'
			return True
		if verbose == 'return':
			return self.__current_entry
		if type(verbose) is str:
			if self.__open_entries[verbose]:
				self.__current_entry = verbose
				return True
			return False
		if self.__current_entry != 'None':
			if verbose:
				return self.__current_entry
			else:
				return True
		else:
			if verbose:
				return 'None'
			else:
				return False

	def is_unique(self, value, field, table):
		query = "SELECT * FROM `{0}` WHERE `{1}` = '{2}'".format(table, field, value)
		self.cursor.execute(query)
		result = self.cursor.fetchall()
		if len(result) > 0:
			return False
		else:
			return True

	def test_data(self, table):
		# TODO: allow rules per column such as length
		pass

	def insert(self, data=None, table=None, tidy_execute=True):
		# todo: check if the table uses participant_id column; if no id in data, add it
		if data is None:
			current = self.current('return')
			data = self.entry(current)
			if not data:
				raise AttributeError("No data was provided and a Database.__currentEntry is not set.")
		data_is_entry_template = False # expected use is to insert from an EntryTemplate object, but raw data is also allowed
		if data.__class__.__name__ == 'EntryTemplate':
			data_is_entry_template = True
			query = data.build_query('insert')
		else:
			# this else statement may be broken as of Aug 2013 (ie. since Ross was involved, it's not been returned to)
			template = None
			if table:
				if not self.__default_table:
					raise AttributeError(
						"Either provide a table when calling insert() or set a defaultTable with App.Database.setDefaultTable().")
				else:
					table = self.__default_table
				template = self.table_schemas[table]
			if not template:
				raise AttributeError(
					"The supplied table name, '{0}' was not found in Database.tableSchemas".format(table))
			field_count = len(template)
			if template['id']:
				field_count -= 1  # id will be supplied by database automatically on cursor.execute()
			clean_data = [None, ] * field_count
			insert_template = [None, ] * field_count
			if len(data) == field_count:
				for fieldName in template:
					field = template[fieldName]
					order = field['order']
					if template['id']:
						order -= 1
					if type(data[order]).__name__ == field['type']:
						insert_template[order] = fieldName
						if field['type'] == ('int' or 'float'):
							clean_data[order] = str(data[order])
						else:
							clean_data[order] = "'" + str(data[order]) + "'"
			else:
				raise AttributeError('Length of data list exceeds number of table columns.')
			query = "INSERT INTO `{0}` ({1}) VALUES ({2})".format(table, ",".join(insert_template), ",".join(clean_data))
		self.cursor.execute(query)
		self.db.commit()
		if tidy_execute and data_is_entry_template:
			if self.__current_entry == data.name:
				self.current()  # when called without a parameter current() clears the current entry
		return True

	def query(self, query, do_return=True):
		result = self.cursor.execute(query)
		self.db.commit()
		if result and do_return:
			return result
		#add in error handling for SQL errors

	def table_headers(self, table, join_with=[], as_string=False):
		# try:
			table = self.table_schemas[table]
			table_headers_list = [None] * len(table)
			participant_headers_list = None
			for column in table:
				table_headers_list[table[column]['order']] = column
			table_headers_list = table_headers_list[1:]  # remove id column

			table_indeces_map = {}  # keeps track of original table column indeces for multiple joins
			for i in range(0, len(table_headers_list)):
				table_indeces_map[str(i)] = i

			# try:
			for join in join_with:
		# 		try:
				print join
				join_headers = self.table_schemas[join[0]]
				excluded_columns = join[2] if len(join) == 3 else []
				join_headers_list = [None] * len(join_headers)
				print join_headers_list
				for column in join_headers:
					if column not in excluded_columns:
						index = join_headers[column]['order']
						join_headers_list[index] = column
				join_headers_list = [col for col in join_headers_list if col is not None]
				join_headers_list = join_headers_list[1:]
							# try:
				print table_indeces_map
				index = table_indeces_map[str(join[1])]
				table_headers_list[index:index] = join_headers_list
				table_indeces_map[str(join[1])] += len(join_headers_list)
				if len(table_indeces_map) < len(table_headers_list):
					table_indeces_map[str(len(table_headers_list))] = len(table_headers_list)
			# 			except Exception as e:
			# 				raise Exception(e)
			# 				raise ValueError("Second element of join_with tables must be a index in range of 'table'")
			# 		except Exception as e:
			# 			raise Exception(e)
			# 			raise ValueError("Table in argument 'join_with' was not found in in Database.tables dict ")
			# except Exception as e:
			# 	raise Exception(e)
#				raise TypeError("Argument 'join_with' must be iterable.")

			return table_headers_list if not as_string else "{0}\n".format("\t ".join(table_headers_list))
		# except:
		# 	raise ValueError("Value for argument 'table' was not found in Database.tables dict.")

	def export(self, path=None, multi_file=True, join_tables=None):
		# todo: write stuff for joining tables
		# todo: add behaviors for how to deal with multiple files with the same participant id (ie. append, overwrite, etc.)
		participants = self.query("SELECT * FROM `participants`").fetchall()
		table_header = self.table_headers("trials", [["participants", 1, ['userhash']]], True)
		# table_header = self.table_headers("trials", as_string=True)
		for p in participants:
			block_num = 1
			trials_this_block = 0
			trials = self.query("SELECT * FROM `trials` WHERE `participant_id` = {0}".format(p[0])).fetchall()
			file_name_str = "p{0}_{1}.txt"
			duplicate_file_name_str = "p{0}.{1}_{2}.txt"
			file_path = Params.data_path
			if len(trials) != Params.trials_per_block * Params.blocks_per_experiment:
				file_path = Params.incomplete_data_path
				file_name_str = "p{0}_{1}_incomplete.txt"
				duplicate_file_name_str = "p{0}.{1}_{2}_incomplete.txt"
			file_name = file_name_str.format(p[0], str(p[5])[:10])  # second format arg = date sliced from date-time
			if os.path.isfile(os.path.join(file_path, file_name)):
				unique_file = False
				append = 1
				while not unique_file:
					file_name = duplicate_file_name_str.format(p[0], append, str(p[5])[:10])
					if not os.path.isfile(os.path.join(file_path, file_name)):
						unique_file = True
					else:
						append += 1
			participant_file = open(os.path.join(file_path, file_name), "w+")
			participant_file.write(table_header)
			for trial in trials:
				trial = trial[1:]
				if trials_this_block == 120:
					block_num += 1
					trials_this_block = 0
				trials_this_block += 1
				trial = list(trial)
				trial[1:1] = p[2:]
				trial[5] = block_num
				row_string = "\t".join([str(col) for col in trial])
				participant_file.write("{0}\n".format(row_string))
			participant_file.close()



	@property
	def default_table(self):
		return self.__default_table

	@default_table.setter
	def default_table(self, name):  # todo: error handling
		self.__default_table = name


class EntryTemplate(object):
	null_field = "DELETE_THIS_FIELD"
	sql_field_delimiter = "`,`"
	table_name = None

	def __init__(self, table_name, table_schema, instance_name):
		
		if type(table_schema) is dict:
			self.schema = table_schema
		else:
			raise TypeError
		if type(table_name) is str:
			self.table_name = table_name
		else:
			raise TypeError
		try:
			self.name = instance_name
			if not self.name:
				raise AttributeError(
					'InstanceName could not be set, ensure parameter is passed during initialization and is a string.')
		except AttributeError as e:
			self.err(e, 'EntryTemplate', '__init__', kill=True)
		self.data = ['null', ] * len(table_schema)  # create an empty tuple of appropriate length

	def pr_schema(self):
		schema_str = "{\n"
		for col in self.schema:
			schema_str += "\t\t\t" + col + " : " + repr(self.schema[col]) + "\n"
		schema_str += "\t\t}"
		return schema_str

	def build_query(self, query_type):
		insert_template = ['null', ] * len(self.schema)
		for field_name in self.schema:
			field_params = self.schema[field_name]
			column_order = field_params['order']
			insert_template[column_order] = field_name
			if self.data[column_order] == self.null_field:
				if field_params['allow_null']:
					insert_template[column_order] = self.null_field
				elif query_type == 'insert' and field_name == 'id':
					self.data[0] = self.null_field
					insert_template[0] = self.null_field
				else:
					raise ValueError("No data for the required (ie. not null) column '{0}'.".format(field_name))

		insert_template = self.__tidy_nulls(insert_template)
		self.data = self.__tidy_nulls(self.data)
		if query_type == 'insert':
			fields = "`{0}`".format(self.sql_field_delimiter.join(insert_template))
			vals = ",".join(self.data)
			query_string = "INSERT INTO `{0}` ({1}) VALUES ({2})".format(self.table_name, fields, vals)
			return query_string
		elif query_type == 'update':
			pass
		#TODO: build logic for update statements as well (as against only insert statements)

	def __tidy_nulls(self, data):
		return filter(lambda column: column != self.null_field, data)

	def log(self, field, value):
		# TODO: Add some basic logic for making type conversions where possible (ie. if expecting a float
		# but an int arrives, try to cast it as a float before giving up
		column_order = self.schema[field]['order']
		column_type = self.schema[field]['type']
		if field not in self.schema:
			raise ValueError("No field named '{0}' exists in the table '{1}'".format(field, self.table_name))
		# SQLite has no bool data type; conversion happens now b/c the value/field comparison below can't handle a bool
		if value is True:
			value = 1
		elif value is False:
			value = 0
		# all values must be strings entering db; values enterting string columns must be single-quote wrapped as well
		if (self.schema[field]['allow_null'] is True) and value is None:
			self.data[column_order] = self.null_field
		elif column_type == 'str':
			self.data[column_order] = "'{0}'".format(str(value))
		else:
			self.data[column_order] = str(value)

	def report(self):
		print self.schema


# class EyeLink(pylink.EyeLink):
# 	dummy_mode = False
# 	__screen_size = None
#
# 	def __init__(self, dummy_mode=False):
# 		self.is_dummy_mode = dummy_mode
#
# 	def tracker_init(self, dummy_mode=False):
# 		if dummy_mode:
# 			self.is_dummy_mode = True
# 		pylink.flushGetkeyQueue()
# 		self.setOfflineMode()
# 		self.sendCommand("screen_pixel_coords = 0 0 {0} {1}".format(self._screenSize[0], self._screenSize[1]))
# 		self.sendMessage("link_event_filter = SACCADE")
# 		self.sendMessage("link_event_data = SACCADE")
# 		self.sendMessage("DISPLAY_COORDS 0 0 {0} {1}".format(self._screenSize[0], self._screenSize[1]))
# 		self.setSaccadeVelocityThreshold(SAC_VEL_THRESH)
# 		self.setAccelerationThreshold(SAC_ACC_THRESH)
# 		self.setMotionThreshold(SAC_MOTION_THRESH)
#
# 	def setup(self, fname="TEST", EDF_PATH="assets" + os.sep + "EDF"):
# 		pylink.openGraphics(self.screen_size)
# 		self.doTrackerSetup()
# 		self.openDataFile(fname + ".EDF")
# 		self.fname = fname
# 		self.EDF_PATH = EDF_PATH
#
# 	def start(self, tnum, samples=1, events=1, linkSamples=1, linkEvents=1):
# 		# ToDo: put some exceptions n here
# 		start = self.startRecording(samples, events, linkSamples, linkEvents)
# 		if start == 0:
# 			if self.__eye():
# 				self.sendMessage("TRIALID {0}".format(str(tnum)))
# 				self.sendMessage("TRIALSTART")
# 				self.sendMessage("SYNCTIME {0}".format('0.0'))
# 				return True
# 			else:
# 				return False
# 		else:
# 			return False
#
# 	def __eye(self):
# 		self.eye = self.eyeAvailable()
# 		if self.eye != -1:
# 			return True
#
# 	def sample(self):
# 		self.__currentSample = self.getNewestSample()
# 		print "Sample = {0}".format(repr(self.__currentSample))
# 		return True
#
# 	def stop(self):
# 		self.stopRecording()
#
# 	def drift(self, loc="center", events=1, samples=1, maxAttempts=1):
# 		if loc == "center":
# 			loc = self.screenc
# 		attempts = 1
# 		result = None
# 		print "Drift Correct Result: ".format(repr(result))
# 		try:
# 			if self.isTuplist(loc):
# 				if events:
# 					if samples:
# 						result = self.doDriftCorrect(loc[0], loc[1], 1, 1)
# 					else:
# 						result = self.doDriftCorrect(loc[0], loc[1], 1, 0)
# 				elif samples:
# 					result = self.doDriftCorrect(loc[0], loc[1], 0, 1)
# 				else:
# 					result = self.el.doDriftCorrect(loc[0], loc[1], 0, 0)
# 		except:
# 			print "****************DRIFT CORRECT EXCEPTION"
# 			return False
# 		# if attempts < maxAttempts:
# 		# 	return self.drift(loc, events, samples, maxAttempts-1)
# 		# else:
# 		# 	return False
# 		# if result == 27 and attempts < maxAttempts:
# 		# 	return self.drift(loc, events, samples, maxAttempts-1)
# 		# elif result == 27 and attempts > maxAttempts:
# 		# 	return False
# 		# else:
# 		# 	return True
# 		return True
#
# 	def gaze(self, eyeReq=None):
# 		if self.dummy_mode:
# 			return pygame.mouse.get_pos()
# 		if self.sample():
# 			if not eyeReq:
# 				rs = self.__currentSample.isRightSample()
# 				ls = self.__currentSample.isLeftSample()
# 				if self.eye == 1 and rs:
# 					return self.__currentSample.getRightEye().getGaze()
# 				if self.eye == 0 and ls:
# 					gaze = self.__currentSample.getLeftEye().getGaze()
# 					print gaze
# 					return gaze
# 				if self.eye == 2:
# 					return self.__currentSample.getLeftEye().getGaze()
# 			else:
# 				if eyeReq == 0:
# 					return self.__currentSample.getLeftEye().getGaze()
# 				if eyeReq == 1:
# 					return self.__currentSample.getLeftEye().getGaze()
# 		else:
# 			e = "Unable to collect a sample from the EyeLink."
# 			raise ValueError(e)
#
# 	def shut_down_eyelink(self):
# 		self.stopRecording()
# 		self.setOfflineMode()
# 		time.sleep(0.5)
# 		self.closeDataFile()  # tell eyelink to close_data_file()
# 		self.receiveDataFile(self.fname, self.EDF_PATH + self.fname)  # copy pa.EDF
# 		self.close()
#
# 	@abc.abstractmethod
# 	def listen(self, **kwargs):
# 		pass
#
# 	@property
# 	def screen_size(self):
# 		return self._screenSize
#
# 	@screen_size.setter
# 	def screen_size(self, screen_size):
# 		if type(screen_size).__name__ in ['tuple', 'list']:
# 			self.__screen_size = screen_size
# 		else:
# 			raise ValueError("EyeLink.screenSize must be a tuple or a list; '{0}' passed.".format(type(screen_size)))
#
# 	@property
# 	def is_dummy_mode(self):
# 		return self.dummy_mode
#
# 	@is_dummy_mode.setter
# 	def is_dummy_mode(self, status):
# 		if type(status) is not bool:
# 			err_string = "Invalid argument provided for setting Eyelink.dummy_mode (boolean required, {0} passed."
# 			raise TypeError(err_string.format(type(status)))
# 		else:
# 			self.dummy_mode = True


class KeyMap(object):
	def __init__(self, name, ui_labels, data_labels, sdl_keysyms):
		self.__any_key = None
		self.any_key_string = "ANY_KEY"
		self.map = [[], [], []]  # ui_labels, data_labels, sdl_keysyms
		if type(name) is str:
			self.name = name
		else:
			raise TypeError("Argument 'name' must be a string.")

		self.__register(ui_labels, sdl_keysyms, data_labels)

	def __str__(self):
		map_string = ""
		for list in self.map:
			map_string += "["
			for key in list:
				map_string += str(key)
			map_string += "],"
		return map_string[0:len(map_string) - 1]  # drop trailing comma

	def __register(self, ui_labels, data_labels, sdl_keysyms, ):
		length = len(ui_labels)
		if not length:
			self.any_key = True

		if any(len(key_arg) != length for key_arg in [ui_labels, sdl_keysyms, data_labels]):
			raise TypeError("Arguments 'ui_labels', 'sdl_keysyms' and 'data_labels' must  the same number of elements.")

		try:
			for key_arg in [ui_labels, sdl_keysyms, data_labels]:
				iterable = iter(key_arg)
		except TypeError:
			raise TypeError("Arguments 'ui_labels', 'sdl_keysyms' and 'data_labels' must be iterable.")

		if all(type(name) is str for name in ui_labels):
			self.map[0] = ui_labels
		else:
			raise TypeError("All elements of 'ui_labels' argument of a KeyMap object must be of type 'str'.")

		if all(type(i) in (int, str) for i in data_labels):
			self.map[1] = data_labels
		else:
			raise TypeError("All elements of 'data_labels' must be of type 'int' or 'str'.")

		if all(type(sdl_keysym) is int for sdl_keysym in sdl_keysyms):
			self.map[2] = sdl_keysyms
		else:
			raise TypeError("All elements of 'sdl_keysyms' argument must be of type 'int'.")

	def validate(self, sdl_keysym):
		if type(sdl_keysym) is int:
			if sdl_keysym in self.map[2]:
				return True
			elif self.any_key:
				return True
			else:
				return False
		else:
			raise TypeError(self.arg_error_str("sdl_keysym", type(sdl_keysym), "int", False))

	def read(self, sdl_keysym, format="ui"):
		if self.any_key:
			return True

		if format == "ui":
			format = 0
		elif format == "data":
			format = 1
		else:
			raise ValueError("Argument 'format' must be either 'ui' or 'data.")

		if type(sdl_keysym) is int:
			if sdl_keysym in self.map[2]:
				return self.map[format][self.map[2].index(sdl_keysym)]
			else:
				raise ValueError("The requested sdl_keysym was not found in the KeyMap '{0}'".format(self.name))
		else:
			raise TypeError("Argument 'sdl_keysym' must be an integer corresponding to an SDL_KeySym value")

	def valid_keys(self):
		if len(self.map[0]) > 0:
			return ", ".join(self.map[0])
		elif self.any_key:
			return "ANY_KEY_ACCEPTED"
		else:
			return None

	# def add_map(self, name, key_names=None, key_codes=None, key_vals=None):
	# 	self.__maps[name] = KeyMap(name, key_names, key_codes, key_vals)
	#
	# def fetch_map(self, name):
	# 	#retrieve registered keymap(s) by name
	# 	if name in self.__maps:
	# 		return self.__maps[name]
	# 	elif name == "any":  # returns first registered map; if using 1 map/project, can call listen() with 1 param only
	# 		if len(self.__maps) > 0:
	# 			map_names = self.__maps.keys()
	# 			return self.__maps[map_names[0]]
	# 	elif name == "*":
	# 		self.__maps['*'] = KeyMap('*', any_key=True)
	# 		return self.__maps['*']

	@property
	def any_key(self):
		return self.__any_key

	@any_key.setter
	def any_key(self, value):
		if type(value) is bool:
			self.__any_key = value
		else:
			raise TypeError("KeyMap.any_key must be a boolean value.")


class TextLayer(object):
	asset_path = "ExpAssets"
	alert_color = (255, 0, 0, 255)
	fonts_directory_path = "/Library/Fonts"
	fonts = {}
	font_sizes = {}
	labels = {}
	monitor_x = None
	monitor_y = None
	queue = {}
	strings = {}
	window_x = None
	window_y = None
	__antialias = True
	__default_color = (0, 0, 0, 255)
	__default_input_color = (3, 118, 163, 255)
	__default_bg_color = (255, 255, 255)
	__default_font_size = None
	__default_font = None
	__print_locations = {'query': None, 'response': None}
	__default_strings = {'query': None, 'response': None}
	__default_message_duration = 1

	def __init__(self, window_dimensions, monitor_dimensions, dpi, default_font=None, default_font_size="18pt",
					asset_path=None, fonts_directory_path=None, default_query_string=None, default_response_string=None,
					default_locations=None):
		
		self.window_x = window_dimensions[0]
		self.window_y = window_dimensions[1]
		self.monitor_x = monitor_dimensions[0]
		self.monitor_y = monitor_dimensions[1]

		if default_response_string:
			self.default_response_string = default_response_string
		if default_query_string:
			self.default_query_string = default_query_string

		if type(default_locations) is list and len(default_locations) == 2:  # query & response exist by default
			self.default_query_location = default_locations[0]
			self.default_response_location = default_locations[1]
		elif type(default_locations) is dict:  # can assert an arbitrarily long number of default locations
			query_location_present = False
			response_location_present = False
			for loc in default_locations:
				if loc == "query":
					query_location_present = True
				if loc == "response":
					response_location_present = True
				if type(default_locations[loc]) is not tuple:
					raise TypeError("Values of default_locations dict keys must be coordinate tuples (ie. x,y).")
			if not query_location_present and response_location_present:
				raise ValueError("default_locations dictionary must contain, minimally, the keys 'query' and 'response'")
			self.__print_locations = default_locations

		if type(asset_path) is str and os.path.exists(asset_path):
			self.asset_path = asset_path

		if type(fonts_directory_path) is str and os.path.exists(fonts_directory_path):
			self.fonts_directory_path = fonts_directory_path

		if type(self.window_x) is int and type(dpi) is int:
			self.__build_font_sizes(dpi)
			self.default_font_size = '18pt'
		else:
			raise ValueError("dpi must be an integer")

		# set a default font, using Trebuchet if not passed; Helvetica is a font suitcase in OS X, and because fuck arial
		if type(default_font) is list:
			if len(default_font) == 2:
				default_font_name, default_font_extension = default_font
				default_font_filename = default_font_name
			elif len(default_font) == 3:
				default_font_name, default_font_filename, default_font_extension = default_font
			else:
				raise ValueError("Argument 'default_font' should be a list of length 2 or 3.")
		else:
			default_font_name, default_font_filename, default_font_extension = ["Arial", "arial", "ttf"]

		if self.add_font(default_font_name, default_font_extension, default_font_filename):
			self.default_font = default_font_name

	def __build_font_sizes(self, dpi):
		size_list = range(3, 96)
		self.font_sizes = {}
		for num in size_list:
			key = str(num) + 'pt'
			self.font_sizes[key] = int(math.floor(1.0 / 72 * dpi * num))

	def __compile_font(self, font_name=None, font_size=None):
		# process font_size argument or assign a default
		if font_size is not None:
			if type(font_size) is str:
				font_size = self.font_sizes[font_size]
			if type(font_size) is not int:
				raise TypeError("font_size must be either a point-string (ie. 18pt) or an int describing pixel height.")
		elif self.__default_font_size:
			font_size = self.__default_font_size
		else:
			raise ValueError("font_size argument is  required or else  default_font_size must be set prior to calling.")
		if not font_name:
			font_name = self.default_font
		return ImageFont.truetype(self.fonts[font_name], font_size)

	def size(self, text):  # TODO: What is this function for?
		rendering_font = ImageFont.truetype(self.default_font, self.__default_font_size)
		return rendering_font.size()

	def render_text(self, string, font=None, font_size=None, color=None, bg_color=None):
		if not color:
			color = self.default_color
		if not font:
			font = self.default_font
		if len(color) == 3:
			color = rgb_to_rgba(color)
		if bg_color and len(bg_color) == 3:
			bg_color = rgb_to_rgba(bg_color)
		else:
			bg_color = (255, 255, 255, 0)

		rendering_font = self.__compile_font(font_name=font, font_size=font_size)
		glyph_bitmap = rendering_font.getmask(string)  # L = antialiasing mode
		bitmap_as_1d_array = numpy.asarray(glyph_bitmap)
		bitmap_as_2d_array = numpy.reshape(bitmap_as_1d_array, (glyph_bitmap.size[1], glyph_bitmap.size[0]), order='C')
		rendered_text = numpy.zeros((glyph_bitmap.size[1], glyph_bitmap.size[0], 4))
		rendered_text[:, :, 0][bitmap_as_2d_array > 0] = color[0] * bitmap_as_2d_array[bitmap_as_2d_array > 0] / 255.0
		rendered_text[:, :, 1][bitmap_as_2d_array > 0] = color[1] * bitmap_as_2d_array[bitmap_as_2d_array > 0] / 255.0
		rendered_text[:, :, 2][bitmap_as_2d_array > 0] = color[2] * bitmap_as_2d_array[bitmap_as_2d_array > 0] / 255.0
		rendered_text[:, :, 3][bitmap_as_2d_array > 0] = color[3] * bitmap_as_2d_array[bitmap_as_2d_array > 0] / 255.0
		rendered_text[:, :, 0][bitmap_as_2d_array == 0] = bg_color[0]
		rendered_text[:, :, 1][bitmap_as_2d_array == 0] = bg_color[1]
		rendered_text[:, :, 2][bitmap_as_2d_array == 0] = bg_color[2]
		rendered_text[:, :, 3][bitmap_as_2d_array == 0] = bg_color[3]

		return NumpySurface(rendered_text.astype(dtype=numpy.uint8))

	def add_font(self, font_name, font_extension="ttf", font_file_name=None):
		"""

		:param font_name: Name of font; should mirror file name without extension. If not, also use font_file_name argument.
		:param font_extension: File extension of the font's file, usually, 'ttf' or 'otf'.
		:param font_file_name: Use to simply 'font name' when file name is large, ie. "Arial Black CN.ttf" => "Arial"
		:return:
		"""
		if type(font_name) is str and type(font_extension) is str:
			if type(font_file_name) is not str:
				font_file_name = ".".join([font_name, font_extension])
			else:
				font_file_name = ".".join([font_file_name, font_extension])
			sys_path = os.path.join(self.fonts_directory_path, font_file_name)
			app_path = os.path.join(self.asset_path, font_file_name)
			if os.path.isfile(sys_path):
				self.fonts[font_name] = sys_path
			elif os.path.isfile(app_path):
				self.fonts[font_name] = app_path
			else:
				e_str = "Font file '{0}' was not found in either system fonts or experiment assets directories"
				raise ImportError(e_str.format(font_file_name))
		else:
			raise TypeError("Arguments 'font' and 'font_extension' must both be strings.")
		return True

	def fetch_print_location(self, location):
		"""

		:param location: String name of stored location (defaults are 'query' and 'response'
		:return: Returns either a tuple of x, y coordinates (if location is found) or False
		"""
		if type(location) is not str:
			raise TypeError("Argument 'location' must be a string.")
		if location in self.__print_locations:
			return self.__print_locations[location]
		else:
			return False

	def fetch_string(self, string_name):
		if type(string_name) is not str:
			raise TypeError("Argument 'string_name' must be a string.")
		if string_name in self.__default_strings:
			return self.__default_strings[string_name]
		else:
			return False

	def wrapped_text(self, text, delimiter=None, font_size=None, font=None, wrap_width=None):
		render_font_name = None
		render_font_size = None
		if font is not None:
			render_font_name = font
		if font_size is not None:
			render_font_size = font_size
		if delimiter is None:
			delimiter = "\n"
		try:
			if wrap_width is not None:
				if type(wrap_width) not in [int, float]:
					e_str = "The config option 'wrapWidth' must be an int or a float; '{0}' was passed. \
							Defaulting to 80% of app width."
					raise ValueError(e_str.format(repr(wrap_width)))
				elif 1 > wrap_width > 0:  # assume it's a percentage of app width.
					wrap_width = int(wrap_width * self.appx)
				elif wrap_width > self.appx or wrap_width < 0:
					e_str = "A wrapWidth of '{0}' was passed which is either too big to fit inside the app or else is\
							negative (and must be positive). Defaulting to 80% of app width."
					raise ValueError(e_str)
				#having passed these tests, wrapWidth must now be correct
			else:
				wrap_width = int(0.8 * self.appx)
		except ValueError as e:
			print self.warn(e.message, {'class': self.__class__.__name__, 'method': 'wrapText'})
			wrap_width = int(0.8 * self.appx)
		render_font = self.__compile_font(render_font_name, render_font_size)
		paragraphs = text.split(delimiter)

		render_lines = []
		line_height = 0
		# this loop was written by Mike Lawrence (mike.lwrnc@gmail.com) and then (slightly) modified for this program
		for p in paragraphs:
			word_list = p.split(' ')
			if len(word_list) == 1:
				render_lines.append(word_list[0])
				if p != paragraphs[len(paragraphs) - 1]:
					render_lines.append(' ')
					line_height += render_font.get_linesize()
			else:
				processed_words = 0
				while processed_words < (len(word_list) - 1):
					current_line_start = processed_words
					current_line_width = 0

					while (processed_words < (len(word_list) - 1)) and (current_line_width <= wrap_width):
						processed_words += 1
						current_line_width = render_font.size(' '.join(word_list[current_line_start:(processed_words + 1)]))[0]
					if processed_words < (len(word_list) - 1):
						#last word went over, paragraph continues
						render_lines.append(' '.join(word_list[current_line_start:(processed_words - 1)]))
						line_height = line_height + render_font.get_linesize()
						processed_words -= 1
					else:
						if current_line_width <= wrap_width:
							#short final line
							render_lines.append(' '.join(word_list[current_line_start:(processed_words + 1)]))
							line_height = line_height + render_font.get_linesize()
						else:
							#full line then 1 word final line
							render_lines.append(' '.join(word_list[current_line_start:processed_words]))
							line_height = line_height + render_font.get_linesize()
							render_lines.append(word_list[processed_words])
							line_height = line_height + render_font.get_linesize()
						#at end of paragraph, check whether a inter-paragraph space should be added
						if p != paragraphs[len(paragraphs) - 1]:
							render_lines.append(' ')
							line_height = line_height + render_font.get_linesize()
		return render_lines

	@property
	def antialias(self):
		return self.__antialias

	@antialias.setter
	# @canonical
	def antialias(self, state):
		"""

		:param state:
		"""
		if type(state) is bool:
			self.__antialias = state
		else:
			raise TypeError("Argument 'state' must be boolean.")

	@property
	def default_query_location(self):
		return self.__print_locations['query']

	@default_query_location.setter
	def default_query_location(self, query_location):
		"""
		Set the default screen locations for prompts and responses
		:param query: Set the location of questions to the user.
		"""
		if type(query_location) is tuple:
			self.__print_locations['query'] = query_location
		else:
			raise TypeError("query_location must be a tuple of integers reflecting x and y coordinates.")

	@property
	def default_response_location(self):
		return self.__print_locations['response']

	@default_response_location.setter
	def default_response_location(self, response_location):
		"""
		Set the default screen locations for prompts and responses
		:param response: Set the location of user input for responding to a query
		"""
		if type(response_location) is tuple:
			self.__print_locations['response'] = response_location
		else:
			raise TypeError("response_location must be a tuple of integers reflecting x and y coordinates.")

	@property
	def default_query_string(self):
		return self.__default_strings['query']

	@default_query_string.setter
	def default_query_string(self, query_string):
		if type(query_string) is str:
			self.__default_strings['query'] = query_string
		else:
			raise TypeError("'query_string' must be a string.")

	@property
	def default_response_string(self):
		return self.__default_strings['response']

	@default_response_string.setter
	def default_response_string(self, response_string):
		if type(response_string) is str:
			self.__default_string['response'] = response_string
		else:
			raise TypeError("'response_string' must be a string.")

	@property
	def default_color(self):
		"""

		:return:
		"""
		return self.__default_color

	@default_color.setter
	def default_color(self, color):
		"""

		:param color:
		"""
		if type(color) is list:
			self.__default_color = color

	@property
	def default_input_color(self):
		"""

		:return:
		"""
		return self.__default_color

	@default_input_color.setter
	def default_input_color(self, color):
		"""

		:param color:
		"""
		if type(color) in (list, tuple):
			self.__default_input_color = color

	@property
	def default_bg_color(self):
		"""

		:return:
		"""
		return self.__default_bg_color

	@default_bg_color.setter
	def default_bg_color(self, color):
		"""

		:param color:
		"""
		if type(color) is list:
			self.__default_bg_color = color

	@property
	def default_font_size(self):
		return self.__default_font_size

	@default_font_size.setter
	def default_font_size(self, size):
		"""

		:param size:
		"""
		if type(size) is str:
			self.__default_font_size = self.font_sizes[size]
		elif type(size) is int:
			size = str(size) + "pt"
			self.__default_font_size = self.font_sizes[size]

	@property
	def default_font(self):
		"""

		:return:
		"""
		return self.__default_font

	@default_font.setter
	def default_font(self, font):
		"""

		:param font:
		:raise:
		"""
		self.__default_font = font

	def add_query(self, label, string):
		if type(label) is str and type(string) is str:
			self.labels[label] = string


class NullColumn(Exception):
	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return self.msg


class DatabaseException(Exception):
	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return self.msg

#####################################################
#
# SDL Keycode Reference for creating KeyMaps (https://wiki.libsdl.org/SDL_Keycode)
#
# 2 = SDLK_2
# 3 = SDLK_3
# 4 = SDLK_4
# 5 = SDLK_5
# 6 = SDLK_6
# 7 = SDLK_7
# 8 = SDLK_8
# 9 = SDLK_9
# A = SDLK_a
# B = SDLK_b
# AC Back (the Back key (application control keypad)) = SDLK_AC_BACK
# AC Bookmarks (the Bookmarks key (application control keypad)) = SDLK_AC_BOOKMARKS
# AC Forward (the Forward key (application control keypad)) = SDLK_AC_FORWARD
# AC Home (the Home key (application control keypad)) = SDLK_AC_HOME
# AC Refresh (the Refresh key (application control keypad)) = SDLK_AC_REFRESH
# AC Search (the Search key (application control keypad)) = SDLK_AC_SEARCH
# AC Stop (the Stop key (application control keypad)) = SDLK_AC_STOP
# Again (the Again key (Redo)) = SDLK_AGAIN
# AltErase (Erase-Eaze) = SDLK_ALTERASE
# " = SDLK_QUOTE
# Application (the Application / Compose / Context Menu (Windows) key ) = SDLK_APPLICATION
# AudioMute (the Mute volume key) = SDLK_AUDIOMUTE
# AudioNext (the Next Track media key) = SDLK_AUDIONEXT
# AudioPlay (the Play media key) = SDLK_AUDIOPLAY
# AudioPrev (the Previous Track media key) = SDLK_AUDIOPREV
# AudioStop (the Stop media key) = SDLK_AUDIOSTOP
# \ (Located at the lower left of the return key on ISO keyboards and at the right end of the QWERTY row on ANSI keyboards. Produces REVERSE SOLIDUS (backslash) and VERTICAL LINE in a US layout, REVERSE SOLIDUS and VERTICAL LINE in a UK Mac layout, NUMBER SIGN and TILDE in a UK Windows layout, DOLLAR SIGN and POUND SIGN in a Swiss German layout, NUMBER SIGN and APOSTROPHE in a German layout, GRAVE ACCENT and POUND SIGN in a French Mac layout, and ASTERISK and MICRO SIGN in a French Windows layout.) = SDLK_BACKSLASH
# Backspace = SDLK_BACKSPACE
# BrightnessDown (the Brightness Down key) = SDLK_BRIGHTNESSDOWN
# BrightnessUp (the Brightness Up key) = SDLK_BRIGHTNESSUP
# C = SDLK_c
# Calculator (the Calculator key) = SDLK_CALCULATOR
# Cancel = SDLK_CANCEL
# CapsLock = SDLK_CAPSLOCK
# Clear = SDLK_CLEAR
# Clear / Again = SDLK_CLEARAGAIN
# , = SDLK_COMMA
# Computer (the My Computer key) = SDLK_COMPUTER
# Copy = SDLK_COPY
# CrSel = SDLK_CRSEL
# CurrencySubUnit (the Currency Subunit key) = SDLK_CURRENCYSUBUNIT
# CurrencyUnit (the Currency Unit key) = SDLK_CURRENCYUNIT
# Cut = SDLK_CUT
# D = SDLK_d
# DecimalSeparator (the Decimal Separator key) = SDLK_DECIMALSEPARATOR
# Delete = SDLK_DELETE
# DisplaySwitch (display mirroring/dual display switch, video mode switch) = SDLK_DISPLAYSWITCH
# Down (the Down arrow key (navigation keypad)) = SDLK_DOWN
# E = SDLK_e
# Eject (the Eject key) = SDLK_EJECT
# End = SDLK_END
# = = SDLK_EQUALS
# Escape (the Esc key) = SDLK_ESCAPE
# Execute = SDLK_EXECUTE
# ExSel = SDLK_EXSEL
# F = SDLK_f
# F1 = SDLK_F1
# F10 = SDLK_F10
# F11 = SDLK_F11
# F12 = SDLK_F12
# F13 = SDLK_F13
# F14 = SDLK_F14
# F15 = SDLK_F15
# F16 = SDLK_F16
# F17 = SDLK_F17
# F18 = SDLK_F18
# F19 = SDLK_F19
# F2 = SDLK_F2
# F20 = SDLK_F20
# F21 = SDLK_F21
# F22 = SDLK_F22
# F23 = SDLK_F23
# F24 = SDLK_F24
# F3 = SDLK_F3
# F4 = SDLK_F4
# F5 = SDLK_F5
# F6 = SDLK_F6
# F7 = SDLK_F7
# F8 = SDLK_F8
# F9 = SDLK_F9
# Find = SDLK_FIND
# G = SDLK_g
# ` = SDLK_BACKQUOTE
# H = SDLK_h
# Help = SDLK_HELP
# Home = SDLK_HOME
# I = SDLK_i
# Insert (insert on PC, help on some Mac keyboards (but does send code 73, not 117)) = SDLK_INSERT
# J = SDLK_j
# K = SDLK_k
# KBDIllumDown (the Keyboard Illumination Down key) = SDLK_KBDILLUMDOWN
# KBDIllumToggle (the Keyboard Illumination Toggle key) = SDLK_KBDILLUMTOGGLE
# KBDIllumUp (the Keyboard Illumination Up key) = SDLK_KBDILLUMUP
# Keypad 0 (the 0 key (numeric keypad)) = SDLK_KP_0
# Keypad 00 (the 00 key (numeric keypad)) = SDLK_KP_00
# Keypad 000 (the 000 key (numeric keypad)) = SDLK_KP_000
# Keypad 1 (the 1 key (numeric keypad)) = SDLK_KP_1
# Keypad 2 (the 2 key (numeric keypad)) = SDLK_KP_2
# Keypad 3 (the 3 key (numeric keypad)) = SDLK_KP_3
# Keypad 4 (the 4 key (numeric keypad)) = SDLK_KP_4
# Keypad 5 (the 5 key (numeric keypad)) = SDLK_KP_5
# Keypad 6 (the 6 key (numeric keypad)) = SDLK_KP_6
# Keypad 7 (the 7 key (numeric keypad)) = SDLK_KP_7
# Keypad 8 (the 8 key (numeric keypad)) = SDLK_KP_8
# Keypad 9 (the 9 key (numeric keypad)) = SDLK_KP_9
# Keypad A (the A key (numeric keypad)) = SDLK_KP_A
# Keypad & (the & key (numeric keypad)) = SDLK_KP_AMPERSAND
# Keypad @ (the @ key (numeric keypad)) = SDLK_KP_AT
# Keypad B (the B key (numeric keypad)) = SDLK_KP_B
# Keypad Backspace (the Backspace key (numeric keypad)) = SDLK_KP_BACKSPACE
# Keypad Binary (the Binary key (numeric keypad)) = SDLK_KP_BINARY
# Keypad C (the C key (numeric keypad)) = SDLK_KP_C
# Keypad Clear (the Clear key (numeric keypad)) = SDLK_KP_CLEAR
# Keypad ClearEntry (the Clear Entry key (numeric keypad)) = SDLK_KP_CLEARENTRY
# Keypad : (the : key (numeric keypad)) = SDLK_KP_COLON
# Keypad , (the Comma key (numeric keypad)) = SDLK_KP_COMMA
# Keypad D (the D key (numeric keypad)) = SDLK_KP_D
# Keypad && (the && key (numeric keypad)) = SDLK_KP_DBLAMPERSAND
# Keypad || (the || key (numeric keypad)) = SDLK_KP_DBLVERTICALBAR
# Keypad Decimal (the Decimal key (numeric keypad)) = SDLK_KP_DECIMAL
# Keypad / (the / key (numeric keypad)) = SDLK_KP_DIVIDE
# Keypad E (the E key (numeric keypad)) = SDLK_KP_E
# Keypad Enter (the Enter key (numeric keypad)) = SDLK_KP_ENTER
# Keypad = (the = key (numeric keypad)) = SDLK_KP_EQUALS
# Keypad = (AS400) (the Equals AS400 key (numeric keypad)) = SDLK_KP_EQUALSAS400
# Keypad ! (the ! key (numeric keypad)) = SDLK_KP_EXCLAM
# Keypad F (the F key (numeric keypad)) = SDLK_KP_F
# Keypad < (the Greater key (numeric keypad)) = SDLK_KP_GREATER
# Keypad # (the # key (numeric keypad)) = SDLK_KP_HASH
# Keypad Hexadecimal (the Hexadecimal key (numeric keypad)) = SDLK_KP_HEXADECIMAL
# Keypad { (the Left Brace key (numeric keypad)) = SDLK_KP_LEFTBRACE
# Keypad ( (the Left Parenthesis key (numeric keypad)) = SDLK_KP_LEFTPAREN
# Keypad > (the Less key (numeric keypad)) = SDLK_KP_LESS
# Keypad MemAdd (the Mem Add key (numeric keypad)) = SDLK_KP_MEMADD
# Keypad MemClear (the Mem Clear key (numeric keypad)) = SDLK_KP_MEMCLEAR
# Keypad MemDivide (the Mem Divide key (numeric keypad)) = SDLK_KP_MEMDIVIDE
# Keypad MemMultiply (the Mem Multiply key (numeric keypad)) = SDLK_KP_MEMMULTIPLY
# Keypad MemRecall (the Mem Recall key (numeric keypad)) = SDLK_KP_MEMRECALL
# Keypad MemStore (the Mem Store key (numeric keypad)) = SDLK_KP_MEMSTORE
# Keypad MemSubtract (the Mem Subtract key (numeric keypad)) = SDLK_KP_MEMSUBTRACT
# Keypad - (the - key (numeric keypad)) = SDLK_KP_MINUS
# Keypad * (the * key (numeric keypad)) = SDLK_KP_MULTIPLY
# Keypad Octal (the Octal key (numeric keypad)) = SDLK_KP_OCTAL
# Keypad % (the Percent key (numeric keypad)) = SDLK_KP_PERCENT
# Keypad . (the . key (numeric keypad)) = SDLK_KP_PERIOD
# Keypad + (the + key (numeric keypad)) = SDLK_KP_PLUS
# Keypad +/- (the +/- key (numeric keypad)) = SDLK_KP_PLUSMINUS
# Keypad ^ (the Power key (numeric keypad)) = SDLK_KP_POWER
# Keypad } (the Right Brace key (numeric keypad)) = SDLK_KP_RIGHTBRACE
# Keypad ) (the Right Parenthesis key (numeric keypad)) = SDLK_KP_RIGHTPAREN
# Keypad Space (the Space key (numeric keypad)) = SDLK_KP_SPACE
# Keypad Tab (the Tab key (numeric keypad)) = SDLK_KP_TAB
# Keypad | (the | key (numeric keypad)) = SDLK_KP_VERTICALBAR
# Keypad XOR (the XOR key (numeric keypad)) = SDLK_KP_XOR
# L = SDLK_l
# Left Alt (alt, option) = SDLK_LALT
# Left Ctrl = SDLK_LCTRL
# Left (the Left arrow key (navigation keypad)) = SDLK_LEFT
# [ = SDLK_LEFTBRACKET
# Left GUI (windows, command (apple), meta) = SDLK_LGUI
# Left Shift = SDLK_LSHIFT
# M = SDLK_m
# Mail (the Mail/eMail key) = SDLK_MAIL
# MediaSelect (the Media Select key) = SDLK_MEDIASELECT
# Menu = SDLK_MENU
# - = SDLK_MINUS
# Mute = SDLK_MUTE
# N = SDLK_n
# Numlock (the Num Lock key (PC) / the Clear key (Mac)) = SDLK_NUMLOCKCLEAR
# O = SDLK_o
# Oper = SDLK_OPER
# Out = SDLK_OUT
# P = SDLK_p
# PageDown = SDLK_PAGEDOWN
# PageUp = SDLK_PAGEUP
# Paste = SDLK_PASTE
# Pause (the Pause / Break key) = SDLK_PAUSE
# . = SDLK_PERIOD
# Power (The USB document says this is a status flag, not a physical key - but some Mac keyboards do have a power key.) = SDLK_POWER
# PrintScreen = SDLK_PRINTSCREEN
# Prior = SDLK_PRIOR
# Q = SDLK_q
# R = SDLK_r
# Right Alt (alt gr, option) = SDLK_RALT
# Right Ctrl = SDLK_RCTRL
# Return (the Enter key (main keyboard)) = SDLK_RETURN
# Return = SDLK_RETURN2
# Right GUI (windows, command (apple), meta) = SDLK_RGUI
# Right (the Right arrow key (navigation keypad)) = SDLK_RIGHT
# ] = SDLK_RIGHTBRACKET
# Right Shift = SDLK_RSHIFT
# S = SDLK_s
# ScrollLock = SDLK_SCROLLLOCK
# Select = SDLK_SELECT
# ; = SDLK_SEMICOLON
# Separator = SDLK_SEPARATOR
# / = SDLK_SLASH
# Sleep (the Sleep key) = SDLK_SLEEP
# Space (the Space Bar key(s)) = SDLK_SPACE
# Stop = SDLK_STOP
# SysReq (the SysReq key) = SDLK_SYSREQ
# T = SDLK_t
# Tab (the Tab key) = SDLK_TAB
# ThousandsSeparator (the Thousands Separator key) = SDLK_THOUSANDSSEPARATOR
# U = SDLK_u
# Undo = SDLK_UNDO
# Up (the Up arrow key (navigation keypad)) = SDLK_UP
# V = SDLK_v
# VolumeDown = SDLK_VOLUMEDOWN
# VolumeUp = SDLK_VOLUMEUP
# W = SDLK_w
# WWW (the WWW/World Wide Web key) = SDLK_WWW
# X = SDLK_x
# Y = SDLK_y
# Z = SDLK_z

#===================== SDL2 event codes
#
# SDL_FIRSTEVENT => 0
# SDL_QUIT => 256
# SDL_APP_TERMINATING => 257
# SDL_APP_LOWMEMORY => 258
# SDL_APP_WILLENTERBACKGROUND => 259
# SDL_APP_DIDENTERBACKGROUND => 260
# SDL_APP_WILLENTERFOREGROUND => 261
# SDL_APP_DIDENTERFOREGROUND => 262
# SDL_WINDOWEVENT => 512
# SDL_SYSWMEVENT => 513
# SDL_KEYDOWN => 768
# SDL_KEYUP => 769
# SDL_TEXTEDITING => 770
# SDL_TEXTINPUT => 771
# SDL_MOUSEMOTION => 1024
# SDL_MOUSEBUTTONDOWN => 1025
# SDL_MOUSEBUTTONUP => 1026
# SDL_MOUSEWHEEL => 1027
# SDL_JOYAXISMOTION => 1536
# SDL_JOYBALLMOTION => 1537
# SDL_JOYHATMOTION => 1538
# SDL_JOYBUTTONDOWN => 1539
# SDL_JOYBUTTONUP => 1540
# SDL_JOYDEVICEADDED => 1541
# SDL_JOYDEVICEREMOVED => 1542
# SDL_CONTROLLERAXISMOTION => 1616
# SDL_CONTROLLERBUTTONDOWN => 1617
# SDL_CONTROLLERBUTTONUP => 1618
# SDL_CONTROLLERDEVICEADDED => 1619
# SDL_CONTROLLERDEVICEREMOVED => 1620
# SDL_CONTROLLERDEVICEREMAPPED => 1621
# SDL_FINGERDOWN => 1792
# SDL_FINGERUP => 1793
# SDL_FINGERMOTION => 1794
# SDL_DOLLARGESTURE => 2048
# SDL_DOLLARRECORD => 2049
# SDL_MULTIGESTURE => 2050
# SDL_CLIPBOARDUPDATE => 2304
# SDL_DROPFILE => 4096
# SDL_RENDER_TARGETS_RESET => 8192
# SDL_RENDER_DEVICE_RESET => 8193
# SDL_USEREVENT => 32768
# SDL_LASTEVENT => 65535

# SDL2 MOD KEYS

# KMOD_NONE = 0
# KMOD_LSHIFT = 1
# KMOD_RSHIFT = 2
# KMOD_LCTRL = 64
# KMOD_RCTRL = 128
# KMOD_LALT = 256
# KMOD_RALT = 512
# KMOD_LGUI = 1024   left command
# KMOD_RGUI = 2048   right command
# KMOD_NUM = 4096
# KMOD_CAPS = 8192
# KMOD_MODE = 16384
# KMOD_RESERVED = 32768

#####################################################
