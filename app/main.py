import datetime
from typing import Union
from fastapi import FastAPI, Query, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import delete, or_
import uvicorn
import uuid
from datetime import datetime
from starlette.websockets import WebSocket
import json

from app.database import engine, session_local
from app.schemas import Player as Player_schema, Player_create, Game as Game_schema, Game_create, Status as Status_schema, Player_login_request, Player_login_response, hash_password
from app.models import Base, Player, Game, Status
from app.functions import generate_board, process_move, has_any_ships

BOARD_SIZE = 10
PROGRESS_STATUS_ID = 1
END_STATUS_ID = 2
STEP_CODES = {"Ходит первый": 1, "Ходит второй": 2, "Победил первый": 3, "Победил второй": 4}

app = FastAPI()

Base.metadata.create_all(bind=engine)

def commit_changes(db, changed_object):
    db.commit() # Сохраним изменения
    db.refresh(changed_object) # Обновим БД с учётом изменённого / добавленного объекта

@app.on_event("startup")
def add_reference_data():
    '''Добавление данных в справочные таблицы'''
    db = session_local()
    try:
        STATUSES_NUM = 2
        if len(db.query(Status).all()) != STATUSES_NUM:
            db.execute(delete(Status)) # Очистить таблицу
            statuses = [
                Status(id=PROGRESS_STATUS_ID, status_name="В процессе"),
                Status(id=END_STATUS_ID, status_name="Завершена")
            ]
            db.add_all(statuses)
            db.commit()
            for status in statuses:
                db.refresh(status)
    finally:
        db.close()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.get("/players", response_model=list[Player_schema])
async def read_players(db: Session=Depends(get_db)):
    '''Получение всех доступных (которые на данный момент не играют) игроков'''
    players = db.query(Player).all()
    # Те, кто сейчас играет:
    busy_players = set()
    for active_game_sid in active_games.keys():
        game = db.query(Game).filter(Game.sid == active_game_sid).first()
        busy_players.update([game.id_player1, game.id_player2])
    print(busy_players)
    # Исключим играющих
    free_players = [player for player in players if player.id not in busy_players]
    return free_players

@app.post("/players/register", response_model=Player_schema)
async def register_player(player: Player_create, db: Session = Depends(get_db)) -> Player_schema:
    '''Регистрация игрока в системе'''
    player_for_db = Player(sid=str(uuid.uuid4()), login=player.login, password=player.password)
    db.add(player_for_db)
    commit_changes(db, player_for_db)
    return player_for_db

@app.post("/players/login", response_model=Player_login_response)
async def login_player(login_data: Player_login_request, db: Session = Depends(get_db)):
    '''Авторизация игрока'''
    player = db.query(Player).filter(Player.login == login_data.login).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок с данным логином не найден"
        )
    # Пароль отправляется от клиента в открытом виде и хешируется на сервере для целей тестирования,
    # поскольку клиента нет
    password = hash_password(login_data.password)
    if player.password == password:
        return Player_login_response(sid=player.sid, login=player.login)
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пароль указан неверно"
        )

@app.post("/games/create", response_model=Game_schema)
async def create_game(sid_player1 : str, sid_player2 : str, db: Session = Depends(get_db)):
    '''Создание игры. Метод принимает игроков и привязывает их в новой игре. Создает доску с рандомным расположением (но по правилам) кораблей и возвращает ее'''
    player1 = db.query(Player).filter(Player.sid == sid_player1).first()
    player2 = db.query(Player).filter(Player.sid == sid_player2).first()
    if not player1 or not player2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="sid одного из игроков не найден"
        )

    rand_board1 = generate_board(BOARD_SIZE)
    rand_board2 = generate_board(BOARD_SIZE)
    result_board = [rand_board1,rand_board2]

    cur_datetime = datetime.now()
    game_for_db = Game(sid=str(uuid.uuid4()), board=result_board, start_date=cur_datetime, id_player1=player1.id, id_player2=player2.id, id_status=1)
    db.add(game_for_db)
    commit_changes(db, game_for_db)
    return game_for_db

@app.get("/games")
async def read_games(db: Session = Depends(get_db)):
    '''Получение всех активных игр с досками'''
    games_from_db = []
    for active_game_sid in active_games.keys():
        games_from_db.append(
            db.query(Game).filter(Game.sid == active_game_sid).first()
        )
    return games_from_db

