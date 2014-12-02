########
#Important constants
########

# -----viewing_distance & screen_width in cm's, on April 5/12
viewing_distance = 56.0 #units can be anything so long as they match those used in screen_width below
screen_width = 36.0 #units can be anything so long as they match those used in viewing_distance above
screen_size = [1024,768] #desired screen resolution. Use your system display tools to find a good compromise between screen resolution and refresh rate.
screen_hz = 100.0 #specify refresh rate (include the decimal-zero to ensure it is encoded as a float)

do_eyelink = False
critical_em_size_in_degrees = 1

fixation_duration = 1.000 #specify the fixation interval in seconds
cue_duration = 0.050
target_duration = 0.100
post_duration = 1.000

color_angle_list = [0,12,24,36,48,60,72,84,96,108,120,132,144,156,168,180,192,204,216,228,240,252,264,276,288,300,312,324,336,348]
color_list = [(211,63,106,255),(210,64,104,255),(210,65,101,255),(209,66,99,255),(209,67,96,255),(208,68,94,255),(208,69,91,255),(207,70,89,255),(207,71,86,255),(206,72,84,255),(206,73,81,255),(205,74,78,255),(205,75,75,255),(204,75,72,255),(203,76,69,255),(203,77,66,255),(202,78,63,255),(202,79,59,255),(201,80,56,255),(200,81,52,255),(200,82,48,255),(199,82,43,255),(198,83,39,255),(198,84,33,255),(197,85,27,255),(196,86,19,255),(195,87,7,255),(195,87,0,255),(194,88,0,255),(193,89,0,255),(192,90,0,255),(191,91,0,255),(191,91,0,255),(190,92,0,255),(189,93,0,255),(188,94,0,255),(187,95,0,255),(186,95,0,255),(185,96,0,255),(184,97,0,255),(183,98,0,255),(183,98,0,255),(182,99,0,255),(181,100,0,255),(180,100,0,255),(179,101,0,255),(178,102,0,255),(177,103,0,255),(176,103,0,255),(175,104,0,255),(174,105,0,255),(172,105,0,255),(171,106,0,255),(170,107,0,255),(169,107,0,255),(168,108,0,255),(167,109,0,255),(166,109,0,255),(165,110,0,255),(164,111,0,255),(162,111,0,255),(161,112,0,255),(160,112,0,255),(159,113,0,255),(157,114,0,255),(156,114,0,255),(155,115,0,255),(154,115,0,255),(152,116,0,255),(151,117,0,255),(150,117,0,255),(148,118,0,255),(147,118,0,255),(146,119,0,255),(144,119,0,255),(143,120,0,255),(141,120,0,255),(140,121,0,255),(138,122,0,255),(137,122,0,255),(135,123,0,255),(134,123,0,255),(132,124,0,255),(130,124,0,255),(129,125,0,255),(127,125,0,255),(125,126,0,255),(124,126,0,255),(122,127,0,255),(120,127,0,255),(118,128,0,255),(116,128,0,255),(115,129,0,255),(113,129,0,255),(111,130,0,255),(109,130,0,255),(107,130,0,255),(104,131,0,255),(102,131,0,255),(100,132,0,255),(98,132,0,255),(95,133,0,255),(93,133,0,255),(90,134,0,255),(88,134,0,255),(85,134,0,255),(82,135,0,255),(79,135,0,255),(76,136,0,255),(73,136,0,255),(70,137,0,255),(66,137,0,255),(63,137,0,255),(59,138,0,255),(54,138,0,255),(49,138,0,255),(44,139,0,255),(38,139,0,255),(31,140,0,255),(21,140,0,255),(6,140,0,255),(0,141,0,255),(0,141,0,255),(0,141,0,255),(0,142,0,255),(0,142,0,255),(0,142,0,255),(0,143,0,255),(0,143,0,255),(0,143,0,255),(0,144,0,255),(0,144,0,255),(0,144,0,255),(0,145,0,255),(0,145,0,255),(0,145,0,255),(0,146,0,255),(0,146,0,255),(0,146,0,255),(0,146,0,255),(0,147,4,255),(0,147,17,255),(0,147,25,255),(0,147,31,255),(0,148,37,255),(0,148,41,255),(0,148,46,255),(0,148,50,255),(0,149,53,255),(0,149,57,255),(0,149,60,255),(0,149,63,255),(0,150,67,255),(0,150,70,255),(0,150,72,255),(0,150,75,255),(0,150,78,255),(0,151,80,255),(0,151,83,255),(0,151,86,255),(0,151,88,255),(0,151,90,255),(0,151,93,255),(0,152,95,255),(0,152,97,255),(0,152,100,255),(0,152,102,255),(0,152,104,255),(0,152,106,255),(0,152,108,255),(0,152,110,255),(0,152,113,255),(0,153,115,255),(0,153,117,255),(0,153,119,255),(0,153,121,255),(0,153,123,255),(0,153,125,255),(0,153,127,255),(0,153,128,255),(0,153,130,255),(0,153,132,255),(0,153,134,255),(0,153,136,255),(0,153,138,255),(0,153,140,255),(0,153,141,255),(0,153,143,255),(0,153,145,255),(0,153,147,255),(0,153,149,255),(0,152,150,255),(0,152,152,255),(0,152,154,255),(0,152,155,255),(0,152,157,255),(0,152,159,255),(0,152,161,255),(0,152,162,255),(0,151,164,255),(0,151,165,255),(0,151,167,255),(0,151,169,255),(0,151,170,255),(0,150,172,255),(0,150,173,255),(0,150,175,255),(0,150,176,255),(0,149,178,255),(0,149,179,255),(0,149,181,255),(0,148,182,255),(0,148,184,255),(0,148,185,255),(0,147,187,255),(0,147,188,255),(0,146,189,255),(0,146,191,255),(0,145,192,255),(0,145,193,255),(0,145,195,255),(0,144,196,255),(0,144,197,255),(0,143,198,255),(0,142,200,255),(0,142,201,255),(0,141,202,255),(0,141,203,255),(0,140,204,255),(0,140,205,255),(0,139,207,255),(0,138,208,255),(0,138,209,255),(0,137,210,255),(0,136,211,255),(0,135,212,255),(0,135,213,255),(0,134,214,255),(0,133,214,255),(0,132,215,255),(0,131,216,255),(0,131,217,255),(0,130,218,255),(0,129,219,255),(0,128,219,255),(0,127,220,255),(0,126,221,255),(0,125,221,255),(0,124,222,255),(0,123,222,255),(0,122,223,255),(0,121,224,255),(0,120,224,255),(0,119,224,255),(4,118,225,255),(29,117,225,255),(42,116,226,255),(52,115,226,255),(61,114,226,255),(68,112,227,255),(74,111,227,255),(80,110,227,255),(86,109,227,255),(91,108,227,255),(96,106,227,255),(100,105,227,255),(105,104,227,255),(109,103,227,255),(113,101,227,255),(116,100,227,255),(120,99,227,255),(124,97,227,255),(127,96,227,255),(130,95,227,255),(133,93,226,255),(137,92,226,255),(139,91,226,255),(142,89,225,255),(145,88,225,255),(148,86,224,255),(150,85,224,255),(153,84,224,255),(156,82,223,255),(158,81,222,255),(160,79,222,255),(163,78,221,255),(165,77,221,255),(167,75,220,255),(169,74,219,255),(171,72,218,255),(173,71,218,255),(175,70,217,255),(177,68,216,255),(178,67,215,255),(180,65,214,255),(182,64,213,255),(183,63,212,255),(185,61,211,255),(187,60,210,255),(188,59,209,255),(189,58,208,255),(191,56,207,255),(192,55,206,255),(193,54,205,255),(195,53,204,255),(196,52,202,255),(197,51,201,255),(198,49,200,255),(199,48,199,255),(200,47,197,255),(201,46,196,255),(202,46,195,255),(203,45,193,255),(204,44,192,255),(205,43,190,255),(205,43,189,255),(206,42,188,255),(207,41,186,255),(208,41,185,255),(208,40,183,255),(209,40,182,255),(209,40,180,255),(210,40,178,255),(210,39,177,255),(211,39,175,255),(211,39,174,255),(212,39,172,255),(212,39,170,255),(213,40,169,255),(213,40,167,255),(213,40,165,255),(213,40,163,255),(214,41,162,255),(214,41,160,255),(214,42,158,255),(214,42,156,255),(214,43,155,255),(214,44,153,255),(214,44,151,255),(215,45,149,255),(215,46,147,255),(215,46,145,255),(215,47,143,255),(214,48,142,255),(214,49,140,255),(214,50,138,255),(214,50,136,255),(214,51,134,255),(214,52,132,255),(214,53,130,255),(214,54,128,255),(213,55,126,255),(213,56,123,255),(213,57,121,255),(213,58,119,255),(212,59,117,255),(212,60,115,255),(212,61,113,255),(211,62,110,255),(211,62,108,255)]
soa_list = [0.100]#[0.100,1]
target_location_list = ['left','right']
cue_type_list = ['valid','invalid']

