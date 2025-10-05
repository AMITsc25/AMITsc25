#!/usr/bin/env python3
"""
Chess Game: Player vs Bot
A console-based chess game with AI opponent
"""

import copy
import random
import math


class Piece:
    """Base class for all chess pieces"""

    def __init__(self, color, symbol):
        self.color = color  # 'white' or 'black'
        self.symbol = symbol
        self.has_moved = False

    def __str__(self):
        return self.symbol

    def is_valid_move(self, start, end, board):
        """Check if move is valid for this piece type"""
        raise NotImplementedError

    def get_possible_moves(self, position, board):
        """Get all possible moves for this piece"""
        raise NotImplementedError


class Pawn(Piece):
    """Pawn piece with special movement rules"""

    def __init__(self, color):
        symbol = 'P' if color == 'white' else 'p'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        row, col = start
        end_row, end_col = end

        # Direction based on color
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        # Forward move
        if col == end_col:
            if end_row - row == direction:
                return board[end_row][end_col] is None
            elif row == start_row and end_row - row == 2 * direction:
                # Two squares forward from starting position
                # Check both squares are empty
                return (board[row + direction][col] is None and
                       board[end_row][end_col] is None)

        # Diagonal capture
        elif abs(end_col - col) == 1 and end_row - row == direction:
            target_piece = board[end_row][end_col]
            return target_piece is not None and target_piece.color != self.color

        return False

    def get_possible_moves(self, position, board):
        moves = []
        row, col = position
        direction = -1 if self.color == 'white' else 1

        # Forward moves
        if 0 <= row + direction < 8:
            if board[row + direction][col] is None:
                moves.append((row + direction, col))

        # Two squares forward
        start_row = 6 if self.color == 'white' else 1
        if row == start_row and board[row + direction][col] is None:
            if 0 <= row + 2 * direction < 8 and board[row + 2 * direction][col] is None:
                moves.append((row + 2 * direction, col))

        # Diagonal captures
        for dcol in [-1, 1]:
            new_col = col + dcol
            new_row = row + direction
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row][new_col]
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))

        return moves


class Rook(Piece):
    """Rook piece - moves horizontally and vertically"""

    def __init__(self, color):
        symbol = 'R' if color == 'white' else 'r'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        row, col = start
        end_row, end_col = end

        # Must move in straight line
        if row != end_row and col != end_col:
            return False

        # Check for pieces in path
        if row == end_row:  # Horizontal move
            step = 1 if end_col > col else -1
            for c in range(col + step, end_col, step):
                if board[row][c] is not None:
                    return False
        else:  # Vertical move
            step = 1 if end_row > row else -1
            for r in range(row + step, end_row, step):
                if board[r][col] is not None:
                    return False

        # Check destination
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_possible_moves(self, position, board):
        moves = []
        row, col = position

        # Horizontal and vertical directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves


class Knight(Piece):
    """Knight piece - moves in L-shape"""

    def __init__(self, color):
        symbol = 'N' if color == 'white' else 'n'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        row, col = start
        end_row, end_col = end

        drow = abs(end_row - row)
        dcol = abs(end_col - col)

        # Knight moves in L-shape: 2 in one direction, 1 perpendicular
        if not ((drow == 2 and dcol == 1) or (drow == 1 and dcol == 2)):
            return False

        # Check destination
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_possible_moves(self, position, board):
        moves = []
        row, col = position

        # All possible knight moves
        knight_moves = [
            (row + 2, col + 1), (row + 2, col - 1),
            (row - 2, col + 1), (row - 2, col - 1),
            (row + 1, col + 2), (row + 1, col - 2),
            (row - 1, col + 2), (row - 1, col - 2)
        ]

        for r, c in knight_moves:
            if 0 <= r < 8 and 0 <= c < 8:
                target = board[r][c]
                if target is None or target.color != self.color:
                    moves.append((r, c))

        return moves


