import random

MAX_TRYINGS_NUM = 10000
MIN_BOARD_SIZE = 10

def try_to_place_ship(board, ship_size, is_vertical, y, x):
    '''Попробовать разместить корабль в заданной точке'''
    rect = []
    # Проверка прямоугольника с запасом в одну клетку
    if is_vertical:
        rect = [row[x - 1: x + 2] for row in board[y - 1: y + ship_size + 1]] # Прямоугольник празмером [size+2]x[1+2]
    else:
        rect = [row[x - 1: x + ship_size + 1] for row in board[y - 1: y + 2]] # Прямоугольник празмером [1+2]x[size+2]
    if any(1 in row for row in rect):
        return False
    # Разместить
    if is_vertical:
        for j in range(y, y + ship_size):
            board[j][x] = 1
    else:
        for j in range(x, x + ship_size):
            board[y][j] = 1
    return True


def generate_board(N):
    '''Значения клеток:
       0 - ячейка свободна;
       1 - ячейка занята.
       Правила:
       - четырёхпалубый 1, трёхпалубных 2, двухпалубных 3, однопалубных 4;
       - корабли не могут стоять друг к другу вплотную;
       - корабли располагаются строко по вертикали или горизонтали'''
    size_num = {4: 1, 3: 2, 2: 3, 1: 4}
    board = []

    if N < MIN_BOARD_SIZE: N = MIN_BOARD_SIZE
    for i in range(N+1): # Временно добавим рамку размером в 1 ячейку
        board.append([0 for j in range(N+1)])

    for (size,num) in size_num.items():
        for i in range(num):
            f_placed = False
            tryings_num = 0 # Число попыток разместить корабль
            while (not f_placed) and (tryings_num < MAX_TRYINGS_NUM):
                vertical = random.randint(0, 1)  # Вертикально / горизонтально
                if vertical:
                    f_placed = try_to_place_ship(board, size, vertical, random.randint(1,N-size), random.randint(1,N-1))
                else:
                    f_placed = try_to_place_ship(board, size, vertical, random.randint(1,N-1), random.randint(1,N-size))
                tryings_num+=1
            if not f_placed:
                print("Ошибка: не удалось разместить корабль размером", size)
                return []
    board = [row[1 : N+1] for row in board[1 : N+1]] # Убрать рамку
    return board

def process_move(board, y, x):
    '''Обработка хода игрока:
       0 - ячейка пуста;
       1 - есть корабль;
       2 - попал в пустую;
       3 - ранил;
       4 - убил'''
    N = len(board)
    if N < MIN_BOARD_SIZE:
        return -1
    if len(board[0]) != N:
        return -1
    if x >= N or y >= N:
        return -1
    # В ячейку уже был удар ранее:
    if board[y][x] >= 2:
        return -2

    if board[y][x] == 0:
        return 2
    # Смотрим квадрат вокруг точки (y,x)
    for i in range (y - 1, y + 2):
        if i < 0 or i >= N: continue
        for j in range(x - 1, x + 2):
            if j < 0 or j >= N: continue
            if i == y and j == x: continue # Саму точку не смотрим
            if board[i][j] == 1:
                return 3
    return 4

def has_any_ships(board):
    return any(1 in row for row in board)