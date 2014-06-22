import pygame
from pygame.locals import Rect
from operator import add
import random
import os

# Name of the game
game_name = "Brains and Bones"

# Snake game variables
block_width = 16 # width of snake blocks, sprites are 16x16 so use multiples of 16 to look the best
screen_width = 31 # width of screen, in terms of snake blocks

screen_border = 3 # inset of border, in terms of snake blocks

buffet_mode = None # new food appears when old food is eaten
salamander_mode = None # tails become food

class colour:
	white = (255,255,255)
	black = (0,0,0)
	red = (255,0,0)
	green = (0,255,0)
	blue = (0,0,255)
	yellow = (255,255,0)

def add_positions(position_1, position_2):
	return tuple(map(add, position_1, position_2))

# Setup pygame
pygame.mixer.pre_init(44100, -16, 2, 2048) # something to do with music
pygame.init()
screen = pygame.display.set_mode([block_width*screen_width]*2)
pygame.display.set_caption(game_name)

## sounds
long_munch_sound = pygame.mixer.Sound("sounds/longmunch2.wav")
munch_sound = pygame.mixer.Sound("sounds/longmunch.wav")
crunch_sound = pygame.mixer.Sound("sounds/crunch.wav")

# font
font = pygame.font.SysFont("monospace", 72*block_width/32)
medium_font = pygame.font.SysFont("monospace", 48*block_width/32)
small_font = pygame.font.SysFont("monospace", 36*block_width/32)

## Sprites
def load_sprite(path, scale):
	return pygame.transform.scale(pygame.image.load(os.path.join(path)), (scale,scale))

# heads
snakeredhead = load_sprite("ZombiePack/Zombie_R_Closed.png", block_width)
snakebluehead = load_sprite("ZombiePack/Zombie_B_Closed.png", block_width)
snakeredhead.convert()
snakebluehead.convert()
snakeredhead_nom = load_sprite("ZombiePack/Zombie_R_Open.png", block_width)
snakebluehead_nom = load_sprite("ZombiePack/Zombie_B_Open.png", block_width)
snakeredhead_nom.convert()
snakebluehead_nom.convert()

## spines
# straight bits
Ribs_B_Straight = load_sprite("ZombiePack/Ribs_B_Straight.png", block_width)
Ribs_R_Straight = load_sprite("ZombiePack/Ribs_R_Straight.png", block_width)
Ribs_O_Straight = load_sprite("ZombiePack/Ribs_O_Straight.png", block_width)
Ribs_B_Straight.convert()
Ribs_R_Straight.convert()
Ribs_O_Straight.convert()
# tails
Ribs_B_tail_Straight = load_sprite("ZombiePack/Ribs_B_tail_Straight.png", block_width)
Ribs_R_tail_Straight = load_sprite("ZombiePack/Ribs_R_tail_Straight.png", block_width)
Ribs_O_tail_Straight = load_sprite("ZombiePack/Ribs_O_tail_Straight.png", block_width)
Ribs_B_tail_Straight.convert()
Ribs_R_tail_Straight.convert()
Ribs_O_tail_Straight.convert()
# corners
Ribs_B_Left = load_sprite("ZombiePack/Ribs_B_unSym_Left.png", block_width)
Ribs_B_Right = pygame.transform.flip(Ribs_B_Left, False, True)
Ribs_B_Left.convert()
Ribs_B_Right.convert()
Ribs_R_Left = load_sprite("ZombiePack/Ribs_R_unSym_Left.png", block_width)
Ribs_R_Right = pygame.transform.flip(Ribs_R_Left, False, True)
Ribs_R_Left.convert()
Ribs_R_Right.convert()
Ribs_O_Left = load_sprite("ZombiePack/Ribs_O_unSym_Left.png", block_width)
Ribs_O_Right = pygame.transform.flip(Ribs_O_Left, False, True)
Ribs_O_Left.convert()
Ribs_O_Right.convert()
# braaaaaaaains
braaaaaaiiiiiiiins = load_sprite("ZombiePack/Brains_top.png", block_width)
braaaaaaiiiiiiiins.convert()
# dirt background
game_screen = load_sprite("ZombiePack/GameScreen_006.png", block_width*screen_width)
game_screen.convert()
# pile of bones
pile_of_bones = load_sprite("ZombiePack/Pile_bones_top.png", block_width)
pile_of_bones.convert()
pile_of_small_bones = load_sprite("ZombiePack/Pile_smallbones_top.png", block_width)
pile_of_small_bones.convert()

