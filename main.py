import pygame
import random
import math
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    mass = 1

    class plane:
        def __init__(self):
            self.pos = pygame.Vector2(400, 300)
            self.ship_position = self.pos.copy()
            self.ship_angle = 90
            self.forward = pygame.Vector2(1, 0)
            self.ROTATION_SPEED = 3
            self.SHIP_SPEED = pygame.Vector2(0,0)
            self.acc=pygame.Vector2(0,0)
            self.points = [(-12, 10), (12, 0), (-12, -10)]
            self.rect = pygame.Rect(0, 0, 28, 22)


        def move(self):
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                self.ship_angle += self.ROTATION_SPEED
            if keys[pygame.K_RIGHT]:
                self.ship_angle -= self.ROTATION_SPEED

            radians = math.radians(self.ship_angle)
            self.forward = pygame.Vector2(
                math.cos(radians),
                -math.sin(radians)
            )

            self.acc = pygame.Vector2(0, 0)

            if keys[pygame.K_UP]:
                self.acc += self.forward * 0.5

            if keys[pygame.K_DOWN]:
                self.SHIP_SPEED *= 0.3
                if self.SHIP_SPEED.length() < 0.08:
                    self.SHIP_SPEED = pygame.Vector2(0, 0)
                self.acc = pygame.Vector2(0, 0)
            else:
                self.acc *= 0.85
                if self.acc.length() < 0.001:
                    self.acc = pygame.Vector2(0, 0)

            if self.acc.length() > 0.35:
                self.acc.scale_to_length(0.35)

            self.SHIP_SPEED += self.acc


            self.ship_position += self.SHIP_SPEED

            if self.ship_position.x > 800:
                self.ship_position.x = 0
            elif self.ship_position.x < 0:
                self.ship_position.x = 800
            if self.ship_position.y > 600:
                self.ship_position.y = 0
            elif self.ship_position.y < 0:
                self.ship_position.y = 600

            self.pos = self.ship_position.copy()
            self.rect.center = (int(self.pos.x), int(self.pos.y))

            self.SHIP_SPEED *= 0.97



        def collision(self, other):
            for x, y in self.points:
                px = self.pos.x + x
                py = self.pos.y + y
                dx = px - other.pos.x
                dy = py - other.pos.y
                if dx * dx + dy * dy <= other.radius * other.radius:
                    return True
            return False

        def draw(self):
            front = self.ship_position + self.forward * 20
            left = self.forward.rotate(140)
            right = self.forward.rotate(-140)

            p1 = self.ship_position + self.forward * 22
            p2 = self.ship_position + left * 16
            p3 = self.ship_position + right * 16

            pygame.draw.polygon(
                screen,
                "white",
                [p1, p2, p3],    
            )




    class bullet():
        def __init__(self, pos, vect, color=(0, 255, 0)):
            self.pos = pygame.math.Vector2(pos)
            self.vect = pygame.math.Vector2(vect)
            self.radius = 5
            self.color = color

        def speed(self):
            self.pos += self.vect

        def collision(self, other):
            if hasattr(other, 'rect'):
                bullet_rect = pygame.Rect(
                    self.pos.x - self.radius,
                    self.pos.y - self.radius,
                    self.radius * 2,
                    self.radius * 2,
                )
                return bullet_rect.colliderect(other.rect)

            dx = self.pos.x - other.pos.x
            dy = self.pos.y - other.pos.y
            return dx * dx + dy * dy <= (self.radius + other.radius) ** 2



        def draw(self):
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    class rock:
        def __init__(self, radius):
            self.radius = radius * 10
            self.pos = pygame.math.Vector2(
                random.randint(radius * 10, 800 - radius * 10),
                random.randint(radius * 10, 600 - radius * 10)
            )
            self.vect = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

        def split(self):
            if self.radius <= 15:
                return []

            split_radius = max(1, self.radius // 20)
            rock1 = rock(split_radius)
            rock2 = rock(split_radius)

            angle = random.uniform(0, math.tau)
            offset = self.radius * 0.75
            rock1.pos = self.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * offset
            rock2.pos = self.pos + pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * offset

            speed = 1.8
            rock1.vect = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            rock2.vect = pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * speed

            return [rock1, rock2]

        def speed(self):
            self.pos += self.vect

            max_speed = 2.5
            if self.vect.length() > max_speed:
                self.vect.scale_to_length(max_speed)

            if self.pos.x - self.radius < 0 or self.pos.x + self.radius > 800:
                self.vect.x *= -1
            if self.pos.y - self.radius < 0 or self.pos.y + self.radius > 600:
                self.vect.y *= -1

        def draw(self):
            pygame.draw.circle(screen, (128, 128, 128), (self.pos.x, self.pos.y), self.radius)

        def collision(self, other):
            dx = self.pos.x - other.pos.x
            dy = self.pos.y - other.pos.y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= (self.radius + other.radius) ** 2:
                temp = self.vect.copy()
                self.vect = ((self.radius * mass - other.radius * mass) / (self.radius * mass + other.radius * mass)) * self.vect + ((2 * other.radius * mass) / (self.radius * mass + other.radius * mass)) * other.vect
                other.vect = ((2 * self.radius * mass) / (self.radius * mass + other.radius * mass)) * temp + ((other.radius * mass - self.radius * mass) / (self.radius * mass + other.radius * mass + other.radius * mass)) * other.vect
                return True
            return False

        def draw(self):
            pygame.draw.circle(screen, (128, 128, 128), (int(self.pos.x), int(self.pos.y)), self.radius)


    class Enemy:
        def __init__(self):
            self.pos = pygame.Vector2(120, 120)
            self.ship_position = self.pos.copy()
            self.ship_angle = 90
            self.forward = pygame.Vector2(1, 0)
            self.SHIP_SPEED = pygame.Vector2(0, 0)
            self.points = [(-12, 10), (12, 0), (-12, -10)]
            self.patrol_points = [
                pygame.Vector2(120, 120),
                pygame.Vector2(120, 480),
                pygame.Vector2(680, 480),
                pygame.Vector2(680, 120),
            ]
            self.patrol_index = 0

        def detect(self, other):
            to_player = (other.pos - self.pos).normalize()
            dot = self.forward.dot(to_player)
            distance = (other.pos - self.pos).length()
            if dot>0.7 and distance<400:
                return True
            else:
                return False

        def move(self, other):
            if self.detect(other):
                to_player = other.pos - self.pos
                if to_player.length() > 0:
                    to_player = to_player.normalize()
                    self.forward = to_player
                    self.pos += self.forward * 1.2
            else:
                target = self.patrol_points[self.patrol_index]
                move_dir = target - self.pos

                if move_dir.length() < 8:
                    self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
                    target = self.patrol_points[self.patrol_index]
                    move_dir = target - self.pos

                if move_dir.length() > 8:
                    self.forward = move_dir.normalize()
                    self.pos += self.forward * 1.2
            self.ship_position = self.pos.copy()

        def draw(self):
            front = self.ship_position + self.forward * 20
            left = self.forward.rotate(140)
            right = self.forward.rotate(-140)
            
            p1 = self.ship_position + self.forward * 22
            p2 = self.ship_position + left * 16
            p3 = self.ship_position + right * 16
            
            pygame.draw.polygon(
                screen,
                "red",
                [p1, p2, p3],
            )
            

            

    rocks = []
    for i in range(2):
        rocks.append(rock(random.randint(1,5)))
    player = plane()
    bullets = []
    shoot_cooldown = 0
    rocks_hit = 0
    game_over = False
    invincible_time = 3
    invincible_timer = 3.0
    font = pygame.font.SysFont(None, 36)
    enemy = Enemy()
    enemy_bullets = []
    enemy_shoot_cooldown = 0

    running = True
    while running:
        screen.fill((7, 51, 59))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if enemy_shoot_cooldown > 0:
            enemy_shoot_cooldown -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and shoot_cooldown == 0:
            direction = player.forward.copy()
            bullets.append(bullet(player.ship_position, direction * 16, (255, 255, 0)))
            shoot_cooldown = 4

        if not game_over:
            enemy.draw()
            enemy.move(player)
            player.move()

            if invincible_timer > 0:
                invincible_timer -= clock.get_time() / 1000

            if invincible_timer <= 0 or int(invincible_timer * 10) % 2 == 0:
                player.draw()

            if enemy.detect(player) and enemy_shoot_cooldown == 0:
                direction = (player.pos - enemy.pos).normalize()
                enemy_bullets.append(
                    bullet(enemy.ship_position, direction * 6, (255, 0, 0))
                )
                enemy_shoot_cooldown = 60

            for i in range(len(rocks)):
                if enemy.pos.distance_to(rocks[i].pos) <= rocks[i].radius + 12:
                    new_rocks = rocks[i].split()
                    if new_rocks:
                        rocks[i]=new_rocks[0]
                        rocks.insert(i+1,new_rocks[1])
                    else:
                        rocks.pop(i)
                    break

            for bullet_obj in enemy_bullets:
                bullet_obj.speed()
                bullet_obj.draw()
                if invincible_timer <= 0 and bullet_obj.collision(player):
                    game_over = True
                    break

            for bullet_obj in bullets:
                bullet_obj.speed()
                bullet_obj.draw()
                for i in range(len(rocks)):
                    if bullet_obj.collision(rocks[i]):
                        rocks_hit += 1
                        new_rocks = rocks[i].split()
                        if len(new_rocks)>0:
                            rocks[i]=new_rocks[0]
                            rocks.insert(i+1,new_rocks[1])
                        else:
                            rocks.pop(i)
                        bullets.remove(bullet_obj)
                        break

            for i in range(len(rocks)):
                rocks[i].speed()
                for j in range(i + 1, len(rocks)):
                    dx = rocks[i].pos.x - rocks[j].pos.x
                    dy = rocks[i].pos.y - rocks[j].pos.y
                    if dx * dx + dy * dy <= (rocks[i].radius + rocks[j].radius) ** 2:
                        rocks[i].collision(rocks[j])

            if invincible_timer <= 0 and enemy.pos.distance_to(player.pos) < 20:
                game_over = True

            for rock_obj in rocks:
                if invincible_timer <= 0 and player.collision(rock_obj):
                    game_over = True
                    break
                rock_obj.draw()

            if len(rocks) == 0 and not game_over:
                rocks = [rock(random.randint(1, 5)) for _ in range(2)]
                enemy_bullets.clear()
                enemy_shoot_cooldown = 0
                invincible_timer = invincible_time

        score_text = font.render(f"Rocks hit: {rocks_hit}", True, (0, 0, 0))
        screen.blit(score_text, (20, 20))

        if game_over:
            game_over_text = font.render("You died!", True, (255, 0, 0))
            screen.blit(game_over_text, (320, 260))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())