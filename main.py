import pygame
from spritesheet import BlockSheet
from math import log, sqrt

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
BROAD_CENTER = {(2, 2), (3, 2), (4, 2), (5, 2),
                (2, 3), (5, 3),
                (2, 4), (5, 4),
                (2, 5), (3, 5), (4, 5), (5, 5)}
CENTER = {(3, 3), (3, 4), (4, 3), (4, 4)}
PAWN_STARTS = (None, 1, 6)

ACQUIRE_BONUS = 5
BROAD_CENTER_BONUS = 1
CENTER_BONUS = 2
LIGHT_OPENING_BONUS = 1
KING_BONUS = 2

PIECES = ('p', 'n', 'b', 'r', 'q', 'k')
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
PIECE_POINTS = {key: PIECE_VALUES[key] * ACQUIRE_BONUS for key in PIECE_VALUES}

SCALE_FACTOR = 5
BACKGROUND_COLOR = (255, 255, 255)
FRAME_RATE = 1
PIECE_SIZE = (7, 14)
TILE_SIZE = 120
MARGIN = 20
NUMBER_SCALE_FACTOR = 2
NUMBER_GAP = 20

def find_turn_ratio(turn):
    if turn > 9:
        return 0
    else:
        return round(log(turn * -1 + 10, 10), 2)

def distance(pos1, pos2):
    return sqrt((pos2[1] - pos1[1]) ** 2 + (pos2[0] - pos1[0]) ** 2)

def find_state(pos, board):
    return board[pos[1]][pos[0]][0]

def find_type(pos, board):
    return board[pos[1]][pos[0]][1]

def within_bounds(pos):
    if 0 <= pos[0] < BOARD_SIZE and 0 <= pos[1] < BOARD_SIZE:
        return True
    return False

def safe_find_state(pos, board):
    if within_bounds(pos):
        return board[pos[1]][pos[0]][0]
    return BORDER

def pawn_move(loc, board, side):
    moves = []
    for x in (-1, 1):
        pos = (x + loc[0], side + loc[1])
        if safe_find_state(pos, board) == side * -1:
            moves.append(pos)
    pos = (loc[0], loc[1] + side)
    if safe_find_state(pos, board) == EMPTY:
        moves.append(pos)
        if loc[1] == PAWN_STARTS[side]:
            pos = (loc[0], loc[1] + 2 * side)
            if find_state(pos, board) == EMPTY:
                moves.append(pos)
    return moves

def pawn_attack(loc, board, side):
    return [(x + loc[0], side + loc[1]) for x in (-1, 1)]

def jump_piece_move(loc, board, side, vectors):
    moves = []
    for vector in vectors:
        pos = (loc[0] + vector[0], loc[1] + vector[1])
        if safe_find_state(pos, board) not in (BORDER, side):
            moves.append(pos)
    return moves

def knight_move(loc, board, side):
    return jump_piece_move(loc, board, side, KNIGHT_VECTORS)

def king_move(loc, board, side):
    return jump_piece_move(loc, board, side, KING_VECTORS)

def jump_piece_attack(loc, vectors):
    attacks = []
    for vector in vectors:
        pos = (loc[0] + vector[0], loc[1] + vector[1])
        if within_bounds(pos):
            attacks.append(pos)
    return attacks

def knight_attack(loc, board, side):
    return jump_piece_attack(loc, KNIGHT_VECTORS)

def king_attack(loc, board, side):
    return jump_piece_attack(loc, KING_VECTORS)

def vector_piece_move(loc, board, side, vectors):
    moves = []
    for vector in vectors:
        pos = loc
        while True:
            pos = (pos[0] + vector[0], pos[1] + vector[1])
            tile_state = safe_find_state(pos, board)
            if tile_state in (BORDER, side):
                break
            moves.append(pos)
            if tile_state != EMPTY:
                break
    return moves

def bishop_move(loc, board, side):
    return vector_piece_move(loc, board, side, BISHOP_VECTORS)

def rook_move(loc, board, side):
    return vector_piece_move(loc, board, side, ROOK_VECTORS)

def queen_move(loc, board, side):
    return bishop_move(loc, board, side) + rook_move(loc, board, side)

def vector_piece_attack(loc, board, vectors):
    attacks = []
    for vector in vectors:
        pos = loc
        while True:
            pos = (pos[0] + vector[0], pos[1] + vector[1])
            tile_state = safe_find_state(pos, board)
            if tile_state == BORDER:
                break
            attacks.append(pos)
            if tile_state != EMPTY:
                break
    return attacks

def bishop_attack(loc, board, side):
    return vector_piece_attack(loc, board, BISHOP_VECTORS)

def rook_attack(loc, board, side):
    return vector_piece_attack(loc, board, ROOK_VECTORS)

def queen_attack(loc, board, side):
    return bishop_attack(loc, board, side) + rook_attack(loc, board, side)

PIECE_MOVE_FUNCTIONS = {'p': pawn_move, 'n': knight_move, 'b': bishop_move, 'r': rook_move, 'q': queen_move, 'k': king_move}
PIECE_ATTACK_FUNCTIONS = {'p': pawn_attack, 'n': knight_attack, 'b': bishop_attack, 'r': rook_attack, 'q': queen_attack, 'k': king_attack}

