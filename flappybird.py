#! /usr/bin/env python3

"""Flappy Bird, implemented using Pygame."""

import math
import os
from random import randint, randrange, sample
from collections import deque
import numpy as np
import pygame
from pygame.locals import *


FPS = 60
ANIMATION_SPEED = 0.8  # pixels per millisecond
WIN_WIDTH = 568    # BG image size: 284x512 px; tiled twice
WIN_HEIGHT = 512



class Bird(pygame.sprite.Sprite):
    """Represents the bird controlled by the player.

    The bird is the 'hero' of this game.  The player can make it climb
    (ascend quickly), otherwise it sinks (descends more slowly).  It must
    pass through the space in between pipes (for every pipe passed, one
    point is scored); if it crashes into a pipe, the game ends.

    Attributes:
    x: The bird's X coordinate.
    y: The bird's Y coordinate.
    msec_to_climb: The number of milliseconds left to climb, where a
        complete climb lasts Bird.CLIMB_DURATION milliseconds.

    Constants:
    WIDTH: The width, in pixels, of the bird's image.
    HEIGHT: The height, in pixels, of the bird's image.
    SINK_SPEED: With which speed, in pixels per millisecond, the bird
        descends in one second while not climbing.
    CLIMB_SPEED: With which speed, in pixels per millisecond, the bird
        ascends in one second while climbing, on average.  See also the
        Bird.update docstring.
    CLIMB_DURATION: The number of milliseconds it takes the bird to
        execute a complete climb.
    """

    WIDTH = HEIGHT = 32
    SINK_SPEED = 0
    CLIMB_SPEED = 0.8
    CLIMB_DURATION = 100

    def __init__(self, x, y, msec_to_climb, images):
        """Initialise a new Bird instance.

        Arguments:
        x: The bird's initial X coordinate.
        y: The bird's initial Y coordinate.
        msec_to_climb: The number of milliseconds left to climb, where a
            complete climb lasts Bird.CLIMB_DURATION milliseconds.  Use
            this if you want the bird to make a (small?) climb at the
            very beginning of the game.
        images: A tuple containing the images used by this bird.  It
            must contain the following images, in the following order:
                0. image of the bird with its wing pointing upward
                1. image of the bird with its wing pointing downward
        """
        super(Bird, self).__init__()
        self.x, self.y = x, y
        self.msec_to_climb = msec_to_climb
        self.msec_to_sink = 0
        self._img_wingup, self._img_wingdown = images
        self._mask_wingup = pygame.mask.from_surface(self._img_wingup)
        self._mask_wingdown = pygame.mask.from_surface(self._img_wingdown)

    def update(self, delta_frames=1):
        """Update the bird's position.

        This function uses the cosine function to achieve a smooth climb:
        In the first and last few frames, the bird climbs very little, in the
        middle of the climb, it climbs a lot.
        One complete climb lasts CLIMB_DURATION milliseconds, during which
        the bird ascends with an average speed of CLIMB_SPEED px/ms.
        This Bird's msec_to_climb attribute will automatically be
        decreased accordingly if it was > 0 when this method was called.

        Arguments:
        delta_frames: The number of frames elapsed since this method was
            last called.
        """
        if self.msec_to_climb > 0:
#            frac_climb_done = 1
            self.y -= Bird.CLIMB_SPEED * frames_to_msec(delta_frames)
            self.msec_to_climb -= frames_to_msec(delta_frames)
			
        if self.msec_to_sink > 0:
#            frac_climb_done = 1
            self.y += Bird.CLIMB_SPEED * frames_to_msec(delta_frames) 
            self.msec_to_sink -= frames_to_msec(delta_frames)
        #else:
        #   self.y += Bird.SINK_SPEED * frames_to_msec(delta_frames)

    @property
    def image(self):
        """Get a Surface containing this bird's image.

        This will decide whether to return an image where the bird's
        visible wing is pointing upward or where it is pointing downward
        based on pygame.time.get_ticks().  This will animate the flapping
        bird, even though pygame doesn't support animated GIFs.
        """
        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_wingup
        else:
            return self._img_wingdown



    @property
    def mask(self):
        """Get a bitmask for use in collision detection.

        The bitmask excludes all pixels in self.image with a
        transparency greater than 127."""
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wingup
        else:
            return self._mask_wingdown

    @property
    def rect(self):
        """Get the bird's position, width, and height, as a pygame.Rect."""
        return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):
    """Represents an obstacle.

    A PipePair has a top and a bottom pipe, and only between them can
    the bird pass -- if it collides with either part, the game is over.

    Attributes:
    x: The PipePair's X position.  This is a float, to make movement
        smoother.  Note that there is no y attribute, as it will only
        ever be 0.
    image: A pygame.Surface which can be blitted to the display surface
        to display the PipePair.
    mask: A bitmask which excludes all pixels in self.image with a
        transparency greater than 127.  This can be used for collision
        detection.
    top_pieces: The number of pieces, including the end piece, in the
        top pipe.
    bottom_pieces: The number of pieces, including the end piece, in
        the bottom pipe.

    Constants:
    WIDTH: The width, in pixels, of a pipe piece.  Because a pipe is
        only one piece wide, this is also the width of a PipePair's
        image.
    PIECE_HEIGHT: The height, in pixels, of a pipe piece.
    ADD_INTERVAL: The interval, in milliseconds, in between adding new
        pipes.
    """

    WIDTH = 100
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 500

    def __init__(self, pipe_end_img, pipe_body_img):
        """
        Initialises a new random PipePair.

        The new PipePair will automatically be assigned an x attribute of
        float(WIN_WIDTH - 1).

        Arguments:
        pipe_end_img: The image to use to represent a pipe's end piece.
        pipe_body_img: The image to use to represent one horizontal slice
            of a pipe's body.
        """
        self.x = float(WIN_WIDTH - 1)
        # self.y = randint(0,2) * 87 + 40
        self.score_counted = False
        self.mul_pipe = randint(1,2)

        self.image = pygame.Surface((PipePair.WIDTH, WIN_HEIGHT), SRCALPHA)
        self.image.convert()   # speeds up blitting
        self.image.fill((0, 0, 0, 0))
       
        self.bottom_pieces = 1
        #self.top_pieces = total_pipe_body_pieces - self.bottom_pieces

        #  Add obstacle
        atr_lst = []
        a = sample(range(0, 3),2)
        y = [i * 87 + 40 for i in a]
        for i in range(self.mul_pipe):
            is_bonus = True if randrange(2) % 3 == 0 else False
            if i == 0:
                piece_pos = (0, WIN_HEIGHT - PipePair.PIECE_HEIGHT - y[i])
                if is_bonus:
                    self.image.blit(pipe_body_img, piece_pos)
                    atr_lst = [["bonus",piece_pos[1]]]
                else:
                    self.image.blit(pipe_end_img, piece_pos)
                    atr_lst = [["obstacle",piece_pos[1]]]
            if i == 1:
                piece_pos = (0, WIN_HEIGHT - PipePair.PIECE_HEIGHT - y[i])
                if is_bonus:
                    self.image.blit(pipe_body_img, piece_pos)
                    atr_lst.append(["bonus",piece_pos[1]])
                else:
                    self.image.blit(pipe_end_img, piece_pos)
                    atr_lst.append(["obstacle",piece_pos[1]])
        self.atr = atr_lst
        

        # compensate for added end pieces
        # self.top_pieces += 1
        self.bottom_pieces += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):
        """Get the top pipe's height, in pixels."""
        return self.top_pieces * PipePair.PIECE_HEIGHT

    @property
    def bottom_height_px(self):
        """Get the bottom pipe's height, in pixels."""
        return self.bottom_pieces * PipePair.PIECE_HEIGHT

    @property
    def visible(self):
        """Get whether this PipePair on screen, visible to the player."""
        return -PipePair.WIDTH < self.x < WIN_WIDTH

    @property
    def rect(self):
        """Get the Rect which contains this PipePair."""
        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        """Update the PipePair's position.

        Arguments:
        delta_frames: The number of frames elapsed since this method was
            last called.
        """
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, bird):
        """Get whether the bird collides with a pipe in this PipePair.

        Arguments:
        bird: The Bird which should be tested for collision with this
            PipePair.
        """
        return pygame.sprite.collide_mask(self, bird)


