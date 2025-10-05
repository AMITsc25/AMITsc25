# Chess Game: Player vs Bot

A console-based chess game where you can play against an AI opponent with adjustable difficulty levels.

## Features

- **Complete Chess Engine**: Full implementation of chess rules including castling, en passant, pawn promotion, check, checkmate, and stalemate
- **AI Opponent**: Bot with minimax algorithm and alpha-beta pruning for intelligent play
- **Multiple Difficulty Levels**: Choose from 6 difficulty levels (0=random moves, 5=advanced AI)
- **Interactive Console Interface**: Easy-to-use algebraic notation input
- **Game State Validation**: Prevents illegal moves and detects game-ending conditions

## How to Play

1. Run the game: `python3 chess_game.py`
2. Select bot difficulty (0-5)
3. Enter moves in algebraic notation (e.g., `e2e4`)
4. Type `help` for instructions or `quit` to exit

## Game Rules

- You play as White, bot plays as Black
- White moves first
- Enter moves like `e2e4` (from square to square)
- The game detects check, checkmate, and stalemate
- Bot uses strategic evaluation including material count, center control, and king safety

## Difficulty Levels

- **0**: Random valid moves (fastest)
- **1-2**: Basic evaluation (quick)
- **3-4**: Intermediate strategy (moderate)
- **5**: Advanced AI with deeper search (slowest but strongest)

## File Structure

- `chess_game.py`: Main game implementation with all chess logic
- `test_chess.py`: Test suite to verify game functionality

## Technical Implementation

- **Piece Classes**: Individual classes for each piece type with movement logic
- **Board Representation**: 8x8 grid with coordinate system
- **Minimax Algorithm**: AI uses minimax with alpha-beta pruning for move selection
- **Position Evaluation**: Considers material balance, center control, and king safety
- **Move Validation**: Comprehensive checking for legal moves and game state

Enjoy your game!