def analyze_movement(move, origin, piece_type, piece_points, turn_ratio, king, distance_to_king):
    print(move, ': ', end='')
    points = 0
    if piece_type in ('p', 'n', 'b'):
        points += turn_ratio * LIGHT_OPENING_BONUS
        print("light opening bonus, ", end='')
        if origin not in CENTER and move in CENTER:
            points += CENTER_BONUS
            print("center bonus, ", end='')
        elif origin not in BROAD_CENTER and move in BROAD_CENTER:
            points += BROAD_CENTER_BONUS
            print("broad center bonus, ", end='')
    new_distance = distance(move, king)
    if new_distance < distance_to_king:
        points += KING_BONUS
        print("king bonus, ", end='')
    return points

def analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points):
    points = 0
    tile_state = find_state(move, board)
    if tile_state != EMPTY:
        print("acquire bonus, ", end='')
        points += PIECE_POINTS[find_type(move, board)]

    enemy_number = len(enemy_attacks.get(move, []))
    if enemy_number > 0:
        if piece_points > min(PIECE_POINTS[find_type(enemy, board)] for enemy in enemy_attacks[move]):
            points -= piece_points
            print("death penalty 1", end='')
        elif len(ally_attacks.get(move, [])) <= enemy_number:
            points -= piece_points
            print("death penalty 2", end='')
    return points

def analyze_move_source(move, origin, board, side, ally_stoppers, enemy_moves):
    return 0

def apply_move(move, origin, board, side):
    board[move[1]][move[0]] = (side, find_type(origin, board))
    board[origin[1]][origin[0]] = (EMPTY,)

def play(board, side, turn):
    turn_ratio = find_turn_ratio(turn)
    enemy_attacks = {}
    ally_attacks = {}
    ally_moves = {}
    enemy_king = None
    for i_side in (side * -1, side):
        for y in BOARD_ITERATOR:
            for x in BOARD_ITERATOR:
                if find_state((x, y), board) == i_side:
                    piece_type = find_type((x, y), board)
                    if i_side == side:
                        moves = PIECE_MOVE_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if moves:
                            ally_moves[(x, y)] = moves
                        attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if attacks:
                            for attack in attacks:
                                ally_attacks.setdefault(attack, []).append((x, y))
                    else:
                        attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if attacks:
                            for attack in attacks:
                                enemy_attacks.setdefault(attack, []).append((x, y))
                        if piece_type == 'k':
                            enemy_king = (x, y)

    print(turn, turn_ratio)
    print("ally")
    print(ally_attacks)
    print("enemy")
    print(enemy_attacks)
    print("moves")
    print(ally_moves)


    all_points = {}
    for (x, y) in ally_moves:
        piece_type = find_type((x, y), board)
        piece_points = PIECE_POINTS[piece_type]
        distance_to_king = distance((x, y), enemy_king)
        print(piece_type, piece_points, (x, y), ":")
        temp_points = {}
        for move in ally_moves[(x, y)]:
            points = analyze_movement(move, (x, y), piece_type, piece_points, turn_ratio, enemy_king, distance_to_king)
            points += analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points)
            print(points)
            temp_points[points] = move
        max_points = max(temp_points)
        print(temp_points[max_points], max_points)
        ally_moves[(x, y)] = temp_points[max_points]
        points = analyze_move_source(move, (x, y), board, side, ally_attacks, enemy_attacks) + max_points
        all_points[points] = (x, y)

    final_piece = all_points[max(all_points)]
    apply_move(ally_moves[final_piece], final_piece, board, side)
    print("#################################")

def draw_board(display, piece_sprites, number_sprites, board):
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            coordinates = (x * TILE_SIZE + MARGIN, y * TILE_SIZE + MARGIN)
            display.blit(number_sprites[x], coordinates)
            display.blit(number_sprites[y], (coordinates[0] + NUMBER_GAP, coordinates[1]))
            tile_state = find_state((x, y), board)
            if tile_state != EMPTY:
                sprite = piece_sprites[tile_state][find_type((x, y), board)]
                display.blit(sprite, coordinates)

def main():
    display = pygame.display.set_mode([TILE_SIZE * 8 + MARGIN * 2 for _ in range(2)])
    sprite_sheet = BlockSheet("spritesheet.png", SCALE_FACTOR, PIECE_SIZE)
    piece_sprites = {}
    for side in (1, -1):
        temp_sprites = sprite_sheet.get_blocks(len(PIECES))
        piece_sprites[side] = {piece: temp_sprites[i] for i, piece in enumerate(PIECES)}
    number_sprites = sprite_sheet.get_custom_blocks((7, 7), 10, scale=NUMBER_SCALE_FACTOR)
    board = list(DEFAULT_BOARD)

    side = -1
    turn = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if side == -1:
                    turn += 1
                play(board, side, turn)
                side *= -1
        display.fill(BACKGROUND_COLOR)
        draw_board(display, piece_sprites, number_sprites, board)
        pygame.display.update()

if __name__ == '__main__':
    main()
