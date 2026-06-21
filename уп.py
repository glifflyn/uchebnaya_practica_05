# Для работы с системными функциями (аргументы командной строки, завершение)
import sys
# Для случайного выбора слов/предложений
import random
# Для измерения времени тренировки
import time

# Импорт всех необходимых виджетов и классов из PyQt6
from PyQt6.QtWidgets import (
    QApplication,  # Главный класс приложения
    QMainWindow,  # Главное окно
    QWidget,  # Базовый виджет
    QVBoxLayout,  # Вертикальное расположение
    QHBoxLayout,  # Горизонтальное расположение
    QLabel,  # Текстовая метка
    QPushButton,  # Кнопка
    QStackedWidget,  # Контейнер для переключения экранов
    QTextEdit,  # Многострочное текстовое поле
    QGraphicsDropShadowEffect,  # Эффект тени
    QFrame  # Базовый контейнер с рамкой
)
from PyQt6.QtCore import Qt, QTimer  # Константы Qt и таймер
from PyQt6.QtGui import QColor, QTextCursor, QTextFrameFormat, QPixmap  # Цвета, курсор, формат, картинки



# СТИЛИ (QSS)

# Стиль для всего приложения: светлый фон и шрифт Segoe UI
# QWidget - применяется ко всем виджетам, если не переопределено
# background-color: #F0F4F8 - светло-серый/голубоватый фон
# font-family: 'Segoe UI'
STYLE_SHEET = """
QWidget { background-color: #F0F4F8; font-family: 'Segoe UI'; }
.Card { background-color: white; border-radius: 20px; } 
.PrimaryButton {
    background-color: #3b82f6; color: white; border-radius: 14px;
    font-size: 18px; font-weight: bold; padding: 16px; border: none;
}
.PrimaryButton:hover { background-color: #2563eb; }
.MenuRow {
    background-color: #F8FAFC; border-radius: 16px;
    border: 2px solid #E2E8F0; text-align: left; padding: 15px 20px;
}
.OptionButton {
    background-color: #F8FAFC; border-radius: 14px; border: 2px solid transparent;
    padding: 16px; text-align: left; font-size: 18px;
}
.OptionButton[selected="true"] { background-color: #EFF6FF; border: 4px solid #3b82f6; color: #1d4ed8; }
.NavButton { background-color: white; border-radius: 20px; border: 2px solid #E2E8F0; font-weight: bold; font-size: 20px; }
.CloseButton {
    background-color: white; border-radius: 20px; border: 2px solid #E2E8F0; 
    font-weight: bold; font-size: 20px; color: #64748b;
}
.CloseButton:hover { background-color: #fee2e2; color: #ef4444; border: 2px solid #f87171; }
"""



# СЛОВАРЬ С ТЕКСТАМИ ДЛЯ ТРЕНИРОВОК
VOCABULARY = {
    "Русская": {
        "Лёгкий": ["кот", "дом", "лес", "шар", "сон", "мир", "сок", "час", "друг", "мост", "лето", "зима", "вода",
                   "небо"],
        "Средний": [
            "Быстрая лиса прыгает через ленивую собаку.",
            "Регулярная практика делает из новичка мастера.",
            "Каждый новый день приносит нам новые возможности.",
            "Чтение хороших книг сильно расширяет кругозор."
        ],
        "Сложный": [
            "В 2024 году вышло глобальное обновление версии 2.0!",
            "Синхрофазотрон: работает ли он на 100% мощности?",
            "Совещание начинается ровно в 09:00 утра.",
            "Режим работы: пн-сб (круглосуточно)."
        ]
    },
    "Английская": {
        "Лёгкий": ["cat", "dog", "sun", "fun", "car", "sky", "red", "big", "tree", "bird", "blue", "wind", "star"],
        "Средний": [
            "The quick brown fox jumps over the lazy dog.",
            "Practice makes perfect in typing skills.",
            "Every journey begins with a single step.",
            "Reading books improves your vocabulary."
        ],
        "Сложный": [
            "In 2026, the version 3.0 update was released!",
            "Is the remote server running at 100% capacity?",
            "The formula E=mc^2 is quite famous (Einstein).",
            "Contact us at: support@domain.com (24/7)."
        ]
    }
}