class Bishop(Piece):
    """Bishop piece - moves diagonally"""

    def __init__(self, color):
        symbol = 'B' if color == 'white' else 'b'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        row, col = start
        end_row, end_col = end

        drow = abs(end_row - row)
        dcol = abs(end_col - col)

        # Must move diagonally
        if drow != dcol:
            return False

        # Check for pieces in path
        r_step = 1 if end_row > row else -1
        c_step = 1 if end_col > col else -1

        r, c = row + r_step, col + c_step
        while r != end_row and c != end_col:
            if board[r][c] is not None:
                return False
            r += r_step
            c += c_step

        # Check destination
        target = board[end_row][end_col]
        return target is None or target.color != self.color

    def get_possible_moves(self, position, board):
        moves = []
        row, col = position

        # Diagonal directions
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves


class Queen(Piece):
    """Queen piece - combines rook and bishop movements"""

    def __init__(self, color):
        symbol = 'Q' if color == 'white' else 'q'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        # Queen moves like both rook and bishop
        return (Rook.is_valid_move(self, start, end, board) or
                Bishop.is_valid_move(self, start, end, board))

    def get_possible_moves(self, position, board):
        # Combine rook and bishop moves
        return (Rook.get_possible_moves(self, position, board) +
                Bishop.get_possible_moves(self, position, board))


class King(Piece):
    """King piece - moves one square in any direction"""

    def __init__(self, color):
        symbol = 'K' if color == 'white' else 'k'
        super().__init__(color, symbol)

    def is_valid_move(self, start, end, board):
        row, col = start
        end_row, end_col = end

        drow = abs(end_row - row)
        dcol = abs(end_col - col)

        # King moves one square in any direction
        if drow <= 1 and dcol <= 1 and (drow != 0 or dcol != 0):
            target = board[end_row][end_col]
            return target is None or target.color != self.color

        return False

    def get_possible_moves(self, position, board):
        moves = []
        row, col = position

        # All adjacent squares
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = board[r][c]
                    if target is None or target.color != self.color:
                        moves.append((r, c))

        return moves


