import sys
import random
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget,
                             QTextEdit, QGraphicsDropShadowEffect, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QTextCursor

# --- СТИЛИ (QSS) ---
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
            "Формула E=mc^2 была предложена А. Эйнштейном.",
            "Email для связи: test-email@domain.com (круглосуточно)."
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


def generate_practice_text(lang, diff, is_timer):
    pool = VOCABULARY[lang][diff]
    if diff == "Лёгкий":
        count = 30 if is_timer else 15
    else:
        count = 15 if is_timer else 4
    return " ".join(random.choices(pool, k=count))


class ShadowFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "Card")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


# --- ЭКРАН ВЫБОРА ---
class SelectionScreen(QWidget):
    def __init__(self, parent, title, options, setting_key):
        super().__init__(parent)
        self.parent_app = parent
        self.key, self.val = setting_key, parent.settings[setting_key]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        top_bar = QHBoxLayout()
        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(lambda: self.parent_app.stack.setCurrentIndex(0))
        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 26px; font-weight: bold;")
        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(t_lbl)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch()
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container)
        self.card = ShadowFrame()
        card_lay = QVBoxLayout(self.card)
        self.btns = []
        for o in options:
            btn = QPushButton(o)
            btn.setProperty("class", "OptionButton")
            btn.setProperty("selected", str(o == self.val).lower())
            btn.clicked.connect(lambda ch, v=o: self.select(v))
            card_lay.addWidget(btn)
            self.btns.append(btn)
        c_lay.addWidget(self.card)
        save = QPushButton("Сохранить")
        save.setProperty("class", "PrimaryButton")
        save.clicked.connect(self.save_data)
        c_lay.addWidget(save)
        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def select(self, v):
        self.val = v
        for b in self.btns:
            b.setProperty("selected", str(b.text() == v).lower())
            b.style().unpolish(b)
            b.style().polish(b)

    def save_data(self):
        self.parent_app.settings[self.key] = self.val
        self.parent_app.menu_scr.refresh_ui()
        self.parent_app.stack.setCurrentIndex(0)


# --- ЭКРАН МЕНЮ ---
class MenuScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch()
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container)
        title = QLabel("Меню")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(title)
        c_lay.addSpacing(20)

        card = ShadowFrame()
        card_lay = QVBoxLayout(card)
        self.labels = {}
        for key, idx in [("Раскладка", 2), ("Режим", 3), ("Сложность", 4)]:
            btn = QPushButton()
            btn.setProperty("class", "MenuRow")
            btn.setFixedHeight(80)
            blay = QVBoxLayout(btn)
            t = QLabel(key)
            t.setStyleSheet("color: #64748b; font-size: 16px; background: transparent;")
            v = QLabel(parent.settings[key])
            v.setStyleSheet("font-weight: bold; font-size: 20px; background: transparent;")
            blay.addWidget(t)
            blay.addWidget(v)
            btn.clicked.connect(lambda ch, i=idx: self.parent_app.stack.setCurrentIndex(i))
            card_lay.addWidget(btn)
            self.labels[key] = v

        c_lay.addWidget(card)
        c_lay.addSpacing(25)
        start = QPushButton("Начать")
        start.setProperty("class", "PrimaryButton")
        start.clicked.connect(self.start_training)
        c_lay.addWidget(start)
        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def refresh_ui(self):
        for k, v in self.parent_app.settings.items():
            if k in self.labels: self.labels[k].setText(v)

    def start_training(self):
        self.parent_app.train_scr.init_game()
        self.parent_app.stack.setCurrentIndex(1)


