import random
import tkinter as tk


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=420, height=420, bg="#111827", highlightthickness=0)
        self.canvas.pack()

        self.root.bind("<KeyPress-Up>", self.change_direction)
        self.root.bind("<KeyPress-Down>", self.change_direction)
        self.root.bind("<KeyPress-Left>", self.change_direction)
        self.root.bind("<KeyPress-Right>", self.change_direction)
        self.root.bind("<KeyPress-w>", self.change_direction)
        self.root.bind("<KeyPress-s>", self.change_direction)
        self.root.bind("<KeyPress-a>", self.change_direction)
        self.root.bind("<KeyPress-d>", self.change_direction)

        self.score = 0
        self.running = True
        self.direction = "Right"
        self.next_direction = "Right"
        self.block_size = 20
        self.speed = 120

        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.food = self.spawn_food()

        self.score_text = self.canvas.create_text(10, 10, text=f"점수: {self.score}", anchor="nw", fill="white", font=("Malgun Gothic", 12, "bold"))
        self.message_text = None

        self.update()

    def spawn_food(self):
        while True:
            x = random.randint(0, 19)
            y = random.randint(0, 19)
            if (x, y) not in self.snake:
                return x, y

    def change_direction(self, event):
        if not self.running:
            return

        key_map = {
            "Up": "Up",
            "w": "Up",
            "Down": "Down",
            "s": "Down",
            "Left": "Left",
            "a": "Left",
            "Right": "Right",
            "d": "Right",
        }

        new_dir = key_map.get(event.keysym)
        if new_dir is None:
            return

        opposite = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left",
        }

        if opposite.get(new_dir) != self.direction:
            self.next_direction = new_dir

    def update(self):
        if not self.running:
            return

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]
        if self.direction == "Up":
            new_head = (head_x, head_y - 1)
        elif self.direction == "Down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "Left":
            new_head = (head_x - 1, head_y)
        else:
            new_head = (head_x + 1, head_y)

        if (new_head[0] < 0 or new_head[0] >= 20 or new_head[1] < 0 or new_head[1] >= 20 or
                new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.canvas.itemconfigure(self.score_text, text=f"점수: {self.score}")
            self.food = self.spawn_food()
            self.speed = max(60, self.speed - 2)
        else:
            self.snake.pop()

        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 420, 420, fill="#111827", outline="")

        for x, y in self.snake:
            self.canvas.create_rectangle(
                x * self.block_size,
                y * self.block_size,
                x * self.block_size + self.block_size - 2,
                y * self.block_size + self.block_size - 2,
                fill="#34D399",
                outline="#0F766E",
            )

        fx, fy = self.food
        self.canvas.create_rectangle(
            fx * self.block_size,
            fy * self.block_size,
            fx * self.block_size + self.block_size - 2,
            fy * self.block_size + self.block_size - 2,
            fill="#F472B6",
            outline="#BE185D",
        )

        self.canvas.create_text(10, 10, text=f"점수: {self.score}", anchor="nw", fill="white", font=("Malgun Gothic", 12, "bold"))

        self.root.after(self.speed, self.update)

    def game_over(self):
        self.running = False
        if self.message_text is not None:
            self.canvas.delete(self.message_text)
        self.message_text = self.canvas.create_text(
            210, 210,
            text=f"게임 오버!\n최종 점수: {self.score}\nF5로 다시 실행하세요.",
            fill="white",
            justify="center",
            font=("Malgun Gothic", 14, "bold"),
        )


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