#40x1x2x4 = 320 trials in the design

design_reps = 4
trials_per_break = 30

fixation_size_in_degrees = 0.5
instruction_size_in_degrees = 1 #specify the size of the instruction text
target_size_in_degrees = .5
offset_size_in_degrees = 8
box_size_in_degrees = 2

wheel_size_in_degrees = 8
sampler_size_in_degrees = 1

fixation_thickness = .1 #specify the thickness of the fixation cross lines as a proportion of the size
box_thickness = .1
wheel_thickness = .1

text_width = .9 #specify the proportion of the screen to use when drawing instructions


########
# Import libraries
########
import pygame
import aggdraw
import Image
import ImageChops
import math
import sys
import os
import random
import time
import shutil
import hashlib


########
# Start the random seed
########
seed = time.time() #grab the current time
random.seed(seed) #use the time to set the random seed


########
# Initialize pygame and the screen
########
pygame.init() #initialize pygame
pygame.event.set_allowed([pygame.KEYDOWN,pygame.JOYBUTTONDOWN]) #tell pygame to only look for key & button presses
pygame.mouse.set_visible(False) #make the mouse invisible

# screen_size = pygame.display.list_modes()[0] #get the biggest possible screen size
screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF) #initialize a screen
screen_x_center = screen_size[0]/2 #store the location of the screen's x center
screen_y_center = screen_size[1]/2 #store the location of the screen's y center


