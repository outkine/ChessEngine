import pygame
from spritesheet import BlockSheet

# @formatter:off
DEFAULT_BOARD = [
    # 0         1           2           3           4           5           6           7
    [(1, 'r'), 	(1, 'n'), 	(1, 'b'), 	(1, 'q'), 	(1, 'k'), 	(1, 'b'), 	(1, 'n'), 	(1, 'r'), 	],  # 0
    [(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	],  # 1
    [(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	],  # 2
    [(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	],  # 3
    [(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	],  # 4
    [(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	(0, 0), 	],  # 5
    [(-1, 'p'), (-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	(-1, 'p'), 	],  # 6
    [(-1, 'r'), (-1, 'n'), 	(-1, 'b'), 	(-1, 'q'), 	(-1, 'k'), 	(-1, 'b'), 	(-1, 'n'), 	(-1, 'r'), 	],  # 7
]
# @formatter:on

BOARD_SIZE = 8  
BOARD_ITERATOR = range(BOARD_SIZE)
EMPTY = 0
BORDER = 2
KNIGHT_VECTORS = ((-1, -2), (1, -2),
                  (2, -1), (2, 1),
                  (-1, 2), (1, 2),
                  (-2, -1), (-2, 1))
KING_VECTORS = ((-1, -1), (0, -1), (1, -1),
                (0, -1), (0, 1),
                (-1, 1), (0, 1), (1, 1))
BISHOP_VECTORS = ((-1, -1), (-1, 1), (1, 1), (1, -1))
ROOK_VECTORS = ((-1, 0), (1, 0), (0, -1), (0, 1))
BROAD_CENTER = {(3, 3), (4, 3), (5, 3), (6, 3),
                (3, 4), (4, 4), (5, 4), (6, 4),
                (3, 5), (4, 5), (5, 5), (6, 5),
                (3, 6), (4, 6), (5, 6), (6, 6)}
CENTER = {(4, 4), (5, 4), (4, 5), (5, 5)}
PAWN_STARTS = (None, 1, 6)

ACQUIRE_BONUS = 4
BROAD_CENTER_BONUS = 1
CENTER_BONUS = 2
KING_BONUS = 2

PIECES = ('p', 'n', 'b', 'r', 'q', 'k')
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
PIECE_POINTS = {key: PIECE_VALUES[key] * ACQUIRE_BONUS for key in PIECE_VALUES}

SCALE_FACTOR = 3
BACKGROUND_COLOR = (255, 255, 255)
FRAME_RATE = 1
PIECE_SIZE = (7, 14)
TILE_SIZE = 43
MARGIN = 20

def find_state(pos, board):
    return board[pos[1]][pos[0]][0]

def find_type(pos, board):
    return board[pos[1]][pos[0]][1]

def safe_find_state(pos, board):
    if 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE:
        return board[pos[1]][pos[0]][0]
    return BORDER

def pawn(loc, board, side):
    moves = []
    stoppers = []
    for x in (-1, 1):
        pos = (x + loc[0], side + loc[1])
        if safe_find_state(pos, board) == side * -1:
            moves.append(pos)
    pos = (loc[0], loc[1] + side)
    tile_state = safe_find_state(pos, board)
    if tile_state == EMPTY:
        moves.append(pos)
        if loc[1] == PAWN_STARTS[side]:
            pos = (loc[0], loc[1] + 2 * side)
            tile_state = find_state(pos, board)
            if tile_state == EMPTY:
                moves.append(pos)
            elif tile_state == side:
                stoppers.append(pos)
    elif tile_state == side:
        stoppers.append(pos)

    return moves, stoppers

def jump_piece(loc, board, side, vectors):
    moves = []
    stoppers = []
    opposite_side = side * -1
    for vector in vectors:
        pos = (loc[0] + vector[0], loc[1] + vector[1])
        tile_state = safe_find_state(pos, board)
        if tile_state in (EMPTY, opposite_side):
            moves.append(pos)
        elif tile_state == side:
            stoppers.append(pos)
    return moves, stoppers

def knight(loc, board, side):
    return jump_piece(loc, board, side, KNIGHT_VECTORS)

def king(loc, board, side):
    return jump_piece(loc, board, side, KING_VECTORS)

def vector_piece(loc, board, side, vectors):
    moves = []
    stoppers = []
    for vector in vectors:
        pos = loc
        while True:
            pos = (pos[0] + vector[0], pos[1] + vector[1])
            tile_state = safe_find_state(pos, board)
            if tile_state in (BORDER, side):
                if tile_state == side:
                    stoppers.append(tile_state)
                break
            moves.append(pos)
            if tile_state != EMPTY:
                break
    return moves, stoppers

def bishop(loc, board, side):
    return vector_piece(loc, board, side, BISHOP_VECTORS)

def rook(loc, board, side):
    return vector_piece(loc, board, side, ROOK_VECTORS)

def queen(loc, board, side):
    bishop_moves, bishop_stoppers = bishop(loc, board, side)
    rook_moves, rook_stoppers = rook(loc, board, side)
    return bishop_moves + rook_moves, bishop_stoppers + rook_stoppers

def shallow_analyze(move, board, side):
    points = 0
    tile_state = find_state(move, board)
    if tile_state != EMPTY:
        points += PIECE_POINTS[find_type(move, board)]
    if move in CENTER:
        points += CENTER_BONUS
    elif move in BROAD_CENTER:
        points += BROAD_CENTER_BONUS
    return points

def apply_move(move, origin, board, side):
    board[move[1]][move[0]] = (side, find_type(origin, board))
    board[origin[1]][origin[0]] = (EMPTY,)

def play(board, side):
    all_moves = {}
    # stoppers = {}
    points = {}
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) == side:
                tile_type = find_type((x, y), board)
                if tile_type == 'p':
                    moves, stoppers = pawn((x, y), board, side)
                elif tile_type == 'n':
                    moves, stoppers = knight((x, y), board, side)
                elif tile_type == 'b':
                    moves, stoppers = bishop((x, y), board, side)
                elif tile_type == 'q':
                    moves, stoppers = queen((x, y), board, side)
                elif tile_type == 'r':
                    moves, stoppers = rook((x, y), board, side)
                elif tile_type == 'k':
                    moves, stoppers = king((x, y), board, side)
                if moves:
                    temp_points = {}
                    for move in moves:
                        temp_points[shallow_analyze(move, board, side)] = move
                    max_points = max(temp_points)
                    points[(x, y)] = max_points
                    all_moves[(x, y)] = temp_points[max_points]

    final_points = {}
    for x, y in all_moves:
        final_points[points[(x, y)]] = (x, y)

    final_piece = final_points[max(final_points)]
    apply_move(all_moves[final_piece], final_piece, board, side)
    return board

def draw_board(display, sprites, board):
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            tile_state = find_state((x, y), board)
            if tile_state != EMPTY:
                sprite = sprites[tile_state][find_type((x, y), board)]
                display.blit(sprite, (x * TILE_SIZE + MARGIN, y * TILE_SIZE + MARGIN))

def main():
    display = pygame.display.set_mode([TILE_SIZE * 8 + MARGIN * 2 for _ in range(2)])
    clock = pygame.time.Clock()
    sprite_sheet = BlockSheet("SpriteSheet.png", SCALE_FACTOR, PIECE_SIZE)
    sprites = {}
    for side in (1, -1):
        temp_sprites = sprite_sheet.get_blocks(len(PIECES))
        sprites[side] = {piece: temp_sprites[i] for i, piece in enumerate(PIECES)}
    board = list(DEFAULT_BOARD)

    while True:
        for side in (-1, 1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            display.fill(BACKGROUND_COLOR)
            draw_board(display, sprites, board)
            pygame.display.update()
            clock.tick(FRAME_RATE)
            board = play(board, side)

if __name__ == '__main__':
    main()
