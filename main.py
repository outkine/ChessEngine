import pygame
from spritesheet import BlockSheet
# from math import log, sqrt
from math import sqrt
from copy import deepcopy
from time import time

# @formatter:off
DEFAULT_BOARD = [
    # 0         1           2           3           4           5           6           7
    [(1, 'r'), 	(1, 'n'), 	(1, 'b'), 	(1, 'q'), 	(1, 'k'), 	(1, 'b'), 	(1, 'n'), 	(1, 'r'), 	],  # 0
    [(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	],  # 1
    [(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	],  # 2
    [(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	],  # 3
    [(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	],  # 4
    [(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	(0,),	 	],  # 5
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
SIMULATION_LEVEL = 2

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

DISPLAY = pygame.display.set_mode([TILE_SIZE * 8 + MARGIN * 2 for _ in range(2)])
SPRITE_SHEET = BlockSheet("spritesheet.png", SCALE_FACTOR, PIECE_SIZE)
PIECE_SPRITES = {}
for side in (1, -1):
    temp_sprites = SPRITE_SHEET.get_blocks(len(PIECES))
    PIECE_SPRITES[side] = {piece: temp_sprites[i] for i, piece in enumerate(PIECES)}
NUMBER_SPRITES = SPRITE_SHEET.get_custom_blocks((7, 7), 10, scale=NUMBER_SCALE_FACTOR)

# def find_turn_ratio(turn):
#     if turn > 9:
#         return 0
#     else:
#         return round(log(turn * -1 + 10, 10), 2)

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

PIECE_MOVE_FUNCTIONS = {'p': pawn_move, 'n': knight_move, 'b': bishop_move, 'r': rook_move, 'q': queen_move,
                        'k': king_move}
PIECE_ATTACK_FUNCTIONS = {'p': pawn_attack, 'n': knight_attack, 'b': bishop_attack, 'r': rook_attack, 'q': queen_attack,
                          'k': king_attack}

def analyze_movement(move, origin, piece_type, king, distance_to_king):
    # print(move, ': ', end='')
    points = 0
    if piece_type in ('p', 'n', 'b'):
        # print("light opening bonus, ", end='')
        if origin not in CENTER and move in CENTER:
            points += CENTER_BONUS
            # print("center bonus, ", end='')
        elif origin not in BROAD_CENTER and move in BROAD_CENTER:
            points += BROAD_CENTER_BONUS
            # print("broad center bonus, ", end='')
    new_distance = distance(move, king)
    if new_distance < distance_to_king:
        points += KING_BONUS
        # print("king bonus, ", end='')
    return points

def analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points):
    points = 0
    tile_state = find_state(move, board)
    if tile_state != EMPTY:
        # print("acquire bonus, ", end='')
        points += PIECE_POINTS[find_type(move, board)]

    enemy_number = len(enemy_attacks.get(move, []))
    if enemy_number > 0:
        if piece_points > min(PIECE_POINTS[find_type(enemy, board)] for enemy in enemy_attacks[move]) or len(ally_attacks.get(move, [])) <= enemy_number:
            points -= piece_points
            # print("death penalty", end='')
    return points

# def analyze_move_source(move, origin, board, side, ally_stoppers, enemy_moves):
#     return 0

def apply_move(move, origin, board, side):
    temp_board = deepcopy(board)
    temp_board[move[1]][move[0]] = (side, find_type(origin, board))
    temp_board[origin[1]][origin[0]] = (EMPTY,)
    DISPLAY.fill(BACKGROUND_COLOR)
    draw_board(DISPLAY, PIECE_SPRITES, NUMBER_SPRITES, temp_board)
    pygame.display.update()
    return temp_board

# def update_attacks_2(attacks, removal, addition_attacks, addition_attacker):
#     for attacker in list(attacks):
#         if removal in attacks[attacker]:
#             attacks[attacker].remove(removal)
#         if not len(attacks[attacker]):
#             del attacks[attacker]
#     for attack in addition_attacks:
#         if attack in attacks:
#             if addition_attacker not in attacks[attack]:
#                 attacks[attack].append(addition_attacker)
#         else:
#             attacks[attack] = [addition_attacker]

def analyze_board(board, side):
    # TODO test speed of dict vs list
    scores = {1: 0, -1: 0}
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) != EMPTY:
                scores[find_state((x, y), board)] += PIECE_VALUES[find_type((x, y), board)]
    return scores[side] - scores[side * -1]

def simulate(board, side, level=1):
    moves = {}
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) == side:
                temp_moves = PIECE_MOVE_FUNCTIONS[find_type((x, y), board)]((x, y), board, side)
                if temp_moves:
                    moves[(x, y)] = temp_moves

    if level == SIMULATION_LEVEL:
        # print(level, side)
        points = []
        for piece in moves:
            temp_points = []
            # print('piece')
            for move in moves[piece]:
                # print(piece, move)
                temp_points.append(analyze_board(apply_move(move, piece, board, side), side))
            points.append(max(temp_points))
        return max(points)


    # elif level > 1:
    else:
        # print(level, side)
        points = 0
        length = 0
        for piece in moves:
            for move in moves[piece]:
                # print(piece, move)
                points += simulate(apply_move(move, piece, board, side), side * -1, level + 1)
                length += 1
            # points += temp_points / len(moves[piece])
        return points / length

    # else:
        # points = {}   
        # piece_count = 0
        # for piece in moves:
        #     piece_count += 1
        #     temp_points = {}
        #     for move in moves[piece]:
        #         temp_points[play(apply_move(move, piece, board, side), side * -1, level + 1)] = move
        #     max_points = max(temp_points)
        #     points[max_points] = piece
        #     moves[piece] = temp_points[max_points]
        # final_piece = points[max(points)]
        # print(final_piece, moves[final_piece])
        # return apply_move(moves[final_piece], final_piece, board, side)

def play(board, side):
    # turn_ratio = find_turn_ratio(turn)
    moves = {}
    ally_attacks = {}
    enemy_attacks = {}
    enemy_king = None
    for i_side in (side * -1, side):
        for y in BOARD_ITERATOR:
            for x in BOARD_ITERATOR:
                tile_state = find_state((x, y), board)
                if tile_state == i_side:
                    piece_type = find_type((x, y), board)
                    if i_side == side:
                        temp_moves = PIECE_MOVE_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if temp_moves:
                            moves[(x, y)] = temp_moves
                        attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if attacks:
                            for attack in attacks:
                                ally_attacks.setdefault(attack, []).append((x, y))
                    else:
                        # if (x, y) not in enemy_attacks_1:
                        #     enemy_attacks[(x, y)] = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
                        attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
                        if attacks:
                            for attack in attacks:
                                enemy_attacks.setdefault(attack, []).append((x, y))
                        if piece_type == 'k':
                            enemy_king = (x, y)
                # elif tile_state == EMPTY:
                #     if (x, y) in enemy_attacks:
                #         del enemy_attacks[(x, y)]
                #     elif (x, y) in ally_attacks:
                #         del ally_attacks[(x, y)]

    # print(turn, turn_ratio)
    # print("ally")
    # print(ally_attacks)
    # print("enemy")
    # print(enemy_attacks)
    # print("moves")
    # print(moves)

    # for attack in enemy_attacks:
    #     if find_type(attack, board) == side:

    all_points = {}
    for piece in moves:
        piece_type = find_type(piece, board)
        piece_points = PIECE_POINTS[piece_type]
        distance_to_king = distance(piece, enemy_king)
        # print(piece_type, piece_points, piece, ":")
        temp_points = {}
        for move in moves[piece]:
            points = analyze_movement(move, piece, piece_type, enemy_king, distance_to_king)
            points += analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points)
            # print(points)
            temp_points.setdefault(points, []).append(move)
        max_points = max(temp_points)
        # print(temp_points[max_points], max_points)
        # points = analyze_move_source(move, piece, board, side, ally_attacks, enemy_attacks) + max_points
        all_points.setdefault(max_points, {})[piece] = temp_points[max_points]

    print(all_points)
    max_points = max(all_points)
    if len(all_points[max_points]) != 1:
        final_points = {}
        for piece in all_points[max_points]:
            for move in all_points[max_points][piece]:
                # print(side)
                final_points[simulate(apply_move(move, piece, board, side), side * -1)] = piece, move
        print(final_points)
        # print("#################################")
        final_piece, final_move = final_points[max(final_points)]
        # print(final_piece)
    else:
        final_piece = list(all_points[max_points])[0]
        final_move = all_points[max_points][final_piece][0]
    return apply_move(final_move, final_piece, board, side)


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
    board = list(DEFAULT_BOARD)
    side = -1
    # # turn = 0
    # enemy_attacks_enemy_format = (None, {}, {})
    # enemy_attacks_attack_format = (None, {}, {})
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # if side == -1:
                #     turn += 1
                # play(board, side, turn, enemy_attacks_enemy_format[side], enemy_attacks_attack_format[side])
                current_time = time()
                board = play(board, side)
                print(time() - current_time)
                side *= -1
        DISPLAY.fill(BACKGROUND_COLOR)
        draw_board(DISPLAY, PIECE_SPRITES, NUMBER_SPRITES, board)
        pygame.display.update()

if __name__ == '__main__':
    main()