# ФУНКЦИЯ ГЕНЕРАЦИИ ТЕКСТА
def generate_practice_text(lang, diff, is_timer):
    pool = VOCABULARY[lang][diff]  # Берем список слов/предложений для выбранных параметров
    if diff == "Лёгкий":
        count = 30 if is_timer else 15  # Для лёгкого уровня и таймера нужно больше слов
    else:
        count = 15 if is_timer else 4  # Для среднего/сложного и без таймера меньше предложений
    # Случайно выбираем элементы из списка и объединяем их в строку через пробел
    return " ".join(random.choices(pool, k=count))



# КЛАСС SHADOWFRAME (КАРТОЧКА С ТЕНЬЮ)
class ShadowFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "Card")  # Применяем стиль .Card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)  # Радиус размытия
        shadow.setColor(QColor(0, 0, 0, 15))  # Цвет тени (почти прозрачный)
        shadow.setOffset(0, 4)  # Смещение тени (вниз на 4 пикселя)
        self.setGraphicsEffect(shadow)  # Применяем эффект



# КЛАСС SELECTIONSCREEN (ЭКРАН ВЫБОРА НАСТРОЕК)
class SelectionScreen(QWidget):
    def __init__(self, parent, title, options, setting_key):
        super().__init__(parent)
        self.parent_app = parent
        # self.key - ключ настройки (например, "Раскладка")
        # self.val - текущее значение настройки (берём из parent.settings)
        self.key, self.val = setting_key, parent.settings[setting_key]

        # Основной макет
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30) # Отступы от краев со всех сторон по 30

        top_bar = QHBoxLayout()

        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(lambda: self.parent_app.stack.setCurrentIndex(0))  # В меню

        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)  # Закрыть приложение

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 26px; font-weight: bold;")

        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(t_lbl)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch()  # Промежуток

        # Центральный контейнер
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container)

        self.card = ShadowFrame()
        card_lay = QVBoxLayout(self.card)

        self.btns = []  # Список для хранения кнопок опций

        for o in options:
            btn = QPushButton(o)
            btn.setProperty("class", "OptionButton")
            btn.setProperty("selected", str(o == self.val).lower())  # Выбрана ли опция
            btn.clicked.connect(lambda ch, v=o: self.select(v))  # lambda с замыканием v=o фиксирует значение o
            card_lay.addWidget(btn)
            self.btns.append(btn)  # Сохраняем в список

        c_lay.addWidget(self.card)

        save = QPushButton("Сохранить")
        save.setProperty("class", "PrimaryButton")
        save.clicked.connect(self.save_data)
        c_lay.addWidget(save)

        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()  # Промежуток внизу

    def select(self, v):
        self.val = v # Запоминает что нажал пользователь
        for b in self.btns:
            # Устанавливаем свойство selected для каждой кнопки
            b.setProperty("selected", str(b.text() == v).lower())
            b.style().unpolish(b)  # Убираем стиль
            b.style().polish(b)    # Применяем новый стиль

    def save_data(self):
        self.parent_app.settings[self.key] = self.val # Сохраняем выбранное значение в словарь настроек родительского приложения
        self.parent_app.menu_scr.refresh_ui()  # Обновляем меню
        self.parent_app.stack.setCurrentIndex(0)  # Переключаемся на меню



