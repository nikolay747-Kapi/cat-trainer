# -*- coding: utf-8 -*-
"""
Cat Training Coach - приложение для дрессировки кота (Android, Kivy 2.3.1 + KivyMD 1.2.0).

Что изменено по сравнению с прошлой сборкой:
- Вместо MDBottomNavigation (он обрезает вкладки, когда их больше 5 на узком экране)
  сделана собственная нижняя панель из 6 равных кнопок + ScreenManager.
  Теперь все 6 вкладок всегда видны.
- Все тексты переносятся по ширине экрана и прокручиваются.
"""

import os
import random
from datetime import date, timedelta

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField

# ---------------------------------------------------------------------------
# Цвета
# ---------------------------------------------------------------------------
TEXT = (0.10, 0.10, 0.10, 1)
WHITE = (1, 1, 1, 1)
ACCENT = (0.91, 0.45, 0.12, 1)
GREEN = (0.13, 0.58, 0.24, 1)
RED = (0.80, 0.20, 0.20, 1)
GREY = (0.55, 0.55, 0.55, 1)
CARD_BG = (1, 1, 1, 0.93)
BAR_BG = (1, 1, 1, 0.97)

# ---------------------------------------------------------------------------
# Данные: звания, факты, справки
# ---------------------------------------------------------------------------
RANKS = [
    (0, "Уборщик лотка", "Только пришёл, ещё не осознал масштаб"),
    (21, "Разносчик корма", "Уже понял, кто тут босс"),
    (51, "Массажист дивана", "Кот разрешает почесать пузо (иногда)"),
    (101, "Прислужник кота", "Официально признан персоналом"),
    (200, "Дворецкий его Мурлычества", "Ходит на цыпочках, еду подаёт вовремя"),
    (350, "Верховный жрец Мурлыки", "Кот спит на вашей подушке как на алтаре"),
    (500, "Раб с правом на мурлыканье", "Допущен к священному урчанию"),
    (700, "Легенда кошачьего сервиса", "О вас слагают мяу-легенды"),
    (1000, "Избранный Мурлыкой", "Кот приносит вам мышь. Добровольно."),
]

FACTS = [
    "Мурлыканье кота - 25-150 Гц, такая частота связана с расслаблением.",
    "Кошки спят 12-16 часов в сутки.",
    "У кошки 32 мышцы в каждом ухе.",
    "Кошки не чувствуют сладкое.",
    "Нос кошки уникален, как отпечаток пальца.",
    "Кошки мяукают в основном для людей.",
    "Подушечки лап у кошек могут пахнуть попкорном.",
    "Кошки видят в темноте в 6 раз лучше человека.",
]

CLICKER_HELP = (
    "ЧТО ТАКОЕ КЛИКЕР\n\n"
    "Кликер — маленькая коробочка-трещотка с резким щелчком. "
    "Стоит 100-300 руб в зоомагазине. Альтернатива: приложение-кликер "
    "или слово-маркер Да!.\n\n"
    "ЗАЧЕМ ОН НУЖЕН\n\n"
    "Между действием кота и лакомством проходит 1-2 секунды. Кликер "
    "решает это: звук клика — ТОЧНЫЙ маркер вот именно это, прямо сейчас.\n\n"
    "КАК РАБОТАЕТ\n\n"
    "ФАЗА 1: ЗАРЯЖАЕМ (2-3 дня). Клик -> лакомство. 10 раз за сессию.\n\n"
    "ФАЗА 2: ИСПОЛЬЗУЕМ. Учишь Сидеть. Кот садится. В момент касания "
    "попы пола — КЛИК. Потом (через 1-2 сек) — лакомство.\n\n"
    "ЧАСТЫЕ ОШИБКИ\n\n"
    "1. Кликают без зарядки.\n"
    "2. Кликают с опозданием.\n"
    "3. Кликают много раз подряд.\n"
    "4. Дают еду через 10 секунд.\n"
    "5. Используют кликер для наказания.\n\n"
    "ПРАВИЛА\n\n"
    "Клик — ОДИН раз.\n"
    "Клик всегда = еда.\n"
    "Лакомство через 1-2 сек после клика.\n"
    "Кликер только для тренировок."
)

STOP_SIGNALS = [
    ("Кот уходит сам", "Больше не хочет участвовать"),
    ("Хвост дёргается резко", "Раздражение, стресс"),
    ("Уши прижаты", "Дискомфорт, страх"),
    ("Кот вылизывается", "Признак стресса"),
    ("Зрачки расширены", "Хочет избежать"),
    ("Мяуканье с низкими нотами", "Предупреждение"),
]

REASONS = [
    ("Ты торопишься", "Кот не понял шаг. Перескочил микрошаг.", "Откатись назад."),
    ("Кот не голоден", "Сытый кот не работает.", "Тренируйся до кормления."),
    ("Награда не ценная", "Обычный корм = ноль мотивации.", "Нужно особое лакомство."),
    ("Долгая сессия", "Кошки теряют концентрацию.", "Сессия 2-3 мин."),
    ("Кот не в настроении", "Кошки не работают по расписанию.", "Лови момент."),
    ("Наказал за подход", "Зов = плохо.", "Неприятное делай сам, а не зови для этого."),
]

FIXES = [
    ("Сидеть", ["Проверь мотивацию", "Веди медленнее", "Награждай за движение вниз"]),
    ("Дай лапу", ["Кулак с лакомством", "Нос игнор, лапа клик", "Не хватай лапу сам"]),
    ("Ко мне", ["Сократи дистанцию", "Клик за первый шаг", "Зов = праздник"]),
    ("Лежать", ["Начни с Сидеть", "Веди по полу медленно", "Награждай за локти"]),
    ("Зайка", ["Чуть выше головы", "Награждай за подъём", "Падает - ниже руку"]),
    ("Кувырок", ["Отработай Лежать", "Веди по дуге медленно", "Награждай за поворот"]),
]

