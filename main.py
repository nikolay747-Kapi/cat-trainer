# main.py — Cat Training Coach (KivyMD 1.2.0)
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.storage.jsonstore import JsonStore
from datetime import datetime, date
import random

DATA_FILE = "cat_training_data.json"
STORE = JsonStore(DATA_FILE)

TC = (0.88, 0.88, 0.88, 1)
AC = (0.80, 0.65, 0.97, 1)
CC = (0.10, 0.10, 0.15, 1)

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

CAT_FACTS = [
    "Мурлыканье кота - 25-150 Гц, заживляет кости.",
    "Кошки спят 12-16 часов в сутки.",
    "У кошки 32 мышцы в каждом ухе.",
    "Кошки не чувствуют сладкое.",
    "Нос кошки уникален, как отпечаток пальца.",
    "Кошки мяукают только для людей.",
    "Подушечки лап пахнут попкорном.",
    "Кошки видят в темноте в 6 раз лучше человека.",
]

CLICKER_INFO = (
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

DIAGNOSTICS_STOPS = [
    ("Кот уходит сам", "Больше не хочет участвовать"),
    ("Хвост дёргается резко", "Раздражение, стресс"),
    ("Уши прижаты", "Дискомфорт, страх"),
    ("Кот вылизывается", "Признак стресса"),
    ("Зрачки расширены", "Хочет избежать"),
    ("Мяуканье с низкими нотами", "Предупреждение"),
]

DIAGNOSTICS_REASONS = [
    ("Ты торопишься, кот не понял шаг", "Перескочил микрошаг", "Откатись назад"),
    ("Кот не голоден", "Сытый кот не работает", "Тренируйся до кормления"),
    ("Награда не ценная", "Обычный корм = ноль мотивации", "Особое лакомство"),
    ("Долгая сессия", "Теряют концентрацию", "Сессия 2-3 мин"),
    ("Кот не в настроении", "Кошки не работают по расписанию", "Лови момент"),
    ("Наказал за подход", "Зов = плохо", "Неприятное делай сам"),
]

DIAGNOSTICS_FIXES = {
    "Сидеть": ["Проверь мотивацию", "Веди медленнее", "Награждай за движение вниз"],
    "Дай лапу": ["Кулак с лакомством", "Нос игнор, лапа клик", "Не хватай лапу сам"],
    "Ко мне": ["Сократи дистанцию", "Клик за первый шаг", "Зов = праздник"],
    "Лежать": ["Начни с Сидеть", "Веди по полу медленно", "Награждай за локти"],
    "Зайка": ["Чуть выше головы", "Награждай за подъём", "Падает - ниже руку"],
    "Кувырок": ["Отработай Лежать", "Веди по дуге медленно", "Награждай за поворот"],
}

DIAGNOSTICS_PHILOSOPHY = [
    "Я не дрессирую кошек, я договариваюсь с ними — Ю. Куклачёв",
    "Кошку нельзя заставить. Только мотивировать.",
    "Кошка не обязана. Она делает, если видит выгоду.",
    "Не получается — проблема в методе.",
    "Наказание не работает. Только терпение.",
]


def load_state():
    if STORE.exists("state"):
        return STORE.get("state")
    return {
        "cat_name": "", "start_date": str(date.today()),
        "total_points": 0, "completed_days": [], "day_sessions": {},
        "day_notes": {}, "streak": 0, "last_session_date": None,
        "clicker_count": 0, "theme": "night",
    }

def save_state(state):
    STORE.put("state", **state)

def get_rank(points):
    rank = RANKS[0][1]
    for th, name, _ in RANKS:
        if points >= th:
            rank = name
    return rank

def get_program_day(state):
    try:
        start = datetime.strptime(state["start_date"], "%Y-%m-%d").date()
    except Exception:
        start = date.today()
    delta = (date.today() - start).days + 1
    return max(1, min(delta, len(PROGRAM)))

def get_day_info(num):
    for d in PROGRAM:
        if d["day"] == num:
            return d
    return PROGRAM[-1]


class TodayScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.scroll = MDScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(12),
                               spacing=dp(10), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.box.clear_widgets()
        s = self.app.state
        if not s["cat_name"]:
            self.box.add_widget(MDLabel(
                text="Настройте профиль кота на вкладке Профиль",
                halign="center", bold=True,
                theme_text_color="Custom", text_color=TC))
            return

        day_num = get_program_day(s)
        day = get_day_info(day_num)
        done = day_num in s["completed_days"]
        status = "ВЫПОЛНЕНО" if done else "НЕ ВЫПОЛНЕНО"

        self.box.add_widget(MDLabel(
            text=f"ДЕНЬ {day_num} / {len(PROGRAM)}",
            halign="center", bold=True,
            theme_text_color="Custom", text_color=AC))
        self.box.add_widget(MDLabel(
            text=f"{day['level']} | Неделя {day['week']} | {status}",
            halign="center", theme_text_color="Custom", text_color=TC))
        self.box.add_widget(MDLabel(
            text=day["title"], halign="center", bold=True,
            theme_text_color="Custom", text_color=TC))

        card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(6),
                      size_hint_y=None, radius=[dp(16)], elevation=2)
        card.bind(minimum_height=card.setter("height"))
        card.md_bg_color = CC

        card.add_widget(MDLabel(
            text=f"Цель: {day['goal']}",
            theme_text_color="Custom", text_color=TC))
        card.add_widget(MDLabel(
            text=f"Сессий: {day['sessions']} по {day['minutes']}",
            theme_text_color="Custom", text_color=TC))
        card.add_widget(MDLabel(
            text="ЧТО ДЕЛАТЬ:", bold=True,
            theme_text_color="Custom", text_color=AC))
        for i, step in enumerate(day["steps"], 1):
            card.add_widget(MDLabel(
                text=f"{i}. {step}", theme_text_color="Custom",
                text_color=TC))
        card.add_widget(MDLabel(
            text=f"Критерий: {day['success']}", bold=True,
            theme_text_color="Custom", text_color=(0.65, 0.89, 0.63, 1)))
        self.box.add_widget(card)

        self.box.add_widget(MDLabel(
            text="Отметь сессии:", bold=True,
            theme_text_color="Custom", text_color=AC))

        sessions_done = s["day_sessions"].get(str(day_num), [])
        for i in range(day["sessions"]):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                              height=dp(40), spacing=dp(8))
            cb = MDCheckbox(active=(i < len(sessions_done) and sessions_done[i]),
                            size_hint=(None, None), size=(dp(40), dp(40)))
            cb.bind(active=lambda inst, val, idx=i: self.app.toggle_session(idx, val))
            row.add_widget(cb)
            row.add_widget(MDLabel(
                text=f"Сессия {i+1}", valign="middle",
                theme_text_color="Custom", text_color=TC))
            self.box.add_widget(row)

        self.box.add_widget(MDLabel(
            text="Заметка:", bold=True,
            theme_text_color="Custom", text_color=AC))
        note = s["day_notes"].get(str(day_num), "")
        self.note_field = MDTextField(text=note, multiline=True,
                                      hint_text="Как прошло?")
        self.box.add_widget(self.note_field)

        btn = MDRaisedButton(text="Сохранить заметку", pos_hint={"center_x": 0.5})
        btn.bind(on_release=lambda x: self.app.save_note(self.note_field.text))
        self.box.add_widget(btn)


class ClickerScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        box.add_widget(MDLabel(
            text="КЛИКЕР", halign="center", bold=True,
            theme_text_color="Custom", text_color=AC,
            size_hint_y=None, height=dp(60)))

        self.btn = MDRaisedButton(
            text="КЛИК",
            size_hint=(None, None), size=(dp(220), dp(120)),
            pos_hint={"center_x": 0.5})
        self.btn.bind(on_release=self.do_click)
        box.add_widget(self.btn)

        self.counter = MDLabel(
            text="Всего кликов: 0", halign="center", bold=True,
            theme_text_color="Custom", text_color=AC,
            size_hint_y=None, height=dp(40))
        box.add_widget(self.counter)

        rst = MDRaisedButton(text="Сбросить", pos_hint={"center_x": 0.5})
        rst.bind(on_release=self.reset_counter)
        box.add_widget(rst)

        scroll = MDScrollView()
        info = MDLabel(
            text=CLICKER_INFO, size_hint_y=None,
            theme_text_color="Custom", text_color=TC)
        info.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        scroll.add_widget(info)
        box.add_widget(scroll)
        self.add_widget(box)

    def refresh(self):
        self.counter.text = f"Всего кликов: {self.app.state['clicker_count']}"

    def do_click(self, *args):
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            vibrator.vibrate(60)
        except Exception:
            pass
        self.app.state["clicker_count"] += 1
        save_state(self.app.state)
        self.refresh()

    def reset_counter(self, *args):
        self.app.state["clicker_count"] = 0
        save_state(self.app.state)
        self.refresh()


class ProgramScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.scroll = MDScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(12),
                               spacing=dp(4), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.box.clear_widgets()
        current = get_program_day(self.app.state)
        last_week = None

        for d in PROGRAM:
            if d["week"] != last_week:
                self.box.add_widget(MDLabel(
                    text=f"НЕДЕЛЯ {d['week']} - {d['level']}",
                    bold=True,
                    theme_text_color="Custom", text_color=AC,
                    size_hint_y=None, height=dp(32)))
                last_week = d["week"]

            done = d["day"] in self.app.state["completed_days"]
            mark = "[X]" if done else "[ ]"
            today_mark = " СЕГОДНЯ" if d["day"] == current else ""

            btn = MDRaisedButton(
                text=f"{mark} День {d['day']}: {d['title']}{today_mark}",
                size_hint_x=1, size_hint_y=None, height=dp(40))
            btn.bind(on_release=lambda x, day=d: self.app.open_day(day))
            self.box.add_widget(btn)


class DayDetailScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.scroll = MDScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(12),
                               spacing=dp(8), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def show(self, day):
        self.box.clear_widgets()
        back = MDRaisedButton(text="<- Назад")
        back.bind(on_release=lambda x: self.app.switch("program"))
        self.box.add_widget(back)

        self.box.add_widget(MDLabel(
            text=f"День {day['day']}: {day['title']}",
            halign="center", bold=True,
            theme_text_color="Custom", text_color=AC))
        self.box.add_widget(MDLabel(
            text=f"{day['level']} | Неделя {day['week']}",
            halign="center", theme_text_color="Custom", text_color=TC))

        card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(6),
                      size_hint_y=None, radius=[dp(16)], elevation=2)
        card.bind(minimum_height=card.setter("height"))
        card.md_bg_color = CC

        card.add_widget(MDLabel(
            text=f"Цель: {day['goal']}",
            theme_text_color="Custom", text_color=TC))
        card.add_widget(MDLabel(
            text=f"Сессий: {day['sessions']} по {day['minutes']}",
            theme_text_color="Custom", text_color=TC))
        card.add_widget(MDLabel(
            text="ЧТО ДЕЛАТЬ:", bold=True,
            theme_text_color="Custom", text_color=AC))
        for i, step in enumerate(day["steps"], 1):
            card.add_widget(MDLabel(
                text=f"{i}. {step}", theme_text_color="Custom",
                text_color=TC))
        card.add_widget(MDLabel(
            text=f"Критерий: {day['success']}", bold=True,
            theme_text_color="Custom", text_color=(0.65, 0.89, 0.63, 1)))
        self.box.add_widget(card)


class RewardsScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.scroll = MDScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(12),
                               spacing=dp(8), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.box.clear_widgets()
        points = self.app.state["total_points"]
        rank = get_rank(points)

        self.box.add_widget(MDLabel(
            text="ВИТРИНА ЗВАНИЙ", halign="center", bold=True,
            theme_text_color="Custom", text_color=AC))
        self.box.add_widget(MDLabel(
            text=f"{points} баллов\n{rank}", halign="center",
            theme_text_color="Custom", text_color=TC))

        current_idx = 0
        for i, (th, name, _) in enumerate(RANKS):
            if points >= th:
                current_idx = i

        for i, (th, name, desc) in enumerate(RANKS):
            card = MDCard(orientation="vertical", padding=dp(10),
                          size_hint_y=None, radius=[dp(12)], elevation=2)
            card.bind(minimum_height=card.setter("height"))
            card.md_bg_color = CC

            if points >= th:
                icon, color = "[+]", (0.65, 0.89, 0.63, 1)
                extra = f"Получено при {th} баллах"
            elif i == current_idx + 1:
                icon, color = "[>]", AC
                extra = f"Осталось {th - points}"
            else:
                icon, color = "[-]", (0.42, 0.44, 0.52, 1)
                extra = f"При {th} баллах"

            card.add_widget(MDLabel(
                text=f"{icon}  {name}", bold=True,
                theme_text_color="Custom", text_color=color))
            card.add_widget(MDLabel(
                text=desc,
                theme_text_color="Custom", text_color=TC))
            card.add_widget(MDLabel(
                text=extra,
                theme_text_color="Custom", text_color=color))
            self.box.add_widget(card)


class DiagScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        box = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        box.add_widget(MDLabel(
            text="ДИАГНОСТИКА", halign="center", bold=True,
            theme_text_color="Custom", text_color=AC,
            size_hint_y=None, height=dp(40)))

        row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(40), spacing=dp(4))
        for text, key in [("Стоп", "stops"), ("Причины", "reasons"),
                          ("Команды", "commands"), ("Мудрость", "phil")]:
            b = MDRaisedButton(text=text)
            b.bind(on_release=lambda x, k=key: self.show(k))
            row1.add_widget(b)
        box.add_widget(row1)

        self.scroll = MDScrollView()
        self.out = MDLabel(
            text="Выбери раздел сверху", size_hint_y=None,
            theme_text_color="Custom", text_color=TC)
        self.out.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        self.scroll.add_widget(self.out)
        box.add_widget(self.scroll)
        self.add_widget(box)

    def refresh(self):
        pass

    def show(self, key):
        if key == "stops":
            text = "СТОП-СИГНАЛЫ\n\n"
            for sign, meaning in DIAGNOSTICS_STOPS:
                text += f"! {sign}\n   -> {meaning}\n\n"
            text += "\nЗакончи сессию. Вернись позже."
        elif key == "reasons":
            text = "6 ПРИЧИН\n\n"
            for i, (name, why, fix) in enumerate(DIAGNOSTICS_REASONS, 1):
                text += f"{i}. {name}\n   {why}\n   + {fix}\n\n"
        elif key == "commands":
            text = "ИСПРАВЛЕНИЕ\n\n"
            for cmd, fixes in DIAGNOSTICS_FIXES.items():
                text += f"=== {cmd} ===\n"
                for f in fixes:
                    text += f"  - {f}\n"
                text += "\n"
        elif key == "phil":
            text = "ФИЛОСОФИЯ\n\n"
            for q in DIAGNOSTICS_PHILOSOPHY:
                text += f"- {q}\n\n"
        else:
            text = "-"
        self.out.text = text


class ProfileScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.scroll = MDScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(12),
                               spacing=dp(10), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        self.scroll.add_widget(self.box)
        self.add_widget(self.scroll)

    def refresh(self):
        self.box.clear_widgets()
        s = self.app.state

        self.box.add_widget(MDLabel(
            text="ПРОФИЛЬ", halign="center", bold=True,
            theme_text_color="Custom", text_color=AC))

        self.name_field = MDTextField(text=s["cat_name"], hint_text="Имя кота")
        self.box.add_widget(self.name_field)

        btn = MDRaisedButton(text="Сохранить", pos_hint={"center_x": 0.5})
        btn.bind(on_release=lambda x: self.app.save_profile(self.name_field.text))
        self.box.add_widget(btn)

        card = MDCard(orientation="vertical", padding=dp(12),
                      size_hint_y=None, radius=[dp(12)], elevation=2)
        card.bind(minimum_height=card.setter("height"))
        card.md_bg_color = CC
        card.add_widget(MDLabel(
            text="4 ПРАВИЛА", bold=True,
            theme_text_color="Custom", text_color=AC))
        for i, r in enumerate([
            "Награда в течение 1-2 секунд",
            "Сессия 2-5 минут, 2-3 раза в день",
            "Занятия до еды, а не после",
            "Никогда не наказывать",
        ], 1):
            card.add_widget(MDLabel(
                text=f"{i}. {r}",
                theme_text_color="Custom", text_color=TC))
        self.box.add_widget(card)