# splash screen
splash_screen = load_sprite("ZombiePack/SplashScreen01_001.png", block_width*screen_width)
splash_screen.convert()

# controls sprites
blue_controls = load_sprite("ZombiePack/BLUEWASD.png", block_width*8)
blue_controls.convert()
red_controls = load_sprite("ZombiePack/REDARROWS.png", block_width*8)
red_controls.convert()

def direct_to_angle(direct):
	if (direct == (0,-1)):
		return 180
	elif (direct == (0,1)):
		return 0
	elif (direct == (1,0)):
		return 90
	elif (direct == (-1,0)):
		return 270

def scaled_block_location(block):
	return (block_width*block[0], block_width*block[1])

def direction_between_blocks(block1, block2):
	return (block1[0]-block2[0], block1[1]-block2[1])

def three_blocks_go_left(block1, block2, block3): # well do they?
	vector1 = (block1[0]-block2[0], block1[1]-block2[1])
	vector2 = (block2[0]-block3[0], block2[1]-block3[1])
	return vector1[0]*vector2[1] - vector1[1]*vector2[0]>0 # holy shit vector algebra

# Snake class
class snake:
	def __init__(self, blocks, colour):
		self.blocks = blocks
		self.colour = colour

	def move_block(self, index, delta_position):
		current_position = self.blocks[index]
		self.blocks[index] = add_positions(current_position, delta_position)
		for i in reversed(range(index+2, len(self.blocks))):
			self.blocks[i] = self.blocks[i-1]
		self.blocks[index+1] = current_position			

	def draw(self, enemy_snake, direction, force_mouth_open = False):
		## vector graphics
		if False:
			# draw vector blocks
			for i, (x, y) in enumerate(self.blocks):
				block_colour = self.colour
				if (i == 0):
					continue
					block_colour = tuple([min(255,block_colour[j]+128) for j in range(0,3)])
				pygame.draw.rect(screen, block_colour, Rect((block_width*x+1,block_width*y+1), (block_width-2,block_width-2)))

		## sprites
		# draw head
		head_direction = direction
		## check if there's anything to eat in front of us
		if force_mouth_open:
			eat = True
		else:
			eat = False
			eat_place = tuple(map(add, head_direction, self.blocks[0]))
			# check food
			for food in foods:
				if (food == eat_place):
					eat = True
					break
			# check enemy snake
			if not eat:
				for block in enemy_snake.blocks:
					if (block == eat_place):
						eat = True
						break
		# decide head sprite
		head_sprite = None
		if not eat:
			if (self.colour == colour.red):
				head_sprite = snakeredhead
			elif (self.colour == colour.blue):
				head_sprite = snakebluehead
		else:
			if (self.colour == colour.red):
				head_sprite = snakeredhead_nom
			elif (self.colour == colour.blue):
				head_sprite = snakebluehead_nom
		screen.blit(pygame.transform.rotate(head_sprite,direct_to_angle(head_direction)), scaled_block_location(self.blocks[0]))

	def draw_body(self, snake_lost):
		# draw body
		straight_body = None
		straight_tail = None
		if snake_lost:
			straight_body = Ribs_O_Straight
			straight_tail = Ribs_O_tail_Straight
			left_body = Ribs_O_Left
			right_body = left_body = Ribs_O_Right # these two lines make the corners align correctly, but i dont know or cannot remember why
		elif (self.colour == colour.red):
			straight_body = Ribs_R_Straight
			straight_tail = Ribs_R_tail_Straight
			left_body = Ribs_R_Left
			right_body = left_body = Ribs_R_Right
		elif (self.colour == colour.blue):
			straight_body = Ribs_B_Straight
			straight_tail = Ribs_B_tail_Straight
			left_body = Ribs_B_Left
			right_body = left_body = Ribs_B_Right

		for i, block in enumerate(self.blocks):
			if (i==0 or i==len(self.blocks)-1):
				continue
			direct = direction_between_blocks(self.blocks[i-1], self.blocks[i])
			# straight segment case
			if (direct == direction_between_blocks(self.blocks[i], self.blocks[i+1])):
				straight_body_or_tail = None
				if (i<len(self.blocks)-2):
					straight_body_or_tail = straight_body
				else:
					straight_body_or_tail = straight_tail
				if (len(self.blocks)>0):
					screen.blit(pygame.transform.rotate(straight_body_or_tail,direct_to_angle(direct)), scaled_block_location(block))
			else:
				if three_blocks_go_left(self.blocks[i-1], self.blocks[i], self.blocks[i+1]):
					screen.blit(pygame.transform.rotate(left_body,direct_to_angle(direct)+180), scaled_block_location(block))
				else:
					screen.blit(pygame.transform.rotate(right_body,direct_to_angle(direct)+90), scaled_block_location(block))


