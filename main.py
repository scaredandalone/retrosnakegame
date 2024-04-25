import pyxel
import enum
import time
import random
import collections


class Direction(enum.Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


#  game states
class GameState(enum.Enum):
    STARTUP = 0
    RUNNING = 1
    GAME_OVER = 2

class Level:
    def __init__(self):
        self.tm = 0
        self.u = 0
        self.v = 0
        self.w = 192
        self.h = 128

    def draw(self):
        pyxel.bltm(0, 0, 0, 0, 0, self.w, self.h)


class Apple:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, self.w, self.h)

    def intersects(self, u, v, w, h):
        is_intersected = False
        if (
            u + w > self.x
            and self.x + self.w > u
            and v + h > self.y
            and self.y + self.h > v
        ):
            is_intersected = True
        return is_intersected

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


class SnakeSection:
    def __init__(self, x, y, is_head=False):
        self.x = x
        self.y = y
        self.w = 8
        self.h = 8
        self.is_head = is_head

    def draw(self, direction):
        width = self.w
        height = self.h
        sprite_x = 0
        sprite_y = 0

        if self.is_head:
            if direction == Direction.RIGHT:
                sprite_x = 8
                sprite_y = 0
            if direction == Direction.LEFT:
                sprite_x = 8
                sprite_y = 0
                width = width * -1
            if direction == Direction.DOWN:
                sprite_x = 0
                sprite_y = 8
            if direction == Direction.UP:
                sprite_x = 0
                sprite_y = 8
                height = height * -1
        pyxel.blt(self.x, self.y, 0, sprite_x, sprite_y, width, height)

    def intersects(self, u, v, w, h):
        is_intersected = False
        if (
            u + w > self.x
            and self.x + self.w > u
            and v + h > self.y
            and self.y + self.h > v
        ):
            is_intersected = True
        return is_intersected