# --- ЭКРАН ТРЕНИРОВКИ ---
class TrainingScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.last_len = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        top_bar = QHBoxLayout()
        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(self.go_back)
        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e293b;")
        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_timer)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        font_style = "font-family: 'Consolas', 'Courier New', monospace; font-size: 26px; padding: 16px;"

        self.ref_container = ShadowFrame()
        self.ref_lay = QVBoxLayout(self.ref_container)
        self.ref_lay.setContentsMargins(0, 0, 0, 0)
        self.ref = QTextEdit()
        self.ref.setReadOnly(True)
        self.ref.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.ref.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ref.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ref.setStyleSheet(font_style + " color: #94a3b8; background: transparent; border: none;")
        self.ref.setFixedHeight(90)
        self.ref_lay.addWidget(self.ref)
        layout.addWidget(self.ref_container)

        self.inp = QTextEdit()
        self.inp.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.inp.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.inp.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.inp.setStyleSheet(font_style + " border: 2px solid #3b82f6; border-radius: 12px; background: white;")
        self.inp.setFixedHeight(90)
        self.inp.textChanged.connect(self.on_change)

        self.inp.horizontalScrollBar().valueChanged.connect(self.ref.horizontalScrollBar().setValue)

        layout.addWidget(self.inp)
        layout.addSpacing(25)

        s_lay = QHBoxLayout()
        self.s_speed = self.stat_mini("Скорость", "0")
        self.s_acc = self.stat_mini("Точность", "100%")
        s_lay.addWidget(self.s_speed)
        s_lay.addWidget(self.s_acc)
        layout.addLayout(s_lay)
        layout.addStretch()

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
        f.val = lbl_v
        return f

    def init_game(self):
        s = self.parent_app.settings
        is_timer = s["Режим"] == "С таймером"
        self.target = generate_practice_text(s["Раскладка"], s["Сложность"], is_timer)

        self.errs, self.active, self.start_t = 0, False, None
        self.last_len = 0

        self.inp.clear()
        self.ref.clear()
        self.inp.setReadOnly(False)

        if is_timer:
            timer_mapping = {"Лёгкий": 15, "Средний": 30, "Сложный": 45}
            self.time_limit = timer_mapping[s["Сложность"]]
            m, sec = divmod(self.time_limit, 60)
            self.lbl_timer.setText(f"{m:02d}:{sec:02d}")
            self.lbl_timer.show()
        else:
            self.time_limit = 0
            self.lbl_timer.hide()

        self.on_change()

        self.s_speed.val.setText("0")
        self.s_acc.val.setText("100%")
        self.inp.setFocus()

    def go_back(self):
        self.timer.stop()
        self.parent_app.stack.setCurrentIndex(0)

    def on_change(self):
        t = self.inp.toPlainText()

        if '\n' in t:
            t = t.replace('\n', '')
            self.inp.setPlainText(t)
            cur = self.inp.textCursor()
            cur.movePosition(QTextCursor.MoveOperation.End)
            self.inp.setTextCursor(cur)
            return

        if not self.active and len(t) > 0:
            self.active = True
            self.start_t = time.time()
            self.timer.start(500)

        if len(t) > 0 and len(t) <= len(self.target) and len(t) > self.last_len:
            if t[-1] != self.target[len(t) - 1]:
                self.errs += 1

        self.last_len = len(t)

        if len(t) > 0:
            dynamic_acc = max(0, int(((len(t) - self.errs) / len(t)) * 100))
        else:
            dynamic_acc = 100
        self.s_acc.val.setText(f"{dynamic_acc}%")

        current_pos = len(t)

        # сколько символов показывать слева и справа
        left_chars = 25
        right_chars = 40

        start = max(0, current_pos - left_chars)
        end = min(len(self.target), current_pos + right_chars)

        visible_target = self.target[start:end]

        html_parts = []

        for local_i, char in enumerate(visible_target):
            i = start + local_i

            if char == " ":
                disp = "&nbsp;"
            elif char == "<":
                disp = "&lt;"
            elif char == ">":
                disp = "&gt;"
            else:
                disp = char

            if i < len(t):
                if t[i] == char:
                    html_parts.append(
                        f'<span style="color:#10b981;">{disp}</span>'
                    )
                else:
                    html_parts.append(
                        f'<span style="color:#ef4444; background:#fee2e2;">{disp}</span>'
                    )
            else:
                if i == len(t):
                    html_parts.append(
                        f'<span style="color:#ffffff; background:#3b82f6; '
                        f'border-radius:4px;">{disp}</span>'
                    )
                else:
                    html_parts.append(
                        f'<span style="color:#94a3b8;">{disp}</span>'
                    )

        self.ref.setHtml(
            f"""
            <div style="
                white-space: nowrap;
                font-family: Consolas, monospace;
                text-align: center;
            ">
                {''.join(html_parts)}
            </div>
            """
        )

        if len(t) >= len(self.target):
            self.finish_game()

    def tick(self):
        if not self.start_t: return
        elaps = time.time() - self.start_t
        if self.time_limit > 0:
            rem = max(0, int(self.time_limit - elaps))
            m, sec = divmod(rem, 60)
            self.lbl_timer.setText(f"{m:02d}:{sec:02d}")
            if rem <= 0: self.finish_game(); return
        cpm = int((len(self.inp.toPlainText()) / elaps) * 60) if elaps > 0 else 0
        self.s_speed.val.setText(str(cpm))

    def finish_game(self):
        self.timer.stop()
        self.active = False
        self.inp.setReadOnly(True)
        t = self.inp.toPlainText()
        elaps = max(1, time.time() - self.start_t)
        cpm = int((len(t) / elaps) * 60)
        acc = max(0, int(((len(t) - self.errs) / max(len(t), 1)) * 100))
        self.parent_app.stats_data = {"speed": cpm, "accuracy": acc, "errors": self.errs}
        self.parent_app.stats_scr.update_stats()
        self.parent_app.stack.setCurrentIndex(5)