QUOTE = "Я не дрессирую кошек, я договариваюсь с ними - Ю. Куклачёв"
PRINCIPLES = [
    "Кошку нельзя заставить. Только мотивировать.",
    "Кошка не обязана. Она делает, если видит выгоду.",
    "Не получается - проблема в методе.",
    "Наказание не работает. Только терпение.",
]

RULES = [
    "Награда в течение 1-2 секунд",
    "Сессия 2-5 минут, 2-3 раза в день",
    "Занятия до еды, а не после",
    "Никогда не наказывать",
]

# ---------------------------------------------------------------------------
# Программа: 42 дня, 6 недель
# ---------------------------------------------------------------------------
PROGRAM = [
    {"day":1,"week":1,"level":"Контакт","title":"Клик = еда",
     "goal":"Кот понимает: клик = немедленная награда",
     "sessions":3,"minutes":"2 мин",
     "steps":["Сядь на пол. Возьми кликер и 10 кусочков лакомства.",
              "Щёлкни ОДИН раз - сразу лакомство (1-2 сек).",
              "Пауза 5 сек. Повтори. 10 раз за сессию.",
              "Ничего не требуй. Просто клик - еда."],
     "success":"Кот оживляется при клике и ищет руку"},
    {"day":2,"week":1,"level":"Контакт","title":"Маркер + внимание",
     "goal":"Закрепить клик = еда","sessions":3,"minutes":"2 мин",
     "steps":["Сядь на пол с кликером и лакомствами.",
              "Кот посмотрел - клик - лакомство.",
              "Мяукнул - клик - лакомство.",
              "Подошёл - клик - лакомство.",
              "10 кликов за сессию только за внимание."],
     "success":"5 из 10 кликов вызывают реакцию"},
    {"day":3,"week":1,"level":"Контакт","title":"Сидеть - первый шаг",
     "goal":"Кот садится, когда еда над головой","sessions":3,"minutes":"2-3 мин",
     "steps":["Лакомство к носу кота.",
              "Медленно веди руку над головой.",
              "Нос вверх - попа вниз.",
              "В момент касания пола - КЛИК - лакомство.",
              "10 повторов за сессию."],
     "success":"Кот садится сам 3 раза из 5"},
    {"day":4,"week":1,"level":"Контакт","title":"Сидеть + слово",
     "goal":"Кот садится по команде","sessions":3,"minutes":"3 мин",
     "steps":["Скажи Сидеть ОДИН раз.",
              "Через 0,5 сек веди лакомство над головой.",
              "Кот сел - КЛИК - лакомство.",
              "10-12 повторов."],
     "success":"5 из 10 - кот садится по слову"},
    {"day":5,"week":1,"level":"Контакт","title":"Сидеть - меньше подсказки",
     "goal":"Кот садится на пустой жест","sessions":3,"minutes":"3 мин",
     "steps":["Сидеть + подними ПУСТУЮ руку.",
              "Сел - клик - лакомство из ДРУГОЙ руки.",
              "Не сел - покажи лакомство.",
              "10 повторов."],
     "success":"7 из 10 - кот садится на жест"},
    {"day":6,"week":1,"level":"Контакт","title":"Сидеть в разных местах",
     "goal":"Команда работает в разных местах","sessions":3,"minutes":"3 мин",
     "steps":["Сессия 1 - кухня.","Сессия 2 - комната.","Сессия 3 - у окна.",
              "5-7 повторов в каждом месте."],
     "success":"Кот садится в 2 разных местах"},
    {"day":7,"week":1,"level":"Контакт","title":"Отдых",
     "goal":"Закрепить Сидеть","sessions":2,"minutes":"2 мин",
     "steps":["5 повторов на кухне.","5 повторов в комнате.","Без нового."],
     "success":"Кот стабильно садится"},
    {"day":8,"week":2,"level":"Базовые команды","title":"Дай лапу - знакомство",
     "goal":"Кот трогает ладонь лапой","sessions":3,"minutes":"3 мин",
     "steps":["Сядь на пол. Лакомство в кулак.","Кулак на пол перед котом.",
              "Нос - игнор. Лапа - КЛИК - открой ладонь.",
              "10 попыток за сессию."],
     "success":"Кот тронул ладонь лапой хотя бы раз"},
    {"day":9,"week":2,"level":"Базовые команды","title":"Дай лапу + команда",
     "goal":"Кот даёт лапу по слову","sessions":3,"minutes":"3 мин",
     "steps":["Скажи Дай лапу ОДИН раз.",
              "Держи кулак на уровне груди кота.",
              "Нос - игнор. Лапа - клик - лакомство.","10-12 повторов."],
     "success":"3-4 раза из 10 кот трогает ладонь лапой"},
    {"day":10,"week":2,"level":"Базовые команды","title":"Дай лапу - держи",
     "goal":"Кот держит лапу 1 секунду","sessions":3,"minutes":"3 мин",
     "steps":["Дай лапу + открытая ладонь.",
              "Кот положил лапу - закрой ладонь.",
              "Считай до 1. Клик - открой - лакомство.","8-10 повторов."],
     "success":"Кот держит лапу 1 сек 3 раза из 5"},
    {"day":11,"week":2,"level":"Базовые команды","title":"Дай лапу - пустая рука",
     "goal":"Кот даёт лапу без лакомства","sessions":3,"minutes":"3 мин",
     "steps":["Протяни ПУСТУЮ руку.",
              "Дай лапу. Дал - клик - лакомство из ДРУГОЙ руки.",
              "10 повторов."],
     "success":"5 из 10 - даёт лапу на пустую руку"},
    {"day":12,"week":2,"level":"Базовые команды","title":"Цепочка Сидеть+Дай лапу",
     "goal":"Кот делает 2 команды подряд","sessions":3,"minutes":"3 мин",
     "steps":["Сидеть - сел - клик - лакомство.","Пауза 1 сек.",
              "Дай лапу - дал - клик - лакомство.","5-7 цепочек."],
     "success":"Цепочка 3 раза из 5"},
    {"day":13,"week":2,"level":"Базовые команды","title":"Другой человек",
     "goal":"Кот даёт лапу другому","sessions":2,"minutes":"3 мин",
     "steps":["Позови члена семьи.",
              "Он говорит Дай лапу + показывает руку.",
              "Кот дал - клик - лакомство (даёте вы).","7-10 повторов."],
     "success":"Кот даёт лапу другому 3 раза"},
    {"day":14,"week":2,"level":"Базовые команды","title":"Отдых",
     "goal":"Закрепить 2 команды","sessions":2,"minutes":"2 мин",
     "steps":["Сидеть x 5 + Дай лапу x 5.","Цепочка x 5."],
     "success":"Команды стабильны"},
    {"day":15,"week":3,"level":"Базовые команды","title":"Ко мне - 1 метр",
     "goal":"Кот подходит на зов","sessions":3,"minutes":"3 мин",
     "steps":["Отойди на 1 метр.","Имя + Ко мне радостно.",
              "Первый шаг - клик - лакомство.","10 повторов."],
     "success":"5 из 10 - подходит"},
    {"day":16,"week":3,"level":"Базовые команды","title":"Ко мне - 2 метра",
     "goal":"Кот подходит с 2 метров","sessions":3,"minutes":"3 мин",
     "steps":["Отойди на 2 метра.","Зов радостно.",
              "Не идёт - вернись на 1 метр.","8-10 повторов."],
     "success":"5 из 10 - подходит с 2 м"},
    {"day":17,"week":3,"level":"Трюки","title":"Лежать - первый шаг",
     "goal":"Кот ложится","sessions":3,"minutes":"3 мин",
     "steps":["Кот сидит. Лакомство в руке.",
              "Веди руку от носа вниз по полу.",
              "Локти на полу - клик - лакомство.","8-10 повторов."],
     "success":"Кот ложится 3 раза из 5"},
    {"day":18,"week":3,"level":"Трюки","title":"Лежать + слово",
     "goal":"Кот ложится по слову","sessions":3,"minutes":"3 мин",
     "steps":["Скажи Лежать ОДИН раз.",
              "Через 0,5 сек веди руку вниз.",
              "Лёг - клик - лакомство.","10 повторов."],
     "success":"5 из 10 - ложится по слову"},
    {"day":19,"week":3,"level":"Трюки","title":"Ко мне + Сидеть",
     "goal":"Кот подходит и садится","sessions":3,"minutes":"3 мин",
     "steps":["Ко мне - подошёл - клик - лакомство.",
              "Сразу Сидеть - сел - клик - лакомство.","5-7 цепочек."],
     "success":"Цепочка 3 раза из 5"},
    {"day":20,"week":3,"level":"Трюки","title":"Лежать из Сидеть",
     "goal":"Кот садится - ложится","sessions":3,"minutes":"3 мин",
     "steps":["Сидеть - сел - клик.","Лежать - лёг - клик.","5-7 цепочек."],
     "success":"3 раза из 5"},
    {"day":21,"week":3,"level":"Трюки","title":"Отдых",
     "goal":"Закрепить 4 команды","sessions":2,"minutes":"2 мин",
     "steps":["Все 4 команды по 3 раза."],"success":"Все команды узнаются"},
    {"day":22,"week":4,"level":"Трюки","title":"Зайка - подъём",
     "goal":"Кот встаёт на задние лапы","sessions":3,"minutes":"3 мин",
     "steps":["Лакомство чуть выше головы.","Кот тянется - встаёт.",
              "Клик - лакомство.","8-10 повторов."],
     "success":"Кот встаёт 3 раза из 5"},
    {"day":23,"week":4,"level":"Трюки","title":"Зайка + слово",
     "goal":"Кот встаёт по слову","sessions":3,"minutes":"3 мин",
     "steps":["Зайка + рука чуть выше головы.",
              "Встал - клик - лакомство.","10 повторов."],
     "success":"5 из 10"},
    {"day":24,"week":4,"level":"Трюки","title":"Кувырок - подготовка",
     "goal":"Кот поворачивает голову","sessions":3,"minutes":"3 мин",
     "steps":["Лежать - лёг - клик.",
              "Веди лакомство над головой к плечу.",
              "Повернул голову - клик.","7-8 повторов."],
     "success":"Поворот 5 из 10"},
    {"day":25,"week":4,"level":"Трюки","title":"Кувырок - переворот",
     "goal":"Кот перекатывается","sessions":3,"minutes":"3 мин",
     "steps":["Лежать.","Веди лакомство за плечо по дуге.",
              "Перекатился - клик - лакомство.","5-7 попыток."],
     "success":"2 раза из 5"},
    {"day":26,"week":4,"level":"Трюки","title":"Кувырок + слово",
     "goal":"По слову Кувырок","sessions":3,"minutes":"3 мин",
     "steps":["Кувырок + дуга рукой.",
              "Перекатился - клик - лакомство.","8-10 повторов."],
     "success":"5 из 10"},
    {"day":27,"week":4,"level":"Трюки","title":"Цепочка трюков",
     "goal":"Кот делает 2 трюка","sessions":3,"minutes":"3 мин",
     "steps":["Сидеть - клик - лакомство.",
              "Дай лапу - клик - лакомство.","5-7 цепочек."],
     "success":"3 из 5"},
    {"day":28,"week":4,"level":"Трюки","title":"Отдых",
     "goal":"Закрепить трюки","sessions":2,"minutes":"2 мин",
     "steps":["Зайка x 5, Кувырок x 3.","Цепочка x 5."],
     "success":"Трюки идут с интересом"},
    {"day":29,"week":5,"level":"Мастер","title":"Переноска - знакомство",
     "goal":"Кот заходит в открытую переноску","sessions":3,"minutes":"3 мин",
     "steps":["Переноска на полу в тихой комнате.",
              "Лакомство внутри, у входа.",
              "Заходит - клик - лакомство.",
              "7-8 повторов. Дверь не закрывай!"],
     "success":"Заходит сам 3 раза"},
    {"day":30,"week":5,"level":"Мастер","title":"Переноска - глубже",
     "goal":"Кот заходит полностью","sessions":3,"minutes":"3 мин",
     "steps":["Лакомство в середине.",
              "Заходит - клик - лакомство.","7-8 повторов."],
     "success":"Заходит полностью 3 из 5"},
    {"day":31,"week":5,"level":"Мастер","title":"Переноска - закрываем",
     "goal":"Кот спокойно переносит дверь","sessions":3,"minutes":"3 мин",
     "steps":["Зашёл - закрой дверь на 2 сек.",
              "Клик - открой - лакомство.",
              "До 5 сек постепенно."],
     "success":"5 сек без паники"},
    {"day":32,"week":5,"level":"Мастер","title":"Переноска - 30 секунд",
     "goal":"Кот сидит в закрытой переноске","sessions":3,"minutes":"3 мин",
     "steps":["Зашёл - закрой дверь.",
              "10 сек - клик - открой - лакомство.",
              "До 30 сек постепенно."],
     "success":"30 сек без стресса"},
    {"day":33,"week":5,"level":"Мастер","title":"Переноска - поднимаем",
     "goal":"Кот не боится подъёма","sessions":3,"minutes":"3 мин",
     "steps":["Кот в переноске, дверь закрыта.",
              "Подними на 5 см - опусти - клик.",
              "Постепенно выше."],
     "success":"Спокойно переносит подъём"},
    {"day":34,"week":5,"level":"Мастер","title":"Переноска - переносим",
     "goal":"Кот спокойно едет","sessions":3,"minutes":"3 мин",
     "steps":["Кот в переноске.",
              "2 шага - стоп - клик - лакомство.",
              "До 10 шагов."],
     "success":"Спокойно едет по комнате"},
    {"day":35,"week":5,"level":"Мастер","title":"Отдых",
     "goal":"Закрепить переноску","sessions":2,"minutes":"2 мин",
     "steps":["Заходим, закрываем на 10 сек.",
              "Заходим, поднимаем, 5 шагов."],
     "success":"Заходит без страха"},
    {"day":36,"week":6,"level":"Мастер","title":"Когти - касание",
     "goal":"Кот даёт трогать лапу","sessions":3,"minutes":"3 мин",
     "steps":["Коснись лапы на 1 сек.","Клик - лакомство.",
              "10 раз за сессию."],
     "success":"Не убирает лапу"},
    {"day":37,"week":6,"level":"Мастер","title":"Когти - нажим",
     "goal":"Кот позволяет показать коготь","sessions":3,"minutes":"3 мин",
     "steps":["Нажми на пальцы - коготь вышел.","Клик - лакомство.",
              "8-10 повторов."],
     "success":"Позволяет показать коготь"},
    {"day":38,"week":6,"level":"Мастер","title":"Когти - когтерез рядом",
     "goal":"Кот не боится когтереза","sessions":3,"minutes":"3 мин",
     "steps":["Когтерез в руке рядом с лапой.","Клик - лакомство.",
              "Не режем пока!"],
     "success":"Спокоен при виде когтереза"},
    {"day":39,"week":6,"level":"Мастер","title":"Когти - один",
     "goal":"Стрижём один коготь","sessions":3,"minutes":"3 мин",
     "steps":["Покажи коготь - отрежь кончик.","Клик - лакомство.",
              "1 коготь за сессию."],
     "success":"Спокойно переносит стрижку"},
    {"day":40,"week":6,"level":"Мастер","title":"Когти - два",
     "goal":"Стрижём 2 когтя","sessions":3,"minutes":"3 мин",
     "steps":["По одному с наградой.","Максимум 2."],
     "success":"Спокоен при 2 когтях"},
    {"day":41,"week":6,"level":"Мастер","title":"Когти - вся лапа",
     "goal":"Обрабатываем всю лапу","sessions":3,"minutes":"3 мин",
     "steps":["По одному когтю с наградой.",
              "Дёргается - пауза.","1 лапа за сессию."],
     "success":"Обрабатываем лапу полностью"},
    {"day":42,"week":6,"level":"Мастер","title":"ФИНАЛ",
     "goal":"Показать всё","sessions":1,"minutes":"5 мин",
     "steps":["Сидеть - Дай лапу - Ко мне.",
              "Лежать - Зайка - Кувырок.",
              "Переноска 30 сек.","Стрижка 1 когтя.",
              "Финальная награда!"],
     "success":"Вы — выпускник курса!"},
]

