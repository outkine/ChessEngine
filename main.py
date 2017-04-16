from math import sqrt

BOARD_SIZE = 8
BOARD_ITERATOR = range(BOARD_SIZE)
EMPTY = 0
EMPTY_TILE = (EMPTY, EMPTY)
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
BOARD_EDGES = (0, 7)

ACQUIRE_BONUS = 5
BROAD_CENTER_BONUS = 1
CENTER_BONUS = 4
LIGHT_OPENING_BONUS = 1
KING_BONUS = 2
PAWN_BONUS = 1
# MAX_SIMULATION_LEVELS = ((17, 4), (10, 5), (8, 6), (5, 7), (1, 8))
MAX_SIMULATION_LEVEL = 4
PIECE_VALUES = {'p': 1, 'n': 3, 'b': 3.25, 'r': 5, 'q': 9, 'k': 20}
PIECE_POINTS = {key: PIECE_VALUES[key] * ACQUIRE_BONUS for key in PIECE_VALUES}
PAWN_PROMOTION_POINTS = PIECE_POINTS['q'] - PIECE_POINTS['p']

UNMOVED_KING = [None, True, True]
UNMOVED_ROOKS = [None, {(0, 0): True, (7, 0): True}, {(0, 7): True, (7, 7): True}]
ROOK_POSITIONS = (None, ((0, 0), (7, 0)), ((0, 7), (7, 7)))
KING_POSITIONS = (None, (4, 0), (4, 7))
ROOK_CASTLE_POSITIONS = (None, ((3, 0), (5, 0)), ((3, 7), (5, 7)))
KING_CASTLE_POSITIONS = (None, ((2, 0), (6, 0)), ((2, 7), (6, 7)))
CASTLE_TILES = (
    None,
    (((2, 0), (3, 0)), ((6, 0), (5, 0))),
    (((2, 7), (3, 7)), ((6, 7), (5, 7)))
)
KING_PATH = (
    None,
    (((1, 0), (2, 0), (3, 0)), ((6, 0), (5, 0))),
    (((1, 7), (2, 7), (3, 7)), ((6, 7), (5, 7)))
)

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

def pawn_move(loc, board, side, double_pawn):
    moves = []
    passant_moves = []
    for x in (-1, 1):
        pos = (x + loc[0], side + loc[1])
        if safe_find_state(pos, board) == side * -1:
            moves.append(pos)
        elif (loc[0] + x, loc[1]) == double_pawn:
            moves.append(pos)
            passant_moves.append(pos)
    pos = (loc[0], loc[1] + side)
    if safe_find_state(pos, board) == EMPTY:
        moves.append(pos)
        if loc[1] == PAWN_STARTS[side]:
            pos = (loc[0], loc[1] + 2 * side)
            if find_state(pos, board) == EMPTY:
                moves.append(pos)
    return moves, passant_moves

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

# noinspection PyUnusedLocal
def pawn_attack(loc, board, side):
    return [(x + loc[0], side + loc[1]) for x in (-1, 1)]

def jump_piece_attack(loc, vectors):
    attacks = []
    for vector in vectors:
        pos = (loc[0] + vector[0], loc[1] + vector[1])
        if within_bounds(pos):
            attacks.append(pos)
    return attacks

# noinspection PyUnusedLocal
def knight_attack(loc, board, side):
    return jump_piece_attack(loc, KNIGHT_VECTORS)

# noinspection PyUnusedLocal
def king_attack(loc, board, side):
    return jump_piece_attack(loc, KING_VECTORS)

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

# noinspection PyUnusedLocal
def bishop_attack(loc, board, side):
    return vector_piece_attack(loc, board, BISHOP_VECTORS)

# noinspection PyUnusedLocal
def rook_attack(loc, board, side):
    return vector_piece_attack(loc, board, ROOK_VECTORS)

# noinspection PyUnusedLocal
def queen_attack(loc, board, side):
    return bishop_attack(loc, board, side) + rook_attack(loc, board, side)

PIECE_MOVE_FUNCTIONS = {'n': knight_move, 'b': bishop_move, 'r': rook_move, 'q': queen_move, 'k': king_move}
PIECE_ATTACK_FUNCTIONS = {'p': pawn_attack, 'n': knight_attack, 'b': bishop_attack, 'r': rook_attack, 'q': queen_attack,
                          'k': king_attack}

def is_double_pawn(origin, move, piece_type):
    if piece_type == 'p' and abs(move[1] - origin[1]) == 2:
        return True
    return False

