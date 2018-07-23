__author__ = "Jon Mulle"

# Import required KLibs classes and functions

import klibs
from klibs.KLConstants import RC_COLORSELECT, RC_KEYPRESS
from klibs import P
from klibs.KLUtilities import *
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLGraphics import fill, blit, flip, clear
from klibs.KLGraphics.KLNumpySurface import NumpySurface
import klibs.KLGraphics.KLDraw as kld
from klibs.KLCommunication import message, user_queries

# Import additional required libraries

import os
import time
import math
import random
from copy import copy
import numpy as np
import imageio

# Define colours for the experiment

WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 255]
LIGHT_BLUE = [20, 180, 220, 255]

# Define some constants to avoid retyping strings throughout

NA = "NA"
TOJ = "TOJ"
BASE = "base"
GLOVE = "glove"
BALL = "ball"
RUNNER = "runner"


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
	self.evm (EventManager, which can also be used for timing events)
	self.rc (a ResponseCollector object for collecting responses)
	"""

	ball_speed = -30  # px per frame
	#contact_frame = 936

	def setup(self):
		
		# Stimulus Sizes
		
		wheel_diam = deg_to_px(10.8)
		probe_size = 20 #deg_to_px(0.45)
		
		# Stimulus Drawbjects
		
		self.wheel = kld.ColorWheel(wheel_diam, thickness=wheel_diam//8)
		self.wheel_disc = kld.Ellipse(int(wheel_diam*0.75), fill=BLACK) # to mimic old-style wheel
		self.probe = kld.Ellipse(probe_size, fill=WHITE)
		
		# Layout
		
		x_offset = P.screen_c[0] - (1024 // 2)
		y_offset = P.screen_c[1] - (768 // 2)
		
		self.probe_positions = {}
		self.probe_positions[BASE] = [320 + x_offset, 560 + y_offset]
		self.probe_positions[GLOVE] = [560 + x_offset, 245 + y_offset]
		
		self.ball_initial_x = 1024 + 20 + x_offset # 20 = width of ball image
		self.ball_initial_y = 259 + y_offset
		self.ball_vanish_line = 575 + x_offset
		
		# Timing
		
		scene_frames_cut = 300
		contact_frame_pre_cut = 467
		first_frame = scene_frames_cut*2
		self.post_arrival_buffer_frames = 19
		self.contact_frame = contact_frame_pre_cut - scene_frames_cut
		
		probe_framecount = 20 # 333.33ms at 60Hz (16.667ms * 20 = 333.33ms)
		probe_start_frame = self.contact_frame - (probe_framecount // 2) # 166.66ms offset
		self.probe_frames = range(probe_start_frame, probe_start_frame + probe_framecount+1)
		
		# Experiment Messages
		
		self.txtm.add_style("large", 36)
		self.txtm.add_style("loc", 36, color=LIGHT_BLUE)
		
		self.strings = {
			"choose_color": "Click the colour which best matches the flash from the video.",
			"timeout": "Too slow! Try to respond faster."
		}
		
		self.toj_prompt = message("Safe or out?", "large", blit_txt=False)
		self.color_prompt = message(self.strings['choose_color'], blit_txt=False)
		
		# Load in and prerender frames from baseball video
		
		scene_mov_path = os.path.join(P.image_dir, 'baseball.mp4')
		ball_frames_path = os.path.join(P.image_dir, 'rendered_ball_blur')
		
		fill()
		blit(message("Loading...", blit_txt=False), 5, P.screen_c)
		flip()
		
		clip = imageio.get_reader(scene_mov_path, 'ffmpeg') # load in baseball clip 
		framecount = clip.get_length()
		
		self.scene_frames = []
		for index in range(first_frame, framecount, 2):
			# Read in frame and append opacity layer to it (OpenGL requires RGBA arrays)
			frame = self.frame_to_rgba(clip.get_data(index))
			self.scene_frames.append(frame)
			# Show loading percentage and process user input while rendering frames
			frames = 1.0 * (framecount - first_frame)
			percent = int(((index-first_frame) / frames) * 100)
			msg_str = "Loading... ({0}%)"
			funny_mode = True
			if funny_mode:
				if percent < 25:
					msg_str = "Loading science... ({0}%)"
				elif percent < 50:
					msg_str = "Smashing atoms ... ({0}%)"
				elif percent < 75:
					msg_str = "Generating quandries ... ({0}%)"
				else:
					msg_str = "Reinventing wheels... ({0}%)"
			ui_request()
			fill()
			blit(message(msg_str.format(percent), blit_txt=False), 5, P.screen_c)
			flip()
		
		# Load in and render frames of baseball and glove mask
		
		self.ball_frames = []
		for x in range(1, 25):
			x = str(x).zfill(2)
			path = os.path.join(ball_frames_path, "{0}.png".format(x))
			surface = NumpySurface(path)
			surface.render()
			self.ball_frames.append(surface)
		movement_per_frame = (self.ball_initial_x - self.ball_vanish_line) / float(self.ball_speed)
		self.ball_frame_count = int(math.ceil(abs(movement_per_frame)))
		# extend list of ball frames to be long enough for entire animation
		if self.ball_frame_count > len(self.ball_frames):
			diff = self.ball_frame_count - len(self.ball_frames)
			self.ball_frames.append(self.ball_frames[0: diff])
		elif self.ball_frame_count < len(self.ball_frames):
			self.ball_frames = self.ball_frames[0: self.ball_frame_count]
			
		self.glove_mask = NumpySurface(os.path.join(P.image_dir, "glove_mask.png"))


	def block(self):

		# Determine probe bias for block and generate list of probe locs accordingly
		
		if P.block_number % 2 == 1: # alternate bias location every block
			self.probe_bias = P.first_bias
			nonbiased_loc = GLOVE if P.first_bias == BASE else BASE
		else:
			self.probe_bias = GLOVE if P.first_bias == BASE else BASE
			nonbiased_loc = P.first_bias
		loc_list = [self.probe_bias]*4 + [nonbiased_loc]
		probe_trials_per_block = P.trials_per_block//3 # probes are only on 1/3 of trials
		self.probe_locs = loc_list * int(probe_trials_per_block/float(len(loc_list))+1)
		random.shuffle(self.probe_locs)
		
		# Show block start message indicating probe bias for the block

		blocks_remaining_str = "Block {0} of {1}".format(P.block_number, P.blocks_per_experiment)
		distribution_msg1 = (
			"During the next block of trials,\nthe colour dot will appear more frequently at the"
			"\n\nand less frequently at the\n"
		)
		distribution_msg2 = ("\n\n{0}".format(self.probe_bias) + "\n\n{0}".format(nonbiased_loc))
		fill()
		message(blocks_remaining_str, location=[P.screen_c[0], 50], registration=5)
		message(distribution_msg1, "large", registration=5, location=P.screen_c, align="center")
		message(distribution_msg2, "loc", registration=5, location=P.screen_c, align="center")
		message("Press any key to start.", registration=5, location=[P.screen_c[0], P.screen_y*0.8])
		flip()
		flush()
		any_key()
		

	def setup_response_collector(self):
		
		self.probe_trial = self.trial_type == "probe"

		# Set up Response Collector to get keypress responses

		if self.probe_trial:
			self.rc.uses(RC_COLORSELECT)
			self.rc.terminate_after = [10, TK_S]
			self.rc.display_callback = self.wheel_callback
			self.rc.color_listener.interrupts = True
			self.rc.color_listener.color_response = True
			self.rc.color_listener.set_wheel(self.wheel)
			self.rc.color_listener.set_target(self.probe)
		else:
			self.rc.uses(RC_KEYPRESS)
			self.rc.terminate_after = [10, TK_S]
			self.rc.display_callback = None
			self.rc.keypress_listener.key_map = {'s': 'safe', 'o': 'out'}
			self.rc.keypress_listener.interrupts = True
			

	def trial_prep(self):
		
		# Set up colour probe and colour wheel
		
		self.wheel.rotation = random.randrange(0, 360, 1)
		self.wheel.render()
		self.probe.fill = self.wheel.color_from_angle(random.randrange(0, 360, 1))
		self.probe.render()
		
		# Determine the probe location for the trial
		
		if self.probe_trial:
			self.probe_location = self.probe_locs.pop()
			self.probe_pos = self.probe_positions[self.probe_location]
		else:
			self.probe_location = NA
			self.probe_pos = None
		
		# Reset the ball start position
		
		self.ball_x = self.ball_initial_x
		self.ball_y = self.ball_initial_y
		
		# Generate offset of frames between runner contact with base and clip start
		
		self.runner_offset = 92 + random.randrange(1, 30, 1)
		
		# Show trial start message and wait for keypress
		if P.trial_number > 1:
			msg = message("Press spacebar to begin trial.", "large", blit_txt=False)
			fill()
			blit(msg, registration=5, location=P.screen_c)
			flip()
			any_key()
		

	def trial(self):
		
		# Play video clip with order and offset of ball arrival in glove and runner arrival at base
		# varying between trials based on self.soa_frames and self.first_arrival values

		self.play_video()
		
		# Once video has finished, collect either TOJ (safe/out) or colour wheel response

		if self.probe_trial:
			self.rc.collect()
		else:
			self.toj_callback()
			self.rc.collect()
			
		# Parse collected response data before writing to the database
		
		if not self.probe_trial:
			toj_response = self.rc.keypress_listener.response(rt=False)
			toj_rt = self.rc.keypress_listener.response(value=False)
			if toj_response == 'NO_RESPONSE':
				toj_response, toj_rt = ['NA', 'timeout']

			response_col, angle_err, wheel_rt = ['NA', 'NA', 'NA']
		else:
			try:
				angle_err, response_col = self.rc.color_listener.response(rt=False)
				wheel_rt = self.rc.color_listener.response(value=False)
			except ValueError:
				# if no response made (timeout), only one value will be returned
				angle_err, response_col, wheel_rt = ['NA', 'NA', 'timeout']
			toj_response, toj_rt = ['NA', 'NA']

		return {
			"block_num": P.block_number,
			"trial_num": P.trial_number,
			"soa": self.soa_frames * P.refresh_time,
			"baserun_offset": self.runner_offset * 15, # extra frames runner shown for at start
			"first_arrival": self.first_arrival,
			"probed_trial": str(self.probe_trial).upper(),
			"glove_probe_dist": 0.8 if self.probe_bias == GLOVE else 0.2,
			"base_probe_dist": 0.8 if self.probe_bias == BASE else 0.2,
			"probe_location": self.probe_location,
			"probe_color": str(self.probe.fill_color) if self.probe_trial else 'NA',
			"color_response": str(list(response_col[:3])) if self.probe_trial else 'NA',
			"color_diff": angle_err,
			"color_rt": wheel_rt,
			"toj_response": toj_response,
			"response_time": toj_rt
		}


	def trial_clean_up(self):
		pass
		

	def clean_up(self):
		
		# At end of experiment, ask particiapants whether they know the 'tie goes to the runner'
		# convention in baseball, and if so whether they used it when making safe/out judgements
		
		tie_run_familiar = user_queries.experimental[0]
		if tie_run_familiar == "y":
			tie_run_used = user_queries.experimental[1]
		else:
			tie_run_used = 'NA'

		tie_run_survey = {
			'participant_id': P.participant_id,
			'tie_run_familiar': tie_run_familiar,
			'tie_run_used': tie_run_used
		}
		self.db.insert(tie_run_survey, table='surveys')


	def play_video(self):

		scene_start_frame = self.contact_frame - self.runner_offset

		if self.first_arrival == BALL:
			ball_last_frame = self.contact_frame - self.soa_frames
			scene_last_frame = self.contact_frame + self.post_arrival_buffer_frames
			rt_start_frame = ball_last_frame
		else:
			ball_last_frame = self.contact_frame + self.soa_frames
			scene_last_frame = ball_last_frame + self.post_arrival_buffer_frames
			rt_start_frame = self.contact_frame
		ball_first_frame = ball_last_frame - len(self.ball_frames) + 1
			
		hide_mouse_cursor()
		for frame in range(scene_start_frame, scene_last_frame):
			ui_request()
			fill()
			blit(self.scene_frames[frame], 5, P.screen_c)

			if ball_last_frame >= frame >= ball_first_frame:
				self.ball_x += self.ball_speed
				ball_frame = copy(self.ball_frames[frame-ball_first_frame])
				if self.ball_x < self.ball_vanish_line:
					# apply transparency mask to ball so it disappears into glove
					mask_offset = [(self.ball_vanish_line - self.ball_x) - 50, -15]
					ball_frame.mask(self.glove_mask, mask_offset)
				blit(ball_frame, location=(self.ball_x, self.ball_y))

			if frame in self.probe_frames and self.probe_trial:
				blit(self.probe, 7, self.probe_pos)

			if frame == rt_start_frame:
				self.rt_start = time.time()
				
			flip()
			
	def frame_to_rgba(self, frame, opacity=255):
		frame_opacity = np.full((frame.shape[0], frame.shape[1], 1), opacity, dtype=np.uint8)
		return np.dstack((frame, frame_opacity))
		
	def toj_callback(self):
		fill()
		blit(self.toj_prompt, 5, P.screen_c)
		flip()

	def wheel_callback(self):
		fill()
		blit(self.color_prompt, location=(25, 25), registration=7)
		blit(self.wheel, location=P.screen_c, registration=5)
		blit(self.wheel_disc, location=P.screen_c, registration=5)
		flip()
