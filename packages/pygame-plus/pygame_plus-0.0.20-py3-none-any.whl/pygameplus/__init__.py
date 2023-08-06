
__version__ = "0.0.1"

# Remove PyGame load message in console
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame

pygame.init()

from pygameplus.screen import *
from pygameplus.sprite import *
from pygameplus.painter import *
from pygameplus.turtle import *
from pygameplus.event_loop import *
from pygameplus.pgputils import *

Sound = pygame.mixer.Sound
music_stream = pygame.mixer.music

__all__ = [
    'Color', 
    'Painter', 
    'Screen', 
    'Sound',
    'Sprite', 
    'Turtle', 
    'from_pygame_coordinates', 
    'get_active_screen', 
    'get_game_loop', 
    'load_picture', 
    'music_stream',
    'start_game', 
    'end_game', 
    'to_pygame_coordinates',
]