foods = [(screen_width/2,screen_width/2)]

# eat food at this position
def eat_food(position):
	munch_sound.play()
	for i in range(0,len(foods)):
		if (foods[i] == position):
			del foods[i]
			return
			
# add_food() adds food to a random location, or specify the position
def add_food(position = None):
	global foods
	if position is None:
		while True:
			position = (random.randint(screen_border,screen_width-1-screen_border),random.randint(screen_border,screen_width-1-screen_border))
			clash = False
			for food in foods:
				if (food==position):
					clash = True
					break
			for block in snake1.blocks:
				if (position==block):
					clash = True
					break
			for block in snake2.blocks:
				if (position==block):
					clash = True
					break
			if clash:
				continue
			else:
				break
	foods.append(position)

# scatter more initial food around
#for i in range(10):
#	add_food()

# draw the food
def draw_food():
	for food in foods:
		#pygame.draw.rect(screen, colour.yellow, Rect((block_width*food[0]+1,block_width*food[1]+1), (block_width-2,block_width-2)))
		if buffet_mode:
			screen.blit(braaaaaaiiiiiiiins, scaled_block_location(food))
		else:
			screen.blit(pile_of_small_bones, scaled_block_location(food))

# Setup snakes
snake1 = snake([(screen_width-5,i) for i in range(15,25)], colour.red)
snake2 = snake([(4,i) for i in range(15,25)], colour.blue)

# snake directions
direct1 = (0,-1)
direct2 = (0,-1)

# losing
snake1_lost = False
snake2_lost = False

running = True

collided = False

end_reasons = [] # reasons why game ended, not including boredom, or winning properly

player1_moved = False
player1_valid_move = False # player 1 done a valid move
player2_moved = False
player2_valid_move = False # player 1 done a valid move
direct1_buffered = None
direct2_buffered = None

first_loop = True # is it the first run (so show the controls)

def reset():
	global snake1, snake2, direct1, direct2, snake1_lost, snake2_lost, running, foods, collided, end_reasons
	global player1_moved, player1_valid_move, player2_moved, player2_valid_move, direct1_buffered, direct2_buffered
	global firstloop

	# Setup snakes
	snake1 = snake([(screen_width-5,i) for i in range(15,25)], colour.red)
	snake2 = snake([(4,i) for i in range(15,25)], colour.blue)

	# snake directions
	direct1 = (0,-1)
	direct2 = (0,-1)

	# losing
	snake1_lost = False
	snake2_lost = False

	running = True

	foods = [(screen_width/2,screen_width/2)]

	collided = False

	end_reasons = []

	player1_moved = False
	player1_valid_move = False

	player2_moved = False
	player2_valid_move = False

	direct1_buffered = None
	direct2_buffered = None

	first_loop = True

