import tkinter as tk
import random


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)



class Ball(GameObject):
    def __init__(self, canvas, x, y, direction=None):
        self.radius = 10
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        # increase the below value to increase the speed of ball
        self.speed = 7
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)
        self.direction = direction if direction else self.direction

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)
        self.ball_list = []  # List to store multiple ball

    def move_with_mouse(self, event):
        x = self.canvas.canvasx(event.x)
        self.set_position(x, self.get_position()[1])

    def click_paddle(self, event):
        self.clicked = True

    def drag_paddle(self, event):
        if self.clicked:
            x = self.canvas.canvasx(event.x)
            self.set_position(x, self.get_position()[1])

    def release_paddle(self, event):
        self.clicked = False

    def set_position(self, x, y):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if x - self.width / 2 >= 0 and x + self.width / 2 <= width:
            super(Paddle, self).move(x - coords[0], 0)
            if self.ball is not None:
                # Calculate the new ball position based on the original paddle size
                original_paddle_width = 80
                scale_factor = self.width / original_paddle_width
                new_ball_x = (x - self.width / 2) + (self.width / 2 - self.ball.radius)
                self.ball.move((new_ball_x - self.ball.get_position()[0]) / scale_factor, 0)

    def set_ball(self, ball):
        self.ball = ball
        if self.ball is not None:
            # Calculate the new ball position based on the original paddle size
            original_paddle_width = 80
            scale_factor = self.width / original_paddle_width
            new_ball_x = (self.get_position()[0] - self.width / 2) + (self.width / 2 - self.ball.radius)
            self.ball.move(new_ball_x - self.ball.get_position()[0], 0)

    def move_ball(self):
        # Move the ball periodically using the after method
        if self.ball is not None:
            self.ball.update()
            self.after(50, self.move_ball)

    def add_ball(self):
        if self.ball_list:
            paddle_coords = self.get_position()
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            new_ball = Ball(self.canvas, x, 532, direction=[1, -1])
            self.ball_list.append(new_ball)


    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class PowerUp(GameObject):
    def __init__(self, canvas, x, y, activation_function):
        self.width = 20
        self.height = 20
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='yellow', tags='power-up')
        super(PowerUp, self).__init__(canvas, item)
        self.activation_function = activation_function

    def activate(self):
        # Trigger the activation function when the power-up is hit
        self.activation_function()
        self.delete()

class PaddlePowerUp(PowerUp):
    def __init__(self, canvas, x, y, activation_function):
        super(PaddlePowerUp, self).__init__(canvas, x, y, activation_function)
        self.canvas.itemconfig(self.item, fill='red')  # Change color to distinguish from other power-ups

    def activate(self):
        # Trigger the activation function when the power-up is hit
        self.activation_function()
        self.delete()


class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])

