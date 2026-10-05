import tkinter as tk
import random

CELL = 30
COLS = 10
ROWS = 20
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]]
]

COLORS = [
    "cyan",
    "yellow",
    "purple",
    "green",
    "red",
    "blue",
    "orange"
]


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Tetris")

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="black"
        )
        self.canvas.pack()

        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]

        self.score = 0
        self.game_over = False

        self.new_piece()

        root.bind("<Left>", self.move_left)
        root.bind("<Right>", self.move_right)
        root.bind("<Down>", self.move_down)
        root.bind("<Up>", self.rotate)
        root.bind("<space>", self.hard_drop)

        self.update_game()

    def new_piece(self):
        index = random.randint(0, len(SHAPES) - 1)

        self.shape = SHAPES[index]
        self.color = COLORS[index]

        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

        if not self.valid_position(self.x, self.y, self.shape):
            self.game_over = True

    def valid_position(self, new_x, new_y, shape):
        for y, row in enumerate(shape):
            for x, value in enumerate(row):
                if value:
                    board_x = new_x + x
                    board_y = new_y + y

                    if board_x < 0 or board_x >= COLS:
                        return False

                    if board_y >= ROWS:
                        return False

                    if board_y >= 0 and self.board[board_y][board_x]:
                        return False

        return True

    def move_left(self, event=None):
        if self.valid_position(self.x - 1, self.y, self.shape):
            self.x -= 1
            self.draw()

    def move_right(self, event=None):
        if self.valid_position(self.x + 1, self.y, self.shape):
            self.x += 1
            self.draw()

    def move_down(self, event=None):
        if self.valid_position(self.x, self.y + 1, self.shape):
            self.y += 1
        else:
            self.lock_piece()

        self.draw()

    def rotate(self, event=None):
        rotated = [list(row) for row in zip(*self.shape[::-1])]

        if self.valid_position(self.x, self.y, rotated):
            self.shape = rotated

        self.draw()

    def hard_drop(self, event=None):
        while self.valid_position(self.x, self.y + 1, self.shape):
            self.y += 1

        self.lock_piece()
        self.draw()

    def lock_piece(self):
        for y, row in enumerate(self.shape):
            for x, value in enumerate(row):
                if value:
                    board_x = self.x + x
                    board_y = self.y + y

                    if 0 <= board_y < ROWS:
                        self.board[board_y][board_x] = self.color

        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        new_board = []

        lines_cleared = 0

        for row in self.board:
            if all(row):
                lines_cleared += 1
            else:
                new_board.append(row)

        for _ in range(lines_cleared):
            new_board.insert(0, [None for _ in range(COLS)])

        self.board = new_board
        self.score += lines_cleared * 100

    def draw(self):
        self.canvas.delete("all")

        for y in range(ROWS):
            for x in range(COLS):

                x1 = x * CELL
                y1 = y * CELL
                x2 = x1 + CELL
                y2 = y1 + CELL

                color = self.board[y][x]

                if color:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=color,
                        outline="gray"
                    )
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="black",
                        outline="#222"
                    )

        if not self.game_over:
            for y, row in enumerate(self.shape):
                for x, value in enumerate(row):
                    if value:
                        x1 = (self.x + x) * CELL
                        y1 = (self.y + y) * CELL
                        x2 = x1 + CELL
                        y2 = y1 + CELL

                        self.canvas.create_rectangle(
                            x1, y1, x2, y2,
                            fill=self.color,
                            outline="white"
                        )

        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            text=f"Score: {self.score}",
            fill="white",
            font=("Arial", 16)
        )

        if self.game_over:
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2,
                text="GAME OVER",
                fill="white",
                font=("Arial", 28, "bold")
            )

    def update_game(self):
        if not self.game_over:
            self.move_down()
            self.root.after(500, self.update_game)
        else:
            self.draw()


root = tk.Tk()
game = Tetris(root)
root.mainloop()