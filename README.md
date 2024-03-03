

# Connect Four GUI Game

This project is a Python implementation of the classic game Connect Four with a graphical user interface (GUI) powered by tkinter. Players take turns dropping colored discs from the top into a seven-column, six-row vertically suspended grid. The first player to form a horizontal, vertical, or diagonal line of four of their own discs wins the game.

## Features

- **Graphical User Interface**: Play Connect Four in a visually appealing setup with easy mouse clicks to drop pieces.
- **Monte Carlo Tree Search AI**: Includes an AI opponent that uses the Monte Carlo Tree Search (MCTS) algorithm to decide on moves.
- **Customizable Settings**: Default game settings can be easily adjusted within the code, including the starting player and grid dimensions.

## Requirements

To run this game, you need:

- Python 3.x
- tkinter (usually comes with Python)

## Installation

No installation is required. Ensure you have Python and tkinter installed on your system.

## How to Play

1. Clone or download this repository to your local machine.
2. Navigate to the directory containing the game files.
3. Run the game with Python:

    ```bash
    python main.py
    ```

4. The game window will open. Click on the column where you wish to drop your piece.
5. Play against the AI or another player, depending on the game mode set in the code.

## Customization

You can customize the game settings by modifying the `ConnectFour` class parameters in `connect_four_gui.py`. This includes changing the board dimensions and the starting player.

## AI and Game Mechanics

- The game includes an AI player using the Monte Carlo Tree Search algorithm to calculate its moves. 
- The game follows standard Connect Four rules where the goal is to connect four of your pieces vertically, horizontally, or diagonally before your opponent.
