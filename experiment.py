__author__ = 'jono'
import klibs
from klibs import Params
import os
import time
from PIL import Image
import sdl2
import sdl2.ext
import numpy
import math
import aggdraw
import random
from copy import copy

PI = math.pi
Params.screen_x = 2560
Params.screen_y = 1440

NA = "NA"
TOJ = "toj"
BASE = "base"
GLOVE = "glove"
BALL = "ball"
RUNNER = "runner"
GLOVE_LIKELY = "glove_likely"
BALL_LIKELY = "ball_likely"
key_maps = {}

Params.collect_demographics = False
Params.practicing = False
Params.eye_tracking = False
Params.instructions = False
Params.blocks_per_experiment = 4
Params.trials_per_block = 120
Params.practice_blocks = 0
Params.trials_per_practice_block = 0
Params.exp_meta_factors = {"probe_target_distribution": [{BASE: 0.8, GLOVE: 0.2}, {BASE: 0.2, GLOVE: 0.8}]}

Params.exp_factors = {
						"SOA": [15, 15, 15, 45, 45, 90, 90, 135, 135, 240],
						"probe_targets": [BASE, GLOVE, TOJ, TOJ, TOJ, TOJ],
						"condition": [RUNNER, BALL]
}


class RSVP(klibs.App):
	scene_frames_cut = 300
	scene_path = None
	ball_frames_path = None
	scene_frames = []
	ball_frames = []
	glove_mask = None

	ball_frame_count = None  # used in set-up to compute number of ball surfaces needed
	ball_vanish_line = 575  # ditto
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
	probe_dimensions = (20, 20)  # px
	probe_distribution = None

	response_timeout = 2  # seconds
	color_diff = NA
	color_response = NA
	toj_response = NA
	response_time = NA
	rt_start = None

	last_likely_probe = None

	def __init__(self, *args, **kwargs):
		klibs.App.__init__(self, *args, **kwargs)

	def setup(self):
		self.since_last_trial = 0
		if Params.screen_x > 1024:
			x_offset = (Params.screen_x - 1024) // 2
			self.probe_locations[BASE][0] += x_offset
			self.probe_locations[GLOVE][0] += x_offset
			self.ball_vanish_line += x_offset
		if Params.screen_y > 768:
			y_offset = int((Params.screen_y - 768) // 2)
			self.probe_locations[BASE][1] += y_offset
			self.probe_locations[GLOVE][1] += y_offset

		self.scene_path = os.path.join(Params.asset_path, 'JPG')
		self.ball_frames_path = os.path.join(Params.asset_path, 'rendered_ball_blur')
		self.color_list = eval(open(os.path.join(Params.asset_path, "color_list.txt")).read())
		self.wheel_diam = 8 * Params.ppd
		self.wheel_dimensions = (self.wheel_diam, self.wheel_diam)
		self.wheel_rad = self.wheel_diam / 2
		self.wheel_bounds = []
		self.wheel_thickness = 0.1 * self.wheel_diam
		self.wheel_stroke = 0.01 * self.wheel_diam
		self.post_arrival_buffer_frames = 19
		self.ball_x = copy(self.ball_initial_x)
		self.ball_y = copy(self.ball_initial_y)
		self.glove_mask = klibs.NumpySurface(os.path.join(Params.asset_path, "glove_mask.png"))
		self.contact_frame = self.contact_frame_pre_cut - self.scene_frames_cut
		Params.key_maps["toj"] = klibs.KeyMap("toj", ["s", "o"], [sdl2.SDLK_s, sdl2.SDLK_o], ["safe", "out"])
		Params.key_maps["trial_start"] = klibs.KeyMap("trial_start", ["spacebar"], [sdl2.SDLK_SPACE], ["spacebar"])
		Params.key_maps["block_start"] = klibs.KeyMap("block_start", ["j"], [sdl2.SDLK_j], ["j"])

		for x in range(1, 522 - self.scene_frames_cut):
			sdl2.SDL_PumpEvents()
			self.fill()
			frames = 1.0 * (522 - self.scene_frames_cut)
			percent = int((x / frames) * 100)
			msg_str = "Loading... ({0}%)"
			funny_mode = False
			if funny_mode:
				if percent < 25:
					msg_str = "Loading science... ({0}%)"
				elif percent < 50:
					msg_str = "Smashing atoms ... ({0}%)"
				elif percent < 75:
					msg_str = "Generating quandries ... ({0}%)"
				elif percent < 90:
					msg_str = "Reinventing wheels... ({0}%)"
			self.message(msg_str.format(percent), bg_color="(255,255,255)", location="center",
						registration=5, flip=True)
			x = str(int(x * 2) + (2 * self.scene_frames_cut)).zfill(8)
			path = os.path.join(self.scene_path, "{0}.jpg".format(x))
			surface = self.numpy_surface(path)
			surface.prerender()
			self.scene_frames.append(surface)

		for x in range(1, 25):
			x = str(x).zfill(2)
			path = os.path.join(self.ball_frames_path, "{0}.png".format(x))
			surface = self.numpy_surface(path)
			surface.prerender()
			self.ball_frames.append(surface)

		self.ball_frame_count = int(abs(math.ceil((self.ball_initial_x - self.ball_vanish_line) / self.ball_speed)))

		#  extend list of ball frames surfaces to be long enough for entire animation (ie. repeat from frame 0)
		if self.ball_frame_count > len(self.ball_frames):
			diff = self.ball_frame_count - len(self.ball_frames)
			self.ball_frames.append(self.ball_frames[0: diff])
		elif self.ball_frame_count < len(self.ball_frames):
			self.ball_frames = self.ball_frames[0: self.ball_frame_count]

		if Params.collect_demographics:
			self.collect_demographics()

		if Params.instructions:
			self.instructions()

		if Params.eye_tracking:
			self.el.trackerInit()
			self.el.setup()
			Params.practicing = False

	def block(self, block_num):
		if self.last_likely_probe is None:
			self.last_likely_probe = BASE if Params.version == GLOVE_LIKELY else GLOVE

		if self.last_likely_probe == GLOVE_LIKELY:
			self.probe_distribution = Params.exp_meta_factors['probe_target_distribution'][0]
			likely_location = BASE
			unlikely_location = GLOVE
		else:
			self.probe_distribution = Params.exp_meta_factors['probe_target_distribution'][1]
			likely_location = GLOVE
			unlikely_location = BASE

		probe_target_cond_count = len(Params.exp_factors["probe_targets"])
		toj_cond_count = Params.exp_factors["probe_targets"].count(TOJ)
		probe_cond_count = probe_target_cond_count - toj_cond_count
		probe_trial_ratio = probe_target_cond_count // probe_cond_count
		glove_trials = int((Params.trials_per_block // probe_trial_ratio) * self.probe_distribution[GLOVE]) * [GLOVE]
		base_trials = int((Params.trials_per_block // probe_trial_ratio) * self.probe_distribution[BASE]) * [BASE]
		self.probe_trials = glove_trials + base_trials
		random.shuffle(self.probe_trials)
		for i in range(0, len(self.probe_trials)):
			self.probe_trials[i] = self.probe_locations[self.probe_trials[i]]

		self.clear()
		blocks_remaining_str = "Block {0} of {1}".format(block_num, Params.blocks)
		self.message(blocks_remaining_str, location=[Params.screen_c[0], 50], registration=5)
		locations = [(Params.screen_c[0], (Params.screen_c[1] // 1.1) - 50),
					(Params.screen_c[0], (Params.screen_c[1] // 1.1)),
					(Params.screen_c[0], (Params.screen_c[1] // 0.9) - 50),
					(Params.screen_c[0], (Params.screen_c[1] // 0.9))]
		distribution_strings = ["During the next block of trials, the colored disk will appear more frequently at the:",
								"and less likely at the:"]
		self.message(distribution_strings[0], location=locations[0], registration=5)
		self.message(unlikely_location, font_size=48, color=(20, 180, 220, 255), location=locations[1], registration=5)
		self.message(distribution_strings[1], location=locations[2], registration=5)
		self.message(likely_location, font_size=48, color=(20, 180, 220, 255), location=locations[3], registration=5)
		self.message("Press j to start.", location=[Params.screen_c[0], Params.screen_y * 0.8], registration=5)
		self.listen(klibs.MAX_WAIT, 'block_start')

	def flip_callback(self):
		return True

	def trial_prep(self, *args, **kwargs):
		random.shuffle(self.probe_trials)
		self.wheel = self.wheel_surface(random.uniform(0, 360))
		self.probe_color = random.choice(self.color_list)
		self.probe = self.probe_surface()
		self.baserun_offset = self.baserun_constant + random.choice(self.baserun_offsets)

		if self.probe_frame_count == 1:
			self.probe_frames.append(self.contact_frame)
		else:
			probe_start_frame = self.contact_frame - (self.probe_frame_count // 2)
			self.probe_frames = range(probe_start_frame, probe_start_frame + self.probe_frame_count)

		if Params.eye_tracking:
			self.fill()
			self.blit(Params.drift_target, 5, Params.screen_c)
			self.flip()
			self.el.el.doDriftCorrect(Params.screen_c[0], Params.screen_c[1], 0, 1)
			self.el.el.acceptTrigger()
		else:
			self.db.init_entry('trials')
			self.clear()
			self.message("Press spacebar to begin trial.", location="center", font_size=48)
			self.listen(klibs.MAX_WAIT, "block_start")

	def trial(self, trial_factors, trial_num):
		print time.time() - self.since_last_trial
		self.since_last_trial = time.time()
		if trial_factors[2] != TOJ:  # ie. if this is a probe trial because a location is specified
			self.probe_trial_count += 1

		self.play_video(trial_factors[1], trial_factors[3], trial_factors[2])

		if trial_factors[2] == TOJ:
			self.get_toj_response()
			self.probe_color = NA
		else:
			self.get_color_response()

		return {
			"block_num": self.block_number,
			"trial_num": self.trial_number,
			"soa": trial_factors[1],
			"baserun_offset": self.baserun_offset * 15,  # number of extra frames runner is shown for at video start
			"first_arrival": trial_factors[3],
			"probed_trial": "true" if trial_factors[2] != TOJ else "false",
			"glove_probe_dist": self.probe_distribution[GLOVE],
			"base_probe_dist": self.probe_distribution[BASE],
			"probe_location": self.probe_location,
			"probe_color": str(self.probe_color)[0:-6] + ")" if self.probe_color != NA else NA,
			"color_response": str(self.color_response)[0:-6] + ")" if self.color_response != NA else NA,
			"color_diff": self.color_diff,
			"toj_response": self.toj_response,
			"response_time": str(self.response_time)[0:4]
		}

	def trial_clean_up(self, *args, **kwargs):
		self.baserun_offset = None
		self.color_diff = NA
		self.color_response = NA
		self.response_time = NA
		self.rt_start = None
		self.ball_x = copy(self.ball_initial_x)
		self.ball_y = copy(self.ball_initial_y)
		self.toj_response = NA

	def clean_up(self):
		self.db.init_entry("surveys", set_current=True)

		tie_run_familiar_query = "Are you familiar with the baseball convention that states 'a tie goes to the runner'?"
		tie_run_use_query = "Did you use this convention in make 'safe' or 'out' judgements during this experiment?"

		tie_run_familiar_resp = self.query(tie_run_familiar_query, accepted=["y", "n"])
		self.db.log('tie_run_familiar', tie_run_familiar_resp)

		if tie_run_familiar_resp == "y":
			self.db.log('tie_run_used', self.query(tie_run_use_query, accepted=["y", "n"]))
		else:
			self.db.log('tie_run_used', NA)
		self.db.log(Params.id_field_name, self.participant_id)
		self.db.insert()
		return True

	def play_video(self, soa, first_arrival, probe_condition):
		self.fill()
		self.flip()
		scene_start_frame = self.contact_frame - self.baserun_offset
		soa_in_frames = int(soa / 15)
		ball_first_frame = None
		scene_last_frame = None
		if first_arrival == BALL:
			ball_last_frame = self.contact_frame - soa_in_frames
			scene_last_frame = self.contact_frame + self.post_arrival_buffer_frames
		else:
			ball_last_frame = self.contact_frame + soa_in_frames
			scene_last_frame = ball_last_frame + self.post_arrival_buffer_frames
		ball_first_frame = ball_last_frame - len(self.ball_frames) + 1
		rt_start_frame = self.contact_frame if first_arrival == RUNNER else ball_last_frame
		ball_frames_shown = 0

		self.probe_location = NA if probe_condition == TOJ else self.probe_trials.pop()
		for frame in range(scene_start_frame, scene_last_frame):
			sdl2.SDL_PumpEvents()
			sdl2.mouse.SDL_ShowCursor(sdl2.SDL_DISABLE)
			self.fill()
			self.blit(self.scene_frames[frame], 5, 'center')

			if frame >= ball_first_frame and frame <= ball_last_frame:
				self.ball_x += self.ball_speed
				ball_frame = copy(self.ball_frames[ball_frames_shown])
				if self.ball_x < self.ball_vanish_line:
					# 36px = constant offset to lineup glove mask with glove in scene
					mask_offset = [0, -15]  # y is constant, just aligns center of glove to center of ball
					mask_offset[0] = (self.ball_vanish_line - self.ball_x) - 50
					ball_frame.mask(self.glove_mask, mask_offset)
				self.blit(ball_frame, position=(self.ball_x, self.ball_y))
				ball_frames_shown += 1

			if frame in self.probe_frames and probe_condition != TOJ:
				self.blit(self.probe, 7, self.probe_location)

			if frame == rt_start_frame:
				self.rt_start = time.time()

			self.flip()

	def get_toj_response(self):
		self.clear()
		self.message("Safe or out?", font_size="48pt", location="center", registration=5)
		self.toj_response = self.listen(klibs.MAX_WAIT, "toj")[0]  # returns tuple of (response, rt), only need response
		self.response_time = time.time() - self.rt_start

	def get_color_response(self):
		self.clear()
		sdl2.mouse.SDL_WarpMouseGlobal(Params.screen_c[0], Params.screen_c[1])
		sdl2.mouse.SDL_ShowCursor(sdl2.SDL_ENABLE)
		sdl2.SDL_PumpEvents()
		start = time.time()
		self.message(self.strings['choose_color'])
		self.blit(self.wheel, 5, 'center')
		self.flip()
		while self.color_response == NA:
			for event in sdl2.ext.get_events():
				if event.type == sdl2.SDL_MOUSEBUTTONUP:
					pos = [event.button.x, event.button.y]
					pos[0] -= int((Params.screen_x - self.wheel.width) / 2)
					pos[1] -= int((Params.screen_y - self.wheel.height) / 2)
					clicked_px_color = self.wheel.get_pixel_value(pos).tolist()
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
		probe = Image.frombytes(probe.mode, probe.size, probe.tostring())
		return klibs.NumpySurface(numpy.asarray(probe))

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

		wheel = Image.frombytes(wheel.mode, wheel.size, wheel.tostring())
		# print numpy.asarray(wheel.tostring())
		return klibs.NumpySurface(numpy.asarray(wheel))

Params.version = GLOVE_LIKELY
#Params.version = BALL_LIKELY
app = RSVP('baseball_TOJ').run()