def right_text(text, page_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return page_width - (text_width + char_width)


def center_text(text, page_width, char_width=pyxel.FONT_WIDTH):
    text_width = len(text) * char_width
    return (page_width - text_width) // 2

class Hud:
    def __init__(self):
        self.title_text = "SNAKE"
        self.title_text_x = center_text(self.title_text, 196)
        self.score_text = str(0)
        self.score_text_x = center_text(self.score_text, 196)
        self.level_text = "Level 0"
        self.level_text_x = 10
        self.apples_text = "Apples "
        self.apples_text_x = len(self.level_text) * pyxel.FONT_WIDTH + self.level_text_x + 5

    def draw_title(self):
        pyxel.rect(self.title_text_x - 1, 0, len(self.title_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.title_text_x, 1, self.title_text, 12)

    def draw_score(self, score):
        self.score_text = str(score)
        self.score_text_x = right_text(self.score_text, 196)
        pyxel.rect(self.score_text_x - 11, 0, len(self.score_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.score_text_x - 10, 1, self.score_text, 3)

    def draw_level(self, level):
        self.level_text = "Level " + str(level)
        pyxel.rect(self.level_text_x - 1, 0, len(self.level_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.level_text_x, 1, self.level_text, 3)

    def draw_apples(self, apples):
        self.apples_text = "Apples " + str(apples)
        pyxel.rect(self.apples_text_x - 1, 0, len(self.apples_text) * pyxel.FONT_WIDTH + 1, pyxel.FONT_HEIGHT + 1, 1)
        pyxel.text(self.apples_text_x, 1, self.apples_text, 3)
class App:
    def __init__(self):
        pyxel.init(192, 128, display_scale=8, fps=60)
        pyxel.load("assets/assets.pyxres")
        self.current_game_state = GameState.STARTUP
        self.level = Level()
        self.hud = Hud()
        self.apple = Apple(64, 32)
        self.snake = []  # store snake sections
        self.snake.append(SnakeSection(32, 32, is_head=True))
        self.snake.append(SnakeSection(24, 32))
        self.snake.append(SnakeSection(16, 32))
        self.snake_direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 3
        self.time_last_frame = time.time()
        self.dt = 0
        self.time_since_last_move = 0
        self.score = 0
        self.apples_eaten_total = 0
        self.current_level = 1
        self.input_queue = collections.deque()  # store directions
        self.play_music = True
        if self.play_music:
            pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def start_new_game(self):
        self.current_game_state = GameState.RUNNING
        self.snake.clear()
        # Add initial snake to the game
        self.snake.append(SnakeSection(32, 32, is_head=True))
        self.snake.append(SnakeSection(24, 32))
        self.snake.append(SnakeSection(16, 32))
        self.snake_direction: Direction = Direction.RIGHT
        self.sections_to_add = 0
        self.speed = 3
        self.time_last_frame = time.time()
        self.dt = 0
        self.apples_eaten_total = 0
        self.score = 0
        self.time_since_last_move = 0
        self.input_queue.clear()
        self.move_apple()
        pyxel.stop()
        if self.play_music:
            pyxel.playm(0, loop=True)

    def update(self):
        time_this_frame = time.time()
        self.dt = time_this_frame - self.time_last_frame
        self.time_last_frame = time_this_frame
        self.time_since_last_move += self.dt
        self.check_input()
        if self.current_game_state == GameState.RUNNING:
            if self.time_since_last_move >= 1 / self.speed:
                self.time_since_last_move = 0
                self.move_snake()
                self.check_collisions()
                self.score += len(self.snake) * self.apples_eaten_total + 1

    def toggle_music(self):
        if self.play_music:
            self.play_music = False
            pyxel.stop()
        else:
            self.play_music = True

    def draw(self):
        pyxel.cls(0)
        self.level.draw()
        for s in self.snake:
            s.draw(self.snake_direction)
        self.hud.draw_title()
        self.hud.draw_score(self.score)
        self.hud.draw_level(self.current_level)
        self.hud.draw_apples(self.apples_eaten_total)

        if self.current_game_state == GameState.RUNNING:
            self.apple.draw()

        elif self.current_game_state == GameState.STARTUP:  # Draw startup screen
            title_text = "SNAKE"
            title_text_x = (pyxel.width - len(title_text) * pyxel.FONT_WIDTH) // 2
            pyxel.text(title_text_x, 50, title_text, 7)

            instruction_text = "Press Q to Start"
            instruction_text_x = (pyxel.width - len(instruction_text) * pyxel.FONT_WIDTH) // 2
            pyxel.text(instruction_text_x, 70, instruction_text, 7)
            return

        elif self.current_game_state == GameState.GAME_OVER:
            pyxel.text(50,50, "GAMEOVER! PRESS Q TO RESTART", 12)


        # pyxel.text(10, 114, str(self.current_game_state), 12)

    def check_collisions(self):
        if self.apple.intersects(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
            pyxel.play(3,3) #apple pickup sound
            self.speed += (self.speed * 0.1)
            self.sections_to_add += 4
            self.move_apple()
            self.apples_eaten_total += 1
        for s in self.snake:
            if s == self.snake[0]:
                continue
            if s.intersects(self.snake[0].x, self.snake[0].y, self.snake[0].w, self.snake[0].h):
                self.current_game_state = GameState.GAME_OVER
                pyxel.stop()
                pyxel.play(3, 1) # dead sound

        if pyxel.tilemap(0).pget(self.snake[0].x/8, self.snake[0].y/8)[0] == 3:
            pyxel.stop()
            pyxel.play(3, 1)  # dead sound
            self.current_game_state = GameState.GAME_OVER

    def move_apple(self):
        good_position = False
        while not good_position:
            new_x = random.randrange(8, 184, 8)
            new_y = random.randrange(8, 120, 8)
            good_position = True
            for s in self.snake:
                if (
                    new_x + 8 > s.x
                    and s.x + s.w > new_x
                    and new_y + 8 > s.y
                    and s.y + s.h > new_y
                ):
                    good_position = False
                    break
            # check wall

            # if pos good move, the apple.
            if good_position:
                self.apple.move(new_x, new_y)

    def move_snake(self):
        if len(self.input_queue):
            self.snake_direction = self.input_queue.popleft()
        # move the head
        if self.sections_to_add > 0:
            self.snake.append(SnakeSection(self.snake[-1].x, self.snake[-1].y))
            self.sections_to_add -= 1
        previous_location_x = self.snake[0].x
        previous_location_y = self.snake[0].y
        if self.snake_direction == Direction.RIGHT:
            self.snake[0].x += self.snake[0].w
        if self.snake_direction == Direction.LEFT:
            self.snake[0].x -= self.snake[0].w
        if self.snake_direction == Direction.DOWN:
            self.snake[0].y += self.snake[0].w
        if self.snake_direction == Direction.UP:
            self.snake[0].y -= self.snake[0].w
        # move the tail
        for s in self.snake:
            if s == self.snake[0]:
                continue
            current_location_x = s.x
            current_location_y = s.y
            s.x = previous_location_x
            s.y = previous_location_y
            previous_location_x = current_location_x
            previous_location_y = current_location_y

    def check_input(self):
        if self.current_game_state == GameState.GAME_OVER:
            if pyxel.btn(pyxel.KEY_Q):
                self.start_new_game()
        elif self.current_game_state == GameState.STARTUP:
            if pyxel.btn(pyxel.KEY_Q):
                self.start_new_game()
        if pyxel.btnp(pyxel.KEY_M):
            self.toggle_music()
        if pyxel.btn(pyxel.KEY_RIGHT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.LEFT and self.snake_direction != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
            else:
                if self.input_queue[-1] != Direction.LEFT and self.input_queue[-1] != Direction.RIGHT:
                    self.input_queue.append(Direction.RIGHT)
        elif pyxel.btn(pyxel.KEY_LEFT):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.RIGHT and self.snake_direction != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
            else:
                if self.input_queue[-1] != Direction.RIGHT and self.input_queue[-1] != Direction.LEFT:
                    self.input_queue.append(Direction.LEFT)
        elif pyxel.btn(pyxel.KEY_DOWN):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.UP and self.snake_direction != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
            else:
                if self.input_queue[-1] != Direction.UP and self.input_queue[-1] != Direction.DOWN:
                    self.input_queue.append(Direction.DOWN)
        elif pyxel.btn(pyxel.KEY_UP):
            if len(self.input_queue) == 0:
                if self.snake_direction != Direction.DOWN and self.snake_direction != Direction.UP:
                    self.input_queue.append(Direction.UP)
            else:
                if self.input_queue[-1] != Direction.DOWN and self.input_queue[-1] != Direction.UP:
                    self.input_queue.append(Direction.UP)


App()
