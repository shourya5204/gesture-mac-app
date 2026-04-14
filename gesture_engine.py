import time
import math

class GestureEngine:
    def __init__(self):
        self.cooldown_time = 0
        self.delay = 0.25

        self.top_zone = 0.2
        self.bottom_zone = 0.8

        self.dwell_start = None
        self.dwell_delay = 0.25

        # 🔥 repeat control
        self.last_scroll_time = 0
        self.scroll_interval = 0.05

    def distance(self, p1, p2):
        return math.hypot(p2.x - p1.x, p2.y - p1.y)

    def update(self, hand):
        if hand is None:
            self.dwell_start = None
            return None

        x = hand["x"]
        y = hand["y"]
        landmarks = hand["landmarks"]

        thumb = landmarks[4]
        index = landmarks[8]

        dist = self.distance(thumb, index)
        pinch = dist < 0.04

        current_time = time.time()

        # =========================
        # 🤏 PINCH → SWITCH
        # =========================
        if pinch and (current_time - self.cooldown_time > self.delay):
            self.cooldown_time = current_time
            self.dwell_start = None

            if x < 0.4:
                return "LEFT"
            elif x > 0.6:
                return "RIGHT"

        # =========================
        # 🔼 TOP → SCROLL UP
        # =========================
        if y < self.top_zone:
            if self.dwell_start is None:
                self.dwell_start = current_time

            elif current_time - self.dwell_start > self.dwell_delay:
                if current_time - self.last_scroll_time > self.scroll_interval:
                    self.last_scroll_time = current_time
                    return "SCROLL_UP"

        # =========================
        # 🔽 BOTTOM → SCROLL DOWN
        # =========================
        elif y > self.bottom_zone:
            if self.dwell_start is None:
                self.dwell_start = current_time

            elif current_time - self.dwell_start > self.dwell_delay:
                if current_time - self.last_scroll_time > self.scroll_interval:
                    self.last_scroll_time = current_time
                    return "SCROLL_DOWN"

        else:
            self.dwell_start = None

        return None