# ---------------------------------------------------------------------------
# Хранилище и состояние
# ---------------------------------------------------------------------------
STORE = None
STATE = {}


def default_state():
    """Возвращает словарь состояния со всеми полями по умолчанию."""
    return {
        "cat_name": "",
        "points": 0,
        "streak": 0,
        "last_date": "",
        "start_date": date.today().isoformat(),
        "clicks": 0,
        "done": {},
        "sessions": {},
        "notes": {},
    }


def load_state(store):
    """Загружает состояние из JsonStore. Если ключа state нет - создаёт его."""
    global STORE, STATE
    STORE = store
    defaults = default_state()
    try:
        if STORE.exists("state"):
            data = dict(STORE.get("state"))
        else:
            data = {}
    except Exception as exc:
        print("Ошибка чтения хранилища:", exc)
        data = {}
    # Добавляем недостающие поля (на случай старой версии файла)
    for key, value in defaults.items():
        if key not in data:
            data[key] = value
    STATE = data
    save_state()


def save_state():
    """Сохраняет состояние в JsonStore."""
    try:
        STORE.put("state", **STATE)
    except Exception as exc:
        print("Ошибка записи хранилища:", exc)


def get_rank(points):
    """Возвращает (индекс, название, описание) текущего звания."""
    index = 0
    for i, rank in enumerate(RANKS):
        if points >= rank[0]:
            index = i
    return index, RANKS[index][1], RANKS[index][2]