# how many times each snake has won, displayed in each corner
snake1_score = 0
snake2_score = 0

def is_off_screen((x,y)):
	if (x<screen_border or y<screen_border or x>=screen_width-screen_border or y>=screen_width-screen_border):
		return True
	else:
		return False

# when snakes collide head-on, decide who won
def game_end(snake1_length, snake2_length):
	global snake1_lost, snake2_lost, collided
	if (snake1_length >= snake2_length):
		snake2_lost = True
	if (snake2_length >= snake1_length):
		snake1_lost = True
	if (snake1_length == snake2_length):
		end_reasons.append("you ate each other")
	collided = True
	long_munch_sound.play()

# to prevent self-collisions on tight turns
def is_block_directly_behind(snake, direct):
	return (tuple(map(add, snake.blocks[0], direct)) == snake.blocks[1])

# draws text with a black outline
def draw_text(font, string, position, colour, border=3):
	text = font.render(string, 1, (0,0,0))
	for offset in [(i,j) for i in range(-border,border+1) for j in range(-border,border+1) if not (i,j) == (0,0)]:
		screen.blit(text, tuple(map(add, position, offset)))
	text = font.render(string, 0, colour)
	screen.blit(text, position)

# everybody needs a clock
clock = pygame.time.Clock()

## intro screen aka splash screen
def show_intro_screen():
	global running, buffet_mode, salamander_mode
	# draw instructions
	screen.fill(colour.black)
	if False:
		draw_text(medium_font, game_name.upper(), (block_width, block_width), (64,255,64), border=2)
		draw_text(small_font, "red controls: up, down, left, right", (block_width, block_width+128*block_width/32), (255,64,64), border=2)
		draw_text(small_font, "blue controls: w, a, s, d", (block_width, block_width+(128+64)*block_width/32), (128,128,255), border=2)
		draw_text(small_font, "goal: get bigger than the other player,", (block_width, block_width+(128+236)*block_width/32), (255,255,255), border=2)
		draw_text(small_font, "      then eat their face", (block_width, block_width+(128+256+32)*block_width/32), (255,255,255), border=2)
		draw_text(small_font, "press space for mode a, ctrl for mode b...", (block_width, block_width*(screen_width-2)), (255,255,255), border=2)
	else:
		screen.blit(splash_screen, (0,0))
		draw_text(small_font, "press space for brains, ctrl for bones...", (block_width, block_width*(screen_width-2)), (255,255,255), border=2)
	pygame.display.flip()
	# wait for space to start game
	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				waiting = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
					waiting = False
					try: # bad code, please correct at some point
						pygame.quit()
					except pygame.error:
						pass
				if event.key == pygame.K_SPACE:
					waiting = False
					buffet_mode = True
					salamander_mode = False
				if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
					waiting = False
					buffet_mode = False
					salamander_mode = True
		clock.tick(10)

show_intro_screen()

