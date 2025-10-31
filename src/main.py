import pygame
import sys
import os
import time
import pyperclip

# Import get_weather_data function from weather_api.py
try:
    from weather_api import get_weather_data
except ImportError:  # Check if file is missing or not
    print("error: Could not find 'weather_api.py'.")
    sys.exit(1)

# File path where all data will be saved
DATA_FILE_PATH = "src/data.txt"

# GUI Configuration
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
CAPTION = "MINI WEATHER"
FPS = 30

# Define colors
WHITE = (220, 220, 220)
BLACK = (20, 20, 20)

# Pygame initialization
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(CAPTION)

clock = pygame.time.Clock()

pygame.key.set_repeat(200, 200)

# Font setup
try:
    font_verylarge = pygame.font.Font("res/fonts/Jersey10-Regular.ttf", 90)
    font_large = pygame.font.Font("res/fonts/Jersey10-Regular.ttf", 60)
    font_medium = pygame.font.Font("res/fonts/Jersey10-Regular.ttf", 30)
    font_small = pygame.font.Font("res/fonts/Jersey10-Regular.ttf", 24)
except:
    font_verylarge = pygame.font.Font(None, 90)
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 30)
    font_small = pygame.font.Font(None, 24)


# Used for saving app state data
class AppState:
    def __init__(self):
        self.app_api_phase = True
        self.api_key = ""
        self.input_api_key = ""

        self.input_text = ""
        self.weather_result = None
        self.loading = False
        self.status_message = "Enter city name and press ENTER"


def draw_text(surface, text, font, color, x, y, center=False):
    """Renders text to the screen"""
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_surface, rect)
    return rect


def get_placeholder_weather():
    """Returns a placeholder structure for initial display"""
    return {
        "city": "CITY",
        "country": "CT",
        "temp": "??.°C",
        "description": "Waiting for Input",
    }


