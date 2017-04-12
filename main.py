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
MAX_SIMULATION_LEVEL = 2
# MAX_ALLY_SIMULATION_NUMBER = 20
# MAX_ENEMY_SIMULATION_NUMBER = 20
# MAX_SIMULATION_NUMBERS = (None, MAX_ENEMY_SIMULATION_NUMBER, MAX_ALLY_SIMULATION_NUMBER)

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

def analyze_movement(move, origin, piece_type, enemy_king, distance_to_king):
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
    new_distance = distance(move, enemy_king)
    if new_distance < distance_to_king:
        points += KING_BONUS
        # print("king bonus, ", end='')
    return points


def analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points):
    points = 0
    exchange_points = 0
    if find_state(move, board) != EMPTY:
        exchange_points = PIECE_POINTS[find_type(move, board)]
        points += exchange_points

    enemy_number = len(enemy_attacks.get(move, []))
    if enemy_number > 0:
        if piece_points > min(PIECE_POINTS[find_type(enemy, board)] for enemy in enemy_attacks[move]) or len(ally_attacks.get(move, [])) <= enemy_number:
            points -= piece_points
    return exchange_points, points

# def analyze_exchange(move, board):
#     # scores = {1: 0, -1: 0}
#     points = 0
#     if find_state(move, board) != EMPTY:
#         points += PIECE_POINTS[find_type(move, board)]
#
#     return 0
    # for y in BOARD_ITERATOR:
    #     for x in BOARD_ITERATOR:
    #         if find_state((x, y), board) != EMPTY:
    #             scores[find_state((x, y), board)] += PIECE_VALUES[find_type((x, y), board)]
    # return scores[side] - scores[side * -1]


# def analyze_move_source(move, origin, board, side, ally_stoppers, enemy_moves):
#     return 0

def apply_move(move, origin, board, side):
    temp_board = deepcopy(board)
    temp_board[move[1]][move[0]] = (side, find_type(origin, board))
    temp_board[origin[1]][origin[0]] = (EMPTY, EMPTY)
    # DISPLAY.fill(BACKGROUND_COLOR)
    # draw_board(DISPLAY, PIECE_SPRITES, NUMBER_SPRITES, temp_board)
    # pygame.display.update()
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
    scores = [None, 0, 0]
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) != EMPTY:
                scores[find_state((x, y), board)] += PIECE_VALUES[find_type((x, y), board)]
    return scores[side] - scores[side * -1]


