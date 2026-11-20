"""ESON CALCULATOR 🇿🇲 — offline, touch-friendly Kivy calculator."""
from __future__ import annotations

import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.metrics import dp, sp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform

from calculator import CalculationError, evaluate, format_result


BLUE = (0.12, 0.48, 1, 1)


class CalcButton(Button):
    """Button with consistent rounded, touch-friendly styling."""
    def __init__(self, app, text, role="number", **kwargs):
        self.calc_app = app
        self.role = role
        super().__init__(text=text, **kwargs)
        self.font_size = sp(23)
        self.bold = role in ("operator", "action", "equals")
        self.background_normal = ""
        self.background_down = ""
        self.bind(on_press=self._pressed)
        self.bind(on_release=self._released)

    def _color(self, down=False):
        dark = self.calc_app.dark_theme
        if self.role == "equals": return (0.08, 0.38, 0.88, 1) if not down else (0.04, 0.28, 0.68, 1)
        if self.role == "action": return ((0.12, 0.19, 0.30, 1) if dark else (0.82, 0.87, 0.94, 1)) if not down else (0.20, 0.35, 0.55, 1)
        if self.role == "operator": return ((0.09, 0.16, 0.27, 1) if dark else (0.87, 0.91, 0.97, 1)) if not down else (0.12, 0.30, 0.54, 1)
        return ((0.055, 0.075, 0.12, 1) if dark else (0.95, 0.96, 0.98, 1)) if not down else (0.12, 0.28, 0.47, 1)

    def _pressed(self, *_):
        self.background_color = self._color(True)
        self.calc_app.haptic()

    def _released(self, *_):
        self.background_color = self._color(False)
        self.calc_app.animate_press(self)

    def refresh_color(self):
        self.background_color = self._color(False)


class CalculatorUI(BoxLayout):
    expression_text = StringProperty("0")
    result_text = StringProperty("")

    def __init__(self, app, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(10), **kwargs)
        self.calc_app = app
        self.buttons = []
        self._build()
        self.refresh_theme()

    def _build(self):
        header = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        brand = Label(text="ESON CALCULATOR 🇿🇲", font_size=sp(17), bold=True, halign="left", valign="middle")
        brand.bind(size=lambda obj, size: setattr(obj, "text_size", size))
        header.add_widget(brand)
        for title, action in (("◷", self.calc_app.show_history), ("☼", self.calc_app.toggle_theme), ("▣", self.calc_app.copy_result)):
            button = Button(text=title, size_hint_x=None, width=dp(46), font_size=sp(21), background_normal="", background_color=(0, 0, 0, 0))
            button.bind(on_release=lambda _b, fn=action: fn())
            header.add_widget(button)
        self.header = header
        self.brand = brand
        self.add_widget(header)

        display = BoxLayout(orientation="vertical", padding=[dp(8), dp(12)], spacing=dp(6))
        self.expression_label = Label(text="0", font_size=sp(43), halign="right", valign="bottom", shorten=True, shorten_from="left", text_size=(0, None), size_hint_y=0.62)
        self.expression_label.bind(size=lambda obj, size: setattr(obj, "text_size", (size[0], None)))
        self.result_label = Label(text="", font_size=sp(23), halign="right", valign="top", size_hint_y=0.38)
        self.result_label.bind(size=lambda obj, size: setattr(obj, "text_size", size))
        display.add_widget(self.expression_label)
        display.add_widget(self.result_label)
        self.display = display
        self.add_widget(display)

        rows = [
            [("AC", "action"), ("( )", "action"), ("%", "action"), ("÷", "operator")],
            [("7", "number"), ("8", "number"), ("9", "number"), ("×", "operator")],
            [("4", "number"), ("5", "number"), ("6", "number"), ("−", "operator")],
            [("1", "number"), ("2", "number"), ("3", "number"), ("+", "operator")],
            [("+/−", "action"), ("0", "number"), (".", "number"), ("=", "equals")],
            [("DEL", "action"), ("x²", "operator"), ("√", "operator"), ("^", "operator")],
        ]
        self.keypad = GridLayout(cols=4, spacing=dp(9), size_hint_y=1)
        for row in rows:
            for title, role in row:
                button = CalcButton(self.calc_app, title, role)
                button.bind(on_release=lambda b, value=title: self.calc_app.press(value))
                self.buttons.append(button)
                self.keypad.add_widget(button)
        self.add_widget(self.keypad)

    def refresh_theme(self):
        dark = self.calc_app.dark_theme
        self.background_color = (0.018, 0.027, 0.05, 1) if dark else (0.91, 0.94, 0.98, 1)
        self.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(*self.background_color)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *_: setattr(self._bg, "pos", self.pos), size=lambda *_: setattr(self._bg, "size", self.size))
        self.brand.color = (0.91, 0.95, 1, 1) if dark else (0.05, 0.09, 0.16, 1)
        self.display.canvas.before.clear()
        with self.display.canvas.before:
            Color(*( (0.035, 0.052, 0.085, 1) if dark else (1, 1, 1, 1) ))
            self._display_bg = Rectangle(pos=self.display.pos, size=self.display.size)
        self.display.bind(pos=lambda *_: setattr(self._display_bg, "pos", self.display.pos), size=lambda *_: setattr(self._display_bg, "size", self.display.size))
        self.expression_label.color = (0.96, 0.98, 1, 1) if dark else (0.04, 0.07, 0.12, 1)
        self.result_label.color = BLUE
        for button in self.buttons: button.refresh_color()

    def update_display(self, expression, result=""):
        self.expression_label.text = expression or "0"
        self.result_label.text = result


