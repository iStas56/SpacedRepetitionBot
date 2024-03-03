from database import Base
from sqlalchemy import Column, Integer, String, DateTime

class UserWord(Base):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # ID пользователя в Telegram
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    description = Column(String, nullable=True)  # Новое поле для описания
    interval = Column(Integer, nullable=True)  # Новое поле для интервала повторения
    reminder_date = Column(DateTime)  # Существующее поле для даты напоминания