class MultiBallPowerUp(PowerUp):
    def __init__(self, canvas, x, y, activation_function):
        super(MultiBallPowerUp, self).__init__(canvas, x, y, activation_function)
        self.canvas.itemconfig(self.item, fill='blue')  # Change color to distinguish from other power-ups


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 830
        self.height = 600
        self.spawn_power_up_interval = 10000
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 550)
        self.items[self.paddle.item] = self.paddle
        # adding brick with different hit capacities - 3,2 and 1
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)
            self.add_brick(x + 37.5, 110, 3)
            self.add_brick(x + 37.5, 130, 2)
            self.add_brick(x + 37.5, 150, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))
        self.canvas.bind('<Button-1>', self.paddle.click_paddle)
        self.canvas.bind('<B1-Motion>', self.paddle.drag_paddle)
        self.canvas.bind('<ButtonRelease-1>', self.paddle.release_paddle)
        self.power_up = None
        self.add_ball()
        self.create_multi_ball_power_up()  # Start spawning blue balls

    def setup_game(self):
        # Remove all moving balls
        for ball in self.paddle.ball_list:
            ball.delete()
        self.paddle.ball_list = []  # Clear the ball list

        self.add_ball()  # Ensure that a ball is created before calling add_ball
        self.update_lives_text()
        self.text = self.draw_text(400, 300, 'Press Space to start!')
        self.canvas.bind('<space>', lambda _: self.start_game)
        self.lives_reduced = False  # Initialize the flag

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) / 2
        y = paddle_coords[1] - self.ball.radius - 2 if self.ball else paddle_coords[1]
        self.ball = Ball(self.canvas, x, y, direction=[-1, 1])
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.unbind('Button-1')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.lives_reduced = False  # Reset the flag
        self.game_loop()

    def setup_game(self):
        # Remove all moving balls
        for ball in self.paddle.ball_list:
            ball.delete()
        self.paddle.ball_list = []  # Clear the ball list

        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(400, 300, 'Press Space to start!')
        self.canvas.bind('<space>', lambda _: self.start_game())
        self.lives_reduced = False  # Initialize the flag

    def game_loop(self):
        self.check_collisions()
        self.check_power_up_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))

        # Check if there are no balls left on the canvas
        num_balls = len(self.canvas.find_withtag('ball')) + len(self.paddle.ball_list)

        if num_balls == 0 and not self.lives_reduced:
            # Check if any ball is present in the paddle's ball_list
            if any(ball.get_position()[3] >= self.paddle.get_position()[1] for ball in self.paddle.ball_list):
                # There is at least one ball that can hit the paddle, so no lives are reduced
                pass
            else:
                # No ball can hit the paddle, reduce lives
                self.update_lives_text()  # Update lives display
                self.lives_reduced = True  # Set the flag to True

                # Remove all balls instantly
                for ball in self.paddle.ball_list:
                    ball.delete()
                self.paddle.ball_list = []  # Clear the ball list

        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(400, 300, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            self.update_lives_text()  # Update lives display
            if self.lives < 0:
                self.draw_text(400, 300, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            for ball in self.paddle.ball_list:
                ball.update()
                self.check_extra_ball_collisions(ball)
            self.after(50, self.game_loop)


    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

    def activate_paddle_power_up(self):
        # Fetch the paddle's position before deleting it
        paddle_coords = self.paddle.get_position()
        # Double the paddle width
        self.paddle.width *= 2
        # Delete the old paddle and remove it from items
        self.items.pop(self.paddle.item, None)
        self.paddle.delete()
        # Redraw the paddle
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        y = paddle_coords[1]
        self.paddle.item = self.canvas.create_rectangle(x - self.paddle.width / 2,
                                                        y - self.paddle.height / 2,
                                                        x + self.paddle.width / 2,
                                                        y + self.paddle.height / 2,
                                                        fill='#FFB643')
        # Add the new paddle to items
        self.items[self.paddle.item] = self.paddle
        # Update the ball's position to keep it attached to the paddle
        if self.ball is not None:
            self.ball.move(x - self.ball.get_position()[0], 0)
        # Set a timer to shrink the paddle back to original size after 5 seconds
        self.after(5000, self.deactivate_paddle_power_up)

    def deactivate_paddle_power_up(self):
        # Fetch the paddle's position before deleting it
        paddle_coords = self.paddle.get_position()
        # Shrink the paddle back to original size
        self.paddle.width /= 2
        # Delete the old paddle and remove it from items
        self.items.pop(self.paddle.item, None)
        self.paddle.delete()
        # Redraw the paddle
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        y = paddle_coords[1]
        self.paddle.item = self.canvas.create_rectangle(x - self.paddle.width / 2,
                                                        y - self.paddle.height / 2,
                                                        x + self.paddle.width / 2,
                                                        y + self.paddle.height / 2,
                                                        fill='#FFB643')
        # Add the new paddle to items
        self.items[self.paddle.item] = self.paddle
        # Update the ball's position to keep it attached to the paddle
        if self.ball is not None:
            self.ball.move(x - self.ball.get_position()[0], 0)

    def create_multi_ball_power_up(self):
        # Randomly choose between multi-ball and paddle power-up
        power_up_type = random.choice([MultiBallPowerUp, PaddlePowerUp])
        # Spawn the power-up at the top
        x = random.randint(50, self.width - 50)
        y = 50  # Top of the canvas
        if power_up_type == MultiBallPowerUp:
            self.power_up = power_up_type(self.canvas, x, y, self.activate_multi_ball_power_up)
        else:
            self.power_up = power_up_type(self.canvas, x, y, self.activate_paddle_power_up)
        self.items[self.power_up.item] = self.power_up
        # Move the power-up in the downward direction
        self.move_power_up(self.power_up)
        # Schedule the next spawn after 10 seconds
        self.canvas.after(self.spawn_power_up_interval, self.create_multi_ball_power_up)

    def activate_multi_ball_power_up(self):
        # Triggered when the paddle hits the blue ball
        for _ in range(4):  # Create 4 additional balls
            x, y = self.paddle.get_position()[0], self.paddle.get_position()[1]
            new_ball = Ball(self.canvas, x, y, direction=[random.choice([-1, 1]), -1])
            self.paddle.ball_list.append(new_ball)
            self.move_extra_ball(new_ball)

    def move_extra_ball(self, ball):
        # Move the extra ball
        if ball:
            coords = ball.get_position()
            if coords:  # Check if the ball exists
                ball.update()
                self.check_extra_ball_collisions(ball)
                self.after(50, lambda: self.move_extra_ball(ball))

    def check_extra_ball_collisions(self, ball):
        # Check for collisions with bricks and update the game accordingly
        ball_coords = ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        ball.collide(objects)


    def move_power_up(self, power_up):
        # Move the power-up item downward
        speed = 7
        self.canvas.move(power_up.item, 0, speed)

        # Check collision with paddle
        if self.paddle_collision(power_up):
            power_up.activate()

        self.after(50, lambda: self.move_power_up(power_up))

    def paddle_collision(self, power_up):
        if power_up and isinstance(power_up, PowerUp):
            power_up_coords = self.canvas.coords(power_up.item)
            paddle_coords = self.paddle.get_position()

            if power_up_coords and paddle_coords and len(power_up_coords) >= 4 and len(paddle_coords) >= 4:
                return (paddle_coords[0] < power_up_coords[2] and
                        paddle_coords[2] > power_up_coords[0] and
                        paddle_coords[1] < power_up_coords[3] and
                        paddle_coords[3] > power_up_coords[1])

        return False

    def check_power_up_collisions(self):
        power_up_items = self.canvas.find_withtag('power-up')
        if not power_up_items:
            return

        power_up_objects = [self.items[x] for x in power_up_items if x in self.items]

        # Filter out balls from the list of objects
        non_ball_objects = [obj for obj in power_up_objects if not isinstance(obj, Ball)]

        for power_up in non_ball_objects:
            # Check if the power-up collides with the paddle
            if self.paddle_collision(power_up):
                power_up.activate()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()