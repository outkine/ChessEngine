import pygame
from spritesheet import BlockSheet
from time import time

from main import play as play1
# from main2 import play as play2

from main import BOARD_ITERATOR
from main import EMPTY
from main import PIECE_MOVE_FUNCTIONS
from main import find_state
from main import find_type
from main import apply_move

# @formatter:off
DEFAULT_BOARD = (
    # 0         1           2           3           4           5           6           7
    ((1, 'r'), 	(1, 'n'), 	(1, 'b'), 	(1, 'q'), 	(1, 'k'), 	(1, 'b'), 	(1, 'n'), 	(1, 'r'), 	),  # 0
    ((1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	),  # 1
    ((0,),  	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	),  # 2
    ((0,),  	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	),  # 3
    ((0,),  	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	),  # 4
    ((0,),  	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	),  # 5
    ((-1, 'p'), (-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	),  # 6
    ((-1, 'r'), (-1, 'n'), 	(-1, 'b'), 	(-1, 'q'), 	(-1, 'k'), 	(-1, 'b'), 	(-1, 'n'), 	(-1, 'r'), 	),  # 7
)
# @formatter:on

PIECES = ('p', 'n', 'b', 'r', 'q', 'k')

SCALE_FACTOR = 5
FRAME_RATE = 1
PIECE_SIZE = (7, 14)
TILE_SIZE = 100
TILE_DIMENSIONS = (TILE_SIZE, TILE_SIZE)
TILE_COLORS = (None, (99, 114, 124), (160, 160, 160))
NUMBER_SCALE_FACTOR = 3
NUMBER_GAP = 25
SHOW_NUMBERS = False
PLAYER_TILE_COLOR = (174, 126, 126)

COMPUTER_SIDES = (1,)
COMPUTERS = (None, play1, None)
CONFIRM_TURN = False

DISPLAY = pygame.display.set_mode([TILE_SIZE * 8 for _ in range(2)])
SPRITE_SHEET = BlockSheet("spritesheet.png", SCALE_FACTOR, PIECE_SIZE)
PIECE_SPRITES = {}
for side in (1, -1):
    temp_sprites = SPRITE_SHEET.get_blocks(len(PIECES))
    PIECE_SPRITES[side] = {piece: temp_sprites[i] for i, piece in enumerate(PIECES)}
NUMBER_SPRITES = SPRITE_SHEET.get_custom_blocks((7, 7), 10, scale=NUMBER_SCALE_FACTOR)

def find_center(dimensions_1, dimensions_2, coordinates=(0, 0)):
    return [(coordinates[i] + (dimensions_1[i] / 2 - dimensions_2[i] / 2)) for i in range(2)]

def draw_board(display, piece_sprites, number_sprites, board, piece_tile):
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            tile_state = find_state((x, y), board)
            coordinates = (x * TILE_SIZE, y * TILE_SIZE)
            if (x, y) == piece_tile:
                color = PLAYER_TILE_COLOR
            else:
                if (x - y) % 2 == 0:
                    color = TILE_COLORS[-1]
                else:
                    color = TILE_COLORS[1]
            pygame.draw.rect(display, color, (coordinates, TILE_DIMENSIONS))
            if SHOW_NUMBERS:
                display.blit(number_sprites[x], coordinates)
                display.blit(number_sprites[y], (coordinates[0] + NUMBER_GAP, coordinates[1]))

            if tile_state != EMPTY:
                sprite = piece_sprites[tile_state][find_type((x, y), board)]
                display.blit(sprite, find_center(TILE_DIMENSIONS, sprite.get_size(), coordinates))

times = [None, None, None]

def run(board, side, turn):
    current_time = time()
    board = COMPUTERS[side](board, side, side)
    times[side] = time() - current_time
    # print("##############################################")
    turn, side = update(turn, side)
    return board, side, turn

def update(turn, side):
    return turn + 1, side * -1

def convert_to_grid(coordinates):
    return [int(coordinate / TILE_SIZE) for coordinate in coordinates]

def main():
    board = list(DEFAULT_BOARD)
    side = -1
    turn = 1
    # for _ in range(50):
    #     board, side, turn = run(board, side, turn)
    piece = None
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quit()

        if side in COMPUTER_SIDES:
            if not CONFIRM_TURN or pygame.key.get_pressed()[pygame.K_SPACE]:
                board, side, turn = run(board, side, turn)

        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = tuple(convert_to_grid(event.pos))
                    if find_state(pos, board) == side:
                        piece = pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if piece:
                        move = tuple(convert_to_grid(event.pos))
                        if move in PIECE_MOVE_FUNCTIONS[find_type(piece, board)](piece, board, side):
                            board = apply_move(move, piece, board, side)
                            turn, side = update(turn, side)
                        piece = None

        draw_board(DISPLAY, PIECE_SPRITES, NUMBER_SPRITES, board, piece)
        pygame.display.update()

if __name__ == '__main__':
    main()