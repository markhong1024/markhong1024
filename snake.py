import random
import tkinter as tk


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("AI vs Human Snake")
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

        self.running = True
        self.block_size = 20
        self.speed = 140
        self.grid_size = 20

        self.human_snake = [(8, 8), (7, 8), (6, 8)]
        self.ai_snake = [(12, 12), (13, 12), (14, 12)]
        self.human_direction = "Right"
        self.next_human_direction = "Right"
        self.ai_direction = "Left"

        self.human_score = 0
        self.ai_score = 0
        self.food = self.spawn_food()
        self.message_text = None

        self.update()

    def spawn_food(self):
        occupied = set(self.human_snake) | set(self.ai_snake)
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
            if (x, y) not in occupied:
                return x, y

    def change_direction(self, event):
        if not self.running:
            return

        key_map = {
            "Up": "Up", "w": "Up",
            "Down": "Down", "s": "Down",
            "Left": "Left", "a": "Left",
            "Right": "Right", "d": "Right",
        }
        new_dir = key_map.get(event.keysym)
        if new_dir is None:
            return

        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if opposite.get(new_dir) != self.human_direction:
            self.next_human_direction = new_dir

    def move_snake(self, snake, direction):
        head_x, head_y = snake[0]
        if direction == "Up":
            new_head = (head_x, head_y - 1)
        elif direction == "Down":
            new_head = (head_x, head_y + 1)
        elif direction == "Left":
            new_head = (head_x - 1, head_y)
        else:
            new_head = (head_x + 1, head_y)
        return new_head

    def is_collision(self, new_head, snake_body, other_snake):
        return (
            new_head[0] < 0
            or new_head[0] >= self.grid_size
            or new_head[1] < 0
            or new_head[1] >= self.grid_size
            or new_head in snake_body
            or new_head in other_snake
        )

    def choose_ai_direction(self):
        head = self.ai_snake[0]
        directions = ["Up", "Down", "Left", "Right"]
        opposite = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        candidates = []

        for direction in directions:
            if opposite.get(direction) == self.ai_direction:
                continue
            new_head = self.move_snake(self.ai_snake, direction)
            if self.is_collision(new_head, self.ai_snake, self.human_snake):
                continue

            dx = new_head[0] - self.food[0]
            dy = new_head[1] - self.food[1]
            distance = abs(dx) + abs(dy)
            candidates.append((distance, direction, new_head))

        if not candidates:
            for direction in directions:
                if opposite.get(direction) == self.ai_direction:
                    continue
                new_head = self.move_snake(self.ai_snake, direction)
                if not self.is_collision(new_head, self.ai_snake, self.human_snake):
                    candidates.append((0, direction, new_head))

        if not candidates:
            return self.ai_direction

        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][1]

    def update(self):
        if not self.running:
            return

        self.human_direction = self.next_human_direction
        human_new_head = self.move_snake(self.human_snake, self.human_direction)
        self.ai_direction = self.choose_ai_direction()
        ai_new_head = self.move_snake(self.ai_snake, self.ai_direction)

        human_dead = self.is_collision(human_new_head, self.human_snake, self.ai_snake)
        ai_dead = self.is_collision(ai_new_head, self.ai_snake, self.human_snake)

        if not human_dead:
            self.human_snake.insert(0, human_new_head)
            if human_new_head == self.food:
                self.human_score += 10
                self.food = self.spawn_food()
            else:
                self.human_snake.pop()

        if not ai_dead:
            self.ai_snake.insert(0, ai_new_head)
            if ai_new_head == self.food:
                self.ai_score += 10
                self.food = self.spawn_food()
            else:
                self.ai_snake.pop()

        if human_dead and ai_dead:
            self.game_over("무승부!")
            return
        if human_dead:
            self.game_over("AI 승리!")
            return
        if ai_dead:
            self.game_over("당신의 승리!")
            return

        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 420, 420, fill="#111827", outline="")

        for x, y in self.human_snake:
            self.canvas.create_rectangle(
                x * self.block_size, y * self.block_size,
                x * self.block_size + self.block_size - 2,
                y * self.block_size + self.block_size - 2,
                fill="#34D399", outline="#0F766E"
            )

        for x, y in self.ai_snake:
            self.canvas.create_rectangle(
                x * self.block_size, y * self.block_size,
                x * self.block_size + self.block_size - 2,
                y * self.block_size + self.block_size - 2,
                fill="#FBBF24", outline="#B45309"
            )

        fx, fy = self.food
        self.canvas.create_rectangle(
            fx * self.block_size, fy * self.block_size,
            fx * self.block_size + self.block_size - 2,
            fy * self.block_size + self.block_size - 2,
            fill="#F472B6", outline="#BE185D"
        )

        self.canvas.create_text(10, 10, text=f"당신: {self.human_score}   AI: {self.ai_score}", anchor="nw", fill="white", font=("Malgun Gothic", 12, "bold"))
        self.root.after(self.speed, self.update)

    def game_over(self, text):
        self.running = False
        if self.message_text is not None:
            self.canvas.delete(self.message_text)
        self.message_text = self.canvas.create_text(
            210, 210,
            text=f"{text}\n최종 점수: 당신 {self.human_score} : AI {self.ai_score}\nF5로 다시 실행하세요.",
            fill="white", justify="center", font=("Malgun Gothic", 14, "bold")
        )


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
