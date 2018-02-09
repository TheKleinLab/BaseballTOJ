__author__ = "Jon Mulle"


# Import required KLibs classes and functions

import klibs
from klibs.KLExceptions import *
from klibs import P
from klibs.KLUtilities import *
from klibs.KLKeyMap import KeyMap
from klibs.KLUserInterface import any_key
from klibs.KLGraphics import fill, blit, flip, clear
from klibs.KLGraphics.colorspaces import const_lum
from klibs.KLGraphics.KLNumpySurface import NumpySurface
import klibs.KLGraphics.KLDraw as kld
from klibs.KLCommunication import message

# Import additional required libraries

import os
import time
from PIL import Image
import sdl2
import sdl2.ext
import numpy as np
import math
import aggdraw
import random
from copy import copy

# Define colours for the experiment

WHITE = [255, 255, 255, 255]
LIGHT_BLUE = [20, 180, 220, 255]

# Define some constants to avoid retyping strings throughout

PI = math.pi
NA = "NA"
TOJ = "toj"
BASE = "base"
GLOVE = "glove"
BALL = "ball"
RUNNER = "runner"
GLOVE_LIKELY = "glove_likely"
BASE_LIKELY = "base_likely"
MAX_WAIT = 5
TIMEOUT = "timeout"


P.exp_meta_factors = {"probe_target_distribution": [{BASE: 0.8, GLOVE: 0.2}, {BASE: 0.2, GLOVE: 0.8}]}


