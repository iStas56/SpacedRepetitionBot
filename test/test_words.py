from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from main import app, get_db, REPEAT_SCHEDULE
import pytest
from database import Base
from models import UserWord

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_word():
    word = UserWord(
        user_id=1,
        word="example",
        translation="пример",
        description="",
        interval=7,
        reminder_date=datetime.utcnow().date(),
    )

    db = TestingSessionLocal()
    db.add(word)
    db.commit()
    yield word
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM user_words;"))
        connection.commit()


def test_add_word(test_word):
    request_data = {
        'user_id': 1,
        'word': 'example',
        'translation': 'пример',
        'interval': 7,
    }

    response = client.post('/word/', json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(UserWord).filter(UserWord.id == 1).first()
    assert model.user_id == request_data.get('user_id')
    assert model.word == request_data.get('word')
    assert model.translation == request_data.get('translation')
    assert model.interval == request_data.get('interval')


def test_get_word_and_change_interval(test_word):
    response = client.get('/word/')
    assert response.status_code == 200

    db = TestingSessionLocal()
    # Получаем текущую дату без времени и добавляем 7 дней
    today = datetime.utcnow().date()
    next_date = today + timedelta(days=7)

    # Ищем слово с обновленной датой напоминания
    word_model = db.query(UserWord).filter(func.date(UserWord.reminder_date) == next_date).first()

    assert word_model is not None
    assert word_model.reminder_date.date() == next_date