# def simulate(board, side, level=1):
#     moves = {}
#     for y in BOARD_ITERATOR:
#         for x in BOARD_ITERATOR:
#             if find_state((x, y), board) == side:
#                 temp_moves = PIECE_MOVE_FUNCTIONS[find_type((x, y), board)]((x, y), board, side)
#                 if temp_moves:
#                     moves[(x, y)] = temp_moves
#
#     if level == SIMULATION_LEVEL:
#         # print(level, side)
#         points = []
#         for piece in moves:
#             temp_points = []
#             # print('piece')
#             for move in moves[piece]:
#                 # print(piece, move)
#                 temp_points.append(analyze_board(apply_move(move, piece, board, side), side))
#             points.append(max(temp_points))
#         return max(points)
#
#
#     # elif level > 1:
#     else:
#         # print(level, side)
#         points = 0
#         length = 0
#         for piece in moves:
#             for move in moves[piece]:
#                 # print(piece, move)
#                 points += simulate(apply_move(move, piece, board, side), side * -1, level + 1)
#                 length += 1
#             # points += temp_points / len(moves[piece])
#         return points / length

    # else:
    #     points = {}
    #     piece_count = 0
    #     for piece in moves:
    #         piece_count += 1
    #         temp_points = {}
    #         for move in moves[piece]:
    #             temp_points[play(apply_move(move, piece, board, side), side * -1, level + 1)] = move
    #         max_points = max(temp_points)
    #         points[max_points] = piece
    #         moves[piece] = temp_points[max_points]
    #     final_piece = points[max(points)]
    #     print(final_piece, moves[final_piece])
    #     return apply_move(moves[final_piece], final_piece, board, side)

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
    
    # for i_side in (side * -1, side):
    #     for y in BOARD_ITERATOR:
    #         for x in BOARD_ITERATOR:
    #             tile_state = find_state((x, y), board)
    #             if tile_state == i_side:
    #                 piece_type = find_type((x, y), board)
    #                 if i_side == side:
    #                     temp_moves = PIECE_MOVE_FUNCTIONS[piece_type]((x, y), board, i_side)
    #                     if temp_moves:
    #                         moves[(x, y)] = temp_moves
    #                     # attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
    #                     # if attacks:
    #                     #     for attack in attacks:
    #                     #         ally_attacks.setdefault(attack, []).append((x, y))
    #                 else:
    #                     # if (x, y) not in enemy_attacks_1:
    #                     #     enemy_attacks[(x, y)] = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
    #                     # attacks = PIECE_ATTACK_FUNCTIONS[piece_type]((x, y), board, i_side)
    #                     # if attacks:
    #                     #     for attack in attacks:
    #                     #         enemy_attacks.setdefault(attack, []).append((x, y))
    #                     if piece_type == 'k':
    #                         enemy_king = (x, y)
    #             elif tile_state == EMPTY:
    #                 if (x, y) in enemy_attacks:
    #                     del enemy_attacks[(x, y)]
    #                 elif (x, y) in ally_attacks:
    #                     del ally_attacks[(x, y)]

    # print(turn, turn_ratio)
    # print("ally")
    # print(ally_attacks)
    # print("enemy")
    # print(enemy_attacks)
    # print("moves")
    # print(moves)

    # for attack in enemy_attacks:
    #     if find_type(attack, board) == side:

    if simulation_level == MAX_SIMULATION_LEVEL and side == base_side:
        all_deep_exchange_points = []
        for piece in moves:
            piece_points = PIECE_POINTS[find_type(piece, board)]
            for move in moves[piece]:
                _, deep_exchange_points = analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points)
                all_deep_exchange_points.append(deep_exchange_points)
        # print("MAX SIMULATION LEVEL current points:", current_points, "final_points:", max(all_deep_exchange_points) + current_points)
        print("MAX:", all_deep_exchange_points)
        return max(all_deep_exchange_points) + current_points

    else:
        all_points = {}
        all_exchange_points = {}
        all_deep_exchange_points = {}
        for piece in moves:
            piece_points = PIECE_POINTS[find_type(piece, board)]
            for move in moves[piece]:
                exchange_points, deep_exchange_points = analyze_exchanges(move, board, ally_attacks, enemy_attacks, piece_points)
                all_exchange_points[move] = exchange_points
                if deep_exchange_points > 0:
                    all_points.setdefault(deep_exchange_points, {}).setdefault(piece, []).append(move)
                elif not all_points and deep_exchange_points == 0:
                    all_deep_exchange_points.setdefault(piece, []).append(move)

        if not all_points:
            for piece in all_deep_exchange_points:
                piece_type = find_type(piece, board)
                distance_to_king = distance(piece, enemy_king)
                for move in all_deep_exchange_points[piece]:
                    all_points.setdefault(analyze_movement(move, piece, piece_type, enemy_king, distance_to_king), {}).setdefault(piece, []).append(move)
        del all_deep_exchange_points




        # points = 0
        # length = 0
        # for piece in moves:
        #     for move in moves[piece]:
        #         # print(piece, move)
        #         points += simulate(apply_move(move, piece, board, side), side * -1, level + 1)
        #         length += 1
        #         # points += temp_points / len(moves[piece])
        # return points / length

        # if simulation_level > 1:
        #     print(side, "side,", simulation_level, "simulation level,", "current points:", current_points)
        #     final_points = 0
        #     simulation_count = 0
        #     for points in sorted(all_points, reverse=True):
        #         for piece in all_points[points]:
        #             for move in all_points[points][piece]:
        #                 print(move, "move,", piece, "piece")
        #                 final_points += play(apply_move(move, piece, board, side), base_side, side * -1, current_points + all_exchange_points[move] * base_side * side, simulation_level + 1)
        #                 simulation_count += 1
        #                 if simulation_count == SIMULATION_NUMBERS[side]:
        #                     break
        #             if simulation_count == SIMULATION_NUMBERS[side]:
        #                 break
        #         if simulation_count == SIMULATION_NUMBERS[side]:
        #             break
        #     print(final_points, "final points")
        #     return final_points / simulation_count

        if simulation_level > 1:
            if side == base_side:
                simulation_level += 1
            # print(side, "side,", simulation_level, "simulation level,", current_points, "current points,")
            final_points = 0
            length = 0
            # simulation_count = 0
            print("SIMULATED POINTS:")
            for points in sorted(all_points, reverse=True):
                print(points, all_points[points])
            for points in sorted(all_points, reverse=True):
                for piece in all_points[points]:
                    for move in all_points[points][piece]:
                        # print("SIMULATED:", move, "move,", piece, "piece")
                        final_points += play(apply_move(move, piece, board, side), base_side, side * -1, current_points + all_exchange_points[move] * base_side * side, simulation_level)
                        length += 1
                        # simulation_count += 1
                        # print(MAX_SIMULATION_NUMBERS[side], simulation_count)
                        #         if simulation_count == MAX_SIMULATION_NUMBERS[side]:
                        #             break
                        #     if simulation_count == MAX_SIMULATION_NUMBERS[side]:
                        #         break
                        # if simulation_count == MAX_SIMULATION_NUMBERS[side]:
                        #     break
            # print(final_points, "final SIMULATED points")
            # return final_points / simulation_count
            return final_points / length

        else:
            current_points = analyze_board(board, base_side)
            final_points = {}

            for points in sorted(all_points, reverse=True):
                print(points, all_points[points])

            for points in sorted(all_points, reverse=True):
                for piece in all_points[points]:
                    for move in all_points[points][piece]:
                        print('PIECE:', piece, move, 'move,', points, "points,", all_exchange_points[move] * base_side * side, "exchange points")
                        temp_points = play(apply_move(move, piece, board, side), base_side, side * -1, current_points + all_exchange_points[move] * base_side * side, simulation_level + 1)
                        print(temp_points, "final points")
                        final_points.setdefault(temp_points, []).append((piece, move))
            # print("FINAL POINTS: ", final_points)
            print(final_points)

            max_final_points = final_points[max(final_points)]
            if len(max_final_points) == 1:
                piece, move = max_final_points[0]
                return apply_move(move, piece, board, side)
            for points in sorted(all_points, reverse=True):
                for piece in all_points[points]:
                    for move in all_points[points][piece]:
                        if (piece, move) in max_final_points:
                            print('FINAL:', piece, move)
                            return apply_move(move, piece, board, side)

            # end_points = {}
            # for piece, move in final_points[max(final_points)]:
            #     end_points[all_points[]]
            # if final_points:
            #     final_piece, final_move = final_points[max(final_points)]
            # else:
            #     final_piece, final_move = list(all_points[sorted(all_points, reverse=True)[0]].items())[0]
            #     final_move = final_move[0]
            #
            # print("FINAL:", final_piece, final_move)
            # # print("FINAL: ", final_piece, final_move)
            # return apply_move(final_move, final_piece, board, side)


    # if len(all_points[max_points]) != 1:
    #     final_points = {}
    #     for piece in all_points[max_points]:
    #         for move in all_points[max_points][piece]:
    #             # print(side)
    #             final_points[simulate(apply_move(move, piece, board, side), side * -1)] = piece, move
    #     print(final_points)
    #     # print("#################################")
    #     final_piece, final_move = final_points[max(final_points)]
    #     # print(final_piece)
    # else:
    #     final_piece = list(all_points[max_points])[0]
    #     final_move = all_points[max_points][final_piece][0]
    # print("FINAL: ", final_piece, final_move)
    # return apply_move(final_move, final_piece, board, side)


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
    # piece = None
    # board = play(board, side)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_time = time()
                board = play(board, side, side)
                print("TIME TAKEN:", time() - current_time)
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