# КЛАСС MENUSCREEN (ГЛАВНОЕ МЕНЮ)
class MenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Верхняя панель
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)

        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch()

        # Центральный контейнер
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container)

        title = QLabel("Меню")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(title)
        c_lay.addSpacing(20)

        # Карточка с параметрами
        card = ShadowFrame()
        card_lay = QVBoxLayout(card)

        self.labels = {}  # Словарь для хранения меток значений

        # Создаём три кнопки-строки для параметров
        for key, idx in [("Раскладка", 2), ("Режим", 3), ("Сложность", 4)]:
            btn = QPushButton()
            btn.setProperty("class", "MenuRow")
            btn.setFixedHeight(80)

            blay = QVBoxLayout(btn)
            # Метка с названием параметра
            t = QLabel(key)
            t.setStyleSheet("color: #64748b; font-size: 16px; background: transparent;")
            # Метка со значением параметра
            v = QLabel(parent.settings[key])
            v.setStyleSheet("font-weight: bold; font-size: 20px; background: transparent;")

            blay.addWidget(t)
            blay.addWidget(v)

            # При нажатии переключаемся на соответствующий экран выбора
            btn.clicked.connect(lambda ch, i=idx: self.parent_app.stack.setCurrentIndex(i))

            card_lay.addWidget(btn)
            self.labels[key] = v  # Сохраняем ссылку на метку значения

        c_lay.addWidget(card)
        c_lay.addSpacing(25)

        # Кнопка "Начать"
        start = QPushButton("Начать")
        start.setProperty("class", "PrimaryButton")
        start.clicked.connect(self.start_training)
        c_lay.addWidget(start)

        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def refresh_ui(self):
        for k, v in self.parent_app.settings.items():
            if k in self.labels: # Если для этого ключа есть метка в self.labels
                self.labels[k].setText(v) # Обновляем текст метки новым значением

    def start_training(self):
        self.parent_app.train_scr.init_game()  # Инициализируем тренировку
        self.parent_app.stack.setCurrentIndex(1)  # Переключаемся на экран тренировки



