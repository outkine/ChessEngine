import pygame
from spritesheet import BlockSheet
from math import sqrt
from copy import deepcopy
from time import time

# @formatter:off
DEFAULT_BOARD = [
    # 0         1           2           3           4           5           6           7
    [(1, 'r'), 	(1, 'n'), 	(1, 'b'), 	(1, 'q'), 	(1, 'k'), 	(1, 'b'), 	(1, 'n'), 	(1, 'r'), 	],  # 0
    [(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	(1, 'p'), 	],  # 1
    [(0, 0),	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	],  # 2
    [(0, 0),	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	],  # 3
    [(0, 0),	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	],  # 4
    [(0, 0),	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	(0, 0),	 	],  # 5
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
                (-1, 0), (1, 0),
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
MAX_SIMULATION_LEVEL = 2

PIECES = ('p', 'n', 'b', 'r', 'q', 'k')
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 20}
PIECE_POINTS = {key: PIECE_VALUES[key] * ACQUIRE_BONUS for key in PIECE_VALUES}

SCALE_FACTOR = 4
BACKGROUND_COLOR = (255, 255, 255)
FRAME_RATE = 1
PIECE_SIZE = (7, 14)
TILE_SIZE = 80
MARGIN = 50
NUMBER_SCALE_FACTOR = 2
NUMBER_GAP = 15

DISPLAY = pygame.display.set_mode([TILE_SIZE * 8 + MARGIN * 2 for _ in range(2)])
SPRITE_SHEET = BlockSheet("spritesheet.png", SCALE_FACTOR, PIECE_SIZE)
PIECE_SPRITES = {}
for side in (1, -1):
    temp_sprites = SPRITE_SHEET.get_blocks(len(PIECES))
    PIECE_SPRITES[side] = {piece: temp_sprites[i] for i, piece in enumerate(PIECES)}
NUMBER_SPRITES = SPRITE_SHEET.get_custom_blocks((7, 7), 10, scale=NUMBER_SCALE_FACTOR)

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

def analyze_movement(move, origin, piece_type, enemy_king, distance_to_king):
    points = 0
    if piece_type in ('p', 'n', 'b'):
        if origin not in CENTER and move in CENTER:
            points += CENTER_BONUS
        elif origin not in BROAD_CENTER and move in BROAD_CENTER:
            points += BROAD_CENTER_BONUS
    new_distance = distance(move, enemy_king)
    if new_distance < distance_to_king:
        points += KING_BONUS
    return points

def analyze_exchanges(move, origin, piece_type, board, ally_attacks, enemy_attacks, piece_points):
    points = 0
    exchange_points = 0
    if find_state(move, board) != EMPTY:
        exchange_points = PIECE_POINTS[find_type(move, board)]
        points += exchange_points

    enemy_number = len(enemy_attacks.get(move, []))
    ally_number = len(ally_attacks.get(move, []))
    if piece_type != 'p' or move[0] - origin[0] != 0:
        ally_number -= 1
    if enemy_number > 0:
        if piece_points > min(
                PIECE_POINTS[find_type(enemy, board)] for enemy in enemy_attacks[move]) or ally_number < enemy_number:
            points -= piece_points
    return exchange_points, points

def apply_move(move, origin, board, side):
    temp_board = deepcopy(board)
    temp_board[move[1]][move[0]] = (side, find_type(origin, board))
    temp_board[origin[1]][origin[0]] = (EMPTY, EMPTY)
    return temp_board

def analyze_board(board, side):
    # TODO test speed of dict vs list
    scores = [None, 0, 0]
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) != EMPTY:
                scores[find_state((x, y), board)] += PIECE_POINTS[find_type((x, y), board)]
    return scores[side] - scores[side * -1]