class EsonCalculator(App):
    title = "ESON CALCULATOR 🇿🇲"

    def build(self):
        self.dark_theme = True
        self.expression = ""
        self.just_calculated = False
        self.history = []
        self._load_history()
        self.ui = CalculatorUI(self)
        return self.ui

    @property
    def history_path(self):
        return os.path.join(self.user_data_dir, "history.json")

    def _load_history(self):
        try:
            with open(self.history_path, encoding="utf-8") as file:
                data = json.load(file)
            self.history = data if isinstance(data, list) else []
        except (OSError, ValueError, TypeError):
            self.history = []

    def _save_history(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as file:
                json.dump(self.history[:100], file, ensure_ascii=False)
        except OSError:
            pass

    def haptic(self):
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                activity.runOnUiThread(lambda: activity.getSystemService("vibrator").vibrate(18))
            except Exception:
                try:
                    from plyer import vibrator
                    vibrator.vibrate(0.018)
                except Exception:
                    pass

    def animate_press(self, button):
        from kivy.animation import Animation
        original = button.opacity
        button.opacity = 0.78
        Animation(opacity=original, duration=0.12, t="out_quad").start(button)

    def _show(self, expression=None, result=""):
        self.ui.update_display(self.expression if expression is None else expression, result)

    def press(self, key):
        if key == "AC":
            self.expression = ""
            self.just_calculated = False
            self._show()
            return
        if key == "DEL":
            if self.just_calculated: self.just_calculated = False
            self.expression = self.expression[:-1]
            self._show()
            return
        if key == "=":
            self.calculate()
            return
        if key == "+/−":
            self.toggle_sign()
            return
        if key == "( )":
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] == ")"):
                self.expression += "×("
            else:
                self.expression += "("
            self.just_calculated = False
            self._show()
            return
        if key == "x²": key = "^2"
        if self.just_calculated:
            if key in ("+", "−", "×", "÷", "%", "^", "^2"):
                self.just_calculated = False
            else:
                self.expression = ""
                self.just_calculated = False
        if key in ("+", "−", "×", "÷", "^"):
            op = {"+": "+", "−": "−", "×": "×", "÷": "÷", "^": "^"}[key]
            if self.expression and self.expression[-1] in "+−×÷^":
                self.expression = self.expression[:-1] + op
            elif not self.expression and key == "−":
                self.expression = "−"
            elif self.expression:
                self.expression += op
        elif key == "√":
            self.expression += "√"
        elif key == "%":
            if self.expression and (self.expression[-1].isdigit() or self.expression[-1] == ")"):
                self.expression += "%"
        elif key == ".":
            # Permit only one decimal point in the current numeric literal.
            segment = re_last_number(self.expression)
            if "." not in segment:
                self.expression += "."
        else:
            if self.expression.endswith(")") or self.expression.endswith("%"):
                self.expression += "×"
            self.expression += key
        self._show()
        self._preview()

    def _preview(self):
        try:
            result = format_result(evaluate(self.expression))
            self.ui.result_label.text = "= " + result
        except CalculationError:
            self.ui.result_label.text = ""

    def toggle_sign(self):
        text = self.expression
        if not text:
            self.expression = "−"
        else:
            end = len(text)
            start = end
            while start > 0 and (text[start - 1].isdigit() or text[start - 1] == "."):
                start -= 1
            if start == end and text[-1] == ")":
                self.expression = "−(" + text + ")"
            elif start < end:
                if start > 0 and text[start - 1] == "−" and (start == 1 or text[start - 2] in "+−×÷^(" or text[start - 2] == "√"):
                    self.expression = text[:start - 1] + text[start:]
                else:
                    self.expression = text[:start] + "−" + text[start:]
            else:
                self.expression = "−" + text
        self.just_calculated = False
        self._show()
        self._preview()

    def calculate(self):
        try:
            result = format_result(evaluate(self.expression))
            original = self.expression
            self.history.insert(0, {"expression": original, "result": result})
            self.history = self.history[:100]
            self._save_history()
            self.expression = result
            self.just_calculated = True
            self._show(result, "= " + result)
        except CalculationError as error:
            self._show(self.expression, str(error))

    def copy_result(self):
        value = self.expression if self.just_calculated else ""
        if value:
            Clipboard.copy(value)
            self.ui.result_label.text = "Copied to clipboard"

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.ui.refresh_theme()

    def show_history(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        if not self.history:
            content.add_widget(Label(text="No calculations yet", font_size=sp(18)))
        else:
            from kivy.uix.scrollview import ScrollView
            from kivy.uix.gridlayout import GridLayout as Rows
            scroll = ScrollView()
            entries = Rows(cols=1, spacing=dp(6), size_hint_y=None)
            entries.bind(minimum_height=entries.setter("height"))
            for item in self.history:
                btn = Button(text=f"{item['expression']}  =  {item['result']}\nTap to reuse result", size_hint_y=None, height=dp(58), font_size=sp(15), background_normal="", background_color=(0.10, 0.20, 0.35, 1))
                btn.bind(on_release=lambda _b, result=item["result"]: self._reuse(result, popup))
                entries.add_widget(btn)
            scroll.add_widget(entries)
            content.add_widget(scroll)
        close = Button(text="Close", size_hint_y=None, height=dp(46), background_normal="", background_color=BLUE)
        content.add_widget(close)
        popup = Popup(title="Calculation history", content=content, size_hint=(0.9, 0.75), auto_dismiss=True)
        close.bind(on_release=popup.dismiss)
        popup.open()

    def _reuse(self, value, popup):
        self.expression = value
        self.just_calculated = True
        self._show(value, "Previous result")
        popup.dismiss()


def re_last_number(text):
    index = len(text)
    while index > 0 and (text[index - 1].isdigit() or text[index - 1] == "."):
        index -= 1
    return text[index:]


if __name__ == "__main__":
    EsonCalculator().run()