# Main loop
while running:
	# there is a buffer system thing, so you can do tight corners, its a bit hard to explain
	# i dont really understand it
	player1_moved = False
	player1_valid_move = False
	player2_moved = False
	player2_valid_move = False
	
	if (not snake1_lost and not snake2_lost): # if the game isnt over
		# control input
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					reset()
					show_intro_screen()
				# snake 1
				if event.key == pygame.K_LEFT:
					player1_moved = True
					if not is_block_directly_behind(snake1, (-1,0)) and not player1_valid_move:
						player1_valid_move = True
						direct1 = (-1,0)
					else:
						direct1_buffered = (-1,0)
				elif event.key == pygame.K_RIGHT:
					player1_moved = True
					if not is_block_directly_behind(snake1, (1,0)) and not player1_valid_move:
						player1_valid_move = True
						direct1 = (1,0)
					else:
						direct1_buffered = (1,0)
				elif event.key == pygame.K_UP:
					player1_moved = True
					if not is_block_directly_behind(snake1, (0,-1)) and not player1_valid_move:
						player1_valid_move = True
						direct1 = (0,-1)
					else:
						direct1_buffered = (0,-1)
				elif event.key == pygame.K_DOWN:
					player1_moved = True
					if not is_block_directly_behind(snake1, (0,1)) and not player1_valid_move:
						player1_valid_move = True
						direct1 = (0,1)
					else:
						direct1_buffered = (0,1)
				# snake 2
				elif event.key == pygame.K_a:
					player2_moved = True
					if not is_block_directly_behind(snake2, (-1,0)) and not player2_valid_move:
						player2_valid_move = True
						direct2 = (-1,0)
					else:
						direct2_buffered = (-1,0)
				elif event.key == pygame.K_d:
					player2_moved = True
					if not is_block_directly_behind(snake2, (1,0)) and not player2_valid_move:
						player2_valid_move = True
						direct2 = (1,0)
					else:
						direct2_buffered = (1,0)
				elif event.key == pygame.K_w:
					player2_moved = True
					if not is_block_directly_behind(snake2, (0,-1)) and not player2_valid_move:
						player2_valid_move = True
						direct2 = (0,-1)
					else:
						direct2_buffered = (0,-1)
				elif event.key == pygame.K_s:
					player2_moved = True
					if not is_block_directly_behind(snake2, (0,1)) and not player2_valid_move:
						player2_valid_move = True
						direct2 = (0,1)
					else:
						direct2_buffered = (0,1)
		# buffered commands
		if not player1_moved and direct1_buffered is not None:
			if not is_block_directly_behind(snake1, direct1_buffered):
				direct1 = direct1_buffered

			direct1_buffered = None

		if not player2_moved and direct2_buffered is not None:
			if not is_block_directly_behind(snake2, direct2_buffered):
				direct2 = direct2_buffered

			direct2_buffered = None
	
	## game
	snake1_length = len(snake1.blocks)
	snake2_length = len(snake2.blocks)

	## check if the heads are about to collide
	eat_place_snake1 = tuple(map(add, direct1, snake1.blocks[0]))
	eat_place_snake2 = tuple(map(add, direct2, snake2.blocks[0]))
	if (eat_place_snake1 == eat_place_snake2 or eat_place_snake1 == snake2.blocks[0] or eat_place_snake2 == snake1.blocks[0]):
		game_end(snake1_length, snake2_length)


	## snakes
	# keep track of where to add to snake if food is collected
	last_snake1_pos = snake1.blocks[-1]
	last_snake2_pos = snake2.blocks[-1]
	# move the snakes
	snake1.move_block(0,direct1)
	snake2.move_block(0,direct2)
	# snakes eat each other, possibly creating food
	if (not snake1_lost and not snake2_lost): # if the game isnt over
		for i in range(0,len(snake2.blocks)):
			if (snake2.blocks[i] == snake1.blocks[0]):
				crunch_sound.play()
				if salamander_mode:
					for dead_block in snake2.blocks[i+1:]:
						add_food(dead_block)
				snake2.blocks = snake2.blocks[:i+1]
				break
		for i in range(0,len(snake1.blocks)):
			if (snake1.blocks[i] == snake2.blocks[0]):
				crunch_sound.play()
				if salamander_mode:
					for dead_block in snake1.blocks[i+1:]:
						add_food(dead_block)
				snake1.blocks = snake1.blocks[:i+1]
				break
		# check if snakes have collided into themselves
		for block in snake1.blocks[1:-1]:
			if (block == snake1.blocks[0]):
				end_reasons.append("red suicided")
				snake1_lost = True
		for block in snake2.blocks[1:-1]:
			if (block == snake2.blocks[0]):
				end_reasons.append("blue suicided")
				snake2_lost = True
		# check if snakes have eaten any food
		for food in foods:
			if (food == snake1.blocks[0]):
				eat_food(food)
				snake1.blocks.append(last_snake1_pos)
				if buffet_mode:
					add_food()
		for food in foods:
			if (food == snake2.blocks[0]):
				eat_food(food)
				snake2.blocks.append(last_snake2_pos)
				if buffet_mode:
					add_food()
	# check if snakes have gone off the screen
	if is_off_screen(snake1.blocks[0]):
		end_reasons.append("red hit the fence")
		snake1_lost = True
	if is_off_screen(snake2.blocks[0]):
		end_reasons.append("blue hit the fence")
		snake2_lost = True
	## draw
	screen.fill(colour.black)
	# background
	screen.blit(game_screen, (0,0))
	draw_food()
	snake1.draw_body(snake1_lost)
	snake2.draw_body(snake2_lost)
	# if one face won, face the body of the enemy snake
	if False:
		if collided:
			if snake2_lost:
				direct1 = direction_between_blocks(snake2.blocks[1], snake1.blocks[0])
			if snake1_lost:
				direct2 = direction_between_blocks(snake1.blocks[0], snake2.blocks[1])
	# if the snake is still alive, draw the head
	if not snake1_lost:
		snake1.draw(enemy_snake = snake2, direction = direct1, force_mouth_open = collided)
	if not snake2_lost:
		snake2.draw(enemy_snake = snake1, direction = direct2, force_mouth_open = collided)
	# draw the scores so far
	draw_text(medium_font, str(snake2_score), (10,10), (0,128,255), border=2)
	draw_text(medium_font, str(snake1_score), (block_width*screen_width-(24+24*len(str(snake1_score)))*block_width/32, 10), (255,64,64), border=2)
	# if the game is over, draw ending messages
	message_pos = (block_width*3, block_width*0)
	if (snake1_lost and snake2_lost):
		# draw pile of bones at heads
		if collided:
			screen.blit(pile_of_bones, scaled_block_location(snake1.blocks[0]))
			screen.blit(pile_of_bones, scaled_block_location(snake2.blocks[0]))
		draw_text(font, "DRAW", message_pos, (255,255,255))
	elif (snake1_lost):
		draw_text(font, "BLUE WINS", message_pos, (0,128,255))
		snake2_score += 1
	elif (snake2_lost):
		draw_text(font, "RED WINS", message_pos, (255,64,64))
		snake1_score += 1
	if (snake1_lost or snake2_lost):
		for i, end_reason in enumerate(end_reasons):
			draw_text(small_font, end_reason, (block_width*16, block_width*0+(0*100+20-20*(1 if len(end_reasons) == 2 else 0)+36*i)*block_width/32), (255,255,255), border=2)
		draw_text(small_font, "press space to continue...", (block_width, block_width*(screen_width-1.75)), (255,255,255), border=2)
	if first_loop:
		draw_text(small_font, "press space to continue...", (block_width, block_width*(screen_width-1.75)), (255,255,255), border=2)
		screen.blit(blue_controls, scaled_block_location((5,11)))
		screen.blit(red_controls, scaled_block_location((screen_width-6-8+1,11)))
	pygame.display.flip()

	# wait if its the first loop
	if first_loop:
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					waiting = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						waiting = False
						reset()
						show_intro_screen()
					if event.key == pygame.K_SPACE:
						waiting = False
						reset()
			clock.tick(10)
	first_loop = False

	# wait
	clock.tick(10)
	#clock.tick(1)

	# if game over
	if (snake1_lost or snake2_lost):
		waiting = True
		while waiting:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					waiting = False
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						waiting = False
						reset()
						show_intro_screen()
					if event.key == pygame.K_SPACE:
						waiting = False
						reset()
			clock.tick(10)
		
# Quit
pygame.quit()