# КЛАСС TRAININGSCREEN (ЭКРАН ТРЕНИРОВКИ)
class TrainingScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent

        # Таймер для обновления времени и скорости
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)  # При срабатывании вызываем функцию tick

        self.last_len = 0  # Предыдущая длина введённого текста

        # Основной макет
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        # Верхняя панель
        top_bar = QHBoxLayout()

        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(self.go_back)  # В меню

        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)

        # Таймер (изначально скрыт или показывает 00:00)
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")

        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_timer)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        # Стиль для текста
        font_style = "font-family: 'Consolas', 'Courier New', monospace; font-size: 26px; padding: 12px;"

        # Эталонный текст (карточка с тенью)
        self.ref_container = ShadowFrame()
        self.ref_lay = QVBoxLayout(self.ref_container)
        self.ref_lay.setContentsMargins(0, 0, 0, 0)

        self.ref = QTextEdit()
        self.ref.setReadOnly(True)
        self.ref.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.ref.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Без вертикальной прокрутки
        self.ref.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # И горизонтальной тоже
        self.ref.setStyleSheet(font_style + " color: #94a3b8; background: transparent; border: none;")
        self.ref.setFixedHeight(70)

        self.ref_lay.addWidget(self.ref) # Поле в карточку
        layout.addWidget(self.ref_container) # Карточку в макет

        # Поле ввода
        self.inp = QTextEdit()
        self.inp.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.inp.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.inp.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.inp.setStyleSheet(font_style + " border: 2px solid #3b82f6; border-radius: 12px; background: white;")
        self.inp.setFixedHeight(70)
        self.inp.textChanged.connect(self.on_change)  # При изменении текста вызываем on_change

        # Синхронизируем горизонтальную прокрутку ввода и этал текста
        self.inp.horizontalScrollBar().valueChanged.connect(self.ref.horizontalScrollBar().setValue)

        layout.addWidget(self.inp)
        layout.addSpacing(15)

        # Картинка с клавиатурой
        self.img_lbl = QLabel()
        pix = QPixmap("fingers.png")  # Загружаем изображение из файла
        # Установка размеров, при жтом сохранение пропорций
        pix = pix.scaled(1400, 700, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img_lbl.setPixmap(pix)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.img_lbl, stretch=1)  # Растягиваем на всё свободное место

        layout.addSpacing(15)

        # Блок статистики (скорость и точность)
        s_lay = QHBoxLayout()
        self.s_speed = self.stat_mini("Скорость (зн/мин)", "0")
        self.s_acc = self.stat_mini("Точность", "100%")
        s_lay.addWidget(self.s_speed)
        s_lay.addWidget(self.s_acc)
        layout.addLayout(s_lay)

    def stat_mini(self, t, v):
        f = ShadowFrame()
        f.setFixedSize(210, 90)

        l = QVBoxLayout(f)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_t = QLabel(t)
        lbl_t.setStyleSheet("color: #64748b; font-size: 15px;")

        lbl_v = QLabel(v)
        lbl_v.setStyleSheet("font-size: 26px; font-weight: bold; color: #3b82f6;")

        l.addWidget(lbl_t)
        l.addWidget(lbl_v)

        f.val = lbl_v  # Сохраняем ссылку на метку значения
        return f

    def init_game(self):
        s = self.parent_app.settings
        is_timer = s["Режим"] == "С таймером"

        # Генерируем текст
        self.target = generate_practice_text(s["Раскладка"], s["Сложность"], is_timer)

        # Сбрасываем переменные
        self.errs = 0  # Ошибки
        self.active = False  # Активна ли тренировка
        self.start_t = None  # Время старта
        self.last_len = 0

        # Очищаем поля
        self.inp.clear()
        self.ref.clear()
        self.inp.setReadOnly(False)  # Разрешаем ввод

        # Настраиваем таймер
        if is_timer:
            timer_mapping = {"Лёгкий": 15, "Средний": 30, "Сложный": 45}
            self.time_limit = timer_mapping[s["Сложность"]]
            m, sec = divmod(self.time_limit, 60)
            self.lbl_timer.setText(f"{m:02d}:{sec:02d}")
            self.lbl_timer.show()
        else:
            self.time_limit = 0
            self.lbl_timer.hide()

        self.on_change()  # Обновляем отображение эталонного текста

        # Сбрасываем статистику
        self.s_speed.val.setText("0")
        self.s_acc.val.setText("100%")

        # Устанавливаем фокус на поле ввода
        self.inp.setFocus()

    def go_back(self):
        self.timer.stop()  # Останавливаем таймер
        self.parent_app.stack.setCurrentIndex(0)

    def on_change(self):
        t = self.inp.toPlainText()  # Текущий введённый текст просто в виде строки

        # Если пользователь нажал Enter
        if '\n' in t:
            t = t.replace('\n', '')
            self.inp.setPlainText(t)
            cur = self.inp.textCursor()
            cur.movePosition(QTextCursor.MoveOperation.End)
            self.inp.setTextCursor(cur)
            return

        # Если тренировка не активна, но пользователь начал печатать
        if not self.active and len(t) > 0:
            self.active = True
            self.start_t = time.time() # Заопимнаем время старта
            self.timer.start(500)  # Запускаем таймер (каждые 500 мс)

        # Проверяем новый символ на ошибку
        if len(t) > 0 and len(t) <= len(self.target) and len(t) > self.last_len:
            if t[-1] != self.target[len(t) - 1]:
                self.errs += 1

        self.last_len = len(t)

        # Вычисляем динамическую точность
        if len(t) > 0:
            dynamic_acc = max(0, int(((len(t) - self.errs) / len(t)) * 100))
        else:
            dynamic_acc = 100
        self.s_acc.val.setText(f"{dynamic_acc}%")

        # Подсветка эталонного текста
        current_pos = len(t)
        left_chars = 30
        right_chars = 35
        # Вычисляем начальный и конечный индексы видимой части текста
        start = max(0, current_pos - left_chars)
        end = min(len(self.target), current_pos + right_chars)
        visible_target = self.target[start:end]

        html_parts = []

        for local_i, char in enumerate(visible_target):
            i = start + local_i # Индекс символа в ПОЛНОМ тексте

            # Экранируем специальные символы для HTML
            if char == " ":
                disp = "&nbsp;"
            elif char == "<":
                disp = "&lt;"
            elif char == ">":
                disp = "&gt;"
            else:
                disp = char

            # Определяем цвет подсветки
            if i < len(t):
                if t[i] == char:
                    html_parts.append(f'<span style="color:#10b981;">{disp}</span>')  # Зелёный
                else:
                    html_parts.append(f'<span style="color:#ef4444; background:#fee2e2;">{disp}</span>')  # Красный
            else:
                if i == len(t):
                    html_parts.append(
                        f'<span style="color:#ffffff; background:#3b82f6; border-radius:4px;">{disp}</span>')  # Текущая позиция
                else:
                    html_parts.append(f'<span style="color:#94a3b8;">{disp}</span>')  # Будущие символы

        # Устанавливаем HTML в поле эталонного текста
        self.ref.setHtml(
            f"""
            <div style="white-space: nowrap; font-family: Consolas, monospace; text-align: center;">
                {''.join(html_parts)}
            </div>
            """
        )

        # Если текст полностью введён - завершаем
        if len(t) >= len(self.target):
            self.finish_game()

    def tick(self):
        if not self.start_t: # Если тренировка не начата, выходим
            return

        elaps = time.time() - self.start_t  # Прошедшее время

        # Обновляем таймер, если он активен
        if self.time_limit > 0:
            rem = max(0, int(self.time_limit - elaps))
            m, sec = divmod(rem, 60)
            self.lbl_timer.setText(f"{m:02d}:{sec:02d}")
            if rem <= 0:
                self.finish_game()
                return

        # Вычисляем скорость (символов в минуту)
        cpm = int((len(self.inp.toPlainText()) / elaps) * 60) if elaps > 0 else 0
        self.s_speed.val.setText(str(cpm))

    def finish_game(self):
        self.timer.stop()
        self.active = False
        self.inp.setReadOnly(True)  # Блокируем ввод

        t = self.inp.toPlainText()
        elaps = max(1, time.time() - self.start_t)  # Минимум 1 секунда

        # Вычисляем итоговую статистику
        cpm = int((len(t) / elaps) * 60)
        acc = max(0, int(((len(t) - self.errs) / max(len(t), 1)) * 100))

        # Сохраняем данные и переключаемся на экран статистики
        self.parent_app.stats_data = {"speed": cpm, "accuracy": acc, "errors": self.errs}
        self.parent_app.stats_scr.update_stats()
        self.parent_app.stack.setCurrentIndex(5)