# --- ЭКРАН СТАТИСТИКИ ---
class StatsScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        top_bar = QHBoxLayout()
        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.setProperty("class", "NavButton")
        back.clicked.connect(lambda: parent.stack.setCurrentIndex(0))
        close = QPushButton("×")
        close.setFixedSize(40, 40)
        close.setProperty("class", "CloseButton")
        close.clicked.connect(self.window().close)
        t_lbl = QLabel("Статистика")
        t_lbl.setStyleSheet("font-size: 28px; font-weight: bold;")
        top_bar.addWidget(back)
        top_bar.addStretch()
        top_bar.addWidget(t_lbl)
        top_bar.addStretch()
        top_bar.addWidget(close)
        layout.addLayout(top_bar)

        layout.addStretch()
        container = QWidget()
        container.setFixedWidth(460)
        c_lay = QVBoxLayout(container)
        self.card = ShadowFrame()
        card_lay = QVBoxLayout(self.card)
        self.row_speed = self.make_row("Скорость", "#3b82f6", "#EFF6FF")
        self.row_acc = self.make_row("Точность", "#10b981", "#ECFDF5")
        self.row_err = self.make_row("Ошибки", "#f97316", "#FFF7ED")
        card_lay.addWidget(self.row_speed)
        card_lay.addWidget(self.row_acc)
        card_lay.addWidget(self.row_err)
        c_lay.addWidget(self.card)
        c_lay.addSpacing(15)

        self.btn_restart = QPushButton("↻ Заново")
        self.btn_restart.setProperty("class", "PrimaryButton")
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
        l = QHBoxLayout(f)
        icon = QFrame()
        icon.setFixedSize(45, 45)
        icon.setStyleSheet(f"background-color: {color}; border-radius: 12px;")
        v_lay = QVBoxLayout()
        t = QLabel(title)
        t.setStyleSheet("color: #64748b; font-size: 15px; background: transparent;")
        v = QLabel("0")
        v.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; background: transparent;")
        v_lay.addWidget(t)
        v_lay.addWidget(v)
        l.addWidget(icon)
        l.addLayout(v_lay)
        l.addStretch()
        f.val_lbl = v
        return f

    def update_stats(self):
        s = self.parent_app.stats_data
        self.row_speed.val_lbl.setText(f"{s['speed']} зн/мин")
        self.row_acc.val_lbl.setText(f"{s['accuracy']}%")
        self.row_err.val_lbl.setText(str(s['errors']))


# --- ГЛАВНЫЙ КЛАСС ---
class TrainerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тренажер")
        self.resize(900, 780)
        self.setStyleSheet(STYLE_SHEET)
        self.settings = {"Раскладка": "Русская", "Режим": "С таймером", "Сложность": "Средний"}
        self.stats_data = {"speed": 0, "accuracy": 0, "errors": 0}
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_scr = MenuScreen(self)
        self.train_scr = TrainingScreen(self)
        self.sel_lang = SelectionScreen(self, "Раскладка", ["Русская", "Английская"], "Раскладка")
        self.sel_mode = SelectionScreen(self, "Режим", ["С таймером", "Без таймера"], "Режим")
        self.sel_diff = SelectionScreen(self, "Сложность", ["Лёгкий", "Средний", "Сложный"], "Сложность")
        self.stats_scr = StatsScreen(self)

        self.stack.addWidget(self.menu_scr)
        self.stack.addWidget(self.train_scr)
        self.stack.addWidget(self.sel_lang)
        self.stack.addWidget(self.sel_mode)
        self.stack.addWidget(self.sel_diff)
        self.stack.addWidget(self.stats_scr)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrainerApp()
    window.show()
    sys.exit(app.exec())