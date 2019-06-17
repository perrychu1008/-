#! /usr/bin/env python3

"""NTU DUMB Bird, implemented using Pygame."""

import os
from random import randint, randrange, sample
from collections import deque
import numpy as np
import pygame
from pygame.locals import *

#Setting
FPS = 60
ANIMATION_SPEED = 0.6  # pixels per millisecond
WIN_WIDTH = 568    # BG image size: 284x512 px; tiled twice
WIN_HEIGHT = 512


class Bird(pygame.sprite.Sprite):

    WIDTH = HEIGHT = 32 #The width and height of the bird's image.
    MOVE_SPEED = 0.8 #With which speed, in pixels per millisecond
    MOVE_DURATION = 100 #The number of milliseconds it takes the bird to execute a complete Move.

    def __init__(self, x, y, msec_to_move, images):

        super(Bird, self).__init__()
        self.x, self.y = x, y
        self.msec_to_move = msec_to_move
        self.msec_to_sink = 0
        self._img_wingup, self._img_wingdown = images
        self._mask_wingup = pygame.mask.from_surface(self._img_wingup)
        self._mask_wingdown = pygame.mask.from_surface(self._img_wingdown)

    def update(self, delta_frames=1):

        if self.msec_to_move > 0:
            self.y -= Bird.MOVE_SPEED * frames_to_msec(delta_frames)
            self.msec_to_move -= frames_to_msec(delta_frames)
			
        if self.msec_to_sink > 0:
            self.y += Bird.MOVE_SPEED * frames_to_msec(delta_frames) 
            self.msec_to_sink -= frames_to_msec(delta_frames)

    @property
    def image(self):

        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_wingup
        else:
            return self._img_wingdown

    @property
    def mask(self):
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wingup
        else:
            return self._mask_wingdown

    @property
    def rect(self):
        return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):
    """Represents an obstacle.

    A PipePair has a top and a bottom pipe, and only between them can
    the bird pass -- if it collides with either part, the game is over.

    Attributes:
    x: The PipePair's X position.  This is a float, to make Movement
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
    global ADD_INTERVAL
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

    def load_image(img_file_name):
        file_name = os.path.join('.', 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'startscr': load_image('ntudb_cover.png'),
            'ggscr': load_image('GAMEOVER.png'),
            'background1': load_image('ntu_background_1.png'),
            'background2': load_image('ntu_background_2.png'),
            'pipe-end': load_image('pipe_end.png'),
            'pipe-body': load_image('pipe_body.png'),
            'bird_origin': load_image('bird_origin1.png'),
            'bird-run': load_image('bird-run1.png')}

def frames_to_msec(frames, fps=FPS):
    return 1000.0 * frames / fps

def msec_to_frames(milliseconds, fps=FPS):
    return fps * milliseconds / 1000.0

def welcomeScr(disp, pic):
    NAVYBLUE = pygame.Color(100, 150, 255)
    SLOWMOTION = 7
    tictoc = pygame.time.Clock()
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
    enter = font2Obj.render('Press Enter to play!!!', True, NAVYBLUE)
    score = font3Obj.render('Highscore: %d     Lastscore: %d' %(highscore, last_score), True, NAVYBLUE)
    mode = 0
    Flappy = []
    Flappy_rec = []
 
    birdx, birdy = WIN_WIDTH / 2, WIN_HEIGHT / 8
    CHECK = 0
    BLINKER = 0
    while True:
        disp.blit(pic, (0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP and event.key == K_RETURN:
                return True

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
            disp.blit(enter, (WIN_WIDTH / 2, WIN_HEIGHT / 2 + 200  ))
            BLINKER = 0
        disp.blit(score, (50, 400))
        tictoc.tick(SLOWMOTION)
        pygame.display.update()

def gameoverScr(disp, pic):
    NAVYBLUE = pygame.Color(100, 150, 255)
    SLOWMOTION = 7
    tictoc = pygame.time.Clock()
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
    enter = font2Obj.render('Press Enter to Continue!!!', True, NAVYBLUE)
    enter2 = font2Obj.render('Press Esc to Quit!!!', True, NAVYBLUE)
    score = font3Obj.render('Highscore: %d     Lastscore: %d' %(highscore, last_score), True, NAVYBLUE)
    mode = 0
    Flappy = []
    Flappy_rec = []

    birdx, birdy = WIN_WIDTH / 3, WIN_HEIGHT / 8
    CHECK = 0
    BLINKER = 0

    while True:
        disp.blit(pic, (0,0))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return True

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

        disp.blit(enter, (WIN_WIDTH / 2, WIN_HEIGHT / 2 + 200 ))
        disp.blit(enter2, (50, WIN_HEIGHT / 2 + 200 ))
        
        disp.blit(score, (50, 400))
        tictoc.tick(SLOWMOTION)
        pygame.display.update()

def redrawWindow(backgroundPic1, backgroundPic2, firstPicPos , secondPicPos , win): #用來架設背景，blit設定背景位置
	win.blit(backgroundPic1 , (firstPicPos, 0))
	win.blit(backgroundPic2 , (secondPicPos, 0))
	
	
def main(welcome = 0):
    """The application's entry point.

    If someone executes this module (instead of importing it, for
    example), this function is called.
    """
    global FPS
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

    bird = Bird(30, int(WIN_HEIGHT* 3/4)-30, 2,
                (images['bird_origin'], images['bird-run']))

    pipes = deque()

    frame_clock = 0  # this counter is only incremented if the game isn't paused
    score = 0
    position = 1
    speedPlus = 1
    bgSpeed = 3
    bg1 = images['background1'] #儲存background圖片，背景用同一張圖片重複出現
    bg2 = images['background2'] #儲存background圖片，背景用同一張圖片重複出現
    bgX = 0					    #第一張圖片的位置為零
    bgX2 = bg1.get_width()      #第二張圖片的位置為前一張的寬度之後
	
    done = paused = False
    if welcome == 0:
        start_screen = images['startscr'] #儲存background圖片，背景用同一張圖片重複出現
        welcomeScr(display_surface, start_screen) #開始介面
    while not done:
        redrawWindow(bg1, bg2, bgX, bgX2 , display_surface) #架設背景
        clock.tick(FPS)

        bgX -= bgSpeed								  #第一張背景的位置會0 - 1.4，一直減下去，背景就會一直往左走
        bgX2 -= bgSpeed								  #同上
        if bgX < bg1.get_width() * -1:				  #如果第一張背景的位置跑到負的背景圖寬度，代表背景完全跑到視窗左側，把第一張背景位置重新設為右側(圖片寬度位置)
            bgX = bg1.get_width()
        if bgX2 < bg2.get_width() * -1:				  #同上
            bgX2 = bg2.get_width()

        # Handle this 'manually'.  If we used pygame.time.set_timer(),
        # pipe addition would be messed up when paused.
        if not (paused or frame_clock % msec_to_frames(ADD_INTERVAL)):
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
                    bird.msec_to_move = Bird.MOVE_DURATION
                    position +=1
            elif e.type == KEYDOWN and e.key == K_DOWN:
                if position != 0:
                    bird.msec_to_sink = Bird.MOVE_DURATION
                    position -=1
        if paused:
            continue  # don't draw anything

        for p in pipes:
            if p.collides_with(bird) :
                col_atr = p.atr[np.argmin([abs(bird.y - atr[1]) for atr in p.atr])][0]
                if col_atr == "bonus":
                    score += 3
                    p.score_counted = True
                    p.atr[np.argmin([abs(bird.y - atr[1]) for atr in p.atr])][0] = 'None' #將原本紀錄成bonus改成none，讓鬆餅碰一下只加一分
                elif col_atr == "None":													  #所以遇到替代bonus的None，不會做任何事
                    pass
                else:
                    done = True
            if p.x + PipePair.WIDTH < bird.x and not p.score_counted:
                score += 1
                p.score_counted = True		
        if score % 10 == 1 :    #每得到10分，會加速一點
            global ANIMATION_SPEED
            ANIMATION_SPEED += 0.001 #每10分，障礙物速度加0.001
            FPS += 10
            bgSpeed += 0.05			 #每10分，背景速度增加1

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            display_surface.blit(p.image, p.rect)

        bird.update()
        display_surface.blit(bird.image, bird.rect)

        score_surface = score_font.render(str(score), True, (0, 0, 0))
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
    gameover_screen = images['ggscr'] #儲存background圖片，背景用同一張圖片重複出現
    if gameoverScr(display_surface, gameover_screen) == True:
        ANIMATION_SPEED = 0.6
        main(1)


if __name__ == '__main__':
    main()
