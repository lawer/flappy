import random

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = -0.5
JUMP_SPEED = 10


class FlappyBirdGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Flappy Bird Game")

        self.bird = arcade.Sprite("planeRed1.png", center_x=100, center_y=SCREEN_HEIGHT // 2)
        self.pipe_list = arcade.SpriteList()
        self.is_jumping = False
        self.score = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        arcade.start_render()
        self.bird.draw()
        self.pipe_list.draw()

        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

    def on_update(self, delta_time):
        self.bird.center_y += self.bird.change_y
        self.bird.change_y += GRAVITY

        if self.bird.top > SCREEN_HEIGHT:
            self.bird.top = SCREEN_HEIGHT
            self.bird.change_y = 0

        if self.bird.bottom < 0:
            self.bird.bottom = 0
            self.bird.change_y = 0
            self.game_over()

        self.generate_pipes()
        self.pipe_list.update()

        for pipe in self.pipe_list:
            pipe.center_x -= 2
            if arcade.check_for_collision(self.bird, pipe):
                self.game_over()

            if pipe.right <= 0:
                pipe.remove_from_sprite_lists()
                self.score += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.bird.change_y = JUMP_SPEED

    def game_over(self):
        print("Game Over!")
        self.bird.kill()
        self.pipe_list.clear()
        arcade.exit()

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


if __name__ == "__main__":
    game = FlappyBirdGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()
