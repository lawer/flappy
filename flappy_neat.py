import random

import arcade
import neat
from aitk.algorithms.neat import visualize

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = -0.5
JUMP_SPEED = 10
GAME = None


class FlappyBirdGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Flappy Bird Game")
        self.birds = None
        self.pipe_list = None
        self.score = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self, genomes, config):
        self.birds = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()
        for genome_id, genome in genomes:
            genome.fitness = 0
            bird = Bird(
                "planeRed1.png", center_x=100, center_y=SCREEN_HEIGHT // 2, genome=genome,
                conf=config, pipe_list=self.pipe_list
            )
            self.birds.append(bird)
        self.score = 0

    def on_draw(self):
        arcade.start_render()
        self.birds.draw()
        self.pipe_list.draw()

        arcade.draw_text(f"Score: {int(self.score)}", 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 18)

    def on_update(self, delta_time):
        self.birds.update()

        for bird in self.birds:
            if bird.bottom < 0 or arcade.check_for_collision_with_list(bird, self.pipe_list):
                bird.bottom = 0
                bird.change_y = 0

                bird.genome.fitness += self.score * 5
                bird.kill()

        if not self.birds:
            self.game_over()

        self.generate_pipes()
        self.pipe_list.move(change_x=-2, change_y=0)
        for pipe in self.pipe_list:
            if pipe.right <= 0:
                pipe.remove_from_sprite_lists()
                self.score += 0.5

    def generate_pipes(self):
        if len(self.pipe_list) < 2 or (self.pipe_list and self.pipe_list[-1].center_x < SCREEN_WIDTH - 300):
            possible_offsets = [-125, -100, -75, -50, -25, 0, 25, 50, 75, 100]
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
        self.pipe_list.clear()
        arcade.exit()


class Bird(arcade.Sprite):
    def __init__(self, filename, center_x, center_y, genome, conf, pipe_list=None):
        super().__init__(filename)
        self.center_x = center_x
        self.center_y = center_y
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, conf)
        self.pipe_list = pipe_list
        self.is_jumping = False

    def update(self):
        if len(self.pipe_list):
            next_pipe = self.pipe_list[0] if self.pipe_list[0].right > self.center_x else self.pipe_list[2]

            output = self.net.activate(
                (
                    self.center_y,
                    next_pipe.left, next_pipe.bottom,
                )
            )
            self.genome.fitness += 0.1
            if output[0] > 0:
                self.change_y = JUMP_SPEED

            self.center_y += self.change_y
            self.change_y += GRAVITY

        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
            self.change_y = 0


def eval_genomes(genomes, config):
    global GAME

    GAME.setup(genomes, config)
    arcade.run()


def run_neat():
    global GAME

    config_path = "config-file.txt"  # Reemplaza con la ruta de tu archivo de configuración NEAT
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    population.add_reporter(neat.Checkpointer(1))

    GAME = FlappyBirdGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    winner = population.run(eval_genomes, 50)  # Ajusta el número de generaciones según tus necesidades

    # Puedes hacer lo que quieras con el ganador, como guardarlo en un archivo para su uso posterior
    print("Best genome:\n", winner)

    visualize.draw_net(config, winner, True)


if __name__ == "__main__":
    run_neat()