# КЛАСС STATSSCREEN (ЭКРАН СТАТИСТИКИ)
class StatsScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent  # Сохраняем ссылку на родительское приложение

        layout = QVBoxLayout(self) # Создаём основной вертикальный макет
        layout.setContentsMargins(30, 30, 30, 30) # Устанавливаем отступы

        # Верхняя панель
        top_bar = QHBoxLayout()

        back = QPushButton("←") # Кнопка возврата
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(lambda: parent.stack.setCurrentIndex(0))  # В меню по индексу

        close = QPushButton("×") # Кнопка закрытия
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)

        t_lbl = QLabel("Статистика")
        t_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")

        # Сборка этой верхней панели
        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(t_lbl)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch() # Промежуток

        # Центральный контейнер
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container) # Применяется не к всему экрану а только к виджету контейнера

        self.card = ShadowFrame() # Создание самой карточки для вывода
        card_lay = QVBoxLayout(self.card)

        self.row_speed = self.make_row("Скорость", "#3b82f6", "#EFF6FF")
        self.row_acc = self.make_row("Точность", "#10b981", "#ECFDF5")
        self.row_err = self.make_row("Ошибки", "#f97316", "#FFF7ED")

        card_lay.addWidget(self.row_speed)
        card_lay.addWidget(self.row_acc)
        card_lay.addWidget(self.row_err)

        c_lay.addWidget(self.card)
        c_lay.addSpacing(15)

        # Кнопка "Заново"
        self.btn_restart = QPushButton("↻ Заново")
        self.btn_restart.setProperty("class", "PrimaryButton") # Применяем праймарибтн к кнопке
        self.btn_restart.clicked.connect(self.restart_game)
        c_lay.addWidget(self.btn_restart)

        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def restart_game(self):
        self.parent_app.train_scr.init_game()
        self.parent_app.stack.setCurrentIndex(1)

    def make_row(self, title, color, bg):
        f = QFrame()
        f.setStyleSheet(f"background-color: {bg}; border-radius: 16px;")
        f.setFixedHeight(85)
        l = QHBoxLayout(f) # Горизонтальный макет внутри рамки

        # Цветной квадратик-иконка
        icon = QFrame()
        icon.setFixedSize(45, 45)
        icon.setStyleSheet(f"background-color: {color}; border-radius: 12px;")

        v_lay = QVBoxLayout() # Блок с названием и значением

        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-size: 15px; background: transparent;")
        v = QLabel("0")
        v.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; background: transparent;")

        v_lay.addWidget(t)
        v_lay.addWidget(v)

        l.addWidget(icon) # Собираем стркоу из элементов
        l.addLayout(v_lay)
        l.addStretch()

        f.val_lbl = v  # Сохраняем указатель на метку значения для последующего легкого обновлаения
        return f # Возвращаем рамку

    def update_stats(self):
        s = self.parent_app.stats_data # Получаем данные из родительского приложения
        self.row_speed.val_lbl.setText(f"{s['speed']} зн/мин") # И все строки статистики
        self.row_acc.val_lbl.setText(f"{s['accuracy']}%")
        self.row_err.val_lbl.setText(str(s['errors']))