def allow_modify(func):
    def temp(board, *args):
        board = list(board)
        func(board, *args)
        return tuple(board)

    return temp

def modify_tile(board, tile, new_tile):
    board[tile[1]] = list(board[tile[1]])
    board[tile[1]][tile[0]] = new_tile
    board[tile[1]] = tuple(board[tile[1]])

@allow_modify
def safe_modify_tile(board, tile, new_tile):
    modify_tile(board, tile, new_tile)

def apply_move(board, origin, move, side):
    modify_tile(board, move, (side, find_type(origin, board)))
    modify_tile(board, origin, EMPTY_TILE)

@allow_modify
def safe_apply_move(board, origin, move, side):
    apply_move(board, origin, move, side)

@allow_modify
def castle(board, side, direction):
    UNMOVED_KING[side] = False
    apply_move(board, ROOK_POSITIONS[side][direction], ROOK_CASTLE_POSITIONS[side][direction], side)
    apply_move(board, KING_POSITIONS[side], KING_CASTLE_POSITIONS[side][direction], side)

@allow_modify
def process_move(board, origin, move, side, passant_move):
    apply_move(board, origin, move, side)
    if can_promote(find_type(move, board), move):
        modify_tile(board, move, (side, 'q'))
    if passant_move:
        modify_tile(board, (move[0], move[1] - side), EMPTY_TILE)


def find_castle_directions(board, side, enemy_attacks):
    directions = []
    if UNMOVED_KING[side] and (True in UNMOVED_ROOKS[side].values()) and KING_POSITIONS[side] not in enemy_attacks:
        for direction in (0, 1):
            coordinates = ROOK_POSITIONS[side][direction]
            if UNMOVED_ROOKS[side][coordinates] and find_state(coordinates, board) == side:
                for coordinates in CASTLE_TILES[side][direction]:
                    if find_state(coordinates, board) != EMPTY or coordinates in enemy_attacks:
                        break
                else:
                    directions.append(direction)
    return directions

def can_promote(piece_type, move):
    if piece_type == 'p' and move[1] in BOARD_EDGES:
        return True
    return False

def analyze_board(board, side):
    scores = [None, 0, 0]
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            if find_state((x, y), board) != EMPTY:
                scores[find_state((x, y), board)] += PIECE_POINTS[find_type((x, y), board)]
    return scores[side] - scores[side * -1]

def analyze_movement(move, origin, piece_type, enemy_king, distance_to_king):
    points = 0
    if piece_type in ('p', 'n', 'b'):
        if origin not in CENTER and move in CENTER:
            points += CENTER_BONUS
        elif origin not in BROAD_CENTER and move in BROAD_CENTER:
            points += BROAD_CENTER_BONUS
        elif piece_type == 'p':
            points += PAWN_BONUS
    if piece_type not in ('k', 'p'):
        new_distance = distance(move, enemy_king)
        if new_distance < distance_to_king:
            points += KING_BONUS
    return points

def analyze_exchanges(move, origin, piece_type, piece_points, board, ally_attacks, enemy_attacks, passant_moves):
    exchange_points = 0
    if can_promote(piece_type, move):
        piece_points = PIECE_POINTS['q']
        exchange_points += PAWN_PROMOTION_POINTS
    if find_state(move, board) != EMPTY:
        exchange_points += PIECE_POINTS[find_type(move, board)]
    elif move in passant_moves:
        exchange_points += PIECE_POINTS['p']
    points = exchange_points

    enemy_number = len(enemy_attacks.get(move, []))
    ally_number = len(ally_attacks.get(move, []))
    if piece_type != 'p' or move[0] - origin[0] != 0:
        ally_number -= 1
    if enemy_number > 0:
        if piece_points > min(
                PIECE_POINTS[find_type(enemy, board)] for enemy in enemy_attacks[move]) or ally_number < enemy_number:
            points -= piece_points
    return exchange_points, points

def update_constants(board, side, piece):
    piece_type = find_type(piece, board)
    # noinspection PyTypeChecker
    if piece_type == 'k' and UNMOVED_KING[side]:
        UNMOVED_KING[side] = False
    elif piece_type == 'r' and UNMOVED_ROOKS[side].get(piece, False):
        UNMOVED_ROOKS[side][piece] = False

def update_double_pawn(piece, move, piece_type):
    if is_double_pawn(piece, move, piece_type):
        return move
    return None

