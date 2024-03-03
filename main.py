from datetime import datetime
from sqlalchemy import func
from fastapi import FastAPI, HTTPException, Path, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from models import Base, UserWord
from database import engine, SessionLocal
from starlette import status
from pydantic import BaseModel, Field
from yandex_api import *

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
REPEAT_SCHEDULE = [1, 7, 14, 30, 60, 120, 180]


class WordRequest(BaseModel):
    user_id: int
    word: str
    translation: str


@app.get('/healthy')
async def health_check():
    return {'status': 'Healthy'}


@app.get('/word', status_code=status.HTTP_200_OK)
async def get_word(db: db_dependency):
    current_utc = datetime.utcnow().date()  # Получаем текущую дату без времени
    word_model = db.query(UserWord).filter(func.date(UserWord.reminder_date) <= current_utc).first()

    if word_model:
        # Проверяем, является ли текущий интервал последним в расписании
        if word_model.interval == REPEAT_SCHEDULE[-1]:
            # Поскольку это последний интервал, возвращаем слово пользователю и удаляем его из базы данных
            response = {"word": word_model.word, "translation": word_model.translation}

            # Удаление слова из базы данных
            db.delete(word_model)
            db.commit()

            response["message"] = "This was the last repetition. The word has been deleted."
            return response
        else:
            # Находим следующий интервал для повторения
            element_index = REPEAT_SCHEDULE.index(word_model.interval)
            next_index = element_index + 1 if element_index + 1 < len(REPEAT_SCHEDULE) else element_index
            new_reminder_date = current_utc + timedelta(days=REPEAT_SCHEDULE[element_index])
            new_interval = REPEAT_SCHEDULE[next_index]

            # Обновляем дату напоминания и интервал в модели
            word_model.reminder_date = new_reminder_date
            word_model.interval = new_interval
            db.commit()

            return {"word": word_model.word, "translation": word_model.translation, 'date': word_model.reminder_date}
    else:
        # Если подходящих слов для повторения нет
        return {"message": "No words for repetition found."}


@app.post('/word', status_code=status.HTTP_201_CREATED)
async def add_word(db: db_dependency, word_request: WordRequest):
    word_data = word_request.dict()
    word_model = UserWord(**word_data)

    word_model.interval = REPEAT_SCHEDULE[1]
    word_model.reminder_date = datetime.utcnow().date() + timedelta(days=REPEAT_SCHEDULE[0])

    # TODO создать платежный акк яндекса
    # yandex_api = YandexApi()
    # translation = yandex_api.translate(word_request.word)
    #
    # if translation:
    #     word_model.translation = translation
    # else:
    #     return 'Translate error'

    db.add(word_model)
    db.commit()


