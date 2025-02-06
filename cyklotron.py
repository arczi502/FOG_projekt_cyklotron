import pygame
import pygame_gui
import math

# Pygame setup
WIDTH, HEIGHT = 800, 728
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyclotron Simulation")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (100, 50)), text='Start',
                                            manager=manager)
stop_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 120), (100, 50)), text='Stop',
                                           manager=manager)
restart_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 190), (100, 50)), text='Restart',
                                              manager=manager)
particle_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=['Proton', 'Electron', 'Alpha Particle'],
                                                       starting_option='Proton',
                                                       relative_rect=pygame.Rect((50, 260), (150, 50)),
                                                       manager=manager)

# Cyclotron Parameters
cyclotron_radius = 200
cyclotron_line_width = 2
cyclotron_color = (100, 100, 100)

# Electric field Parameters
E_FIELD_STRENGTH = 1e10
E_FIELD_FREQUENCY_SCALE = 1.0

# Loading background image
background = pygame.image.load("template2.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

CENTER = (WIDTH // 2, HEIGHT // 2)
max_radius = cyclotron_radius



def get_particle_properties(particle):
    if particle == 'Proton':
        return 1.602e-19, 1.67e-27, (0, 0, 255), (255, 0, 0)  # blue particle, red trail
    elif particle == 'Electron':
        return -1.602e-19, 9.11e-31, (0, 255, 0), (0, 0, 255)  #green particle, blue trail
    elif particle == 'Alpha Particle':
        return 3.204e-19, 6.64e-27, (255, 0, 0), (0, 255, 0)  # red particle, green trail


# Initial State
running = True
simulating = False
selected_particle = 'Proton'
proton_path = []

B = 2  # Magnetic field strength
time_step = 1e-9


def reset_simulation():
    global v, r, theta, x, y, ejected, proton_path, q, m, particle_color, trail_color
    q, m, particle_color, trail_color = get_particle_properties(selected_particle)
    v = 1e6
    r = (m * v) / (abs(q) * B)
    theta = 0
    x, y = CENTER[0] + r, CENTER[1]
    ejected = False
    proton_path = []
    print("Simulation reset")


reset_simulation()

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.size
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            CENTER = (WIDTH // 2, HEIGHT // 2)
        manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == start_button:
                simulating = True
            elif event.ui_element == stop_button:
                simulating = False
            elif event.ui_element == restart_button:
                reset_simulation()
                simulating = False
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == particle_dropdown:
                selected_particle = event.text
                reset_simulation()

    screen.blit(background, (0, 0))
    pygame.draw.circle(screen, cyclotron_color, CENTER, cyclotron_radius, cyclotron_line_width)

    if simulating and not ejected:
        cyclotron_freq = (abs(q) * B) / (2 * math.pi * m)
        cyclotron_T = (2 * math.pi * m) / (abs(q) * B)

        def electrostatic_force(q, E, t, cyclotron_T):
            polarity = (-1) ** int(2 * t / cyclotron_T)
            return q * E * polarity
        #Electric field impact
        if abs(x - WIDTH / 2) < 60:
            fx = electrostatic_force(q, E_FIELD_STRENGTH, time_step, cyclotron_T) * math.cos(theta)
            fy = electrostatic_force(q, E_FIELD_STRENGTH, time_step, cyclotron_T) * math.sin(theta)
            ax = fx / m
            v_x = v * math.cos(theta) + ax * time_step
            v_y = v * math.sin(theta)
            v = math.sqrt(v_x ** 2 + v_y ** 2)
            theta = math.atan2(v_y, v_x)
            r = (m * v) / (abs(q) * B)

        theta += (v / r) * time_step
        x = CENTER[0] + r * math.cos(theta)
        y = CENTER[1] + r * math.sin(theta)

        if r >= cyclotron_radius:
            ejected = True  # Stop movement
            v = 0  # Set velocity to zero
            # Keeping the particle at the edge without resetting
            x = CENTER[0] + cyclotron_radius * math.cos(theta)
            y = CENTER[1] + cyclotron_radius * math.sin(theta)
            print("Particle reached the edge. Simulation paused.")

        if not ejected:
            proton_path.append((int(x), int(y)))

    # Draw the particle path and particle itself
    if len(proton_path) > 1:
        pygame.draw.lines(screen, trail_color, False, proton_path)
    if not ejected or len(proton_path) > 0:
        pygame.draw.circle(screen, particle_color, (int(x), int(y)), 3)

    # Display velocity
    velocity_text = font.render(f"Velocity: {v:.1f} m/s", True, (0, 0, 0))
    screen.blit(velocity_text, (20, 20))

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