def get_program_day():
    """Текущий день программы (1-42) по дате старта."""
    try:
        start = date.fromisoformat(STATE["start_date"])
    except Exception:
        start = date.today()
    number = (date.today() - start).days + 1
    return max(1, min(42, number))


def get_day_info(day):
    """Возвращает словарь с данными дня (1-42)."""
    day = max(1, min(42, int(day)))
    return PROGRAM[day - 1]


def vibrate(ms=30):
    """Короткая вибрация на Android. На десктопе молча ничего не делает."""
    if platform != "android":
        return
    try:
        from jnius import autoclass
        python_activity = autoclass("org.kivy.android.PythonActivity")
        context = autoclass("android.content.Context")
        vibrator = python_activity.mActivity.getSystemService(context.VIBRATOR_SERVICE)
        vibrator.vibrate(ms)
    except Exception as exc:
        print("Вибрация недоступна:", exc)


# ---------------------------------------------------------------------------
# Вспомогательные виджеты
# ---------------------------------------------------------------------------
def make_label(text, size=15, color=TEXT, bold=False, halign="left"):
    """Текстовая метка с переносом по ширине и автоматической высотой."""
    label = Label(
        text=text,
        font_size=sp(size),
        color=color,
        bold=bold,
        halign=halign,
        valign="top",
        size_hint_y=None,
    )
    label.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
    label.bind(texture_size=lambda inst, s: setattr(inst, "height", s[1] + dp(4)))
    return label