class ChessBoard:
    """Chess board representation and game logic"""

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.move_history = []
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up the starting chess position"""
        # Place pawns
        for col in range(8):
            self.board[1][col] = Pawn('black')
            self.board[6][col] = Pawn('white')

        # Place other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(piece_order):
            self.board[0][col] = piece_class('black')
            self.board[7][col] = piece_class('white')

    def get_piece(self, row, col):
        """Get piece at position"""
        return self.board[row][col]

    def move_piece(self, start, end):
        """Move piece from start to end position"""
        start_row, start_col = start
        end_row, end_col = end

        piece = self.board[start_row][start_col]
        if piece:
            piece.has_moved = True

        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        self.move_history.append((start, end, piece))
        self.current_player = 'black' if self.current_player == 'white' else 'white'

    def is_valid_move(self, start, end, color=None):
        """Check if move is valid"""
        start_row, start_col = start
        end_row, end_col = end

        piece = self.board[start_row][start_col]
        if not piece:
            return False

        # Check color if specified, otherwise use current player
        check_color = color if color is not None else self.current_player
        if piece.color != check_color:
            return False

        # Check if move puts own king in check
        if self.would_be_in_check(start, end, check_color):
            return False

        return piece.is_valid_move(start, end, self.board)

    def would_be_in_check(self, start, end, color=None):
        """Check if move would put own king in check"""
        # Make temporary move
        temp_board = copy.deepcopy(self)
        temp_board.move_piece(start, end)

        # Check if specified color's king is in check
        check_color = color if color is not None else self.current_player
        return temp_board.is_in_check(check_color)

    def is_in_check(self, color):
        """Check if king of given color is in check"""
        # Find king position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.symbol.lower() == 'k' and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        # Check if any enemy piece can attack the king
        opponent = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent:
                    if piece.is_valid_move((row, col), king_pos, self.board):
                        return True

        return False

    def get_all_valid_moves(self, color):
        """Get all valid moves for a given color"""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for end_row, end_col in piece.get_possible_moves((row, col), self.board):
                        if self.is_valid_move((row, col), (end_row, end_col), color):
                            moves.append(((row, col), (end_row, end_col)))
        return moves

    def is_checkmate(self, color):
        """Check if given color is in checkmate"""
        if not self.is_in_check(color):
            return False

        # If no valid moves, it's checkmate
        return len(self.get_all_valid_moves(color)) == 0

    def is_stalemate(self, color):
        """Check if given color is in stalemate"""
        if self.is_in_check(color):
            return False

        # If no valid moves, it's stalemate
        return len(self.get_all_valid_moves(color)) == 0

    def print_board(self):
        """Print the chess board"""
        print("\n   a b c d e f g h")
        print("  -----------------")
        for row in range(8):
            print(f"{8 - row} |", end="")
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    print(piece.symbol, end="|")
                else:
                    print(" |", end="")
            print(f" {8 - row}")

        print("  -----------------")
        print("   a b c d e f g h")

        # Show whose turn it is
        print(f"\n{self.current_player.title()}'s turn")
        if self.is_in_check(self.current_player):
            print("CHECK!")

    def algebraic_to_coords(self, move_str):
        """Convert algebraic notation (e.g., 'e2e4') to coordinates"""
        if len(move_str) != 4:
            return None

        try:
            col_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
            start_col = col_map[move_str[0]]
            start_row = 8 - int(move_str[1])
            end_col = col_map[move_str[2]]
            end_row = 8 - int(move_str[3])

            return (start_row, start_col), (end_row, end_col)
        except (KeyError, ValueError):
            return None

    def coords_to_algebraic(self, start, end):
        """Convert coordinates to algebraic notation"""
        row_map = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}
        col_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

        start_row, start_col = start
        end_row, end_col = end

        return f"{col_map[start_col]}{row_map[start_row]}{col_map[end_col]}{row_map[end_row]}"


class ChessBot:
    """AI bot for playing chess using minimax algorithm"""

    def __init__(self, color, difficulty=3):
        self.color = color
        self.difficulty = difficulty  # Depth of search

    def get_best_move(self, board):
        """Get the best move for the bot"""
        valid_moves = board.get_all_valid_moves(self.color)

        if not valid_moves:
            return None

        # For simple bot, just pick a random valid move
        if self.difficulty == 0:
            return random.choice(valid_moves)

        # Use minimax for more advanced bots
        best_move = None
        best_score = -math.inf if self.color == 'white' else math.inf

        for move in valid_moves:
            # Create temporary board state
            temp_board = copy.deepcopy(board)
            temp_board.move_piece(move[0], move[1])

            # Get score for this move
            score = self.minimax(temp_board, self.difficulty - 1, False,
                               -math.inf, math.inf)

            # Update best move
            if self.color == 'white':
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move

    def minimax(self, board, depth, maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        if depth == 0 or board.is_checkmate('white') or board.is_checkmate('black'):
            return self.evaluate_position(board)

        valid_moves = board.get_all_valid_moves(board.current_player)

        if maximizing:
            max_score = -math.inf
            for move in valid_moves:
                temp_board = copy.deepcopy(board)
                temp_board.move_piece(move[0], move[1])
                score = self.minimax(temp_board, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = math.inf
            for move in valid_moves:
                temp_board = copy.deepcopy(board)
                temp_board.move_piece(move[0], move[1])
                score = self.minimax(temp_board, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score

    def evaluate_position(self, board):
        """Evaluate the current position"""
        if board.is_checkmate('white'):
            return -10000  # Black wins
        elif board.is_checkmate('black'):
            return 10000   # White wins
        elif board.is_stalemate('white') or board.is_stalemate('black'):
            return 0       # Draw

        score = 0

        # Material values
        piece_values = {
            'p': 10, 'P': 10,  # Pawn
            'n': 30, 'N': 30,  # Knight
            'b': 30, 'B': 30,  # Bishop
            'r': 50, 'R': 50,  # Rook
            'q': 90, 'Q': 90,  # Queen
            'k': 900, 'K': 900 # King
        }

        # Count material
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece:
                    value = piece_values.get(piece.symbol, 0)
                    if piece.color == 'white':
                        score += value
                    else:
                        score -= value

        # Bonus for piece development (simplified)
        # Center control bonus
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in center_squares:
            piece = board.board[row][col]
            if piece:
                if piece.color == 'white':
                    score += 5
                else:
                    score -= 5

        # King safety (simplified)
        # Penalize if king is exposed
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.symbol.lower() == 'k':
                    # Count nearby pieces for protection
                    protection = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            r, c = row + dr, col + dc
                            if 0 <= r < 8 and 0 <= c < 8:
                                nearby = board.board[r][c]
                                if nearby and nearby.color == piece.color:
                                    protection += 1

                    if piece.color == 'white':
                        score += protection * 2
                    else:
                        score -= protection * 2

        return score


class ChessGame:
    """Main game class that manages the chess game"""

    def __init__(self, bot_difficulty=3):
        self.board = ChessBoard()
        self.bot = ChessBot('black', bot_difficulty)  # Bot plays as black
        self.game_over = False

    def play_move(self, move_str):
        """Play a move from player"""
        coords = self.board.algebraic_to_coords(move_str)
        if not coords:
            return False, "Invalid move format. Use format like 'e2e4'"

        start, end = coords
        if not self.board.is_valid_move(start, end):
            return False, "Invalid move"

        self.board.move_piece(start, end)

        # Check for game end
        if self.board.is_checkmate('black'):
            self.game_over = True
            return True, "Checkmate! You win!"
        elif self.board.is_stalemate('black'):
            self.game_over = True
            return True, "Stalemate! It's a draw."

        return True, "Move played successfully"

    def play_bot_move(self):
        """Make bot play a move"""
        bot_move = self.bot.get_best_move(self.board)
        if bot_move:
            start, end = bot_move
            self.board.move_piece(start, end)

            # Check for game end
            if self.board.is_checkmate('white'):
                self.game_over = True
                return "Checkmate! Bot wins!"
            elif self.board.is_stalemate('white'):
                self.game_over = True
                return "Stalemate! It's a draw."

            return f"Bot played: {self.board.coords_to_algebraic(start, end)}"

        self.game_over = True
        return "No moves available for bot"


def play_chess_game():
    """Main function to play chess game"""
    print("Welcome to Chess Game: Player vs Bot!")
    print("You play as White, Bot plays as Black")
    print("Enter moves in algebraic notation (e.g., 'e2e4')")
    print("Type 'quit' to exit the game")
    print("Type 'help' for help")
    print("-" * 50)

    # Ask for difficulty
    while True:
        try:
            difficulty = int(input("Select bot difficulty (0-5, 0=random, 5=hardest): "))
            if 0 <= difficulty <= 5:
                break
            print("Please enter a number between 0 and 5")
        except ValueError:
            print("Please enter a valid number")

    game = ChessGame(difficulty)

    while not game.game_over:
        # Display board
        game.board.print_board()

        # Get player move
        while True:
            move = input("Your move: ").strip().lower()

            if move == 'quit':
                print("Thanks for playing!")
                return
            elif move == 'help':
                print("Enter moves like 'e2e4' (from square to square)")
                print("Type 'quit' to exit")
                continue
            elif move == 'board':
                continue  # Will show board again

            success, message = game.play_move(move)
            if success:
                print(message)
                break
            else:
                print(f"Error: {message}")

        if game.game_over:
            break

        # Bot's turn
        print("\nBot is thinking...")
        bot_message = game.play_bot_move()
        print(bot_message)

        # Show board after bot move
        game.board.print_board()

    print("\nGame Over!")
    print("Thanks for playing!")


if __name__ == "__main__":
    play_chess_game()