# ГЛАВНЫЙ КЛАСС TRAINERAPP
class TrainerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.setWindowTitle("Тренажер")
        self.resize(900, 780)
        self.setStyleSheet(STYLE_SHEET)

        # Начальные настройки
        self.settings = {"Раскладка": "Русская", "Режим": "С таймером", "Сложность": "Средний"}
        self.stats_data = {"speed": 0, "accuracy": 0, "errors": 0}

        # Создание контейнера для переключения экранов
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack) # Устанавливаем его как центральный виджет окна

        # Создаём все экраны
        self.menu_scr = MenuScreen(self)  # индекс 0
        self.train_scr = TrainingScreen(self)
        self.sel_lang = SelectionScreen(self, "Раскладка", ["Русская", "Английская"], "Раскладка")
        self.sel_mode = SelectionScreen(self, "Режим", ["С таймером", "Без таймера"], "Режим")
        self.sel_diff = SelectionScreen(self, "Сложность", ["Лёгкий", "Средний", "Сложный"], "Сложность")
        self.stats_scr = StatsScreen(self)  # индекс 5

        # Добавляем экраны в стек
        self.stack.addWidget(self.menu_scr)
        self.stack.addWidget(self.train_scr)
        self.stack.addWidget(self.sel_lang)
        self.stack.addWidget(self.sel_mode)
        self.stack.addWidget(self.sel_diff)
        self.stack.addWidget(self.stats_scr)



# ТОЧКА ВХОДА В ПРОГРАММУ
if __name__ == '__main__':
    app = QApplication(sys.argv) # sys.argv - аргументы командной строки (нужны для Qt)
    window = TrainerApp()
    window.show()
    # Запускаем главный цикл событий
    sys.exit(app.exec())