########
# compute the time halfway between refreshes
########
halfHz = 1.0/(screen_hz*2.0)

########
#Perform some calculations to convert stimulus measurements in degrees to pixels
########
screen_width_in_degrees = math.degrees(math.atan((screen_width/2.0)/viewing_distance)*2)
PPD = screen_size[0]/screen_width_in_degrees #compute the pixels per degree (PPD)
critical_em_size = critical_em_size_in_degrees*PPD

instruction_size = int(instruction_size_in_degrees*PPD)

fixation_thickness = int(fixation_thickness*fixation_size_in_degrees*PPD)
fixation_size = int(fixation_size_in_degrees*PPD)

target_size = int(target_size_in_degrees*PPD)
box_size = int(box_size_in_degrees*PPD)
box_thickness = int(box_thickness*box_size_in_degrees*PPD)
offset_size = int(offset_size_in_degrees*PPD)

wheel_size = int(wheel_size_in_degrees*PPD)
wheel_thickness = int((1-wheel_thickness)*wheel_size_in_degrees*PPD)
sampler_size = int(sampler_size_in_degrees*PPD)

########
#Define some useful colors
########
white = (255,255,255)
black = (0,0,0)
grey = (127,127,127)
dark_grey = (63,63,63)
light_grey = (192, 192, 192)


########
#Initialize the fonts
########

instruction_font_size = 2
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]
while instruction_height<instruction_size:
	instruction_font_size = instruction_font_size + 1
	instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
	instruction_height = instruction_font.size('XXX')[1]

instruction_font_size = instruction_font_size - 1
instruction_font = pygame.font.Font('_Stimuli/DejaVuSans.ttf', instruction_font_size)
instruction_height = instruction_font.size('XXX')[1]


########
# Create sprites for visual stimuli
########

#define a function to turn PIL/aggdraw images to pygame surfaces
def image2surf(image):
	mode = image.mode
	size = image.size
	data = image.tostring()
	return pygame.image.fromstring(data, size, mode)


cross_pen = aggdraw.Pen(grey,fixation_thickness)
cross = aggdraw.Draw('RGBA',[fixation_size,fixation_size],(0,0,0,0))
cross.line( (0,int((fixation_size/2.0)),fixation_size,int((fixation_size/2.0))), cross_pen )
cross.line( (int((fixation_size/2.0)),0,int((fixation_size/2.0)),fixation_size), cross_pen )
cross = image2surf(cross)

box_pen = aggdraw.Pen(grey,box_thickness)
box = aggdraw.Draw('RGBA',[box_size*3,box_size*3],(0,0,0,0))
box.rectangle((box_size,box_size,box_size*2,box_size*2),box_pen)
box = image2surf(box)

cue_pen = aggdraw.Pen(white,box_thickness)
cue = aggdraw.Draw('RGBA',[box_size*3,box_size*3],(0,0,0,0))
cue.rectangle((box_size,box_size,box_size*2,box_size*2),cue_pen)
cue = image2surf(cue)

grey_brush = aggdraw.Brush(grey)
black_brush = aggdraw.Brush(black)
mask = aggdraw.Draw('RGBA',[target_size*3,target_size*3],(0,0,0,0))
mask.ellipse((0,0,target_size*3,target_size*3),grey_brush)
mask.ellipse((target_size,target_size,target_size*2,target_size*2),black_brush)
mask = image2surf(mask)

