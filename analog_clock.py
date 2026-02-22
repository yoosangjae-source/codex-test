#!/usr/bin/env python3
"""Desktop analog clock for macOS with alarm and customization controls."""

from __future__ import annotations

import datetime as dt
import math
import tkinter as tk
from tkinter import colorchooser, messagebox


KOREAN_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


class AnalogClockApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("아날로그 시계")
        self.root.geometry("680x760")
        self.root.resizable(True, True)

        self.number_color = "#1f2937"
        self.face_size = tk.IntVar(value=420)
        self.alarm_hour = tk.StringVar(value="07")
        self.alarm_minute = tk.StringVar(value="00")
        self.alarm_enabled = tk.BooleanVar(value=False)
        self.last_alarm_trigger: str | None = None

        self._build_ui()
        self._redraw_face()
        self._tick()

    def _build_ui(self) -> None:
        wrapper = tk.Frame(self.root, padx=14, pady=14)
        wrapper.pack(fill=tk.BOTH, expand=True)

        control = tk.LabelFrame(wrapper, text="설정", padx=10, pady=10)
        control.pack(fill=tk.X)

        tk.Label(control, text="숫자 색상").grid(row=0, column=0, sticky="w")
        self.color_preview = tk.Label(control, text="    ", bg=self.number_color, relief=tk.SUNKEN)
        self.color_preview.grid(row=0, column=1, padx=(8, 4), sticky="w")
        tk.Button(control, text="색상 선택", command=self._pick_color).grid(row=0, column=2, padx=4, sticky="w")

        tk.Label(control, text="시계 크기").grid(row=1, column=0, pady=(12, 0), sticky="w")
        tk.Scale(
            control,
            from_=280,
            to=600,
            orient=tk.HORIZONTAL,
            variable=self.face_size,
            command=lambda _value: self._redraw_face(),
            length=320,
        ).grid(row=1, column=1, columnspan=2, padx=(8, 4), pady=(12, 0), sticky="w")

        alarm = tk.LabelFrame(wrapper, text="알람", padx=10, pady=10)
        alarm.pack(fill=tk.X, pady=(12, 0))

        tk.Checkbutton(alarm, text="알람 켜기", variable=self.alarm_enabled).grid(row=0, column=0, sticky="w")
        tk.Label(alarm, text="시").grid(row=0, column=1, padx=(16, 2), sticky="e")
        tk.Entry(alarm, width=3, textvariable=self.alarm_hour, justify="center").grid(row=0, column=2)
        tk.Label(alarm, text=":").grid(row=0, column=3)
        tk.Entry(alarm, width=3, textvariable=self.alarm_minute, justify="center").grid(row=0, column=4)
        tk.Button(alarm, text="지금 시간으로 맞추기", command=self._set_alarm_now_plus_one).grid(
            row=0, column=5, padx=(12, 0)
        )

        self.canvas = tk.Canvas(wrapper, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

    def _pick_color(self) -> None:
        color = colorchooser.askcolor(title="숫자 색상 선택", initialcolor=self.number_color)[1]
        if color:
            self.number_color = color
            self.color_preview.configure(bg=color)
            self._redraw_face()

    def _set_alarm_now_plus_one(self) -> None:
        now = dt.datetime.now() + dt.timedelta(minutes=1)
        self.alarm_hour.set(f"{now.hour:02d}")
        self.alarm_minute.set(f"{now.minute:02d}")

    def _current_face_geometry(self) -> tuple[int, int, int]:
        self.canvas.update_idletasks()
        canvas_w = max(self.canvas.winfo_width(), 10)
        canvas_h = max(self.canvas.winfo_height(), 10)
        diameter = min(self.face_size.get(), canvas_w - 20, canvas_h - 20)
        radius = diameter // 2
        cx = canvas_w // 2
        cy = canvas_h // 2
        return cx, cy, radius

    def _draw_date(self, cx: int, cy: int, radius: int, now: dt.datetime) -> None:
        weekday = KOREAN_WEEKDAYS[now.weekday()]
        date_text = f"{now.year}년 {now.month}월 {now.day}일 ({weekday})"
        self.canvas.create_text(cx, cy - radius + 28, text=date_text, fill="#4b5563", font=("Apple SD Gothic Neo", 15))

    def _draw_face_numbers(self, cx: int, cy: int, radius: int) -> None:
        for hour in range(1, 13):
            angle = math.radians(hour * 30 - 90)
            x = cx + int(radius * 0.82 * math.cos(angle))
            y = cy + int(radius * 0.82 * math.sin(angle))
            self.canvas.create_text(x, y, text=str(hour), fill=self.number_color, font=("Helvetica", 18, "bold"))

    def _draw_hands(self, cx: int, cy: int, radius: int, now: dt.datetime) -> None:
        second = now.second + now.microsecond / 1_000_000
        minute = now.minute + second / 60
        hour = (now.hour % 12) + minute / 60

        self._draw_hand(cx, cy, radius * 0.50, hour * 30 - 90, width=7, color="#111827")
        self._draw_hand(cx, cy, radius * 0.68, minute * 6 - 90, width=5, color="#2563eb")
        self._draw_hand(cx, cy, radius * 0.78, second * 6 - 90, width=2, color="#dc2626")

        self.canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="#111827", outline="")

    def _draw_hand(self, cx: int, cy: int, length: float, angle_deg: float, width: int, color: str) -> None:
        angle = math.radians(angle_deg)
        x = cx + int(length * math.cos(angle))
        y = cy + int(length * math.sin(angle))
        self.canvas.create_line(cx, cy, x, y, fill=color, width=width, capstyle=tk.ROUND)

    def _draw_ticks(self, cx: int, cy: int, radius: int) -> None:
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer = radius * 0.93
            inner = radius * (0.86 if i % 5 == 0 else 0.89)
            x1 = cx + int(inner * math.cos(angle))
            y1 = cy + int(inner * math.sin(angle))
            x2 = cx + int(outer * math.cos(angle))
            y2 = cy + int(outer * math.sin(angle))
            self.canvas.create_line(x1, y1, x2, y2, fill="#6b7280", width=(3 if i % 5 == 0 else 1))

    def _redraw_face(self) -> None:
        now = dt.datetime.now()
        self.canvas.delete("all")
        cx, cy, radius = self._current_face_geometry()

        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#f9fafb", outline="#9ca3af", width=3)
        self._draw_date(cx, cy, radius, now)
        self._draw_ticks(cx, cy, radius)
        self._draw_face_numbers(cx, cy, radius)
        self._draw_hands(cx, cy, radius, now)

    def _maybe_trigger_alarm(self, now: dt.datetime) -> None:
        if not self.alarm_enabled.get():
            return

        try:
            hour = int(self.alarm_hour.get())
            minute = int(self.alarm_minute.get())
        except ValueError:
            return

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return

        stamp = now.strftime("%Y-%m-%d %H:%M")
        if now.hour == hour and now.minute == minute and self.last_alarm_trigger != stamp:
            self.last_alarm_trigger = stamp
            self.root.bell()
            messagebox.showinfo("알람", f"알람 시간입니다!\n{hour:02d}:{minute:02d}")

    def _tick(self) -> None:
        now = dt.datetime.now()
        self._redraw_face()
        self._maybe_trigger_alarm(now)
        self.root.after(200, self._tick)


def main() -> None:
    root = tk.Tk()
    AnalogClockApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