class CatTrainingApp(MDApp):
    tc = TC
    ac = AC
    cc = CC

    def build(self):
        self.title = "Cat Training Coach"
        self.theme_cls.theme_style = "Dark"
        self.state = load_state()

        root_layer = FloatLayout()

        self.bg_layer = FloatLayout()
        try:
            for i in range(6):
                for j in range(10):
                    cat = Image(
                        source="cats_bg.png",
                        size_hint=(None, None),
                        size=(dp(90), dp(90)),
                        pos=(i * dp(70) - dp(20), j * dp(90) - dp(20)),
                        opacity=0.35,
                    )
                    self.bg_layer.add_widget(cat)
            root_layer.add_widget(self.bg_layer)
        except Exception:
            pass

        self.top_label = MDLabel(
            text="", size_hint_y=None, height=dp(36),
            halign="center",
            theme_text_color="Custom", text_color=self.ac)
        
        self.bottom_nav = MDBottomNavigation()

        self.screens = {
            "today": TodayScreen(name="today"),
            "clicker": ClickerScreen(name="clicker"),
            "program": ProgramScreen(name="program"),
            "day_detail": DayDetailScreen(name="day_detail"),
            "rewards": RewardsScreen(name="rewards"),
            "diag": DiagScreen(name="diag"),
            "profile": ProfileScreen(name="profile"),
        }
        for scr in self.screens.values():
            scr.app = self
            item = MDBottomNavigationItem(name=scr.name, text=scr.name.capitalize())
            item.add_widget(scr)
            self.bottom_nav.add_widget(item)

        main_box = MDBoxLayout(orientation="vertical")
        main_box.add_widget(self.top_label)
        main_box.add_widget(self.bottom_nav)
        root_layer.add_widget(main_box)

        self.switch("today")
        Clock.schedule_interval(self.update_fact, 30)
        return root_layer

    def switch(self, name):
        self.bottom_nav.switch_tab(name)
        if name in self.screens:
            self.screens[name].refresh()
        self.update_top()

    def open_day(self, day):
        self.screens["day_detail"].show(day)
        self.bottom_nav.switch_tab("day_detail")

    def update_top(self):
        s = self.state
        if s["cat_name"]:
            rank = get_rank(s["total_points"])
            self.top_label.text = (
                f"{s['cat_name']} | {s['total_points']} б. | "
                f"{rank} | Стрик {s['streak']}")
        else:
            self.top_label.text = "Настройте профиль кота"

    def update_fact(self, dt):
        s = self.state
        if s["cat_name"]:
            fact = random.choice(CAT_FACTS)
            self.top_label.text = fact
            Clock.schedule_once(self.restore_top, 5)

    def restore_top(self, dt):
        self.update_top()

    def toggle_session(self, idx, value):
        s = self.state
        day_num = get_program_day(s)
        key = str(day_num)
        day = get_day_info(day_num)
        sessions = s["day_sessions"].get(key, [])
        while len(sessions) < day["sessions"]:
            sessions.append(False)
        if idx >= len(sessions) or sessions[idx] == value:
            return
        sessions[idx] = value
        s["day_sessions"][key] = sessions

        delta = 5 if value else -5
        s["total_points"] = max(0, s["total_points"] + delta)

        all_done = all(sessions[:day["sessions"]])
        was_done = day_num in s["completed_days"]
        if all_done and not was_done:
            s["completed_days"].append(day_num)
            s["total_points"] += 10
        elif not all_done and was_done:
            s["completed_days"].remove(day_num)

        today = str(date.today())
        if s["last_session_date"] != today:
            try:
                last = datetime.strptime(s["last_session_date"], "%Y-%m-%d").date()
                diff = (date.today() - last).days
                s["streak"] = s["streak"] + 1 if diff == 1 else 1
            except Exception:
                s["streak"] = 1
            s["last_session_date"] = today

        save_state(s)
        self.update_top()

    def save_note(self, text):
        s = self.state
        day_num = get_program_day(s)
        s["day_notes"][str(day_num)] = text.strip()
        save_state(s)
        self.top_label.text = "Заметка сохранена"
        Clock.schedule_once(self.restore_top, 3)

    def save_profile(self, name):
        name = name.strip()
        if not name:
            return
        s = self.state
        if not s["cat_name"]:
            s["start_date"] = str(date.today())
        s["cat_name"] = name
        save_state(s)
        self.update_top()
        self.top_label.text = f"Профиль {name} сохранён"
        Clock.schedule_once(self.restore_top, 3)


if __name__ == "__main__":
    CatTrainingApp().run()
