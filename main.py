from math import sqrt
from copy import deepcopy

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
MAX_SIMULATION_LEVEL = 4

PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3.25, 'r': 5, 'q': 9, 'k': 20}
PIECE_POINTS = {key: PIECE_VALUES[key] * ACQUIRE_BONUS for key in PIECE_VALUES}

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
    temp_board = list(board)
    temp_board[move[1]] = list(temp_board[move[1]])
    temp_board[move[1]][move[0]] = (side, find_type(origin, board))
    temp_board[move[1]] = tuple(temp_board[move[1]])
    temp_board[origin[1]] = list(temp_board[origin[1]])
    temp_board[origin[1]][origin[0]] = (EMPTY,)
    temp_board[origin[1]] = tuple(temp_board[origin[1]])
    return tuple(temp_board)

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

    if simulation_level == MAX_SIMULATION_LEVEL:
        # print(current_points, end=' ')
        all_deep_exchange_points = []
        for piece in moves:
            piece_type = find_type(piece, board)
            piece_points = PIECE_POINTS[piece_type]
            for move in moves[piece]:
                _, deep_exchange_points = analyze_exchanges(move, piece, piece_type, board, ally_attacks, enemy_attacks,
                                                            piece_points)
                all_deep_exchange_points.append(deep_exchange_points)
        # print("MAX:", all_deep_exchange_points, max(all_deep_exchange_points))
        return current_points + max(all_deep_exchange_points) * side * base_side

    else:
        final_moves = {}
        all_exchange_points = {}

        # print(current_points, "SIMULATED POINTS: ", end='')
        for piece in moves:
            piece_type = find_type(piece, board)
            piece_points = PIECE_POINTS[piece_type]
            for move in moves[piece]:
                exchange_points, deep_exchange_points = analyze_exchanges(move, piece, piece_type, board, ally_attacks,
                                                                          enemy_attacks,
                                                                          piece_points)
                # print(piece, move, exchange_points, deep_exchange_points, end=' ')
                if side != base_side and exchange_points == PIECE_POINTS['k']:
                    return current_points - PIECE_POINTS['k']
                all_exchange_points[move] = exchange_points
                if deep_exchange_points >= 0:
                    final_moves.setdefault(piece, []).append(move)
        # print()

        if simulation_level > 1:
            final_points = []
            # # print("SIMULATED POINTS:", final_moves)
            for piece in final_moves:
                for move in final_moves[piece]:
                    # print(piece, move, end=' ')
                    final_points.append(play(apply_move(move, piece, board, side), base_side, side * -1,
                                             current_points + all_exchange_points[move] * base_side * side,
                                             simulation_level + 1))
            if side * base_side == -1:
                return min(final_points)
            else:
                return max(final_points)

        else:
            current_points = analyze_board(board, base_side)
            # print(current_points)
            final_points = {}

            for piece in final_moves:
                for move in final_moves[piece]:
                    # print('PIECE:', piece, move, 'move,',
                    #   all_exchange_points[move] * base_side * side, "exchange points")
                    temp_points = play(apply_move(move, piece, board, side), base_side, side * -1,
                                       current_points + all_exchange_points[move] * base_side * side,
                                       simulation_level + 1)
                    # print(temp_points, "final points")
                    final_points.setdefault(temp_points, {}).setdefault(piece, []).append(move)

            # print(final_points)
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
            # print(end_points)
            piece, move = end_points[max(end_points)]
            return apply_move(move, piece, board, side)