@app.get("/players/{player_sid}/stats")
async def read_games(player_sid : str, db: Session = Depends(get_db)):
    '''Получение списка всех игр с датой и результатами'''
    player = db.query(Player).filter(Player.sid == player_sid).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Игрок с указанным sid отсутствует"
        )
    games = db.query(Game).filter(or_(Game.id_player1 == player.id, Game.id_player2 == player.id)).all()
    result = []
    # Доски не возвращаем
    for game in games:
        winner = db.query(Player).filter(Player.id == game.id_winner).first()
        result.append({
            "sid" : game.sid,
            "start_date" : game.start_date,
            "end_date" : game.end_date,
            "winner_sid" : winner.sid if winner else None,
            "winner_login": winner.login if winner else None,
            "status": db.query(Status).filter(Status.id == game.id_status).first().status_name
        })
    return result

class Players_ws:
    def __init__(self):
        self.player1_ws = None
        self.player2_ws = None
        self.next_player_ws = None # Кто ходит следующим
    def has_both_players(self):
        return self.player1_ws and self.player2_ws
    def change_next_player_ws(self):
        self.next_player_ws = self.player2_ws if self.next_player_ws == self.player1_ws else self.player1_ws

def check_player_number(game_sid, player_sid, db):
    '''Проверить: какой из игроков прислал запрос (для сопоставления player_sid с ws)'''
    game = db.query(Game).filter(Game.sid == game_sid).first()
    player1_sid = db.query(Player).filter(Player.id == game.id_player1).first().sid
    player2_sid = db.query(Player).filter(Player.id == game.id_player2).first().sid
    if player1_sid == player_sid:
        return 1
    elif player2_sid == player_sid:
        return 2
    else:
        return -1

def end_game(game_sid, db, sid_winner=None):
    '''Завершить игру. Возвращает успех или неудачу'''
    if game_sid not in active_games:
        return False
    cur_datetime = datetime.now()
    game = db.query(Game).filter(Game.sid == game_sid).first()
    game.end_date = cur_datetime    # Дата и время завершения игры
    game.id_status = END_STATUS_ID  # Смена статуса на завершённый
    if sid_winner:
        id_winner = db.query(Player).filter(Player.sid == sid_winner).first().id  # id победителя
        game.id_winner = id_winner
    commit_changes(db, game)
    active_games.pop(game_sid)
    return True

active_games = {} # sid_game: player1_ws, player2_ws, next_player_ws

# Считаем, что сервер и клиент отправляют друг другу сообщения в формате json.
# Сообщения сервера могут содержать следующие поля:
#       "comment" : обычное сообщение
#       "error" : сообщение об ошибке
#       "y", "x" : координаты ячейки, удар в которую обрабатывался
#       "board" : целиком доска - [доска игрока 1, доска игрока 2] (для обновления данных на клиенте и соответствующей отрисовки)
#       "step_code" : код шага - информация о текущем положении дел в игре (возможные значения - в словаре STEP_CODES)
# От клиента ожидаются сообщения, содержащие следующие поля:
#       "action" : действие, которое запрашивает клиент ("start" / "end" / "move")
#       "player_sid" : sid игрока, от которого пришёл запрос
#       "y", "x" : координаты ячейки, в которую был нанесён удар