def make_card(color=CARD_BG):
    """Карточка с адаптивной высотой."""
    return MDCard(
        orientation="vertical",
        padding=dp(12),
        spacing=dp(6),
        size_hint_y=None,
        adaptive_height=True,
        md_bg_color=color,
        radius=[dp(12)],
    )


def make_button(text, callback, color=ACCENT, height=48):
    """Широкая кнопка MDRaisedButton."""
    return MDRaisedButton(
        text=text,
        md_bg_color=color,
        size_hint=(1, None),
        height=dp(height),
        on_release=callback,
    )


class ScrollScreen(MDScreen):
    """Базовый экран: вертикальная прокрутка + контейнер self.box."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        self.box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(10),
            spacing=dp(10),
        )
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.box.clear_widgets()


# ---------------------------------------------------------------------------
# Экран «Сегодня»
# ---------------------------------------------------------------------------
class TodayScreen(ScrollScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status_label = None
        self.note_field = None

    def refresh(self):
        app = MDApp.get_running_app()
        self.box.clear_widgets()
        day = get_program_day()
        info = get_day_info(day)
        key = str(day)

        # Подсказка, если имя кота не задано
        if not STATE["cat_name"].strip():
            hint = make_card((1.0, 0.93, 0.80, 0.97))
            hint.add_widget(make_label("Настройте профиль кота на вкладке Профиль", 15, bold=True))
            hint.add_widget(make_button("Открыть профиль", lambda *a: app.switch("profile")))
            self.box.add_widget(hint)

        # Заголовок дня
        head = make_card()
        head.add_widget(make_label("ДЕНЬ %d | Неделя %d" % (day, info["week"]), 20, ACCENT, True))
        head.add_widget(make_label(info["title"], 18, bold=True))
        head.add_widget(make_label("Уровень: " + info["level"], 14, GREY))
        self.status_label = make_label("", 16, bold=True)
        head.add_widget(self.status_label)
        self.box.add_widget(head)
        self.update_status()

        # Цель, шаги, критерий
        body = make_card()
        body.add_widget(make_label("Цель: " + info["goal"], 15))
        body.add_widget(make_label("Сессий: %d по %s" % (info["sessions"], info["minutes"]), 15))
        body.add_widget(make_label("ЧТО ДЕЛАТЬ:", 15, ACCENT, True))
        for number, step in enumerate(info["steps"], 1):
            body.add_widget(make_label("%d. %s" % (number, step), 15))
        body.add_widget(make_label("Критерий: " + info["success"], 15, GREEN, True))
        self.box.add_widget(body)

        # Чекбоксы сессий
        sess_card = make_card()
        sess_card.add_widget(make_label("Отметь сессии:", 16, bold=True))
        sessions = STATE["sessions"].get(key)
        if not sessions or len(sessions) != info["sessions"]:
            sessions = [False] * info["sessions"]
        for index in range(info["sessions"]):
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48))
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                active=bool(sessions[index]),
            )
            checkbox.bind(
                active=lambda inst, value, d=day, i=index: app.toggle_session(d, i, value)
            )
            row_label = Label(
                text="Сессия %d (+5 баллов)" % (index + 1),
                font_size=sp(15),
                color=TEXT,
                halign="left",
                valign="middle",
            )
            row_label.bind(size=lambda inst, s: setattr(inst, "text_size", s))
            row.add_widget(checkbox)
            row.add_widget(row_label)
            sess_card.add_widget(row)
        self.box.add_widget(sess_card)

        # Заметка
        note_card = make_card()
        note_card.add_widget(make_label("Заметка:", 16, bold=True))
        self.note_field = MDTextField(
            text=STATE["notes"].get(key, ""),
            hint_text="Как прошло?",
            multiline=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(120),
        )
        note_card.add_widget(self.note_field)
        note_card.add_widget(
            make_button("Сохранить заметку", lambda *a: app.save_note(day, self.note_field.text))
        )
        self.box.add_widget(note_card)
        self.box.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def update_status(self):
        """Обновляет надпись ВЫПОЛНЕНО / НЕ ВЫПОЛНЕНО без пересборки экрана."""
        if self.status_label is None:
            return
        done = STATE["done"].get(str(get_program_day()), False)
        if done:
            self.status_label.text = "ВЫПОЛНЕНО"
            self.status_label.color = GREEN
        else:
            self.status_label.text = "НЕ ВЫПОЛНЕНО"
            self.status_label.color = RED


# ---------------------------------------------------------------------------
# Экран «Кликер»
# ---------------------------------------------------------------------------
class ClickerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.add_widget(self.root_box)
        self.counter_label = None

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.root_box.clear_widgets()

        top = make_card()
        top.add_widget(make_label("КЛИКЕР", 20, ACCENT, True, "center"))
        self.counter_label = make_label("Всего кликов: %d" % STATE["clicks"], 18, bold=True, halign="center")
        top.add_widget(self.counter_label)
        top.add_widget(
            MDRaisedButton(
                text="КЛИК",
                font_size=sp(30),
                md_bg_color=ACCENT,
                size_hint=(1, None),
                height=dp(110),
                on_release=self.do_click,
            )
        )
        top.add_widget(make_button("Сбросить", self.reset_counter, GREY, 40))
        self.root_box.add_widget(top)

        # Прокручиваемая справка
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        help_card = make_card()
        help_card.add_widget(make_label(CLICKER_HELP, 14))
        scroll.add_widget(help_card)
        self.root_box.add_widget(scroll)

    def do_click(self, *args):
        STATE["clicks"] += 1
        save_state()
        vibrate(30)
        if self.counter_label is not None:
            self.counter_label.text = "Всего кликов: %d" % STATE["clicks"]

    def reset_counter(self, *args):
        STATE["clicks"] = 0
        save_state()
        if self.counter_label is not None:
            self.counter_label.text = "Всего кликов: 0"


# ---------------------------------------------------------------------------
# Экран «Программа»
# ---------------------------------------------------------------------------
class ProgramScreen(ScrollScreen):
    def refresh(self):
        app = MDApp.get_running_app()
        self.box.clear_widgets()
        today = get_program_day()
        for week in range(1, 7):
            header = make_card(ACCENT)
            header.add_widget(make_label("НЕДЕЛЯ %d" % week, 16, WHITE, True))
            self.box.add_widget(header)
            for info in PROGRAM:
                if info["week"] != week:
                    continue
                day = info["day"]
                done = STATE["done"].get(str(day), False)
                mark = "[X]" if done else "[ ]"
                text = "%s  %d. %s" % (mark, day, info["title"])
                if day == today:
                    text += "  (СЕГОДНЯ)"
                row = MDCard(
                    orientation="horizontal",
                    padding=dp(12),
                    size_hint_y=None,
                    height=dp(52),
                    md_bg_color=CARD_BG,
                    radius=[dp(10)],
                    on_release=lambda inst, d=day: app.open_day(d),
                )
                row_label = Label(
                    text=text,
                    font_size=sp(15),
                    color=GREEN if done else TEXT,
                    bold=(day == today),
                    halign="left",
                    valign="middle",
                )
                row_label.bind(size=lambda inst, s: setattr(inst, "text_size", s))
                row.add_widget(row_label)
                self.box.add_widget(row)
        self.box.add_widget(Widget(size_hint_y=None, height=dp(20)))


# ---------------------------------------------------------------------------
# Экран подробностей дня
# ---------------------------------------------------------------------------
class DayDetailScreen(ScrollScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.day = 1

    def refresh(self):
        app = MDApp.get_running_app()
        self.box.clear_widgets()
        info = get_day_info(self.day)
        key = str(self.day)
        done = STATE["done"].get(key, False)

        self.box.add_widget(make_button("<- Назад", lambda *a: app.switch("program"), GREY, 44))

        head = make_card()
        head.add_widget(make_label("День %d | Неделя %d" % (self.day, info["week"]), 20, ACCENT, True))
        head.add_widget(make_label(info["title"], 18, bold=True))
        head.add_widget(make_label("Уровень: " + info["level"], 14, GREY))
        head.add_widget(
            make_label("ВЫПОЛНЕНО" if done else "НЕ ВЫПОЛНЕНО", 16, GREEN if done else RED, True)
        )
        self.box.add_widget(head)

        body = make_card()
        body.add_widget(make_label("Цель: " + info["goal"], 15))
        body.add_widget(make_label("Сессий: %d по %s" % (info["sessions"], info["minutes"]), 15))
        body.add_widget(make_label("ЧТО ДЕЛАТЬ:", 15, ACCENT, True))
        for number, step in enumerate(info["steps"], 1):
            body.add_widget(make_label("%d. %s" % (number, step), 15))
        body.add_widget(make_label("Критерий: " + info["success"], 15, GREEN, True))
        self.box.add_widget(body)

        note = STATE["notes"].get(key, "").strip()
        if note:
            note_card = make_card()
            note_card.add_widget(make_label("Заметка:", 15, bold=True))
            note_card.add_widget(make_label(note, 14))
            self.box.add_widget(note_card)
        self.box.add_widget(Widget(size_hint_y=None, height=dp(20)))


# ---------------------------------------------------------------------------
# Экран «Звания»
# ---------------------------------------------------------------------------
class RewardsScreen(ScrollScreen):
    def refresh(self):
        self.box.clear_widgets()
        points = STATE["points"]
        current_index, current_name, current_desc = get_rank(points)

        head = make_card()
        head.add_widget(make_label("ВИТРИНА ЗВАНИЙ", 20, ACCENT, True))
        head.add_widget(make_label("%d баллов" % points, 18, bold=True))
        head.add_widget(make_label("Звание: " + current_name, 16, GREEN, True))
        self.box.add_widget(head)

        next_index = current_index + 1
        for index, (threshold, name, desc) in enumerate(RANKS):
            card = make_card()
            if points >= threshold:
                color = GREEN
                mark = "[+]"
                extra = "Получено при %d баллах" % threshold
            elif index == next_index:
                color = ACCENT
                mark = "[>]"
                extra = "Осталось %d баллов (при %d)" % (threshold - points, threshold)
            else:
                color = GREY
                mark = "[−]"
                extra = "При %d баллах (осталось %d)" % (threshold, threshold - points)
            card.add_widget(make_label("%s %s" % (mark, name), 16, color, True))
            card.add_widget(make_label(desc, 14, color))
            card.add_widget(make_label(extra, 13, color))
            self.box.add_widget(card)
        self.box.add_widget(Widget(size_hint_y=None, height=dp(20)))


# ---------------------------------------------------------------------------
# Экран «Диагностика»
# ---------------------------------------------------------------------------
class DiagScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.add_widget(self.root_box)
        self.text_label = None
        self.current = ""

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        self.root_box.clear_widgets()

        top = make_card()
        top.add_widget(make_label("ДИАГНОСТИКА", 20, ACCENT, True))
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(104))
        for title, key in (("Стоп", "stop"), ("Причины", "reasons"), ("Команды", "fixes"), ("Мудрость", "wisdom")):
            grid.add_widget(
                MDRaisedButton(
                    text=title,
                    md_bg_color=ACCENT,
                    size_hint=(1, 1),
                    on_release=lambda inst, k=key: self.show(k),
                )
            )
        top.add_widget(grid)
        self.root_box.add_widget(top)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        text_card = make_card()
        self.text_label = make_label("Выбери раздел сверху", 15)
        text_card.add_widget(self.text_label)
        scroll.add_widget(text_card)
        self.root_box.add_widget(scroll)

        if self.current:
            self.show(self.current)

    def show(self, key):
        self.current = key
        if key == "stop":
            text = "СТОП-СИГНАЛЫ\n\n"
            for title, meaning in STOP_SIGNALS:
                text += "- %s: %s\n" % (title, meaning)
            text += "\nЗакончи сессию. Вернись позже."
        elif key == "reasons":
            text = "6 ПРИЧИН\n\n"
            for number, (cause, why, fix) in enumerate(REASONS, 1):
                text += "%d. %s\n%s\nЧто делать: %s\n\n" % (number, cause, why, fix)
        elif key == "fixes":
            text = "ИСПРАВЛЕНИЕ\n\n"
            for command, tips in FIXES:
                text += "%s:\n" % command
                for tip in tips:
                    text += "  - %s\n" % tip
                text += "\n"
        else:
            text = "ФИЛОСОФИЯ\n\n" + QUOTE + "\n\n"
            for number, principle in enumerate(PRINCIPLES, 1):
                text += "%d. %s\n" % (number, principle)
        if self.text_label is not None:
            self.text_label.text = text.strip()


# ---------------------------------------------------------------------------
# Экран «Профиль»
# ---------------------------------------------------------------------------
class ProfileScreen(ScrollScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name_field = None

    def refresh(self):
        app = MDApp.get_running_app()
        self.box.clear_widgets()

        card = make_card()
        card.add_widget(make_label("ПРОФИЛЬ", 20, ACCENT, True))
        if not STATE["cat_name"].strip():
            card.add_widget(make_label("Введите имя кота и нажмите Сохранить.", 14, RED))
        else:
            card.add_widget(make_label("Профиль " + STATE["cat_name"], 15, GREEN, True))
        self.name_field = MDTextField(
            text=STATE["cat_name"],
            hint_text="Имя кота",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
        )
        card.add_widget(self.name_field)
        card.add_widget(make_button("Сохранить", lambda *a: app.save_profile(self.name_field.text)))
        self.box.add_widget(card)

        rules = make_card()
        rules.add_widget(make_label("4 ПРАВИЛА", 18, ACCENT, True))
        for number, rule in enumerate(RULES, 1):
            rules.add_widget(make_label("%d. %s" % (number, rule), 15))
        self.box.add_widget(rules)
        self.box.add_widget(Widget(size_hint_y=None, height=dp(20)))


# ---------------------------------------------------------------------------
# Кнопка нижней панели
# ---------------------------------------------------------------------------
class TabButton(ButtonBehavior, BoxLayout):
    def __init__(self, icon, title, **kwargs):
        super().__init__(orientation="vertical", padding=(0, dp(4)), **kwargs)
        self.icon = MDIcon(
            icon=icon,
            halign="center",
            font_size=sp(24),
            theme_text_color="Custom",
            text_color=GREY,
        )
        # Контейнер центрирует иконку по ширине вкладки
        icon_box = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_y=0.6)
        icon_box.add_widget(self.icon)
        self.caption = Label(
            text=title,
            font_size=sp(10),
            color=GREY,
            halign="center",
            valign="middle",
            size_hint_y=0.4,
        )
        self.caption.bind(size=lambda inst, s: setattr(inst, "text_size", s))
        self.add_widget(icon_box)
        self.add_widget(self.caption)

    def set_active(self, active):
        color = ACCENT if active else GREY
        self.icon.text_color = color
        self.caption.color = color
        self.caption.bold = active


# ---------------------------------------------------------------------------
# Главное приложение
# ---------------------------------------------------------------------------
class CatTrainingApp(MDApp):
    TABS = [
        ("today", "calendar-today", "Сегодня"),
        ("clicker", "gesture-tap", "Кликер"),
        ("program", "format-list-bulleted", "Программа"),
        ("rewards", "trophy", "Звания"),
        ("diag", "stethoscope", "Диагноз"),
        ("profile", "account-circle", "Профиль"),
    ]

    def build(self):
        self.title = "Cat Training Coach"
        self.theme_cls.theme_style = "Light"
        Window.clearcolor = (1.0, 0.97, 0.93, 1)
        # Чтобы клавиатура не закрывала поле ввода
        Window.softinput_mode = "below_target"

        # Хранилище в папке данных приложения
        store_path = os.path.join(self.user_data_dir, "cat_training_data.json")
        load_state(JsonStore(store_path))

        self.fact_active = False
        self.tab_buttons = {}

        root = FloatLayout()
        self.build_background(root)

        main = BoxLayout(orientation="vertical", size_hint=(1, 1))

        # Верхняя панель
        top_bar = MDBoxLayout(
            size_hint_y=None,
            height=dp(56),
            padding=(dp(8), dp(4)),
            md_bg_color=ACCENT,
        )
        self.top_label = Label(
            text="",
            font_size=sp(13),
            color=WHITE,
            bold=True,
            halign="center",
            valign="middle",
        )
        self.top_label.bind(size=lambda inst, s: setattr(inst, "text_size", s))
        top_bar.add_widget(self.top_label)
        main.add_widget(top_bar)

        # Экраны
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(TodayScreen(name="today"))
        self.sm.add_widget(ClickerScreen(name="clicker"))
        self.sm.add_widget(ProgramScreen(name="program"))
        self.sm.add_widget(DayDetailScreen(name="day_detail"))
        self.sm.add_widget(RewardsScreen(name="rewards"))
        self.sm.add_widget(DiagScreen(name="diag"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        main.add_widget(self.sm)

        # Нижняя панель: 6 равных вкладок
        bottom_bar = MDBoxLayout(size_hint_y=None, height=dp(62), md_bg_color=BAR_BG)
        for name, icon, title in self.TABS:
            button = TabButton(icon, title)
            button.bind(on_release=lambda inst, n=name: self.switch(n))
            self.tab_buttons[name] = button
            bottom_bar.add_widget(button)
        main.add_widget(bottom_bar)

        root.add_widget(main)

        self.update_top()
        self.switch("today")
        # Каждые 30 секунд показываем факт на 5 секунд
        Clock.schedule_interval(self.update_fact, 30)
        return root

    def build_background(self, root):
        """Фон: картинка cats_bg.png, размноженная сеткой 6x10."""
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cats_bg.png")
            if not os.path.exists(path):
                print("Файл фона не найден:", path)
                return
            grid = GridLayout(cols=6, rows=10, size_hint=(1, 1))
            for _ in range(60):
                grid.add_widget(Image(source=path, opacity=0.35, fit_mode="fill"))
            root.add_widget(grid)
        except Exception as exc:
            print("Не удалось загрузить фон:", exc)

    # ----- Навигация -----
    def switch(self, name):
        """Переключает экран и подсвечивает вкладку."""
        self.sm.current = name
        active = "program" if name == "day_detail" else name
        for tab_name, button in self.tab_buttons.items():
            button.set_active(tab_name == active)

    def open_day(self, day):
        """Открывает подробности дня."""
        screen = self.sm.get_screen("day_detail")
        screen.day = day
        self.switch("day_detail")

    # ----- Верхняя панель -----
    def update_top(self, *args):
        """Показывает: имя кота | баллы | звание | стрик."""
        if self.fact_active:
            return
        name = STATE["cat_name"].strip()
        if not name:
            name = "Настройте профиль кота"
        rank_name = get_rank(STATE["points"])[1]
        self.top_label.text = "%s | %d б. | %s | Стрик %d" % (
            name,
            STATE["points"],
            rank_name,
            STATE["streak"],
        )

    def update_fact(self, dt=None):
        """Подменяет статус случайным фактом на 5 секунд."""
        self.fact_active = True
        self.top_label.text = "Факт: " + random.choice(FACTS)
        Clock.unschedule(self.end_fact)
        Clock.schedule_once(self.end_fact, 5)

    def end_fact(self, dt=None):
        self.fact_active = False
        self.update_top()

    # ----- Действия -----
    def update_streak(self):
        """Обновляет стрик (дней подряд) при отметке сессии."""
        today = date.today()
        last = STATE["last_date"]
        if last == today.isoformat():
            return
        if last == (today - timedelta(days=1)).isoformat():
            STATE["streak"] += 1
        else:
            STATE["streak"] = 1
        STATE["last_date"] = today.isoformat()

    def toggle_session(self, day, index, value):
        """Отметка/снятие сессии: +5 / -5 баллов, бонус +10 за весь день."""
        key = str(day)
        info = get_day_info(day)
        sessions = STATE["sessions"].get(key)
        if not sessions or len(sessions) != info["sessions"]:
            sessions = [False] * info["sessions"]
        if sessions[index] == value:
            return
        sessions[index] = value
        STATE["sessions"][key] = sessions

        if value:
            STATE["points"] += 5
            self.update_streak()
            vibrate(30)
        else:
            STATE["points"] = max(0, STATE["points"] - 5)

        was_done = STATE["done"].get(key, False)
        all_done = all(sessions)
        if all_done and not was_done:
            STATE["points"] += 10
            STATE["done"][key] = True
        elif not all_done and was_done:
            STATE["points"] = max(0, STATE["points"] - 10)
            STATE["done"][key] = False

        save_state()
        self.update_top()
        today_screen = self.sm.get_screen("today")
        today_screen.update_status()

    def save_note(self, day, text):
        """Сохраняет заметку дня."""
        STATE["notes"][str(day)] = text
        save_state()
        vibrate(20)
        self.top_label.text = "Заметка сохранена"
        self.fact_active = True
        Clock.unschedule(self.end_fact)
        Clock.schedule_once(self.end_fact, 2)

    def save_profile(self, name):
        """Сохраняет имя кота."""
        STATE["cat_name"] = name.strip()
        save_state()
        self.update_top()
        self.sm.get_screen("profile").refresh()
        self.sm.get_screen("today").refresh()


if __name__ == "__main__":
    CatTrainingApp().run()
