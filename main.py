# tkinter is used to show GUI application
import tkinter as tk
from tkinter import messagebox
import random
import math


# This class represents a connect four board.
# It supports the functions that are used in the minimax and MCTS algorithms.
# Feel free to add to it, or to change it in any way you see fit.

class ConnectFour:
    EMPTY = 0
    NONE = -1
    BLACK = 1
    WHITE = -1
    DRAW = 0
    ONGOING = -17

    # Initializes an empty connect four board. There are default values for the
    # number of rows and columns and the first player.
    def __init__(self, rows=6, columns=7, first_player=BLACK):
        self.rows = rows
        self.columns = columns
        self.board = [[self.EMPTY for _ in range(columns)] for _ in range(rows)]
        self.current_player = first_player
        self.column_heights = [0 for _ in range(columns)]
        self.game_history = []  # This turns out to be useful to have

    @staticmethod
    def other_player(player):
        return ConnectFour.BLACK if player == ConnectFour.WHITE else ConnectFour.WHITE

    def clone(self):
        copy = ConnectFour(self.rows, self.columns)
        copy.current_player = self.current_player
        copy.board = [row[:] for row in self.board]  # Deep copy of the board
        copy.column_heights = self.column_heights[:]  # Deep copy of the column heights
        copy.game_history = self.game_history[:]   # Deep copy of the game history
        return copy

    def make_move(self, column):
        """Places a piece in the lowest available space of the chosen column."""
        if 0 <= column < self.columns and self.column_heights[column] < self.rows:
            for row in range(self.rows):
                if self.board[row][column] == self.EMPTY:
                    self.board[row][column] = self.current_player
                    self.column_heights[column] += 1
                    self.game_history.append(column)
                    self.current_player = self.other_player(self.current_player)
                    break

    def unmake_move(self):
        if len(self.game_history) > 0:
            move = self.game_history.pop()
            self.column_heights[move] -= 1
            self.board[self.column_heights[move]][move] = self.EMPTY
            self.current_player = self.other_player(self.current_player)

    def legal_moves(self):
        return [column for column in range(self.columns) if self.column_heights[column] < self.rows]

    # Returns the outcome of the game, which can be:
    # WHITE if white won (red here)
    # BLACK if black won
    # DRAW if the game concluded with no winner
    # ONGOING if the game is still in progress
    def outcome(self):
        if not self.game_history:
            return self.ONGOING
        # This was the trickiest function to write.
        # For better efficiency, I am assuming that if the game ended
        # then the last move created a four in a row. So we just check if
        # the last move takes part in a row of length 4 (or more).
        last_move = self.game_history[-1]
        x = self.column_heights[last_move] - 1
        y = last_move
        player = self.board[x][y]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

        for dx, dy in directions:
            count = 1
            i = 1
            while 0 <= x + i * dx < self.rows and 0 <= y + i * dy < self.columns and self.board[x + i * dx][
                y + i * dy] == player:
                count += 1
                i += 1
            i = 1
            while 0 <= x - i * dx < self.rows and 0 <= y - i * dy < self.columns and self.board[x - i * dx][
                y - i * dy] == player:
                count += 1
                i += 1
            if count >= 4:
                return player

        if len(self.game_history) == self.rows * self.columns:
            return self.DRAW

        return self.ONGOING

    def __str__(self):
        result = ""
        for row in reversed(self.board):
            result += "|" + "|".join("XO "[cell] for cell in row) + "|\n"
        result += "-" * (self.columns * 2 + 1) + "\n"
        result += " " + " ".join(map(str, range(self.columns)))
        return result


class MCTSNode:
    def __init__(self, game_state, move=None, parent=None):
        self.game_state = game_state
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game_state.legal_moves()

    def uct_select_child(self):
        log_parent_visits = math.log(self.visits)
        return max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * log_parent_visits / c.visits))

    def add_child(self, move, game_state):
        child_node = MCTSNode(game_state=game_state.clone(), move=move, parent=self)
        self.untried_moves.remove(move)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        self.visits += 1
        self.wins += result


# represent a node in the Monte Carlo Tree Search (MCTS) for game decision-making
class MCTSPlayer:
    def __init__(self, iterations=1000, exploration_weight=1.41):
        self.iterations = iterations
        self.exploration_weight = exploration_weight

    def choose_move(self, game_state):
        root = MCTSNode(game_state=game_state.clone())

        for _ in range(self.iterations):
            node = root
            state = game_state.clone()

            # Selection
            while node.untried_moves == [] and node.children != []:
                node = node.uct_select_child()
                state.make_move(node.move)

            # Expansion
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                state.make_move(move)
                node = node.add_child(move, state.clone())

            # Simulation
            while state.legal_moves():
                state.make_move(random.choice(state.legal_moves()))

            # Backpropagation
            result = state.outcome()
            while node:
                node.update(1 if result == node.game_state.current_player else 0)
                node = node.parent

        return max(root.children, key=lambda c: c.visits).move


class ConnectFourGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Connect Four")
        self.game = ConnectFour()
        self.ai_player = MCTSPlayer(iterations=500)
        self.players = {ConnectFour.BLACK: "human", ConnectFour.WHITE: "AI"}  # Player type: "human" or "AI"
        self.columns = 7
        self.rows = 6
        self.cell_size = 60
        self.canvas = tk.Canvas(master, width=self.columns * self.cell_size, height=self.rows * self.cell_size,
                                bg="blue")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.player_move)
        self.draw_board()

    def draw_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white", tags=f"{row},{col}")

    def update_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                tag = f"{row},{col}"
                piece = self.game.board[row][col]
                color = "white"
                if piece == ConnectFour.BLACK:
                    color = "black"
                elif piece == ConnectFour.WHITE:
                    color = "red"
                self.canvas.itemconfig(tag, fill=color)

    def player_move(self, event):
        if self.game.current_player == ConnectFour.BLACK and self.players[ConnectFour.BLACK] == "human":
            self.handle_move(event)
        elif self.game.current_player == ConnectFour.WHITE and self.players[ConnectFour.WHITE] == "human":
            self.handle_move(event)

    def handle_move(self, event):
        col = event.x // self.cell_size
        if col in self.game.legal_moves():
            self.game.make_move(col)
            self.update_board()
            if self.game.outcome() == ConnectFour.ONGOING and self.players[self.game.current_player] == "AI":
                self.master.after(100, self.ai_move)
            else:
                self.check_game_over()

    def ai_move(self):
        move = self.ai_player.choose_move(self.game)
        self.game.make_move(move)
        self.update_board()
        self.check_game_over()

    def check_game_over(self):
        result = self.game.outcome()
        if result != ConnectFour.ONGOING:
            if result == ConnectFour.DRAW:
                messagebox.showinfo("Game Over", "The game is a draw!")
            else:
                winner = "Black" if result == ConnectFour.BLACK else "Red"
                messagebox.showinfo("Game Over", f"{winner} wins!")
            self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()
