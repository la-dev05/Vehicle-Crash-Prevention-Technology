import pygame
import math
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1500  # Increased width to accommodate three cars
WINDOW_HEIGHT = 900
FPS = 100
SCALE_FACTOR = 0.8
DETECTION_RADIUS = 200  # meters (will be scaled)

# Colors
ROAD_COLOR = (75, 85, 99)      # Sophisticated charcoal gray for asphalt
GRASS_COLOR = (104, 159, 56)   # Fresh, vibrant grass green
LINE_COLOR = (245, 245, 245)   # Crisp white for road markings
CAR1_COLOR = (239, 68, 68)     # Vibrant coral red
CAR2_COLOR = (59, 130, 246)    # Modern electric blue
CAR3_COLOR = (255, 215, 0)     # Golden yellow
BUTTON_COLOR = (34, 197, 94)   # Emerald green
TEXT_COLOR = (243, 244, 246)   # Soft pearl white

class Car:
    def __init__(self, x, y, initial_speed, color):
        self.x = x
        self.y = y
        self.speed = initial_speed
        self.color = color
        self.width = 40
        self.length = 60
        self.initial_speed = initial_speed
        self.initial_x = x
        self.initial_y = y
        self.deceleration = 0  # Optional deceleration
        self.decelerating = False
        
    def move(self, dt):
        # Apply deceleration if active
        if self.decelerating:
            self.speed = max(0, self.speed - self.deceleration * dt)
        
        # Move car
        self.x += self.speed * dt * SCALE_FACTOR

    def reset(self):
        self.x = self.initial_x
        self.y = self.initial_y
        self.speed = self.initial_speed
        self.decelerating = False
        self.deceleration = 0

    def draw(self, screen):
        # Draw car body (main rectangle)
        car_rect = pygame.Rect(
            self.x - self.length/2,
            self.y - self.width/2,
            self.length,
            self.width
        )
        pygame.draw.rect(screen, self.color, car_rect, border_radius=8)

        # Windshield
        windshield = pygame.Rect(
            self.x - self.length/4,
            self.y - self.width/3,
            self.length/2,
            self.width/1.5
        )
        pygame.draw.rect(screen, (150, 150, 150), windshield, border_radius=4)

        # Draw detection radius (very subtle)
        radius_surface = pygame.Surface((DETECTION_RADIUS * 2 * SCALE_FACTOR, DETECTION_RADIUS * 2 * SCALE_FACTOR), pygame.SRCALPHA)
        pygame.draw.circle(radius_surface, (*self.color, 70),
                         (DETECTION_RADIUS * SCALE_FACTOR, DETECTION_RADIUS * SCALE_FACTOR),
                         DETECTION_RADIUS * SCALE_FACTOR)
        screen.blit(radius_surface,
                   (self.x - DETECTION_RADIUS * SCALE_FACTOR,
                    self.y - DETECTION_RADIUS * SCALE_FACTOR))

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_road(screen):
    # Fill background with grass
    screen.fill(GRASS_COLOR)

    # Draw road
    road_width = 150
    pygame.draw.rect(screen, ROAD_COLOR, (0, WINDOW_HEIGHT/2 - road_width/2, WINDOW_WIDTH, road_width))

    # Draw road lines
    dash_length = 30
    gap_length = 30
    for i in range(0, WINDOW_WIDTH, dash_length + gap_length):
        # Horizontal road lines
        pygame.draw.rect(screen, LINE_COLOR, (i, WINDOW_HEIGHT/2 - 2, dash_length, 4))

    # Edge lines (solid)
    pygame.draw.line(screen, LINE_COLOR, (0, WINDOW_HEIGHT/2 - road_width/2), (WINDOW_WIDTH, WINDOW_HEIGHT/2 - road_width/2), 3)
    pygame.draw.line(screen, LINE_COLOR, (0, WINDOW_HEIGHT/2 + road_width/2), (WINDOW_WIDTH, WINDOW_HEIGHT/2 + road_width/2), 3)

def check_radius_collision(car1, car2):
    distance = math.sqrt((car2.x - car1.x)**2 + (car2.y - car1.y)**2)
    detection_threshold = DETECTION_RADIUS * 2 * SCALE_FACTOR
    return distance <= detection_threshold

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Multi-Vehicle Collision Avoidance Simulation")
    clock = pygame.time.Clock()

    # Initial positions with 500m separation
    initial_speed_car1, initial_speed_car2, initial_speed_car3 = 80, 80, 70  # m/s
    initial_y = WINDOW_HEIGHT/2
    car1 = Car(0, initial_y, initial_speed_car1, CAR1_COLOR)
    car2 = Car(500 * SCALE_FACTOR, initial_y, initial_speed_car2, CAR2_COLOR)
    car3 = Car(1000 * SCALE_FACTOR, initial_y, initial_speed_car3, CAR3_COLOR)

    restart_button = Button(WINDOW_WIDTH/2 - 60, WINDOW_HEIGHT - 80, 120, 40, "Restart", BUTTON_COLOR)

    running = True
    simulation_active = True
    last_time = time.time()
    deceleration_rate = 8  # m/s^2
    collision_sequence_started = False

    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not simulation_active and restart_button.is_clicked(event.pos):
                    car1.reset()
                    car2.reset()
                    car3.reset()
                    simulation_active = True
                    collision_sequence_started = False
                
        if simulation_active:
            # Collision avoidance logic
            if not collision_sequence_started and car3.x > car2.x:
                # Third car starts decelerating
                car3.decelerating = True
                car3.deceleration = deceleration_rate
                collision_sequence_started = True

            # Check radius collisions
            if check_radius_collision(car3, car2) and not car2.decelerating:
                car2.decelerating = True
                car2.deceleration = deceleration_rate

            if check_radius_collision(car2, car1) and not car1.decelerating:
                car1.decelerating = True
                car1.deceleration = deceleration_rate

            # Move cars
            car1.move(dt)
            car2.move(dt)
            car3.move(dt)

            # Check if all cars have stopped
            if (car1.speed == 0 and car2.speed == 0 and car3.speed == 0):
                simulation_active = False

        # Draw everything
        draw_road(screen)
        car1.draw(screen)
        car2.draw(screen)
        car3.draw(screen)
        
        # Display speeds with shadow effect
        font = pygame.font.Font(None, 36)
        def draw_text_with_shadow(text, pos):
            shadow = font.render(text, True, (0, 0, 0))
            text_surface = font.render(text, True, TEXT_COLOR)
            screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
            screen.blit(text_surface, pos)
            
        draw_text_with_shadow(f"Car 1: {car1.speed:.1f} m/s", (10, 10))
        draw_text_with_shadow(f"Car 2: {car2.speed:.1f} m/s", (10, 50))
        draw_text_with_shadow(f"Car 3: {car3.speed:.1f} m/s", (10, 90))
        
        if not simulation_active:
            restart_button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
            
    pygame.quit()

if __name__ == "__main__":
    main()