def play(board, side, double_pawn, current_points=None, simulation_level=1):
    moves = {}
    ally_attacks = {}
    enemy_attacks = {}
    enemy_king = None
    passant_moves = []
    for y in BOARD_ITERATOR:
        for x in BOARD_ITERATOR:
            tile_state = find_state((x, y), board)
            if tile_state != EMPTY:
                piece_type = find_type((x, y), board)
                if tile_state == side:
                    if piece_type == 'p':
                        temp_moves, temp_passant_moves = pawn_move((x, y), board, side, double_pawn)
                        passant_moves.extend(temp_passant_moves)
                    else:
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
                    if piece_type == 'k':
                        enemy_king = (x, y)

    if moves:
        if simulation_level == MAX_SIMULATION_LEVEL:
            # print(current_points, end=' ')
            all_deep_exchange_points = []
            for piece in moves:
                piece_type = find_type(piece, board)
                piece_points = PIECE_POINTS[piece_type]
                for move in moves[piece]:
                    all_deep_exchange_points.append(
                        analyze_exchanges(move, piece, piece_type, piece_points, board, ally_attacks, enemy_attacks, passant_moves)[1]
                    )
            # print("MAX:", all_deep_exchange_points, max(all_deep_exchange_points))
            return (current_points + max(all_deep_exchange_points)) * -1

        else:

            final_moves = {}
            all_exchange_points = {}

            # print(current_points, "SIMULATED POINTS: ", end='')
            for piece in moves:
                piece_type = find_type(piece, board)
                piece_points = PIECE_POINTS[piece_type]
                for move in moves[piece]:
                    exchange_points, deep_exchange_points = analyze_exchanges(move, piece, piece_type, piece_points, board,
                                                                              ally_attacks, enemy_attacks, passant_moves)
                    # print(piece, move, exchange_points, deep_exchange_points, end=' ')
                    if exchange_points == PIECE_POINTS['k']:
                        return (current_points + PIECE_POINTS['k']) * -1
                    elif deep_exchange_points >= 0:
                        final_moves.setdefault(piece, []).append(move)
                        all_exchange_points[move] = exchange_points
            # print()

            if simulation_level > 1:
                final_points = []
                # # print("SIMULATED POINTS:", final_moves)
                for piece in final_moves:
                    for move in final_moves[piece]:
                        # print(piece, move, end=' ')
                        # noinspection PyTypeChecker
                        final_points.append(
                            play(process_move(board, piece, move, side, move in passant_moves), side * -1, update_double_pawn(piece, move, find_type(piece, board)),
                                 (current_points + all_exchange_points[move]) * -1, simulation_level + 1)
                        )
                return max(final_points) * -1

            else:

                # move_number = 0
                # for piece in final_moves:
                #     move_number += len(final_moves[piece])
                # for number, level in MAX_SIMULATION_LEVELS:
                #     if move_number >= number:
                #         max_level = level
                #         break
                # print(move_number, max_level)
                current_points = analyze_board(board, side)
                # print(current_points)
                final_points = {}

                for piece in final_moves:
                    for move in final_moves[piece]:
                        # print('PIECE:', piece, move, 'move,',
                        #   all_exchange_points[move] * base_side * side, "exchange points")
                        # noinspection PyTypeChecker
                        temp_points = play(process_move(board, piece, move, side, move in passant_moves), side * -1,
                                           update_double_pawn(piece, move, find_type(piece, board)), (current_points + all_exchange_points[move]) * -1,
                                           simulation_level + 1)
                        # print(temp_points, "final points")
                        final_points.setdefault(temp_points, {}).setdefault(piece, []).append(move)

                # print(final_points)
                max_final_points = final_points[max(final_points)]
                if len(max_final_points.values()) == 1:
                    piece, move = list(max_final_points.items())[0]
                    move = move[0]
                else:
                    castle_directions = find_castle_directions(board, side, enemy_attacks)
                    if castle_directions:
                        return castle(board, side, castle_directions[0]), None
                    end_points = {}
                    for piece in max_final_points:
                        piece_type = find_type(piece, board)
                        distance_to_king = distance(piece, enemy_king)
                        for move in max_final_points[piece]:
                            end_points[analyze_movement(move, piece, piece_type, enemy_king, distance_to_king)] = (
                                piece, move)
                            # print(end_points)
                    piece, move = end_points[max(end_points)]

                update_constants(board, side, piece)
                return process_move(board, piece, move, side, move in passant_moves), update_double_pawn(piece, move, find_type(piece, board))
    if simulation_level != 1:
        return 0
    return board, None