def load_images():
    """Load all images required by the game and return a dict of them.

    The returned dict has the following keys:
    background: The game's background image.
    bird-wingup: An image of the bird with its wing pointing upward.
        Use this and bird-wingdown to create a flapping bird.
    bird-wingdown: An image of the bird with its wing pointing downward.
        Use this and bird-wingup to create a flapping bird.
    pipe-end: An image of a pipe's end piece (the slightly wider bit).
        Use this and pipe-body to make pipes.
    pipe-body: An image of a slice of a pipe's body.  Use this and
        pipe-body to make pipes.
    """

    def load_image(img_file_name):
        """Return the loaded pygame image with the specified file name.

        This function looks for images in the game's images folder
        (./images/).  All images are converted before being returned to
        speed up blitting.

        Arguments:
        img_file_name: The file name (including its extension, e.g.
            '.png') of the required image, without a file path.
        """
        file_name = os.path.join('.', 'images', img_file_name)
        #file_name = "/Users/ryanhuang/Desktop/107-2/FIN programming/PBC-final-project/images/" + img_file_name
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'background': load_image('ntu_background.png'),
            'pipe-end': load_image('pipe_end.png'),
            'pipe-body': load_image('pipe_body.png'),
            # images for animating the flapping bird -- animated GIFs are
            # not supported in pygame
            'bird_origin': load_image('bird_origin1.png'),
            'bird-run': load_image('bird-run1.png')}

def frames_to_msec(frames, fps=FPS):
    """Convert frames to milliseconds at the specified framerate.

    Arguments:
    frames: How many frames to convert to milliseconds.
    fps: The framerate to use for conversion.  Default: FPS.
    """
    return 1000.0 * frames / fps


def msec_to_frames(milliseconds, fps=FPS):
    """Convert milliseconds to frames at the specified framerate.

    Arguments:
    milliseconds: How many milliseconds to convert to frames.
    fps: The framerate to use for conversion.  Default: FPS.
    """
    return fps * milliseconds / 1000.0

def welcomeScr(disp):
    WHITE = pygame.Color(255, 255, 255)
    SLOWMOTION = 7
    tictoc = pygame.time.Clock()
    NAVYBLUE = pygame.Color(113, 197, 207)
    SIZE_ALPHA = 64
    MAGIC_NUMBER = 40
    f = open('score.txt')
    last_score = int(f.readline())
    highscore = f.readline()
    highscore = int(highscore[11:])

    imgObj = pygame.image.load('images/bird_origin2.png')
    fontObj = pygame.font.Font('fonts/VIDEOPHREAK.ttf', SIZE_ALPHA)
    font2Obj = pygame.font.Font('fonts/gooddp.ttf', 32)
    font3Obj = pygame.font.Font('freesansbold.ttf', 32)
    enter = font2Obj.render('Press Enter to play!!!', True, WHITE)
    score = font3Obj.render('Highscore: %d     Lastscore: %d' %(highscore, last_score), True, WHITE)
    mode = 0
    Flappy = []
    Flappy_rec = []
    ALPHA_Y = WIN_HEIGHT / 2
    ALPHA_X_INI = WIN_WIDTH / 2 - (len('NTU Dumbird') / 2)* MAGIC_NUMBER
    birdx, birdy = WIN_WIDTH / 3, WIN_HEIGHT / 8
    CHECK = 0
    BLINKER = 0
    for c, i in zip('NTU Dumbird', range(len('NTU Dumbird'))):
        charObj = fontObj.render(c, True, colorify(i))
        Flappy.append(charObj)
        Flappy_rec.append(Flappy[i].get_rect())
        Flappy_rec[i].center = (ALPHA_X_INI + i * MAGIC_NUMBER , ALPHA_Y - 100)
    while True:
        disp.fill(NAVYBLUE)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_RETURN:
                return True
        for i in range(len('NTU Dumbird')):
            disp.blit(Flappy[i], Flappy_rec[i].center)
        if mode == 0:
            disp.blit(imgObj, (birdx + CHECK, birdy + CHECK))
            CHECK += 3
            if CHECK >= 20:
                mode = 1
        elif mode == 1:
            disp.blit(imgObj, (birdx + CHECK, birdy + CHECK))
            CHECK -= 3
            if CHECK <= -20:
                mode = 0

        if BLINKER == 0:
            BLINKER = 1
        else:
            disp.blit(enter, (WIN_WIDTH / 2, WIN_HEIGHT / 2 + 30 ))
            BLINKER = 0
        disp.blit(score, (50, 400))
        tictoc.tick(SLOWMOTION)
        pygame.display.update()

