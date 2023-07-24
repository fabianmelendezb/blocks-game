import pygame
import sys
from blocks_game.engine import GameEngine, Color
# Inicializar Pygame
pygame.init()
pygame.font.init()

# Definir los colores que utilizarás

# Definir el tamaño de la pantalla
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600



# Crear la pantalla
screen = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Blocks Game")


def main():
    # Dibujar los elementos en la pantalla
    screen.fill((0, 0, 0))  # Limpiar la pantalla con color negro

    # Score
    games = 0

    # Init game
    engine = GameEngine(screen=screen)
    entropy = engine.entropy()

    font = pygame.font.Font(None, 30)
    score = f"Games: {games}"
    text = font.render(score, True, Color.WHITE.value)
    text_rect = text.get_rect(topright=(ANCHO_PANTALLA - 10, ALTO_PANTALLA - 25))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Get the mouse click coordinates
                click = pygame.mouse.get_pos()
                change = engine.handle(click)
                if change:
                    entropy  = engine.entropy()

        if entropy == 0:
            screen.fill((0, 0, 0))
            del engine
            games += 1
            engine = GameEngine(screen=screen)
            entropy = engine.entropy()
            score = f"Games: {games}"
            text = font.render(score, True, Color.WHITE.value)

        screen.blit(text, text_rect)

        pygame.display.flip()

if __name__ == "__main__":
    main()