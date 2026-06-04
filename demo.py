import tkinter as tk


class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Breakout Game")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=800, height=600, bg="#111827")
        self.canvas.pack()

        self.canvas.bind("<KeyPress-Left>", self.move_left)
        self.canvas.bind("<KeyPress-Right>", self.move_right)
        self.canvas.bind("<KeyRelease-Left>", self.stop_left)
        self.canvas.bind("<KeyRelease-Right>", self.stop_right)
        self.canvas.bind("<KeyPress-a>", self.move_left)
        self.canvas.bind("<KeyPress-A>", self.move_left)
        self.canvas.bind("<KeyPress-d>", self.move_right)
        self.canvas.bind("<KeyPress-D>", self.move_right)
        self.canvas.bind("<KeyRelease-a>", self.stop_left)
        self.canvas.bind("<KeyRelease-A>", self.stop_left)
        self.canvas.bind("<KeyRelease-d>", self.stop_right)
        self.canvas.bind("<KeyRelease-D>", self.stop_right)
        self.canvas.focus_set()

        self.score = 0
        self.lives = 1
        self.game_over = False

        self.paddle = self.canvas.create_rectangle(350, 560, 450, 575, fill="#60A5FA", outline="")
        self.ball = self.canvas.create_oval(390, 300, 410, 320, fill="#F472B6", outline="")

        self.ball_dx = 2
        self.ball_dy = -2
        self.paddle_dx = 0

        self.bricks = []
        self.create_bricks()

        self.score_text = self.canvas.create_text(90, 20, text=f"점수: {self.score}", fill="white", anchor="w", font=("Malgun Gothic", 12, "bold"))
        self.lives_text = self.canvas.create_text(700, 20, text=f"생명: {self.lives}", fill="white", anchor="w", font=("Malgun Gothic", 12, "bold"))
        self.message = None

        self.update()

    def create_bricks(self):
        cols = 8
        rows = 5
        brick_w = 90
        brick_h = 25
        start_x = 40
        start_y = 60
        colors = ["#F87171", "#FB7185", "#FBBF24", "#34D399", "#60A5FA"]

        for r in range(rows):
            for c in range(cols):
                x1 = start_x + c * (brick_w + 10)
                y1 = start_y + r * (brick_h + 8)
                x2 = x1 + brick_w
                y2 = y1 + brick_h
                brick = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[r % len(colors)], outline="")
                self.bricks.append(brick)

    def move_left(self, event):
        self.paddle_dx = -12

    def move_right(self, event):
        self.paddle_dx = 12

    def stop_left(self, event):
        if self.paddle_dx < 0:
            self.paddle_dx = 0

    def stop_right(self, event):
        if self.paddle_dx > 0:
            self.paddle_dx = 0

    def update(self):
        if self.game_over:
            return

        paddle = self.canvas.coords(self.paddle)
        new_x = paddle[0] + self.paddle_dx

        if new_x < 0:
            new_x = 0
        if new_x > 700:
            new_x = 700

        self.canvas.move(self.paddle, new_x - paddle[0], 0)

        ball = self.canvas.coords(self.ball)
        x1, y1, x2, y2 = ball
        new_x = x1 + self.ball_dx
        new_y = y1 + self.ball_dy

        if new_x <= 0 or new_x >= 790:
            self.ball_dx *= -1
            new_x = max(0, min(790, new_x))

        if new_y <= 0:
            self.ball_dy *= -1
            new_y = 0

        paddle = self.canvas.coords(self.paddle)
        if y2 >= paddle[1] and y1 <= paddle[3] and x2 >= paddle[0] and x1 <= paddle[2]:
            paddle_center = (paddle[0] + paddle[2]) / 2
            ball_center = (x1 + x2) / 2
            hit_pos = (ball_center - paddle[0]) / (paddle[2] - paddle[0])

            self.ball_dy = -abs(self.ball_dy)
            self.ball_dx = int((hit_pos - 0.5) * 10)

            if self.ball_dx == 0:
                self.ball_dx = 1 if ball_center > paddle_center else -1

            new_y = paddle[1] - 20

        if new_y >= 600:
            self.lives -= 1
            self.canvas.itemconfigure(self.lives_text, text=f"생명: {self.lives}")
            if self.lives <= 0:
                self.end_game("게임 오버! 다시 시작하려면 F5를 눌러 실행하세요.")
                return
            self.reset_ball()
            return

        for brick in list(self.bricks):
            b = self.canvas.coords(brick)
            if x2 >= b[0] and x1 <= b[2] and y2 >= b[1] and y1 <= b[3]:
                self.canvas.delete(brick)
                self.bricks.remove(brick)
                self.score += 10
                self.canvas.itemconfigure(self.score_text, text=f"점수: {self.score}")

                if x2 >= b[2] or x1 <= b[0]:
                    self.ball_dx *= -1
                else:
                    self.ball_dy *= -1
                break

        if not self.bricks:
            self.end_game("축하합니다! 모든 블록을 깨뜨렸습니다.")
            return

        self.canvas.coords(self.ball, new_x, new_y, new_x + 20, new_y + 20)
        self.root.after(16, self.update)

    def reset_ball(self):
        self.canvas.coords(self.ball, 390, 300, 410, 320)
        self.ball_dx = 4
        self.ball_dy = -4
        self.root.after(500, self.update)

    def end_game(self, text):
        self.game_over = True
        if self.message is not None:
            self.canvas.delete(self.message)
        self.message = self.canvas.create_text(400, 300, text=text, fill="white", font=("Malgun Gothic", 16, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    BreakoutGame(root)
    root.mainloop()