def gameoverScr(disp):
    WHITE = pygame.Color(255, 255, 255)
    SLOWMOTION = 7
    tictoc = pygame.time.Clock()
    NAVYBLUE = pygame.Color(113, 197, 207)
    SIZE_ALPHA = 64
    MAGIC_NUMBER = 40
    f = open('score.txt')
    last_score = int(f.readline())
    highscore = f.readline()
    highscore = int(highscore[11:])

    imgObj = pygame.image.load('images/wind_down1.png')
    fontObj = pygame.font.Font('fonts/VIDEOPHREAK.ttf', SIZE_ALPHA)
    font2Obj = pygame.font.Font('fonts/gooddp.ttf', 32)
    font3Obj = pygame.font.Font('freesansbold.ttf', 32)
    enter = font2Obj.render('Press Enter to play!!!', True, WHITE)
    score = font3Obj.render('Highscore: %d     Lastscore: %d' %(highscore, last_score), True, WHITE)
    mode = 0
    Flappy = []
    Flappy_rec = []
    ALPHA_Y = WIN_HEIGHT / 2
    ALPHA_X_INI = WIN_WIDTH / 2 - (len('GAME OVER') / 2)* MAGIC_NUMBER
    birdx, birdy = WIN_WIDTH / 3, WIN_HEIGHT / 8
    CHECK = 0
    BLINKER = 0
    for c, i in zip('GAME OVER', range(len('GAME OVER'))):
        charObj = fontObj.render(c, True, colorify(i))
        Flappy.append(charObj)
        Flappy_rec.append(Flappy[i].get_rect())
        Flappy_rec[i].center = (ALPHA_X_INI + i * MAGIC_NUMBER , ALPHA_Y - 100)
    while True:
        disp.fill(NAVYBLUE)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return True
        for i in range(len('GAME OVER')):
            disp.blit(Flappy[i], Flappy_rec[i].center)
        if mode == 0:
            disp.blit(imgObj, (birdx + CHECK, birdy + CHECK))
            CHECK += 3
            if CHECK >= 20:
                mode = 1
        elif mode == 1:
            disp.blit(imgObj, (birdx + CHECK, birdy + CHECK))
            CHECK -= 3
            if CHECK <= -20:
                mode = 0


        if BLINKER == 0:
            BLINKER = 1
        else:
            disp.blit(enter, (WIN_WIDTH / 2, WIN_HEIGHT / 2 + 30 ))
            BLINKER = 0
        disp.blit(score, (50, 400))
        tictoc.tick(SLOWMOTION)
        pygame.display.update()
		
def colorify(i):
    RED = pygame.Color(255, 0, 0)
    GREEN = pygame.Color(0, 255, 0)
    PURPLE = pygame.Color(158, 9, 182)
    YELLOW = pygame.Color(255, 255, 0)
    ORANGE = pygame.Color(255, 128, 0)
    PINK = pygame.Color(255, 0, 255)
    lis = [RED, GREEN, PURPLE, YELLOW, ORANGE, PINK, RED, GREEN, PURPLE, YELLOW, ORANGE, PINK]
    return lis[i]

