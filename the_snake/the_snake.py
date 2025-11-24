"""Импорт choice и randint из модуля random."""
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Константы для поля счета и рекорда
SCORES_TABLE_EDGE = 100
WHITE_COLOR = (255, 255, 255)
TABLE_TEXT_COORDINATES = (
    SCREEN_WIDTH // 2, SCREEN_HEIGHT + (SCORES_TABLE_EDGE // 2)
)
SCORE = 0
RECORD = 0

ZERO_COORDINATE = (0, 0)
CENTRAL_DOT = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет границы ячейки
BORDER_COLOR = (94, 216, 228)

# Скорость движения змейки:
SPEED = 15

# Настройка игрового окна:
screen = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT + SCORES_TABLE_EDGE), 0, 32
)

# Заголовок окна игрового поля:
pg.display.set_caption("Змейка")

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Инициализация родительского класса игрового обьекта.
    Определение позиции, цвета, направления, счета и рекорда сессии.
    """

    def __init__(self, body_color=None,
                 border_color=None) -> None:
        """Инициализация позиции, цвета тела/ячейки и направления."""
        self.body_color = body_color
        self.border_color = border_color
        self.position = CENTRAL_DOT

    def draw(self):
        """Инициализация метода draw."""
        raise NotImplementedError('Метод не реализован.')

    def draw_cell(self, position):
        """Отрисовка ячейки игрового обьекта."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, self.border_color, rect, 1)


class Apple(GameObject):
    """
    Класс "яблока". Инициализирует "яблоко".
    Отвечает за цвет, позицию и отрисовку яблока на игровом поле.
    """

    def randomize_position(self, snake_positions):
        """Определяет случайную позицию яблока на игровом поле."""
        while True:
            random_width = randint(1, GRID_WIDTH - 1) * GRID_SIZE
            random_height = randint(1, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (random_width, random_height)
            if self.position not in snake_positions:
                break

    def __init__(self, body_color=APPLE_COLOR,
                 border_color=BORDER_COLOR,
                 occupied_positions=[CENTRAL_DOT]) -> None:
        """Инициализация яблока. Определение цвета, позиции."""
        super().__init__(body_color,
                         border_color)
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовка яблока на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """
    Класс "змейки". Инициализирует "змейку".
    Отвечает за:
    Определение цвета, длины, направления и позиции головы,
    Обновление направления движения после нажатия на кнопку,
    Движение змейки по игровому полю,
    Проверку столкновения змейки с яблоком/своим "хвостом",
    Увеличение длины змейки в случае столкновения с яблоком.
    Сброс змейки и текущей игры в случае столкновения с хвостом.
    Отрисовку змейки на игровом поле.
    """

    def __init__(self, body_color=SNAKE_COLOR,
                 border_color=BORDER_COLOR) -> None:
        """Инициализация "змейки"."""
        super().__init__(body_color,
                         border_color)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.lenght = 1
        self.last = None

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы."""
        return self.positions[0]

    def move(self):
        """
        Обновляет позицию змейки,
        добавляя новую голову в начало списка positions.
        """
        x, y = self.direction
        head_x, head_y = self.get_head_position()

        head_x = (head_x + (x * GRID_SIZE)) % SCREEN_WIDTH

        head_y = (head_y + (y * GRID_SIZE)) % SCREEN_HEIGHT

        head_position = (head_x, head_y)

        self.positions.insert(0, head_position)

        if self.lenght < len(self.positions):
            self.last = self.positions.pop()

    def draw(self):
        """
        Отрисовка змейки на игровом поле.
        Затирание последнего сегмента змейки.
        """
        for position in self.positions:
            # Отрисовка тела змейки
            self.draw_cell(position)

            # Отрисовка головы змейки
            self.draw_cell(self.get_head_position())

            # Затирание последнего сегмента
            if self.last:
                last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
                pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """
        Cбрасывает змейку в начальное состояние и
        записывает рекордный счет сесии.
        """
        self.positions = [self.position]
        self.lenght = 1
        self.direction = choice([RIGHT, DOWN, UP, DOWN])


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def score_display():
    """Отображение и отрисовка счета/рекорда сессии."""
    pg.draw.line(
        screen,
        WHITE_COLOR,
        [0, SCREEN_HEIGHT + 5],
        [SCREEN_WIDTH, SCREEN_HEIGHT + 5],
        5,
    )
    font = pg.font.SysFont("Arial", 50)
    record_in_text = RECORD or "-"
    text = f"Cчет: {SCORE}   Рекорд: {record_in_text}"
    text_surface = font.render(text, True, WHITE_COLOR)
    text_rect = text_surface.get_rect(center=TABLE_TEXT_COORDINATES)
    screen.fill(BOARD_BACKGROUND_COLOR, text_rect)
    screen.blit(text_surface, text_rect)


def check_tail_collision(snake_object, apple_object):
    """
    Проверка на столкновение с хвостом.
    Переопределение позиции яблока, "рестарт" змейки и
    заливка экрана в случае столкновения с хвостом.
    Переопределение счета и рекорда сессии.
    """
    if snake_object.get_head_position() in snake_object.positions[1:]:
        apple_object.randomize_position(snake_object.positions)
        snake_object.reset()
        global RECORD, SCORE
        RECORD = max(RECORD, SCORE)
        SCORE = 0
        screen.fill(BOARD_BACKGROUND_COLOR)


def apple_collision_check(snake_object, apple_object):
    """
    Проверка на столкновение с яблоком.
    Переопределение позиции яблока.
    Обновление и отображение счета/рекорда сесии.
    """
    if apple_object.position in snake_object.positions:
        apple_object.randomize_position(snake_object.positions)
        snake_object.lenght += 1
        global SCORE
        SCORE += 1


def main():
    """Основной код игры."""
    # Инициализация PyGame:
    pg.init()

    # Инициализация модуля шрифтов
    pg.font.init()

    # Создание экземляров классов.
    snake = Snake()
    apple = Apple()

    while True:
        # "Скорость" игры.
        clock.tick(SPEED)

        # Захват клавиш и движение.
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка на столкновение с яблоком.
        apple_collision_check(snake, apple)

        # Проверка на столкновение с хвостом.
        check_tail_collision(snake, apple)

        # Отрисовка счета и рекорда сессии.
        score_display()

        # Отрисовка обьектов.
        apple.draw()
        snake.draw()

        pg.display.update()


if __name__ == "__main__":
    main()