########
# Create the color wheel
########

# original_image = Image.open('_Stimuli/wheel.tiff')
# bg = Image.new(original_image.mode, original_image.size, (0,0,0))
# diff = ImageChops.difference(original_image, bg)
# bbox = diff.getbbox()
# cropped_image = original_image.crop(bbox)
# resized_image = cropped_image.resize((wheel_size , wheel_size), Image.ANTIALIAS)
# resized_image = resized_image.convert('RGBA')
# bdata = resized_image.tostring()
# resized_image = pygame.image.fromstring(bdata, [wheel_size,wheel_size], 'RGBA')
# wheel = resized_image.convert_alpha()
# pygame.image.save(wheel,'_Stimuli/Rwheel.png')
# r = wheel_size/2.0
# rgb = []
# for angle in color_angle_list:#range(360):
# 	rad = math.radians(angle)
# 	rgb.append(wheel.get_at((int(r+(r*.9)*math.cos(rad)),int(r+(r*.9)*math.sin(rad)))))

def draw_wheel(wheel_rotation):
	wheel = aggdraw.Draw('RGBA',[wheel_size,wheel_size],(0,0,0,0))
	r = 240
	g = 0
	b = 0
	this_degree = wheel_rotation
	# for i in range(120):
	# 	brush = aggdraw.Brush((r/2,g/2,b/2,255))
	# 	wheel.polygon(
	#      (
	#        int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#      )
	#      , brush
	#     )
	# 	this_degree = this_degree+1
	# 	r = r-2
	# 	g = g+2
	# for i in range(120):
	# 	brush = aggdraw.Brush((r/2,g/2,b/2,255))
	# 	wheel.polygon(
	#      (
	#        int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#      )
	#      , brush
	#     )
	# 	this_degree = this_degree+1
	# 	g = g-2
	# 	b = b+2
	# for i in range(120):
	# 	brush = aggdraw.Brush((r/2,g/2,b/2,255))
	# 	wheel.polygon(
	#      (
	#        int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.sin((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#        , int(round(wheel_size/2.0 + math.cos((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	#      )
	#      , brush
	#     )
	# 	this_degree = this_degree+1
	# 	b = b-2
	# 	r = r+2
	for i in range(360):
		brush = aggdraw.Brush(color_list[i])
		wheel.polygon(
	     (
	       int(round(wheel_size/2.0))
	       , int(round(wheel_size/2.0))
	       , int(round(wheel_size/2.0 + math.sin((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	       , int(round(wheel_size/2.0 + math.cos((this_degree-.25)*math.pi/180)*wheel_size/2.0))
	       , int(round(wheel_size/2.0 + math.sin((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	       , int(round(wheel_size/2.0 + math.cos((this_degree+1.25)*math.pi/180)*wheel_size/2.0))
	     )
	     , brush
	    )
		this_degree = this_degree+1
		if this_degree>360:
			this_degree = this_degree-360
	black_brush = aggdraw.Brush((0,0,0,255))
	wheel.ellipse((wheel_thickness,wheel_thickness,wheel_size-wheel_thickness,wheel_size-wheel_thickness),black_brush)
	wheel = image2surf(wheel)
	return wheel


#get colors at critical angles
wheel = draw_wheel(0)
r = wheel_size/2.0
q = (wheel_size/2-(wheel_size/2-wheel_thickness/2)/2)
rgb = []
for angle in color_angle_list:
	rad = math.radians(angle)
	rgb.append(wheel.get_at((int(r+q*math.cos(rad)),int(r+q*math.sin(rad)))))

del wheel

########
# Drawing and helper functions
########

#define a function that waits for a given duration to pass
def simple_wait(duration):
	start = time.time()
	while time.time() < (start + duration):
		pass


#define a function that formats text for the screen
def draw_text(my_text, instruction_font, text_color, my_surface, text_width):
	my_surface_rect = my_surface.get_rect()
	text_width_max = int(my_surface_rect.size[0]*text_width)
	paragraphs = my_text.split('\n')
	render_list = []
	text_height = 0
	for this_paragraph in paragraphs:
		words = this_paragraph.split(' ')
		if len(words)==1:
			render_list.append(words[0])
			if (this_paragraph!=paragraphs[len(paragraphs)-1]):
				render_list.append(' ')
				text_height = text_height + instruction_font.get_linesize()
		else:
			this_word_index = 0
			while this_word_index < (len(words)-1):
				line_start = this_word_index
				line_width = 0
				while (this_word_index < (len(words)-1)) and (line_width <= text_width_max):
					this_word_index = this_word_index + 1
					line_width = instruction_font.size(' '.join(words[line_start:(this_word_index+1)]))[0]
				if this_word_index < (len(words)-1):
					#last word went over, paragraph continues
					render_list.append(' '.join(words[line_start:(this_word_index-1)]))
					text_height = text_height + instruction_font.get_linesize()
					this_word_index = this_word_index-1
				else:
					if line_width <= text_width_max:
						#short final line
						render_list.append(' '.join(words[line_start:(this_word_index+1)]))
						text_height = text_height + instruction_font.get_linesize()
					else:
						#full line then 1 word final line
						render_list.append(' '.join(words[line_start:this_word_index]))
						text_height = text_height + instruction_font.get_linesize()
						render_list.append(words[this_word_index])
						text_height = text_height + instruction_font.get_linesize()
					#at end of paragraph, check whether a inter-paragraph space should be added
					if (this_paragraph!=paragraphs[len(paragraphs)-1]):
						render_list.append(' ')
						text_height = text_height + instruction_font.get_linesize()
	num_lines = len(render_list)*1.0
	for this_line in range(len(render_list)):
		this_render = instruction_font.render(render_list[this_line], True, text_color)
		this_render_rect = this_render.get_rect()
		this_render_rect.centerx = my_surface_rect.centerx
		this_render_rect.centery = int(my_surface_rect.centery - text_height/2.0 + 1.0*this_line/num_lines*text_height)
		my_surface.blit(this_render, this_render_rect)


#define a function that waits for a response
def wait_for_response():
	done = False
	while not done:
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				response = event.unicode
				if response == '\x1b':
					pygame.quit()
					sys.exit()
				else:
					done = True
					#CHANGE
			if event.type == pygame.JOYBUTTONDOWN:
				done = True
	pygame.event.fill_screen()


#define a function that prints a message on the screen while looking for user input to continue. The function returns the total time it waited
def show_message(my_text):
	message_viewing_time_start = time.time()
	pygame.event.pump()
	pygame.event.fill_screen()
	screen.fill(black)
	pygame.display.flip()
	screen.fill(black)
	draw_text(my_text, instruction_font, light_grey, screen, text_width)
	simple_wait(.5)
	pygame.display.flip()
	screen.fill(black)
	wait_for_response()
	pygame.display.flip()
	screen.fill(black)
	simple_wait(.5)
	message_viewing_time = time.time() - message_viewing_time_start
	return message_viewing_time


#define a function that requests user input
def get_input(get_what):
	get_what = get_what+'\n'
	text_input = ''
	screen.fill(black)
	pygame.display.flip()
	simple_wait(.5)
	my_text = get_what+text_input
	screen.fill(black)
	draw_text(my_text, instruction_font, light_grey, screen, text_width)
	pygame.display.flip()
	screen.fill(black)
	done = False
	while not done:
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				key_down = event.unicode
				if key_down == '\x1b':
					pygame.quit()
					sys.exit()
				elif key_down == '\x7f':
					if text_input!='':
						text_input = text_input[0:(len(text_input)-1)]
						my_text = get_what+text_input
						screen.fill(black)
						draw_text(my_text, instruction_font, light_grey, screen, text_width)
						pygame.display.flip()
				elif key_down == '\r':
					done = True
				else:
					text_input = text_input + key_down
					my_text = get_what+text_input
					screen.fill(black)
					draw_text(my_text, instruction_font, light_grey, screen, text_width)
					pygame.display.flip()
	screen.fill(black)
	pygame.display.flip()
	return text_input


#define a function that obtains subject info via user input
def get_sub_info():
	year = time.strftime('%Y')
	month = time.strftime('%m')
	day = time.strftime('%d')
	hour = time.strftime('%H')
	minute = time.strftime('%M')
	done = False #set done as false in order to enter the loop
	sid = get_input('   ID:   ')
	if sid != 'test':
		password = get_input('B00 number (omit the B00 part):')
		sex = get_input('Sex (m or f):')
		age = get_input('Age (2-digit number):')
		handedness = get_input('Handedness (r or l):')
		blindness = get_input('Do you have any diagnosed difficulty in distinguishing colors?(y or n):')
	else:
		password = 'test'
		sex = 'test'
		age = 'test'
		handedness = 'test'
		blindness = 'test'
	sub_info = [ sid , year , month , day , hour , minute , sex , age , handedness , blindness, password]
	return sub_info


#define a function that initializes the data file
def initialize_data_file():	
	if sub_info[0]=='test':
		filebase = 'test'
	else:
		filebase = '_'.join(sub_info[0:6])
	if not os.path.exists('_Data'):
		os.mkdir('_Data')
	if not os.path.exists('_Data/'+filebase):
		os.mkdir('_Data/'+filebase)
	shutil.copy(__file__, '_Data/'+filebase+'/'+filebase+'_code.py')
	data_file_name = '_Data/'+filebase+'/'+filebase+'_data.txt'
	data_file  = open(data_file_name,'w')
 	header ='\t'.join(['sid' , 'year' , 'month' , 'day' , 'hour' , 'minute' , 'sex' , 'age' , 'handedness' , 'blindness' , 'password' ,'wait' , 'block' , 'trial_num' , 'time' , 'cue_type','cue_location','soa','target_location','target_color','target_angle','wheel_rotation' , 'response_color' , 'response_rt', 'response_x', 'response_y' , 'biggest_em' , 'blink_made'])
	data_file.write(header+'\n')	
	return data_file


#define a function to draw a pygame surface centered on given coordinates
def blit_to_screen(surf,x=0,y=0):
	screen.blit(surf,(screen_x_center-x-int(surf.get_width()/2.0),screen_y_center-y-int(surf.get_height()/2.0)))


#define a function to draw the cross and 3 boxes
def draw_fixation():
	blit_to_screen(cross)
	blit_to_screen(box)
	blit_to_screen(box,offset_size)
	blit_to_screen(box,-offset_size)


#define a function to draw fixation and the cue
def draw_cue(cue_location):
	blit_to_screen(cross)
	if cue_location=='all':
		blit_to_screen(cue)
		blit_to_screen(cue,offset_size)
		blit_to_screen(cue,-offset_size)
	elif cue_location=='center':
		blit_to_screen(cue)
		blit_to_screen(box,offset_size)
		blit_to_screen(box,-offset_size)
	elif cue_location=='left':
		blit_to_screen(box)
		blit_to_screen(box,offset_size)
		blit_to_screen(cue,-offset_size)
	elif cue_location=='right':
		blit_to_screen(box)
		blit_to_screen(box,offset_size)
		blit_to_screen(cue,-offset_size)		


#define a function to draw fixation and the target
def draw_target(target,target_location):
	blit_to_screen(cross)
	blit_to_screen(box)
	blit_to_screen(box,offset_size)
	blit_to_screen(box,-offset_size)
	if target_location=='left':
		blit_to_screen(target,-offset_size)
	else:
		blit_to_screen(target,offset_size)

#define a function to draw fixation and the mask
def draw_mask(target_location):
	blit_to_screen(cross)
	blit_to_screen(box)
	blit_to_screen(box,offset_size)
	blit_to_screen(box,-offset_size)
	if target_location=='left':
		blit_to_screen(mask,-offset_size)
	else:
		blit_to_screen(mask,offset_size)

#define a function for drawing the wheel and sampler
def draw_wheelnsampler(sampler_x,sampler_y,wheel):
	screen.fill(black)
	blit_to_screen( wheel )
	color = screen.get_at((sampler_x,sampler_y))
	if (color[0]<10) & (color[1]<10) & (color[2]<10):
		sampler_brush = aggdraw.Brush((128,128,128,255))
		sampler_hole_brush = aggdraw.Brush(black)
	else:
		sampler_brush = aggdraw.Brush((0,0,0,255))
		sampler_hole_brush = aggdraw.Brush((color[0],color[1],color[2],255))
	sampler = aggdraw.Draw('RGBA',[sampler_size,sampler_size],(0,0,0,0))
	sampler.ellipse((0,0,sampler_size,sampler_size),sampler_brush)
	sampler.ellipse((int(sampler_size/4.0),int(sampler_size/4.0),int(sampler_size/4.0*3),int(sampler_size/4.0*3)),sampler_hole_brush)
	sampler = image2surf(sampler)
	blit_to_screen( sampler, screen_x_center-sampler_x , screen_y_center - sampler_y )


#define a timed wait function that looks for color choice
def get_color_response(wheel):
	start= time.time()
	pygame.event.fill_screen()
	pygame.mouse.set_pos([screen_x_center,screen_y_center])
	sample_angle = 0
	sampler_x = screen_x_center
	sampler_y = screen_y_center
	draw_wheelnsampler(sampler_x,sampler_y,wheel)
	pygame.display.flip()
	done = False
	while not done:
		pygame.event.pump()
		for event in pygame.event.get() :
			if event.type == pygame.KEYDOWN :
				key_down = event.unicode
				if key_down == '\x1b':
					pygame.quit()
					sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				response_color = screen.get_at((sampler_x,sampler_y))#180+math.degrees(math.atan2(screen_y_center-sampler_y,screen_x_center-sampler_x))
				if (response_color[0]+response_color[1]+response_color[2])>100:
					response_rt = time.time()-start
					done = True
			elif event.type == pygame.MOUSEMOTION :
				sampler_x, sampler_y = pygame.mouse.get_pos()
				draw_wheelnsampler(sampler_x,sampler_y,wheel)
				pygame.display.flip()
	pygame.event.fill_screen()
	return [ response_rt , response_color , screen_x_center-sampler_x , screen_y_center-sampler_y ]


#define a function that generates a randomized list of trial-by-trial stimulus information representing a factorial combination of the independent variables.
def get_trials():
	trials=[]
	for color_num in range(len(color_angle_list)):
		target_color = rgb[color_num]
		target_angle = color_angle_list[color_num]
		for cue_type in cue_type_list:
			for target_location in target_location_list:
				if cue_type=='valid':
					cue_location = target_location
				elif cue_type=='invalid':
					if target_location=='right':
						cue_location = 'left'
					else:
						cue_location = 'right'
				else:
					cue_location = cue_type
				wheel_rotation = random.uniform(0,360)
				target_brush = aggdraw.Brush((target_color[0],target_color[1],target_color[2],target_color[3]))
				target = aggdraw.Draw('RGBA',[target_size,target_size],(0,0,0,0))
				target.ellipse((0,0,target_size,target_size),target_brush)
				target = image2surf(target)
				trials.append([cue_type,cue_location,target_location,target_color,target_angle,wheel_rotation])
	random.shuffle(trials)
	return trials


#define a function that runs a block of trials
def run_block(soa,block,message_viewing_time):
	trial_list = get_trials()
	if block=='practice':
		trial_list = trial_list[0:10]
	trial_num = 0
	for this_trial_info in trial_list:
		trial_num = trial_num+1
		cue_type,cue_location,target_location,target_color,target_angle,wheel_rotation, = this_trial_info
		screen.fill(black)
		draw_fixation()
		pygame.display.flip()
		wheel = draw_wheel(wheel_rotation)
		target_brush = aggdraw.Brush((target_color[0],target_color[1],target_color[2],target_color[3]))
		target = aggdraw.Draw('RGBA',[target_size,target_size],(0,0,0,0))
		target.ellipse((0,0,target_size,target_size),target_brush)
		target = image2surf(target)
		wait_for_response()
		if do_eyelink:
			eyelink.startRecording(0,0,1,1)
		trial_start_time = time.time()
		cue_on_time = trial_start_time + fixation_duration
		cue_off_time = cue_on_time + cue_duration
		target_on_time = cue_on_time + soa
		target_off_time = target_on_time + target_duration
		wheel_on_time = target_off_time + post_duration
		#prep the cue screen
		screen.fill(black)
		draw_cue(cue_location)
		while time.time()<(cue_on_time-halfHz):
			pass
		pygame.display.flip() #show the cue screen
		#prep the post-cue screen
		screen.fill(black)
		draw_fixation()
		while time.time()<(cue_off_time-halfHz):
			pass
		pygame.display.flip() #show the post-cue screen
		#prep the target screen
		screen.fill(black)
		draw_target(target,target_location)
		while time.time()<(target_on_time-halfHz):
			pass
		pygame.display.flip() #show the target screen
		#prep the post-target screen
		screen.fill(black)
		draw_mask(target_location)
		while time.time()<(target_off_time-halfHz):
			pass
		pygame.display.flip() #show the post-target screen
		#prep the color wheel
		screen.fill(black)
		draw_wheelnsampler(screen_x_center,screen_y_center,wheel)
		while time.time()<(wheel_on_time-halfHz):
			pass
		pygame.display.flip() #show the color wheel
		#check for eye movements
		blink_made = 'FALSE'
		biggest_em = 0
		if do_eyelink:
			eyelink.stopRecording()
			while eyelink.getDataCount(0,1):
				eyelink.getNextData()
				newEvent = eyelink.getFloatData()
				if isinstance(newEvent, pylink.EndSaccadeEvent):
					start = newEvent.getStartGaze()
					end = newEvent.getEndGaze()
					dx = end[0]-start[0]
					dy = end[1]-start[1]
					dist = math.sqrt(dx*dx+dy*dy)
					if dist>biggest_em:
						biggest_em = dist
				elif isinstance(newEvent,pylink.EndBlinkEvent):
					blink_made = 'TRUE'
		#get color response
		response_rt , response_color , response_x , response_y = get_color_response(wheel)
		screen.fill(black)
		draw_wheelnsampler(screen_x_center-response_x,screen_y_center-response_y,wheel)
		target_rad = math.radians(target_angle-wheel_rotation)
		blit_to_screen(cross,-int(q*math.cos(target_rad)),-int(q*math.sin(target_rad)))
		pygame.display.flip()
		simple_wait(1)
		trial_info = '\t'.join(map(str, [ sub_info_for_file , message_viewing_time , block , trial_num , time.time()-trial_start_time , cue_type,cue_location,soa,target_location,target_color,target_angle,wheel_rotation, response_color , response_rt , response_x , response_y , biggest_em , blink_made ]))
		data_file.write(trial_info+'\n')
		if block!='practice':
			if (trial_num%(trials_per_break)==0):
				if trial_num<len(trial_list):
					message_viewing_time = show_message('Take a break!\nYou\'re about '+str((block-1)*breaks_per_block+trial_num/(trials_per_break))+'/'+str(design_reps*breaks_per_block)+' done.\nPlease check your distance from the screen.\nWhen you are ready, press any button to continue the experiment.')


########
# Start the experiment
########

#get subject info
sub_info = get_sub_info()

# if sub_info[0]=='test':
# 	soa1 = soa_list[0]
# 	soa2 = soa_list[1]
# elif (int(sub_info[0])%2)==0:
# 	soa1 = soa_list[0]
# 	soa2 = soa_list[1]
# 	sub_info[10] = hashlib.sha512(sub_info[10]).hexdigest()
# else:
# 	soa2 = soa_list[0]
# 	soa1 = soa_list[1]
# 	sub_info[10] = hashlib.sha512(sub_info[10]).hexdigest()

if sub_info[0]=='test':
	pass
elif (int(sub_info[0])%2)==0:
	sub_info[10] = hashlib.sha512(sub_info[10]).hexdigest()
else:
	sub_info[10] = hashlib.sha512(sub_info[10]).hexdigest()

soa1 = soa_list[0]

sub_info_for_file = '\t'.join(map(str,sub_info))


#initialize the data file
data_file = initialize_data_file()

temp = get_trials()
breaks_per_block = len(temp)/trials_per_break

#set up the eye tracker if necessary
if do_eyelink:
	import pylink
	eyelink = pylink.EyeLink()
	pylink.openGraphics(screen_size) 
	eyelink.sendCommand("screen_pixel_coords =  0 0 %d %d" %(screen_size[0], screen_size[1]))
	# eyelink.sendMessage("link_event_filter = SACCADE") #only send saccade events over the link
	# eyelink.sendMessage("link_event_data = SACCADE") #only send saccade events over the link
	pylink.setCalibrationColors((255, 255, 255), (0, 0, 0))
	pylink.setCalibrationSounds("off", "off", "off")
	pylink.setDriftCorrectSounds("off", "off", "off")
	eyelink.doTrackerSetup()


#run practice
message_viewing_time = show_message('Please wait for instructions.')
run_block(soa1,'practice',message_viewing_time)
message_viewing_time = show_message('You\'re all done the practice phase of this experiment.\nPlease check your distance from the screen.\nWhen you are ready, press any button to continue to the experiment.')

block = 0
#run the experiment
for i in range(design_reps):
	block = block+1
	run_block(soa1,block,message_viewing_time)
	if (i+1)<design_reps:
		message_viewing_time = show_message('Take a break!\nYou\'re about '+str(block*breaks_per_block)+'/'+str(design_reps*breaks_per_block)+' done.\nPlease check your distance from the screen.\nWhen you are ready, press any button to continue the experiment.')

# message_viewing_time = show_message('The timing of the experiment will now change slightly.\nThe next block of trials will be considered practice so you can get a feel for the new timing.\nPress any key to begin practice.')
# run_block(soa2,'practice',message_viewing_time)
# message_viewing_time = show_message('You\'re all done the practice phase of this experiment.\nPlease check your distance from the screen.\nWhen you are ready, press any button to continue to the experiment.')
# 
# for i in range(design_reps):
# 	block = block+1
# 	run_block(soa2,block,message_viewing_time)
# 	if (i+1)<design_reps:
# 		message_viewing_time = show_message('Take a break!\nYou\'re about '+str(block*breaks_per_block)+'/'+str(design_reps*2*breaks_per_block)+' done.\nPlease check your distance from the screen.\nWhen you are ready, press any button to continue the experiment.')
# 

message_viewing_time = show_message('You\'re all done!\nPlease alert the person conducting this experiment that you have finished.')

data_file.close()
pygame.quit()
sys.exit()