def main():
    """Main application loop"""
    state = AppState()

    # Initialize weather data placeholder
    state.weather_result = get_placeholder_weather()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- API PHASE ---
            if state.app_api_phase == True:

                try:
                    file_size = os.path.getsize(DATA_FILE_PATH)

                    # Check if file is empty or not
                    if file_size > 0:
                        # Read contents of data.txt
                        with open(DATA_FILE_PATH, "r") as file:
                            state.api_key = file.read()

                        # Test saved API key
                        test_api_key = get_weather_data("earth", state.api_key)

                        if "error" in test_api_key:
                            open(
                                DATA_FILE_PATH, "w"
                            ).close()  # Clear data.txt if API key is invalid
                        else:
                            state.app_api_phase = (
                                False  # Change app phase if API key is valid
                            )
                    else:
                        pass

                except FileNotFoundError:
                    pass

                # Handling keyboard input
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        state.api_key = state.input_api_key.strip()
                        state.input_api_key = ""

                        # Save API key to data.txt file
                        with open(DATA_FILE_PATH, "w") as file:
                            file.write(state.api_key)

                    elif event.key == pygame.K_BACKSPACE:
                        state.input_api_key = state.input_api_key[:-1]

                    # Paste from clipboard
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                        try:
                            state.input_api_key = pyperclip.paste()
                        except pyperclip.PyperclipException:
                            pass

                        # Clear pasted API key if its too long (prevents typing issue)
                        if len(state.input_api_key) > 32:
                            state.input_api_key = ""

                    # Ignore control keys for simple text input
                    elif event.key in [
                        pygame.K_LSHIFT,
                        pygame.K_RSHIFT,
                        pygame.K_CAPSLOCK,
                        pygame.K_TAB,
                    ]:
                        pass

                    else:
                        key_name = event.unicode
                        if key_name.isprintable() and len(state.input_api_key) < 32:
                            state.input_api_key += key_name

            # --- MAIN PHASE ---
            elif state.app_api_phase == False:

                # Handling keyboard input
                if event.type == pygame.KEYDOWN:
                    if (
                        event.key == pygame.K_RETURN
                    ):  # If user pressed ENTER, trigger weather data fetch
                        city_to_fetch = state.input_text.strip()
                        state.input_text = ""

                        # If both conditions are true (a city name is entered and the app isn't loading), execute weather data fetch
                        if city_to_fetch and not state.loading:
                            state.weather_result = (
                                None  # Clear weather data before fetching new data
                            )
                            state.loading = (
                                True  # Prevent a new fetch until ongoing is complete
                            )

                            # Fetching data directly without threading for simplicity
                            fetched_data = get_weather_data(
                                city_to_fetch, state.api_key
                            )
                            state.loading = False

                            if "error" in fetched_data:
                                state.status_message = "error"
                                state.weather_result = get_placeholder_weather()
                            else:
                                state.weather_result = fetched_data

                    elif event.key == pygame.K_BACKSPACE:
                        state.input_text = state.input_text[:-1]

                    # Ignore control keys for simple text input
                    elif event.key in [
                        pygame.K_LSHIFT,
                        pygame.K_RSHIFT,
                        pygame.K_CAPSLOCK,
                        pygame.K_TAB,
                    ]:
                        pass

                    # Adding character to input_text and limiting length
                    else:
                        key_name = event.unicode
                        if key_name.isprintable() and len(state.input_text) < 25:
                            state.input_text += key_name
                            state.status_message = (
                                ""  # Clear status message before typing
                            )

        # ---Drawing logic---
        screen.fill(BLACK)

        # --- API PHASE ---
        if state.app_api_phase == True:

            draw_text(screen, "ENTER API KEY", font_large, WHITE, 300, 200, center=True)

            # Draw Input Field
            input_box_rect = pygame.Rect(100, 280, 400, 40)
            pygame.draw.rect(screen, WHITE, input_box_rect, 2)
            input_text_surface = font_medium.render(state.input_api_key, True, WHITE)
            screen.blit(input_text_surface, (input_box_rect.x + 5, input_box_rect.y))

            # Draw blinking cursor
            if time.time() % 1.0 < 0.5:
                cursor_x = input_box_rect.x + 5 + input_text_surface.get_width()
                pygame.draw.line(
                    screen,
                    WHITE,
                    (cursor_x, input_box_rect.y + 10),
                    (cursor_x, input_box_rect.y + 30),
                    2,
                )

        # --- MAIN PHASE ---
        if state.app_api_phase == False:

            # Load background
            background = pygame.image.load("res/images/background.png")
            screen.blit(background, (0, 0))

            # Draw Input Field
            input_box_shadow = pygame.Rect(130, 285, 350, 40)
            pygame.draw.rect(screen, BLACK, input_box_shadow, 0)

            input_box_bg = pygame.Rect(125, 280, 350, 40)
            pygame.draw.rect(screen, WHITE, input_box_bg, 0)

            input_box_rect = pygame.Rect(125, 280, 350, 40)
            pygame.draw.rect(screen, BLACK, input_box_rect, 2)

            input_text_surface = font_medium.render(state.input_text, True, BLACK)
            screen.blit(input_text_surface, (input_box_rect.x + 5, input_box_rect.y))

            # Draw status message
            draw_text(
                screen,
                state.status_message,
                font_small,
                BLACK,
                input_box_rect.x + 10,
                input_box_rect.y + 5,
                center=False,
            )

            # Draw blinking cursor
            if time.time() % 1.0 < 0.5:
                cursor_x = input_box_rect.x + 5 + input_text_surface.get_width()
                pygame.draw.line(
                    screen,
                    BLACK,
                    (cursor_x, input_box_rect.y + 10),
                    (cursor_x, input_box_rect.y + 30),
                    2,
                )

            # Draw weather display box
            if state.weather_result:
                result = state.weather_result

                # Draw box shadow
                display_box_shadow = pygame.Rect(160, 60, 300, 200)
                pygame.draw.rect(screen, BLACK, display_box_shadow, 0)

                # Fill box with white
                display_box_bg = pygame.Rect(150, 50, 300, 200)
                pygame.draw.rect(screen, WHITE, display_box_bg, 0)

                # Draw box border
                display_box_rect = pygame.Rect(150, 50, 300, 200)
                pygame.draw.rect(screen, BLACK, display_box_rect, 5)

                # Display temperature
                draw_text(
                    screen, result["temp"], font_verylarge, BLACK, 300, 140, center=True
                )

                # Display weather description
                draw_text(
                    screen,
                    result["description"],
                    font_medium,
                    BLACK,
                    300,
                    200,
                    center=True,
                )

                # Display location info
                location_info = f"{result['city']}, {result['country']}"
                draw_text(
                    screen, location_info, font_medium, BLACK, 300, 225, center=True
                )

        # Update the display
        pygame.display.flip()

        # Lock the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
