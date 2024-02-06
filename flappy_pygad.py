import random

import arcade
import tensorflow as tf

tf.compat.v1.disable_eager_execution()

import keras
import pygad
import pygad.kerasga

SCALE = 0.5

SCREEN_WIDTH = 800 * SCALE
SCREEN_HEIGHT = 600 * SCALE
GRAVITY = -0.5 * SCALE
JUMP_SPEED = 5 * SCALE
GAME = None
GA_INSTANCE = None
KERAS_GA = None
MODEL = None


class FlappyBirdGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Flappy Bird Game")
        self.birds = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()
        self.score = 0

        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self, solutions):
        self.birds = arcade.SpriteList()
        self.pipe_list = arcade.SpriteList()

        for solu in solutions:
            bird = Bird(
                "planeRed1.png", center_x=100 * SCALE,
                center_y=SCREEN_HEIGHT // 2, solu=solu, pipe_list=self.pipe_list,
                scale=SCALE
            )
            print(bird)
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

                bird.solu["fitness"] += self.score * 50
                bird.kill()

        if not self.birds:
            self.game_over()
            self.ctx.gc()
            arcade.exit()

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

            upper_pipe = arcade.Sprite("pipeGreen_03.png", center_x=SCREEN_WIDTH*SCALE + 50*SCALE, scale=SCALE)
            upper_pipe.top = SCREEN_HEIGHT + 200 * SCALE - offset * SCALE

            lower_pipe = arcade.Sprite("pipeGreen_03.png", center_x=SCREEN_WIDTH*SCALE + 50*SCALE, scale=SCALE)
            lower_pipe.top = 0 + 100 * SCALE - offset * SCALE

            upper_pipe.angle = 180

            self.pipe_list.append(upper_pipe)
            self.pipe_list.append(lower_pipe)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.bird.change_y = JUMP_SPEED

    def game_over(self):
        print("Game Over!")
        self.birds.clear()
        self.pipe_list.clear()

        destroyed = self.ctx.gc()
        print(f"Destroyed: {destroyed}")


class Bird(arcade.Sprite):
    def __init__(self, filename, center_x, center_y, solu, pipe_list=None, scale=1):
        super().__init__(filename, scale=scale)
        self.center_x = center_x
        self.center_y = center_y
        self.solu = solu
        self.pipe_list = pipe_list
        self.is_jumping = False
        self.fitness = 0

        self.model = keras.models.clone_model(MODEL)
        weights = pygad.kerasga.model_weights_as_matrix(
            model=self.model,
            weights_vector=solu["solution"]
        )
        self.model.set_weights(weights)

    def update(self):
        if len(self.pipe_list):
            next_pipe = self.pipe_list[0] if self.pipe_list[0].right > self.center_x else self.pipe_list[2]

            input = [(self.center_y, next_pipe.left, next_pipe.bottom)]
            output = self.model.predict([input])

            self.solu["fitness"] += 1
            if output[0] > 0:
                self.change_y = JUMP_SPEED

            self.center_y += self.change_y
            self.change_y += GRAVITY

        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT
            self.change_y = 0


def fitness_func(ga_instance, solutions, solutions_indices):
    global GAME, GA_INSTANCE, KERAS_GA, MODEL

    solus = [
        {"solution": solu, "fitness": 0}
        for solu in solutions
    ]
    GAME.setup(solus)
    arcade.run()

    fitnesses = [solu["fitness"] for solu in solus]
    return fitnesses


def on_generation(ga_instance):
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution()[1]}")


def run_pygad():
    global GAME, GA_INSTANCE, KERAS_GA, MODEL

    input_layer = keras.layers.Input(3)
    dense_layer1 = keras.layers.Dense(5, activation="relu")(input_layer)
    output_layer = keras.layers.Dense(1, activation="tanh")(dense_layer1)
    MODEL = keras.Model(inputs=input_layer, outputs=output_layer)

    NUM_SOLS = 50
    KERAS_GA = pygad.kerasga.KerasGA(model=MODEL, num_solutions=NUM_SOLS)

    initial_population = KERAS_GA.population_weights  # Initial population of network weights
    num_generations = 250  # Number of generations.
    num_parents_mating = NUM_SOLS // 2  # Number of solutions to be selected as parents in the mating pool.

    GAME = FlappyBirdGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    GA_INSTANCE = pygad.GA(
        num_generations=num_generations,
        num_parents_mating=num_parents_mating,
        initial_population=initial_population,
        fitness_func=fitness_func,
        on_generation=on_generation,
        fitness_batch_size=NUM_SOLS
    )
    GA_INSTANCE.run()


run_pygad()
