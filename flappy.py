import random

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = -0.5
JUMP_SPEED = 10


class FlappyBirdGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Flappy Bird Game")
        self.bird = None
        self.pipe_list = None
        self.score = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.bird = Bird("planeRed1.png", center_x=100, center_y=SCREEN_HEIGHT // 2)
        self.pipe_list = arcade.SpriteList()
        self.score = 0

    def on_draw(self):
        arcade.start_render()
        self.bird.draw()
        self.pipe_list.draw()

        arcade.draw_text(f"Score: {int(self.score)}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

    def on_update(self, delta_time):
        self.bird.update()
        if self.bird.bottom < 0:
            self.bird.bottom = 0
            self.bird.change_y = 0
            self.game_over()

        self.generate_pipes()
        self.pipe_list.move(change_x=-2, change_y=0)
        for pipe in self.pipe_list:
            if pipe.right <= 0:
                pipe.remove_from_sprite_lists()
                self.score += 0.5

        if arcade.check_for_collision_with_list(self.bird, self.pipe_list):
            self.game_over()

    def generate_pipes(self):
        if len(self.pipe_list) < 2 or (self.pipe_list and self.pipe_list[-1].center_x < SCREEN_WIDTH - 300):
            possible_offsets = [-100, -75, -50, -25, 0, 25, 50, 75, 100]
            offset = random.choice(possible_offsets)

            upper_pipe = arcade.Sprite("pipeGreen_03.png", center_x=SCREEN_WIDTH + 50)
            upper_pipe.top = SCREEN_HEIGHT + 200 - offset

            lower_pipe = arcade.Sprite("pipeGreen_03.png", center_x=SCREEN_WIDTH + 50)
            lower_pipe.top = 0 + 100 - offset

            upper_pipe.angle = 180

            self.pipe_list.append(upper_pipe)
            self.pipe_list.append(lower_pipe)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.bird.change_y = JUMP_SPEED

    def game_over(self):
        print("Game Over!")
        self.bird.kill()
        self.pipe_list.clear()
        arcade.exit()


class Bird(arcade.Sprite):
    def __init__(self, filename, center_x, center_y):
        super().__init__(filename)
        self.center_x = center_x
        self.center_y = center_y

    def update(self):
        self.center_y += self.change_y
        self.change_y += GRAVITY

        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
            self.change_y = 0


if __name__ == "__main__":
    game = FlappyBirdGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()