@app.websocket("/games/{game_sid}/play")
async def ws_game(websocket: WebSocket, game_sid: str, db: Session = Depends(get_db)):
    '''Обработка сообщений для начала и завершения игры, ходов игроков и выявление победившего игрока.
       Сохранение результатов игры.'''
    comment_header = "comment"
    error_header = "error"

    await websocket.accept() # Принимаем запрос на соединение
    if not db.query(Game).filter(Game.sid == game_sid).first():
        await websocket.send_json({error_header: "Игра с указанным sid не найдена"})
        await websocket.close()
        return
    print("Игрок присоединился к игре", game_sid)
    players = []
    # Считаем, что клиент оправляет сообщения в формате json
    try:
        while True:
            data = await websocket.receive_text() # Получаем сообщение от клиента
            # Попытка прочитать json-сообщение
            try:
                json_msg = json.loads(data)
                action = json_msg["action"]
                player_sid = json_msg["player_sid"]
            except json.JSONDecodeError:
                await websocket.send_json({error_header: "Некорректный формат сообщения"})
                continue

            if not action:
                await websocket.send_json({error_header: "Отсутствует параметр 'action'"})
                continue
            if not player_sid:
                await websocket.send_json({error_header: "Отсутствует параметр 'player_sid'"})
                continue
            print("Действие:", action)

            # Начало игры
            if action == "start":
                if game_sid not in active_games:
                    active_games[game_sid] = Players_ws()
                elif active_games[game_sid].has_both_players():
                    await websocket.send_json({error_header: "Эта игра уже началась"})
                    continue
                player_number = check_player_number(game_sid, player_sid, db)
                if player_number == 1:
                    active_games[game_sid].player1_ws = websocket
                    active_games[game_sid].next_player_ws = websocket # игрок 1 ходит первым
                elif player_number == 2:
                    active_games[game_sid].player2_ws = websocket
                else:
                    await websocket.send_json({error_header: "Игроку недоступна данная игра"})
                    return
                await websocket.send_json({comment_header: f"Игрок {player_sid} начал игру {game_sid}"})

            # Завершение игры
            elif action == "end":
                success = end_game(game_sid, db) # Завершить игру и внести соотв изменения в БД
                if not success:
                    await websocket.send_json({comment_header: f"Игра {game_sid} уже завершена"})
                    return
                await websocket.send_json({comment_header: f"Игра {game_sid} завершена"})
                return

            # Ход игрока
            elif action == "move":
                # Проверка: может ли этот игрок сейчас ходить
                if websocket != active_games[game_sid].next_player_ws:
                    await websocket.send_json({error_header: "Данный игрок сейчас не может ходить"})
                    continue
                x = json_msg["x"]
                y = json_msg["y"]
                if not x or not y:
                    await websocket.send_json({error_header: "Отсутствует координата хода x или y"})
                    continue
                try:
                    x = int(x)
                    y = int(y)
                except ValueError:
                    await websocket.send_json({error_header: "Некорректный формат координат"})
                    continue
                if x < 0 or x > (BOARD_SIZE-1):
                    await websocket.send_json({error_header: "Координата x выходит за пределы доски"})
                    continue
                if y < 0 or y > (BOARD_SIZE-1):
                    await websocket.send_json({error_header: "Координата y выходит за пределы доски"})
                    continue

                ws1 = active_games[game_sid].player1_ws
                ws2 = active_games[game_sid].player2_ws

                game = db.query(Game).filter(Game.sid == game_sid).first()
                board = game.board
                player1_is_moving = (ws1 == websocket)       # Кто сейчас ходит
                board_index = 1 if player1_is_moving else 0  # На какую доску был ход

                # Обработка хода
                move_result = process_move(board[board_index], y, x)
                if move_result == -2:
                    await websocket.send_json({error_header: f"В ячейку ({y},{x}) уже был нанесён удар ранее"})
                    continue
                game.board[board_index][y][x] = move_result
                flag_modified(game, "board") # Уведомить SQLAlchemy об изменении поля board (т.к. оно json)
                commit_changes(db, game)

                message = ""   # Сообщение с результатом удара
                step_code = -1
                if move_result == 2:
                    message = "мимо"
                    step_code = STEP_CODES["Ходит второй"] if player1_is_moving else STEP_CODES["Ходит первый"] # Переход хода
                    active_games[game_sid].change_next_player_ws()
                elif move_result == 3 or move_result == 4:
                    step_code = STEP_CODES["Ходит первый"] if player1_is_moving else STEP_CODES["Ходит второй"] # Нет перехода
                    if move_result == 3:
                        message = "ранил"
                    else:
                        message = "убил"
                        if not has_any_ships(board[board_index]):
                            id_winner = db.query(Player).filter(Player.sid == player_sid).first().id # id победителя
                            game.id_winner = id_winner
                            db.commit()
                            db.refresh(game)
                            step_code = STEP_CODES["Победил первый"] if player1_is_moving else STEP_CODES["Победил второй"]
                            active_games[game_sid].next_player_ws = None

                # Результат - обоим игрокам
                await ws1.send_json({comment_header: message, "y" : y, "x" : x, "board" : board, "step_code": step_code})
                await ws2.send_json({comment_header: message, "y" : y, "x" : x, "board" : board, "step_code": step_code})
                # Если дальше никто не может ходить, то конец игры
                if active_games[game_sid].next_player_ws == None:
                    result = 1 if player1_is_moving else 2
                    await ws1.send_json({comment_header: f"Игрок {result} победил, игра завершена"})
                    await ws2.send_json({comment_header: f"Игрок {result} победил, игра завершена"})
                    end_game(game_sid, db)
                    return

            else:
                await websocket.send_json({error_header: "Неизвестное действие"})
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)