def play(board, base_side, side, current_points=None, simulation_level=1):
    moves = {}
    ally_attacks = {}
    enemy_attacks = {}
    enemy_king = None
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            tile_state = find_state((x, y), board)
            if tile_state != EMPTY:
                piece_type = find_type((x, y), board)
                if tile_state == side:
                    temp_moves = PIECE_MOVE_FUNCTIONS[piece_type]((x, y), board, side)
                    if temp_moves:
                        moves[(x, y)] = temp_moves
                    attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, side)
                    if attacks:
                        for attack in attacks:
                            ally_attacks.setdefault(attack, []).append((x, y))
                else:
                    attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, side * -1)
                    if attacks:
                        for attack in attacks:
                            enemy_attacks.setdefault(attack, []).append((x, y))
                    if find_type((x, y), board) == 'k':
                        enemy_king = (x, y)

    if simulation_level == MAX_SIMULATION_LEVEL and side == base_side:
        print(current_points, end=' ')
        all_deep_exchange_points = []
        for piece in moves:
            piece_type = find_type(piece, board)
            piece_points = PIECE_POINTS[piece_type]
            for move in moves[piece]:
                _, deep_exchange_points = analyze_exchanges(move, piece, piece_type, board, ally_attacks, enemy_attacks,
                                                            piece_points)
                all_deep_exchange_points.append(deep_exchange_points)
        print("MAX:", all_deep_exchange_points, max(all_deep_exchange_points))
        return max(all_deep_exchange_points) + current_points

    else:
        final_moves = {}
        all_exchange_points = {}

        print(current_points, "SIMULATED POINTS: ", end='')
        for piece in moves:
            piece_type = find_type(piece, board)
            piece_points = PIECE_POINTS[piece_type]
            for move in moves[piece]:
                exchange_points, deep_exchange_points = analyze_exchanges(move, piece, piece_type, board, ally_attacks,
                                                                          enemy_attacks,
                                                                          piece_points)
                print(piece, move, exchange_points, deep_exchange_points, end=' ')
                if side != base_side and exchange_points == PIECE_POINTS['k']:
                    return current_points - PIECE_POINTS['k']
                all_exchange_points[move] = exchange_points
                if deep_exchange_points >= 0:
                    final_moves.setdefault(piece, []).append(move)
        print()

        if simulation_level > 1:
            if side == base_side:
                simulation_level += 1

            final_points = []
            # print("SIMULATED POINTS:", final_moves)
            for piece in final_moves:
                for move in final_moves[piece]:
                    print(piece, move, end=' ')
                    final_points.append(play(apply_move(move, piece, board, side), base_side, side * -1,
                                             current_points + all_exchange_points[move] * base_side * side,
                                             simulation_level))
            return min(final_points)

        else:
            current_points = analyze_board(board, base_side)
            print(current_points)
            final_points = {}

            for piece in final_moves:
                for move in final_moves[piece]:
                    print('PIECE:', piece, move, 'move,',
                          all_exchange_points[move] * base_side * side, "exchange points")
                    temp_points = play(apply_move(move, piece, board, side), base_side, side * -1,
                                       current_points + all_exchange_points[move] * base_side * side,
                                       simulation_level + 1)
                    print(temp_points, "final points")
                    final_points.setdefault(temp_points, {}).setdefault(piece, []).append(move)

            print(final_points)
            max_final_points = final_points[max(final_points)]
            if len(max_final_points.values()) == 1:
                piece, move = list(max_final_points.items())[0]
                return apply_move(move[0], piece, board, side)
            end_points = {}
            for piece in max_final_points:
                piece_type = find_type(piece, board)
                distance_to_king = distance(piece, enemy_king)
                for move in max_final_points[piece]:
                    end_points[analyze_movement(move, piece, piece_type, enemy_king, distance_to_king)] = (piece, move)
            print(end_points)
            piece, move = end_points[max(end_points)]
            return apply_move(move, piece, board, side)

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
    turn = 0
    for x in range(50):
        current_time = time()
        board = play(board, side, side)
        print("TIME TAKEN:", time() - current_time)
        turn += 1
        print(turn)
        print("##############################################")
        side *= -1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_time = time()
                board = play(board, side, side)
                print("TIME TAKEN:", time() - current_time)
                turn += 1
                print(turn)
                print("##############################################")
                side *= -1
                # elif event.type == pygame.MOUSEBUTTONDOWN:
                #     piece = [int((coordinate - MARGIN) / TILE_SIZE) for coordinate in event.pos]
                # elif event.type == pygame.MOUSEBUTTONUP:
                #     move = [int((coordinate - MARGIN) / TILE_SIZE) for coordinate in event.pos]
                #     print(move, piece)
                #     board = apply_move(move, piece, board, side)
                #     board = play(board, side * -1, side * -1)
                #     print("##############################################")

        DISPLAY.fill(BACKGROUND_COLOR)
        draw_board(DISPLAY, PIECE_SPRITES, NUMBER_SPRITES, board)
        pygame.display.update()

if __name__ == '__main__':
    main()
