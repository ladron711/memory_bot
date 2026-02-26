from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


category_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
category_keyboard.add(KeyboardButton("работа"),
                      KeyboardButton("семья"),
                      KeyboardButton("учеба"),
)
category_keyboard.add(KeyboardButton("спорт"),
                      KeyboardButton("хобби"),
                      KeyboardButton("отдых"),
)
category_keyboard.add(KeyboardButton("прочее"))

mood_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
mood_keyboard.add(KeyboardButton("😊"),
                  KeyboardButton("😐"),
                  KeyboardButton("😞"),
)