class BaseballTOJ(klibs.Experiment):
	
	"""
	A brief explanation of the experiment file structure:
	
	Here we define a class with the name of our experiment, and override some of its
	functions to specify what we want it to do. When a KLibs project such as this one
	is launched from the terminal using the klibs runtime environment, it imports and
	instantiates the class defined here and then calls its 'run' method to start the 
	experiment, which runs the methods defined here in sequence sort of like this:
	
	# start of experiment #
	self.setup()
	for block in self.blocks:
		self.block()
		for trials in block:
			self.setup_response_collector()
			self.trial_prep()
			self.trial()
			self.trial_clean_up()
	self.clean_up()
	
	The number of blocks to run and number of trials per block are specified in the
	project's params.py file, and the trial factors for each trial are generated in a
	counterbalanced fashion and shuffled based on the contents of its independent_vars.py file.
	The runtime environment also provides some useful attributes to the experiment class, such as:
	
	self.el (EyeLink eye tracker object)
	self.db (Database connection for writing out data)
	self.txtm (Text manager for managing font styles)
	self.tk (TimeKeeper that can be used for timing events in the experiment)
	self.evm (EventManager, which can also be used for timing events)
	self.rc (a ResponseCollector object for collecting responses)
	"""
	
	scene_frames_cut = 300
	scene_path = None
	ball_frames_path = None
	scene_frames = []
	ball_frames = []
	glove_mask = None

	ball_frame_count = None	 # used in set-up to compute number of ball surfaces needed
	ball_vanish_line = 575	# ditto
	ball_speed = -30  # px per frame
	ball_y = None  # used in play_video()
	ball_x = None  # ditto
	ball_initial_x = 1810
	ball_initial_y = 595
	baserun_offsets = range(1, 30, 1)  # list of numbers from which to choose the frame of jitter runner start
	baserun_offset = None  # used in play_video(), set in trial_prep
	baserun_constant = 92  # number of frames to show, every time, before contact with base; jitter added to this
	post_arrival_buffer_frames = None  # ms
	contact_frame_pre_cut = 467
	contact_frame = None
	contact_time = NA

	strings = {"choose_color": "Click the color which best matches the flash from the video.",
				"timeout": "Too slow! Try to respond faster."}

	wheel = None
	color_arcs = range(0, 360, 12)
	color_list = []
	wheel_diam = None
	wheel_dimensions = None
	wheel_rad = None
	wheel_bounds = []
	wheel_thickness = None
	wheel_stroke = None

	probe = None
	probe_locations = {BASE: [320, 560], GLOVE: [560, 245]}
	probe_frame_count = 20
	probe_frames = []
	probe_dimensions = (20, 20)	 # px
	probe_distribution = None

	# these vars are set and removed each trial
	since_last_trial = None
	probe_color = None
	probe_location = None
	probe_location_name = None
	response_timeout = 2  # seconds
	color_diff = NA
	color_response = NA
	toj_response = NA
	response_time = NA
	rt_start = None

	last_likely_probe = None


	def __init__(self, *args, **kwargs):
		super(BaseballTOJ, self).__init__(*args, **kwargs)

	def setup(self):
		
		self.txtm.add_style("large", 48)
		self.txtm.add_style("loc", 48, color=LIGHT_BLUE)
		
		self.since_last_trial = 0
		if P.screen_x > 1024:
			x_offset = (P.screen_x - 1024) // 2
			self.probe_locations[BASE][0] += x_offset
			self.probe_locations[GLOVE][0] += x_offset
			self.ball_vanish_line += x_offset
			self.ball_initial_x = x_offset + 1024 + 20	# 20 = width of ball image
		if P.screen_y > 768:
			y_offset = int((P.screen_y - 768) // 2)
			self.probe_locations[BASE][1] += y_offset
			self.probe_locations[GLOVE][1] += y_offset
			self.ball_initial_y = y_offset + 259

		self.scene_path = os.path.join(P.image_dir, 'JPG')
		self.ball_frames_path = os.path.join(P.image_dir, 'rendered_ball_blur')
		self.color_list = const_lum
		self.wheel_diam = int(8 * P.pixels_per_degree)
		self.wheel_dimensions = (self.wheel_diam, self.wheel_diam)
		self.wheel_rad = self.wheel_diam / 2
		self.wheel_bounds = []
		self.wheel_thickness = 0.1 * self.wheel_diam
		self.wheel_stroke = 0.01 * self.wheel_diam
		self.post_arrival_buffer_frames = 19
		self.ball_x = copy(self.ball_initial_x)
		self.ball_y = copy(self.ball_initial_y)
		self.glove_mask = NumpySurface(os.path.join(P.image_dir,  "glove_mask.png"))
		self.contact_frame = self.contact_frame_pre_cut - self.scene_frames_cut

		P.key_maps["toj"] = KeyMap("toj", ["s", "o"], ["safe", "out"], [sdl2.SDLK_s, sdl2.SDLK_o])
		P.key_maps["trial_start"] = KeyMap("trial_start", ["spacebar"], ["spacebar"], [sdl2.SDLK_SPACE])
		P.key_maps["block_start"] = KeyMap("block_start", ["j"], ["j"], [sdl2.SDLK_j])

		for x in range(1, 522 - self.scene_frames_cut):
			sdl2.SDL_PumpEvents()
			fill()
			frames = 1.0 * (522 - self.scene_frames_cut)
			percent = int((x / frames) * 100)
			msg_str = "Loading... ({0}%)"
			funny_mode = True
			if funny_mode:
				if percent < 25:
					msg_str = "Loading science... ({0}%)"
				elif percent < 50:
					msg_str = "Smashing atoms ... ({0}%)"
				elif percent < 75:
					msg_str = "Generating quandries ... ({0}%)"
				elif percent < 90:
					msg_str = "Reinventing wheels... ({0}%)"
			fill(WHITE)
			blit(message(msg_str.format(percent), blit_txt=False), 5, P.screen_c)
			flip()
			x = str(int(x * 2) + (2 * self.scene_frames_cut)).zfill(8)
			path = os.path.join(self.scene_path, "{0}.jpg".format(x))
			surface = NumpySurface(path)
			surface.prerender()
			self.scene_frames.append(surface)

		for x in range(1, 25):
			x = str(x).zfill(2)
			path = os.path.join(self.ball_frames_path, "{0}.png".format(x))
			surface = NumpySurface(path)
			surface.prerender()
			self.ball_frames.append(surface)

		self.ball_frame_count = int(abs(math.ceil((self.ball_initial_x - self.ball_vanish_line) / self.ball_speed)))

		#  extend list of ball frames surfaces to be long enough for entire animation (ie. repeat from frame 0)
		if self.ball_frame_count > len(self.ball_frames):
			diff = self.ball_frame_count - len(self.ball_frames)
			self.ball_frames.append(self.ball_frames[0: diff])
		elif self.ball_frame_count < len(self.ball_frames):
			self.ball_frames = self.ball_frames[0: self.ball_frame_count]

	def block(self):
		if self.last_likely_probe is None:
			self.last_likely_probe = BASE if P.version == GLOVE_LIKELY else GLOVE

		if self.last_likely_probe == BASE:
			self.last_likely_probe = GLOVE
			self.probe_distribution = P.exp_meta_factors['probe_target_distribution'][1]
			likely_location = GLOVE
			unlikely_location = BASE
		else:
			self.last_likely_probe = BASE
			self.probe_distribution = P.exp_meta_factors['probe_target_distribution'][0]
			likely_location = BASE
			unlikely_location = GLOVE

		# probe_target_cond_count = len(P.exp_factors["probe_targets"])
		# toj_cond_count = P.exp_factors["probe_targets"].count(TOJ)
		# probe_cond_count = probe_target_cond_count - toj_cond_count
		# probe_trial_ratio = probe_target_cond_count // probe_cond_count
		# glove_trials = int((P.trials_per_block // probe_trial_ratio) * self.probe_distribution[GLOVE]) * [GLOVE]
		# base_trials = int((P.trials_per_block // probe_trial_ratio) * self.probe_distribution[BASE]) * [BASE]
		# self.probe_trials = glove_trials + base_trials
		# random.shuffle(self.probe_trials)
		# for i in range(0, len(self.probe_trials)):
		#	self.probe_trials[i] = self.probe_locations[self.probe_trials[i]]

		clear()
		blocks_remaining_str = "Block {0} of {1}".format(P.block_number, P.blocks_per_experiment)
		fill()
		message(blocks_remaining_str, location=[P.screen_c[0], 50], registration=5)
		locations = [(P.screen_c[0], (P.screen_c[1] // 1.1) - 50),
					(P.screen_c[0], (P.screen_c[1] // 1.1)),
					(P.screen_c[0], (P.screen_c[1] // 0.9) - 50),
					(P.screen_c[0], (P.screen_c[1] // 0.9))]
		distribution_strings = ["During the next block of trials, the colored disk will appear more frequently at the:",
								"and less likely at the:"]
		message(distribution_strings[0], location=locations[0], registration=5)
		message(likely_location, "loc", location=locations[1], registration=5)
		message(distribution_strings[1], location=locations[2], registration=5)
		message(unlikely_location, "loc", location=locations[3], registration=5)
		message("Press j to start.", location=[P.screen_c[0], P.screen_y * 0.8], registration=5)
		#flip()
		#any_key()
		self.listen(MAX_WAIT, 'block_start')

	def flip_callback(self):
		return True

	def trial_prep(self):
		self.wheel = self.wheel_surface(random.uniform(0, 360))
		#self.wheel = kld.ColorWheel(self.wheel_diameter, self.wheel_thickness)
		#self.wheel.rotation = random.uniform(0, 360)
		self.probe_color = random.choice(self.color_list)
		self.probe = self.probe_surface()
		self.baserun_offset = self.baserun_constant + random.choice(self.baserun_offsets)

		if self.probe_frame_count == 1:
			self.probe_frames.append(self.contact_frame)
		else:
			probe_start_frame = self.contact_frame - (self.probe_frame_count // 2)
			self.probe_frames = range(probe_start_frame, probe_start_frame + self.probe_frame_count)

		clear()
		
		msg = message("Press spacebar to begin trial.", "large", blit_txt=False)
		fill()
		blit(msg, registration=5, location=P.screen_c)
		#flip()
		#any_key()
		self.listen(MAX_WAIT, "trial_start")

	def trial(self):
		self.since_last_trial = time.time()
		self.play_video(self.soa, self.probe_targets, self.condition, self.probe_location)

		if self.probe_targets == TOJ:
			self.get_toj_response()
			self.probe_color = NA
		else:
			self.get_color_response()

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"soa": self.soa,
			"baserun_offset": self.baserun_offset * 15,	 # number of extra frames runner is shown for at video start
			"first_arrival": self.condition,
			"probed_trial": "true" if self.probe_targets != TOJ else "false",
			"glove_probe_dist": self.probe_distribution[GLOVE],
			"base_probe_dist": self.probe_distribution[BASE],
			"probe_location": self.probe_location_name,
			"probe_color": str(self.probe_color)[0:-6] + ")" if self.probe_color != NA else NA,
			"color_response": str(self.color_response)[0:-6] + ")" if self.color_response != NA else NA,
			"color_diff": self.color_diff,
			"toj_response": self.toj_response,
			"response_time": str(self.response_time)[0:4]
		}

	def trial_clean_up(self):
		self.baserun_offset = None
		self.color_diff = NA
		self.color_response = NA
		self.response_time = NA
		self.rt_start = None
		self.ball_x = copy(self.ball_initial_x)
		self.ball_y = copy(self.ball_initial_y)
		self.toj_response = NA

	def clean_up(self):
		pass
#		self.db.init_entry("surveys", set_current=True)
# 
#		tie_run_familiar_query = "Are you familiar with the baseball convention that states 'a tie goes to the runner'?"
#		tie_run_use_query = "Did you use this convention in make 'safe' or 'out' judgements during this experiment?"
# 
#		tie_run_familiar_resp = self.query(tie_run_familiar_query, accepted=["y", "n"])
#		self.db.log('tie_run_familiar', tie_run_familiar_resp)
# 
#		if tie_run_familiar_resp == "y":
#			self.db.log('tie_run_used', self.query(tie_run_use_query, accepted=["y", "n"]))
#		else:
#			self.db.log('tie_run_used', NA)
#		self.db.log(P.id_field_name, self.participant_id)
#		self.db.insert()
#		return True

	def play_video(self, soa, first_arrival, probe_condition, probe_location):
		fill()
		flip()
		scene_start_frame = self.contact_frame - self.baserun_offset
		soa_in_frames = int(soa) // 15

		if first_arrival == BALL:
			ball_last_frame = self.contact_frame - soa_in_frames
			scene_last_frame = self.contact_frame + self.post_arrival_buffer_frames
		else:
			ball_last_frame = self.contact_frame + soa_in_frames
			scene_last_frame = ball_last_frame + self.post_arrival_buffer_frames
		ball_first_frame = ball_last_frame - len(self.ball_frames) + 1
		rt_start_frame = self.contact_frame if first_arrival == RUNNER else ball_last_frame
		ball_frames_shown = 0

		self.probe_location = NA if probe_condition == TOJ else self.probe_locations[probe_location]

		if self.probe_location != NA:
			if self.probe_location == self.probe_locations[BASE]:
				self.probe_location_name = BASE
			else:
				self.probe_location_name = GLOVE
		else:
			self.probe_location_name = NA

		for frame in range(scene_start_frame, scene_last_frame):
			ui_request()
			sdl2.mouse.SDL_ShowCursor(sdl2.SDL_DISABLE)
			fill()
			blit(self.scene_frames[frame], 5, P.screen_c)

			if ball_last_frame >= frame >= ball_first_frame:
				self.ball_x += self.ball_speed
				ball_frame = copy(self.ball_frames[ball_frames_shown])
				if self.ball_x < self.ball_vanish_line:
					# 36px = constant offset to lineup glove mask with glove in scene
					mask_offset = [0, -15]	# y is constant, just aligns center of glove to center of ball
					mask_offset[0] = (self.ball_vanish_line - self.ball_x) - 50
					ball_frame.mask(self.glove_mask, mask_offset)
				blit(ball_frame, position=(self.ball_x, self.ball_y))
				ball_frames_shown += 1

			if frame in self.probe_frames and probe_condition != TOJ:
				blit(self.probe, 7, self.probe_location)

			if frame == rt_start_frame:
				self.rt_start = time.time()
				
			flip()

	def get_toj_response(self):
		fill()
		message("Safe or out?", "large", location=P.screen_c, registration=5)
		#flip()
		self.toj_response = self.listen(MAX_WAIT, "toj")[0]	 # returns tuple of (response, rt), only need response
		self.response_time = time.time() - self.rt_start

	def get_color_response(self):
		clear()
		# sdl2.mouse.SDL_WarpMouseGlobal(P.screen_c[0], P.screen_c[1])
		sdl2.mouse.SDL_ShowCursor(sdl2.SDL_ENABLE)
		sdl2.SDL_PumpEvents()
		start = time.time()
		fill()
		message(self.strings['choose_color'], registration=5, location=P.screen_c)
		blit(self.wheel, 5, P.screen_c)
		flip()
		while self.color_response == NA:
			for event in sdl2.ext.get_events():
				if event.type == sdl2.SDL_MOUSEBUTTONUP:
					pos = [event.button.x, event.button.y]
					pos[0] -= int((P.screen_x - self.wheel.width) / 2)
					pos[1] -= int((P.screen_y - self.wheel.height) / 2)
					clicked_px_color = self.wheel.get_pixel_value(pos)
					if type(clicked_px_color) is not bool:
						clicked_px_color = clicked_px_color.tolist()
						color_choice = (clicked_px_color[0], clicked_px_color[1], clicked_px_color[2], 255)
						if color_choice in self.color_list:
							self.color_response = str(color_choice)
							probe_index = self.color_list.index(self.probe_color)
							click_index = self.color_list.index(color_choice)
							self.color_diff = probe_index - click_index
		sdl2.mouse.SDL_ShowCursor(sdl2.SDL_DISABLE)

	def probe_surface(self):
		probe = aggdraw.Draw('RGBA', self.probe_dimensions, (0, 0, 0, 0))
		probe_brush = aggdraw.Brush(self.probe_color)
		probe.ellipse((0, 0, self.probe_dimensions[0], self.probe_dimensions[1]), probe_brush)
		probe = Image.frombytes(probe.mode, probe.size, probe.tobytes())
		return NumpySurface(np.asarray(probe))

	def wheel_surface(self, wheel_rotation):
		wheel = aggdraw.Draw('RGBA', self.wheel_dimensions, (0, 0, 0, 0))

		for i in range(360):
			brush = aggdraw.Brush(self.color_list[i])
			wheel.polygon((int(round(self.wheel_rad)), int(round(self.wheel_rad)),
				int(round(self.wheel_rad + math.sin((wheel_rotation - .25) * PI / 180) * self.wheel_rad)),
				int(round(self.wheel_rad + math.cos((wheel_rotation - .25) * PI / 180) * self.wheel_rad)),
				int(round(self.wheel_rad + math.sin((wheel_rotation + 1.25) * PI / 180) * self.wheel_rad)),
				int(round(self.wheel_rad + math.cos((wheel_rotation + 1.25) * PI / 180) * self.wheel_rad))),
				brush)
			wheel_rotation += 1
			if wheel_rotation > 360:
				wheel_rotation -= 360
		black_brush = aggdraw.Brush((0, 0, 0, 255))
		black_pen = aggdraw.Pen((0, 0, 0, 255))
		wheel.ellipse((self.wheel_thickness, self.wheel_thickness, self.wheel_diam - self.wheel_thickness,
						self.wheel_diam - self.wheel_thickness),
						black_brush)
		wheel.ellipse((self.wheel_thickness, self.wheel_thickness, self.wheel_diam - self.wheel_thickness,
						self.wheel_diam - self.wheel_thickness),
						black_pen)

		wheel = Image.frombytes(wheel.mode, wheel.size, wheel.tobytes())
		# print numpy.asarray(wheel.tostring())
		return NumpySurface(np.asarray(wheel))
		
	def listen(self, max_wait=MAX_WAIT, key_map_name="*", null_response=None):

			key_map = P.key_maps[key_map_name]
			response = None
			rt = -1

			start_time = time.time()
			waiting = True

			# enter with a clean event queue
			sdl2.SDL_PumpEvents()
			sdl2.SDL_FlushEvents(sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)
			flip()

			key = None
			sdl_keysym = None
			key_name = None
			while waiting:
				sdl2.SDL_PumpEvents()
				for event in sdl2.ext.get_events():
					if event.type == sdl2.SDL_KEYDOWN:
						rt = time.time() - start_time
						if not response:
							key = event.key
							sdl_keysym = key.keysym.sym
							ui_request(sdl_keysym)
							key_name = sdl2.keyboard.SDL_GetKeyName(sdl_keysym)
							if key_map is not None:
								valid = key_map.validate(sdl_keysym)
								if valid:
									response = key_map.read(sdl_keysym, "data")
									return [response, rt]


				if (time.time() - start_time) > max_wait:
					waiting = False
					return [TIMEOUT, -1]
			if not response:
				if null_response:
					return [null_response, rt]
				else:
					return [NO_RESPONSE, rt]
			else:
				return [response, rt]