def redrawWindow(backgroundPic, firstPicPos , secondPicPos , win): #用來架設背景，blit設定背景位置
	win.blit(backgroundPic , (firstPicPos, 0))
	win.blit(backgroundPic , (secondPicPos, 0))
	
	
def main():
    """The application's entry point.

    If someone executes this module (instead of importing it, for
    example), this function is called.
    """

    pygame.init()
    try:
        open('score.txt')
    except IOError:
        dummy = open('score.txt', 'w')
        dummy.write('0\nHighscore: 0')
        dummy.close()

    display_surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Pygame Flappy Bird')

    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont(None, 32, bold=True)  # default font
    images = load_images()

    # the bird stays in the same x position, so bird.x is a constant
    # center bird on screen
    bird = Bird(30, int(WIN_HEIGHT* 3/4)-30, 2,
                (images['bird_origin'], images['bird-run']))

    pipes = deque()

    frame_clock = 0  # this counter is only incremented if the game isn't paused
    score = 0
    position = 1
    speedPlus = 1
    bgSpeed = 3
    bg = images['background'] #儲存background圖片，背景用同一張圖片重複出現
    bgX = 0					  #第一張圖片的位置為零
    bgX2 = bg.get_width()     #第二張圖片的位置為前一張的寬度之後
	
    done = paused = False
    welcomeScr(display_surface) #開始介面
    while not done:
        redrawWindow(bg, bgX, bgX2 , display_surface) #架設背景
        clock.tick(FPS)

        bgX -= bgSpeed								  #第一張背景的位置會0 - 1.4，一直減下去，背景就會一直往左走
        bgX2 -= bgSpeed								  #同上
        if bgX < bg.get_width() * -1:				  #如果第一張背景的位置跑到負的背景圖寬度，代表背景完全跑到視窗左側，把第一張背景位置重新設為右側(圖片寬度位置)
            bgX = bg.get_width()
        if bgX2 < bg.get_width() * -1:				  #同上
            bgX2 = bg.get_width()

        # Handle this 'manually'.  If we used pygame.time.set_timer(),
        # pipe addition would be messed up when paused.
        if not (paused or frame_clock % msec_to_frames(PipePair.ADD_INTERVAL)):
            pp = PipePair(images['pipe-end'], images['pipe-body'])
            pipes.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == KEYDOWN and e.key == K_UP:
                if position != 2:	
                    bird.msec_to_climb = Bird.CLIMB_DURATION
                    position +=1
            elif e.type == KEYDOWN and e.key == K_DOWN:
                if position != 0:
                    bird.msec_to_sink = Bird.CLIMB_DURATION
                    position -=1
        if paused:
            continue  # don't draw anything

        # check for collisions
        #pipe_collision = any(p.collides_with(bird) for p in pipes)
        for p in pipes:
            if p.collides_with(bird) :
                #print(p.atr)
                #print(bird.y)
                col_atr = p.atr[np.argmin([abs(bird.y - atr[1]) for atr in p.atr])][0]
                if col_atr == "bonus":
                    score += 1
                    p.score_counted = True
                else:
                    done = True
					
        if score % 10 == 1 :    #每得到10分，會加速一點
            global ANIMATION_SPEED 
            ANIMATION_SPEED += 0.001 #每10分，障礙物速度加0.001
            bgSpeed += 0.05			 #每10分，背景速度增加1

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WIN_WIDTH/2 - score_surface.get_width()/2
        display_surface.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
    print('Game over! Score: %i' % score)
    rea = open('score.txt')
    scorelasttime = rea.readline()
    highscore = rea.readline()
    highscore = int(highscore[11:])
    wri = open('score.txt', 'w')
    if highscore < score:
        wri.write("%d\nHighscore: %d" %(score, score))
    else:
        wri.write("%d\nHighscore: %d" %(score, highscore))
    
    rea.close()
    wri.close()
    gameoverScr(display_surface)
    if gameoverScr(display_surface) == True:
        main()
    #pygame.quit()


if __name__ == '__main__':
    # If this module had been imported, __name__ would be 'flappybird'.
    # It was executed (e.g. by double-clicking the file), so call main.
    main()
