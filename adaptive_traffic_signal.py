import tkinter as tk
from tkinter import messagebox
from collections import deque
import random


class AdaptiveTrafficSignal:

    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Traffic Control - Predictive Processor System")
        self.root.geometry("1450x850")
        self.root.minsize(1200, 700)
        self.root.configure(bg="#071018")

        # =========================================================
        # CONSTANTS
        # =========================================================

        self.DIRECTIONS = ["NORTH", "SOUTH", "EAST", "WEST"]

        self.signal_colors = {
            "NORTH": "#00e5ff",
            "SOUTH": "#00ff9d",
            "EAST": "#ffd166",
            "WEST": "#c77dff"
        }

        # =========================================================
        # COLORS
        # =========================================================

        self.bg = "#071018"
        self.panel = "#0c1822"
        self.panel2 = "#101f2b"
        self.button_bg = "#0b1821"
        self.border = "#31505f"

        self.text = "#e6f7ff"
        self.muted = "#71909e"

        self.cyan = "#00e5ff"
        self.green = "#00ff9d"
        self.yellow = "#ffd166"
        self.red = "#ff5577"
        self.purple = "#c77dff"

        # =========================================================
        # SYSTEM STATE
        # =========================================================

        self.running = False
        self.auto_traffic = False

        self.current_signal = "NORTH"
        self.phase = "GREEN"

        self.remaining_time = 90
        self.yellow_time = 5

        # =========================================================
        # INPUT REGISTERS
        # =========================================================

        self.input_registers = {
            "NORTH": 10,
            "SOUTH": 10,
            "EAST": 10,
            "WEST": 10
        }

        # Traffic actually applied to processor
        self.applied_traffic = {
            "NORTH": 10,
            "SOUTH": 10,
            "EAST": 10,
            "WEST": 10
        }

        # =========================================================
        # NEXT PREDICTED TRAFFIC DENSITY
        # =========================================================

        self.predicted_traffic = {
            "NORTH": random.randint(5, 45),
            "SOUTH": random.randint(5, 45),
            "EAST": random.randint(5, 45),
            "WEST": random.randint(5, 45)
        }

        # =========================================================
        # TRAFFIC HISTORY
        # =========================================================

        self.traffic_history = {
            direction: deque(maxlen=6)
            for direction in self.DIRECTIONS
        }

        for direction in self.DIRECTIONS:
            for _ in range(5):
                self.traffic_history[direction].append(
                    self.input_registers[direction]
                )

        # Simulated traffic movement
        self.traffic_velocity = {
            direction: random.uniform(-0.8, 0.8)
            for direction in self.DIRECTIONS
        }

        # Trend
        self.current_trend = {
            direction: 0.0
            for direction in self.DIRECTIONS
        }

        # Waiting priority
        self.wait_cycles = {
            direction: 0
            for direction in self.DIRECTIONS
        }

        # =========================================================
        # TIME CONTROL
        # =========================================================

        # Persistent manual time
        self.manual_time = None

        # One-time next signal override
        self.next_signal_time = None

        # =========================================================
        # STATISTICS
        # =========================================================

        self.total_cycles = 0
        self.total_vehicles_served = 0
        self.signal_changes = 0

        self.processor_status = "SYSTEM READY"
        self.processor_step = "WAITING FOR INPUT"

        # =========================================================
        # FONTS
        # =========================================================

        self.font_title = ("Segoe UI", 20, "bold")
        self.font_heading = ("Segoe UI", 10, "bold")
        self.font_normal = ("Segoe UI", 9)
        self.font_small = ("Segoe UI", 8)
        self.font_mono = ("Consolas", 9)
        self.font_big = ("Segoe UI", 34, "bold")

        # =========================================================
        # BUILD
        # =========================================================

        self.build_header()
        self.build_main_area()

        self.update_all_ui()

        # =========================================================
        # BACKGROUND LOOPS
        # =========================================================

        self.root.after(1000, self.run_cycle)
        self.root.after(2000, self.auto_traffic_update)
        self.root.after(1200, self.prediction_update)
        self.root.after(800, self.processing_animation)

    # =============================================================
    # UTILITY
    # =============================================================

    def clamp(self, value, low=0, high=50):
        return max(low, min(high, value))

    def direction_short(self, direction):
        return {
            "NORTH": "N",
            "SOUTH": "S",
            "EAST": "E",
            "WEST": "W"
        }[direction]

    def congestion_level(self, value):

        if value <= 10:
            return "LOW"

        elif value <= 20:
            return "MODERATE"

        elif value <= 35:
            return "HIGH"

        return "VERY HIGH"

    def congestion_color(self, value):

        if value <= 10:
            return self.green

        elif value <= 20:
            return self.cyan

        elif value <= 35:
            return self.yellow

        return self.red

    # =============================================================
    # HEADER
    # =============================================================

    def build_header(self):

        header = tk.Frame(
            self.root,
            bg="#08131c",
            height=65,
            highlightbackground=self.border,
            highlightthickness=1
        )

        header.pack(
            fill="x",
            padx=10,
            pady=(8, 5)
        )

        header.pack_propagate(False)

        left = tk.Frame(
            header,
            bg="#08131c"
        )

        left.pack(
            side="left",
            padx=18,
            pady=8
        )

        tk.Label(
            left,
            text="◈ ADAPTIVE TRAFFIC CONTROL",
            font=self.font_title,
            fg=self.cyan,
            bg="#08131c"
        ).pack(anchor="w")

        tk.Label(
            left,
            text="PREDICTIVE PROCESSOR-BASED SIGNAL MANAGEMENT",
            font=("Segoe UI", 7, "bold"),
            fg=self.muted,
            bg="#08131c"
        ).pack(anchor="w")

        self.system_status_label = tk.Label(
            header,
            text="● SYSTEM READY",
            font=("Segoe UI", 9, "bold"),
            fg=self.green,
            bg="#08131c"
        )

        self.system_status_label.pack(
            side="right",
            padx=20
        )

    # =============================================================
    # MAIN AREA
    # =============================================================

    def build_main_area(self):

        main = tk.Frame(
            self.root,
            bg=self.bg
        )

        main.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=3
        )

        # LEFT SIDE
        self.left_area = tk.Frame(
            main,
            bg=self.bg
        )

        self.left_area.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 5)
        )

        # RIGHT SIDE
        self.right_area = tk.Frame(
            main,
            bg=self.bg,
            width=500
        )

        self.right_area.pack(
            side="right",
            fill="y",
            padx=(5, 0)
        )

        self.right_area.pack_propagate(False)

        self.build_signal_cards()
        self.build_timer_controls()
        self.build_statistics()

        self.build_input_register_panel()
        self.build_intelligence_panel()
        self.build_processor_panel()

    # =============================================================
    # SIGNAL CARDS
    # =============================================================

    def build_signal_cards(self):

        section = tk.Frame(
            self.left_area,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        section.pack(
            fill="x",
            pady=(0, 5)
        )

        tk.Label(
            section,
            text="TRAFFIC SIGNAL OUTPUT",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=12,
            pady=(7, 3)
        )

        cards = tk.Frame(
            section,
            bg=self.panel
        )

        cards.pack(
            fill="x",
            padx=8,
            pady=(0, 8)
        )

        self.signal_widgets = {}

        for direction in self.DIRECTIONS:

            card = tk.Frame(
                cards,
                bg="#0a151e",
                highlightbackground=self.border,
                highlightthickness=1
            )

            card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=3
            )

            tk.Label(
                card,
                text=direction,
                font=("Segoe UI", 9, "bold"),
                fg=self.signal_colors[direction],
                bg="#0a151e"
            ).pack(pady=(6, 2))

            lights = tk.Frame(
                card,
                bg="#0a151e"
            )

            lights.pack(pady=1)

            red = tk.Label(
                lights,
                text="●",
                font=("Segoe UI", 19),
                fg="#35151d",
                bg="#0a151e"
            )

            red.pack(side="left")

            yellow = tk.Label(
                lights,
                text="●",
                font=("Segoe UI", 19),
                fg="#3b3014",
                bg="#0a151e"
            )

            yellow.pack(side="left")

            green = tk.Label(
                lights,
                text="●",
                font=("Segoe UI", 19),
                fg="#123a2c",
                bg="#0a151e"
            )

            green.pack(side="left")

            status = tk.Label(
                card,
                text="RED",
                font=("Consolas", 8, "bold"),
                fg=self.red,
                bg="#0a151e"
            )

            status.pack(pady=(0, 3))

            density = tk.Label(
                card,
                text="Density: 10",
                font=("Segoe UI", 8),
                fg=self.muted,
                bg="#0a151e"
            )

            density.pack(pady=(0, 6))

            self.signal_widgets[direction] = {
                "card": card,
                "red": red,
                "yellow": yellow,
                "green": green,
                "status": status,
                "density": density
            }

    # =============================================================
    # BUTTON CREATOR
    # =============================================================

    def make_button(
        self,
        parent,
        text,
        command,
        accent
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 8, "bold"),
            fg=accent,
            bg=self.button_bg,
            activeforeground="#ffffff",
            activebackground="#142936",
            relief="solid",
            bd=1,
            highlightbackground=accent,
            highlightcolor=accent,
            highlightthickness=1,
            cursor="hand2",
            padx=7,
            pady=5
        )

        return button

    # =============================================================
    # TIMER + CONTROLS
    # =============================================================

    def build_timer_controls(self):

        top = tk.Frame(
            self.left_area,
            bg=self.bg
        )

        top.pack(
            fill="x",
            pady=3
        )

        # TIMER
        timer_panel = tk.Frame(
            top,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        timer_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 3)
        )

        tk.Label(
            timer_panel,
            text="ACTIVE SIGNAL",
            font=("Segoe UI", 8),
            fg=self.muted,
            bg=self.panel
        ).pack(pady=(7, 0))

        self.active_signal_label = tk.Label(
            timer_panel,
            text="NORTH",
            font=("Segoe UI", 15, "bold"),
            fg=self.cyan,
            bg=self.panel
        )

        self.active_signal_label.pack()

        self.timer_label = tk.Label(
            timer_panel,
            text="90",
            font=self.font_big,
            fg=self.text,
            bg=self.panel
        )

        self.timer_label.pack()

        self.phase_label = tk.Label(
            timer_panel,
            text="GREEN PHASE",
            font=("Consolas", 8, "bold"),
            fg=self.green,
            bg=self.panel
        )

        self.phase_label.pack(
            pady=(0, 7)
        )

        # CONTROLS
        controls = tk.Frame(
            top,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        controls.pack(
            side="right",
            fill="both",
            expand=True,
            padx=(3, 0)
        )

        tk.Label(
            controls,
            text="SYSTEM CONTROL",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=10,
            pady=(7, 3)
        )

        row1 = tk.Frame(
            controls,
            bg=self.panel
        )

        row1.pack(
            fill="x",
            padx=8,
            pady=2
        )

        self.start_button = self.make_button(
            row1,
            "▶ START",
            self.start_system,
            self.green
        )

        self.start_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        self.pause_button = self.make_button(
            row1,
            "Ⅱ PAUSE",
            self.pause_system,
            self.yellow
        )

        self.pause_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        row2 = tk.Frame(
            controls,
            bg=self.panel
        )

        row2.pack(
            fill="x",
            padx=8,
            pady=2
        )

        self.auto_button = self.make_button(
            row2,
            "AUTO TRAFFIC: OFF",
            self.toggle_auto,
            self.cyan
        )

        self.auto_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        reset_button = self.make_button(
            row2,
            "RESET SYSTEM",
            self.reset_system,
            self.red
        )

        reset_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        row3 = tk.Frame(
            controls,
            bg=self.panel
        )

        row3.pack(
            fill="x",
            padx=8,
            pady=(2, 7)
        )

        reset_time = self.make_button(
            row3,
            "RESET CURRENT TIME",
            self.reset_time,
            self.yellow
        )

        reset_time.pack(
            fill="x",
            expand=True,
            padx=2
        )

    # =============================================================
    # STATISTICS
    # =============================================================

    def build_statistics(self):

        panel = tk.Frame(
            self.left_area,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        panel.pack(
            fill="x",
            pady=4
        )

        tk.Label(
            panel,
            text="SYSTEM STATISTICS",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=12,
            pady=(6, 3)
        )

        stats = tk.Frame(
            panel,
            bg=self.panel
        )

        stats.pack(
            fill="x",
            padx=7,
            pady=(0, 7)
        )

        self.stat_labels = {}

        items = [
            ("CYCLES", "cycles"),
            ("VEHICLES", "served"),
            ("CHANGES", "changes"),
            ("MODE", "mode")
        ]

        for title, key in items:

            box = tk.Frame(
                stats,
                bg="#0a151e",
                highlightbackground=self.border,
                highlightthickness=1
            )

            box.pack(
                side="left",
                fill="x",
                expand=True,
                padx=3
            )

            tk.Label(
                box,
                text=title,
                font=("Segoe UI", 7, "bold"),
                fg=self.muted,
                bg="#0a151e"
            ).pack(pady=(5, 0))

            value = tk.Label(
                box,
                text="0",
                font=("Segoe UI", 11, "bold"),
                fg=self.cyan,
                bg="#0a151e"
            )

            value.pack(
                pady=(0, 5)
            )

            self.stat_labels[key] = value

    # =============================================================
    # INPUT REGISTER PANEL
    # =============================================================

    def build_input_register_panel(self):

        panel = tk.Frame(
            self.right_area,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        panel.pack(
            fill="x",
            pady=(0, 4)
        )

        title_row = tk.Frame(
            panel,
            bg=self.panel
        )

        title_row.pack(
            fill="x",
            padx=10,
            pady=(6, 2)
        )

        tk.Label(
            title_row,
            text="INPUT REGISTER MATRIX",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(side="left")

        self.register_mode_label = tk.Label(
            title_row,
            text="MANUAL",
            font=("Consolas", 8, "bold"),
            fg=self.yellow,
            bg=self.panel
        )

        self.register_mode_label.pack(
            side="right"
        )

        self.sliders = {}
        self.register_value_labels = {}

        for direction in self.DIRECTIONS:

            row = tk.Frame(
                panel,
                bg=self.panel
            )

            row.pack(
                fill="x",
                padx=10,
                pady=1
            )

            tk.Label(
                row,
                text=self.direction_short(direction),
                width=2,
                font=("Consolas", 9, "bold"),
                fg=self.signal_colors[direction],
                bg=self.panel
            ).pack(side="left")

            value_label = tk.Label(
                row,
                text="10",
                width=3,
                font=("Consolas", 9, "bold"),
                fg=self.text,
                bg=self.panel
            )

            value_label.pack(side="right")

            slider = tk.Scale(
                row,
                from_=0,
                to=50,
                orient="horizontal",
                showvalue=False,
                resolution=1,
                bg=self.panel,
                fg=self.text,
                troughcolor="#172a35",
                highlightthickness=0,
                activebackground=self.cyan,
                sliderlength=15,
                command=lambda value, d=direction:
                    self.slider_changed(d, value)
            )

            slider.set(
                self.input_registers[direction]
            )

            slider.pack(
                side="left",
                fill="x",
                expand=True,
                padx=5
            )

            self.sliders[direction] = slider
            self.register_value_labels[direction] = value_label

        button_row = tk.Frame(
            panel,
            bg=self.panel
        )

        button_row.pack(
            fill="x",
            padx=8,
            pady=(5, 7)
        )

        random_button = self.make_button(
            button_row,
            "⚄ RANDOM INPUT",
            self.generate_random_traffic,
            self.purple
        )

        random_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

        apply_button = self.make_button(
            button_row,
            "✓ APPLY REGISTER DATA",
            self.apply_input_data,
            self.green
        )

        apply_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=2
        )

    # =============================================================
    # COMPACT TRAFFIC INTELLIGENCE
    # =============================================================

    def build_intelligence_panel(self):

        panel = tk.Frame(
            self.right_area,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        panel.pack(
            fill="x",
            pady=4
        )

        title_row = tk.Frame(
            panel,
            bg=self.panel
        )

        title_row.pack(
            fill="x",
            padx=10,
            pady=(6, 1)
        )

        tk.Label(
            title_row,
            text="TRAFFIC INTELLIGENCE",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(side="left")

        tk.Label(
            title_row,
            text="CURRENT → TREND → PREDICTED",
            font=("Consolas", 7),
            fg=self.muted,
            bg=self.panel
        ).pack(side="right")

        self.intelligence_rows = {}

        for direction in self.DIRECTIONS:

            row = tk.Frame(
                panel,
                bg="#0a151e",
                highlightbackground=self.border,
                highlightthickness=1
            )

            row.pack(
                fill="x",
                padx=8,
                pady=1
            )

            tk.Label(
                row,
                text=self.direction_short(direction),
                width=2,
                font=("Consolas", 8, "bold"),
                fg=self.signal_colors[direction],
                bg="#0a151e"
            ).pack(side="left")

            current = tk.Label(
                row,
                text="C 10",
                width=7,
                anchor="w",
                font=("Consolas", 8),
                fg=self.text,
                bg="#0a151e"
            )

            current.pack(side="left")

            trend = tk.Label(
                row,
                text="→ 0.0",
                width=8,
                anchor="w",
                font=("Consolas", 8),
                fg=self.cyan,
                bg="#0a151e"
            )

            trend.pack(side="left")

            predicted = tk.Label(
                row,
                text="P 10",
                width=7,
                anchor="w",
                font=("Consolas", 8, "bold"),
                fg=self.green,
                bg="#0a151e"
            )

            predicted.pack(side="left")

            congestion = tk.Label(
                row,
                text="LOW",
                width=9,
                anchor="w",
                font=("Consolas", 7, "bold"),
                fg=self.green,
                bg="#0a151e"
            )

            congestion.pack(side="left")

            self.intelligence_rows[direction] = {
                "current": current,
                "trend": trend,
                "predicted": predicted,
                "congestion": congestion
            }

        summary = tk.Frame(
            panel,
            bg="#0a151e"
        )

        summary.pack(
            fill="x",
            padx=8,
            pady=(3, 5)
        )

        self.next_signal_prediction_label = tk.Label(
            summary,
            text="NEXT: NORTH",
            font=("Consolas", 8, "bold"),
            fg=self.cyan,
            bg="#0a151e"
        )

        self.next_signal_prediction_label.pack(
            side="left",
            padx=5,
            pady=3
        )

        self.predicted_time_label = tk.Label(
            summary,
            text="GREEN: 60s",
            font=("Consolas", 8, "bold"),
            fg=self.yellow,
            bg="#0a151e"
        )

        self.predicted_time_label.pack(
            side="right",
            padx=5,
            pady=3
        )

    # =============================================================
    # PROCESSOR + TIMING CONTROL
    # =============================================================

    def build_processor_panel(self):

        panel = tk.Frame(
            self.right_area,
            bg=self.panel,
            highlightbackground=self.border,
            highlightthickness=1
        )

        # IMPORTANT:
        # This fills remaining vertical space instead of expanding
        # beyond the window.
        panel.pack(
            fill="both",
            expand=True,
            pady=(4, 0)
        )

        tk.Label(
            panel,
            text="PROCESSOR DECISION",
            font=self.font_heading,
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=10,
            pady=(6, 2)
        )

        self.processor_decision_label = tk.Label(
            panel,
            text="WAITING FOR INPUT",
            font=("Segoe UI", 13, "bold"),
            fg=self.cyan,
            bg=self.panel
        )

        self.processor_decision_label.pack(
            pady=(1, 2)
        )

        self.processor_detail_label = tk.Label(
            panel,
            text="Processor is waiting for traffic data.",
            font=("Consolas", 8),
            fg=self.muted,
            bg=self.panel,
            wraplength=460,
            justify="left"
        )

        self.processor_detail_label.pack(
            anchor="w",
            padx=10,
            pady=2
        )

        # =========================================================
        # TIMING CONTROL
        # =========================================================

        timing = tk.Frame(
            panel,
            bg="#0a151e",
            highlightbackground=self.border,
            highlightthickness=1
        )

        timing.pack(
            fill="x",
            padx=8,
            pady=6
        )

        tk.Label(
            timing,
            text="TIMING CONTROL",
            font=self.font_heading,
            fg=self.text,
            bg="#0a151e"
        ).pack(
            anchor="w",
            padx=8,
            pady=(6, 3)
        )

        # MANUAL TIME
        manual_row = tk.Frame(
            timing,
            bg="#0a151e"
        )

        manual_row.pack(
            fill="x",
            padx=7,
            pady=2
        )

        tk.Label(
            manual_row,
            text="MANUAL TIME",
            width=13,
            anchor="w",
            font=("Consolas", 8),
            fg=self.muted,
            bg="#0a151e"
        ).pack(side="left")

        self.manual_entry = tk.Entry(
            manual_row,
            width=7,
            font=("Consolas", 9),
            bg="#111f29",
            fg=self.text,
            insertbackground=self.text,
            relief="solid",
            bd=1
        )

        self.manual_entry.pack(
            side="left",
            padx=4
        )

        manual_set = self.make_button(
            manual_row,
            "SET MANUAL",
            self.set_manual_time,
            self.cyan
        )

        manual_set.pack(
            side="left",
            padx=3
        )

        # NEXT SIGNAL TIME
        next_row = tk.Frame(
            timing,
            bg="#0a151e"
        )

        next_row.pack(
            fill="x",
            padx=7,
            pady=2
        )

        tk.Label(
            next_row,
            text="NEXT SIGNAL",
            width=13,
            anchor="w",
            font=("Consolas", 8),
            fg=self.muted,
            bg="#0a151e"
        ).pack(side="left")

        self.next_entry = tk.Entry(
            next_row,
            width=7,
            font=("Consolas", 9),
            bg="#111f29",
            fg=self.text,
            insertbackground=self.text,
            relief="solid",
            bd=1
        )

        self.next_entry.pack(
            side="left",
            padx=4
        )

        next_set = self.make_button(
            next_row,
            "SET NEXT",
            self.set_next_signal_time,
            self.yellow
        )

        next_set.pack(
            side="left",
            padx=3
        )

        self.timing_status_label = tk.Label(
            timing,
            text="Adaptive timing: 60–90 sec",
            font=("Consolas", 7),
            fg=self.muted,
            bg="#0a151e"
        )

        self.timing_status_label.pack(
            anchor="w",
            padx=8,
            pady=(3, 6)
        )

        # =========================================================
        # CURRENT APPLIED TRAFFIC
        # =========================================================

        applied = tk.Frame(
            panel,
            bg="#0a151e",
            highlightbackground=self.border,
            highlightthickness=1
        )

        applied.pack(
            fill="x",
            padx=8,
            pady=(0, 7)
        )

        tk.Label(
            applied,
            text="CURRENT APPLIED TRAFFIC",
            font=("Segoe UI", 8, "bold"),
            fg=self.text,
            bg="#0a151e"
        ).pack(
            anchor="w",
            padx=8,
            pady=(5, 1)
        )

        self.applied_label = tk.Label(
            applied,
            text="N 10   S 10   E 10   W 10",
            font=("Consolas", 9, "bold"),
            fg=self.green,
            bg="#0a151e"
        )

        self.applied_label.pack(
            pady=(0, 5)
        )

    # =============================================================
    # SLIDER CHANGE
    # =============================================================

    def slider_changed(
        self,
        direction,
        value
    ):

        try:
            value = int(float(value))
        except ValueError:
            return

        self.input_registers[direction] = value

        self.register_value_labels[direction].config(
            text=str(value)
        )

        self.traffic_history[direction].append(
            value
        )

        # AUTO OFF = independent prediction
        if not self.auto_traffic:

            self.predicted_traffic[direction] = random.randint(
                5,
                45
            )

        self.update_intelligence_ui()

    # =============================================================
    # START
    # =============================================================

    def start_system(self):

        self.running = True

        self.system_status_label.config(
            text="● SYSTEM RUNNING",
            fg=self.green
        )

        self.processor_status = "PROCESSOR RUNNING"

    # =============================================================
    # PAUSE
    # =============================================================

    def pause_system(self):

        self.running = False

        self.system_status_label.config(
            text="● SYSTEM PAUSED",
            fg=self.yellow
        )

        self.processor_status = "PROCESSOR PAUSED"

    # =============================================================
    # AUTO TOGGLE
    # =============================================================

    def toggle_auto(self):

        self.auto_traffic = not self.auto_traffic

        if self.auto_traffic:

            self.auto_button.config(
                text="AUTO TRAFFIC: ON",
                fg=self.green
            )

            self.register_mode_label.config(
                text="AUTO SENSOR",
                fg=self.green
            )

            self.processor_status = "AUTO PREDICTIVE MODE"

            for direction in self.DIRECTIONS:

                self.traffic_history[direction].clear()

                for _ in range(5):

                    self.traffic_history[direction].append(
                        self.input_registers[direction]
                    )

                self.traffic_velocity[direction] = random.uniform(
                    -0.7,
                    0.7
                )

            self.update_prediction_from_registers()

        else:

            self.auto_button.config(
                text="AUTO TRAFFIC: OFF",
                fg=self.cyan
            )

            self.register_mode_label.config(
                text="MANUAL",
                fg=self.yellow
            )

            self.processor_status = "MANUAL INPUT MODE"

            # Independent random predictions
            for direction in self.DIRECTIONS:

                self.predicted_traffic[direction] = random.randint(
                    5,
                    45
                )

        self.update_intelligence_ui()

    # =============================================================
    # RANDOM INPUT
    # =============================================================

    def generate_random_traffic(self):

        for direction in self.DIRECTIONS:

            value = random.randint(
                0,
                50
            )

            self.input_registers[direction] = value

            self.sliders[direction].set(
                value
            )

            self.register_value_labels[direction].config(
                text=str(value)
            )

            self.traffic_history[direction].append(
                value
            )

            # AUTO OFF:
            # prediction is independent
            if not self.auto_traffic:

                self.predicted_traffic[direction] = random.randint(
                    5,
                    45
                )

        self.processor_decision_label.config(
            text="NEW INPUT DATA READY",
            fg=self.purple
        )

        self.processor_detail_label.config(
            text=(
                "Random traffic values loaded into the "
                "Input Registers.\n"
                "Press APPLY REGISTER DATA to send the "
                "values to the processor."
            )
        )

        self.update_intelligence_ui()

    # =============================================================
    # APPLY INPUT DATA
    # =============================================================

    def apply_input_data(self):

        self.applied_traffic = self.input_registers.copy()

        if self.auto_traffic:

            self.update_prediction_from_registers()

        else:

            for direction in self.DIRECTIONS:

                self.predicted_traffic[direction] = random.randint(
                    5,
                    45
                )

        selected = self.select_next_signal(
            use_prediction=True,
            allow_current=True
        )

        self.current_signal = selected
        self.phase = "GREEN"

        # ---------------------------------------------------------
        # IMPORTANT:
        # If Manual Time is already set, APPLY uses Manual Time.
        # ---------------------------------------------------------

        if self.manual_time is not None:

            self.remaining_time = self.manual_time

        else:

            self.remaining_time = self.calculate_green_time(
                selected,
                use_prediction=True
            )

        self.processor_decision_label.config(
            text=f"NEXT SIGNAL: {selected}",
            fg=self.signal_colors[selected]
        )

        self.processor_detail_label.config(
            text=(
                f"Processor analyzed Input Registers.\n"
                f"Selected: {selected}\n"
                f"Current density: "
                f"{self.input_registers[selected]}\n"
                f"Predicted density: "
                f"{self.predicted_traffic[selected]}\n"
                f"Green allocation: "
                f"{self.remaining_time} sec"
            )
        )

        self.processor_status = "INPUT DATA APPLIED"

        self.update_all_ui()

    # =============================================================
    # AUTO TRAFFIC SIMULATION
    # =============================================================

    def auto_traffic_update(self):

        if self.auto_traffic:

            for direction in self.DIRECTIONS:

                current = self.input_registers[direction]

                # Occasionally change direction of traffic movement
                if random.random() < 0.25:

                    self.traffic_velocity[direction] += random.uniform(
                        -0.55,
                        0.55
                    )

                self.traffic_velocity[direction] = max(
                    -1.8,
                    min(
                        1.8,
                        self.traffic_velocity[direction]
                    )
                )

                # Density behavior
                if current > 38:

                    density_bias = random.uniform(
                        -0.1,
                        0.6
                    )

                elif current < 8:

                    density_bias = random.uniform(
                        -0.5,
                        0.3
                    )

                else:

                    density_bias = random.uniform(
                        -0.25,
                        0.25
                    )

                sensor_noise = random.uniform(
                    -0.7,
                    0.7
                )

                change = (
                    self.traffic_velocity[direction]
                    + density_bias
                    + sensor_noise
                )

                change = max(
                    -3,
                    min(
                        3,
                        change
                    )
                )

                new_value = round(
                    self.clamp(
                        current + change
                    )
                )

                if current >= 47 and random.random() < 0.5:

                    new_value = max(
                        0,
                        current - random.randint(
                            1,
                            2
                        )
                    )

                self.input_registers[direction] = new_value

                self.sliders[direction].set(
                    new_value
                )

                self.register_value_labels[direction].config(
                    text=str(new_value)
                )

                self.traffic_history[direction].append(
                    new_value
                )

            self.processor_status = "LIVE SENSOR SIMULATION"

            self.update_prediction_from_registers()

            self.update_intelligence_ui()

        self.root.after(
            2000,
            self.auto_traffic_update
        )

    # =============================================================
    # PREDICTION UPDATE
    # =============================================================

    def prediction_update(self):

        if self.auto_traffic:

            self.update_prediction_from_registers()

        else:

            # AUTO OFF = independent prediction
            for direction in self.DIRECTIONS:

                current_prediction = (
                    self.predicted_traffic[direction]
                )

                small_change = random.choice(
                    [-2, -1, 0, 0, 0, 1, 2]
                )

                self.predicted_traffic[direction] = self.clamp(
                    current_prediction + small_change
                )

        self.update_intelligence_ui()

        self.root.after(
            1200,
            self.prediction_update
        )

    # =============================================================
    # PREDICTION ALGORITHM
    # =============================================================

    def update_prediction_from_registers(self):

        for direction in self.DIRECTIONS:

            current = self.input_registers[direction]

            history = list(
                self.traffic_history[direction]
            )

            if len(history) >= 2:

                changes = []

                for i in range(
                    1,
                    len(history)
                ):

                    changes.append(
                        history[i] - history[i - 1]
                    )

                if changes:

                    trend = sum(changes) / len(changes)

                else:

                    trend = 0

            else:

                trend = 0

            # Smooth trend
            previous_trend = self.current_trend[direction]

            trend = (
                previous_trend * 0.55
                + trend * 0.45
            )

            self.current_trend[direction] = trend

            # Future density
            predicted = (
                current
                + trend * 3
            )

            predicted += random.uniform(
                -0.5,
                0.5
            )

            # Keep prediction reasonably related
            if predicted > current + 10:

                predicted = current + 10

            elif predicted < current - 10:

                predicted = current - 10

            self.predicted_traffic[direction] = round(
                self.clamp(predicted)
            )

    # =============================================================
    # GREEN TIME
    # =============================================================

    def calculate_green_time(
        self,
        direction,
        use_prediction=True
    ):

        # Manual time has priority
        if self.manual_time is not None:

            return self.manual_time

        current = self.input_registers[direction]

        if use_prediction:

            predicted = self.predicted_traffic[direction]

            effective_density = (
                current * 0.45
                + predicted * 0.55
            )

            trend = self.current_trend[direction]

            if trend > 0:

                effective_density += min(
                    trend * 2,
                    5
                )

        else:

            effective_density = current

        effective_density = self.clamp(
            effective_density
        )

        green_time = (
            60
            + int(
                effective_density / 50 * 30
            )
        )

        return max(
            60,
            min(
                90,
                green_time
            )
        )

    # =============================================================
    # SELECT SIGNAL
    # =============================================================

    def select_next_signal(
        self,
        use_prediction=True,
        allow_current=False
    ):

        scores = {}

        for direction in self.DIRECTIONS:

            current = self.input_registers[direction]

            if use_prediction:

                predicted = self.predicted_traffic[direction]

            else:

                predicted = current

            trend = self.current_trend[direction]

            score = (
                current * 0.25
                + predicted * 0.55
                + max(trend, 0) * 5
                + min(
                    self.wait_cycles[direction] * 2,
                    10
                )
            )

            if (
                not allow_current
                and direction == self.current_signal
            ):

                score -= 12

            scores[direction] = score

        selected = max(
            scores,
            key=scores.get
        )

        for direction in self.DIRECTIONS:

            if direction == selected:

                self.wait_cycles[direction] = 0

            else:

                self.wait_cycles[direction] += 1

        return selected

    # =============================================================
    # PREDICTION-ONLY SIGNAL
    # =============================================================

    def select_prediction_only(self):

        best_direction = self.DIRECTIONS[0]
        best_score = -9999

        for direction in self.DIRECTIONS:

            current = self.input_registers[direction]
            predicted = self.predicted_traffic[direction]
            trend = self.current_trend[direction]

            score = (
                current * 0.25
                + predicted * 0.55
                + max(trend, 0) * 5
                + min(
                    self.wait_cycles[direction] * 2,
                    10
                )
            )

            if direction == self.current_signal:

                score -= 12

            if score > best_score:

                best_score = score
                best_direction = direction

        return best_direction

    # =============================================================
    # PROCESSING ANIMATION
    # =============================================================

    def processing_animation(self):

        if self.auto_traffic:

            stages = [
                "DETECTING → ANALYZING → PREDICTING",
                "ANALYZING → PREDICTING → SELECTING",
                "PREDICTING → SELECTING → SIGNAL OUTPUT",
                "SELECTING → SIGNAL OUTPUT → MONITORING"
            ]

            index = (
                int(
                    self.root.tk.call(
                        "clock",
                        "milliseconds"
                    ) / 900
                )
                % len(stages)
            )

            # Only show this if prediction panel exists
            # and do not add another widget that increases height.

        self.root.after(
            800,
            self.processing_animation
        )

    # =============================================================
    # TIMER LOOP
    # =============================================================

    def run_cycle(self):

        if self.running:

            if self.phase == "GREEN":

                self.remaining_time -= 1

                self.simulate_vehicle_service()

                if self.remaining_time <= 0:

                    self.phase = "YELLOW"
                    self.remaining_time = self.yellow_time

                    self.processor_step = "YELLOW TRANSITION"

            elif self.phase == "YELLOW":

                self.remaining_time -= 1

                if self.remaining_time <= 0:

                    # Refresh prediction before selecting
                    if self.auto_traffic:

                        self.update_prediction_from_registers()

                    next_signal = self.select_next_signal(
                        use_prediction=True,
                        allow_current=False
                    )

                    self.current_signal = next_signal
                    self.phase = "GREEN"

                    # One-time next signal override
                    if self.next_signal_time is not None:

                        self.remaining_time = (
                            self.next_signal_time
                        )

                        self.next_signal_time = None

                    else:

                        self.remaining_time = (
                            self.calculate_green_time(
                                next_signal,
                                use_prediction=True
                            )
                        )

                    self.total_cycles += 1
                    self.signal_changes += 1

                    self.processor_step = "NEW SIGNAL OUTPUT"

                    self.processor_decision_label.config(
                        text=f"NEXT SIGNAL: {next_signal}",
                        fg=self.signal_colors[next_signal]
                    )

                    self.processor_detail_label.config(
                        text=(
                            f"Predictive processor decision\n"
                            f"Selected road: {next_signal}\n"
                            f"Current density: "
                            f"{self.input_registers[next_signal]}\n"
                            f"Predicted density: "
                            f"{self.predicted_traffic[next_signal]}\n"
                            f"Trend: "
                            f"{self.current_trend[next_signal]:+.1f}\n"
                            f"Green allocation: "
                            f"{self.remaining_time} sec"
                        )
                    )

        self.update_all_ui()

        self.root.after(
            1000,
            self.run_cycle
        )

    # =============================================================
    # VEHICLE SERVICE
    # =============================================================

    def simulate_vehicle_service(self):

        direction = self.current_signal

        current = self.applied_traffic[direction]

        if current > 0:

            served = random.randint(
                0,
                2
            )

            self.applied_traffic[direction] = max(
                0,
                current - served
            )

            self.total_vehicles_served += served

    # =============================================================
    # MANUAL TIME
    # =============================================================

    def set_manual_time(self):

        try:

            value = int(
                self.manual_entry.get().strip()
            )

            if value < 1 or value > 300:

                raise ValueError

            # Persistent manual timing
            self.manual_time = value

            # =====================================================
            # IMPORTANT FIX:
            # Immediately change CURRENT countdown.
            # =====================================================

            self.remaining_time = value

            # Keep current phase
            self.phase = "GREEN"

            self.timing_status_label.config(
                text=f"MANUAL TIME ACTIVE: {value} sec",
                fg=self.cyan
            )

            self.processor_decision_label.config(
                text=f"MANUAL TIME SET: {value}s",
                fg=self.cyan
            )

            self.processor_detail_label.config(
                text=(
                    f"Manual timing override applied immediately.\n"
                    f"Current signal: {self.current_signal}\n"
                    f"Current timer: {value} sec\n"
                    f"Future green signals will also use {value} sec."
                )
            )

            self.update_all_ui()

        except ValueError:

            messagebox.showerror(
                "Invalid Time",
                "Enter a valid time between 1 and 300 seconds."
            )

    # =============================================================
    # NEXT SIGNAL TIME
    # =============================================================

    def set_next_signal_time(self):

        try:

            value = int(
                self.next_entry.get().strip()
            )

            if value < 1 or value > 300:

                raise ValueError

            # One-time override
            self.next_signal_time = value

            self.timing_status_label.config(
                text=(
                    f"NEXT SIGNAL OVERRIDE: "
                    f"{value} sec"
                ),
                fg=self.yellow
            )

            self.processor_decision_label.config(
                text="NEXT SIGNAL TIME READY",
                fg=self.yellow
            )

            self.processor_detail_label.config(
                text=(
                    f"Current signal continues normally.\n"
                    f"Next signal will receive "
                    f"{value} seconds.\n"
                    f"After that, the system returns to "
                    f"Manual Time or Adaptive Time."
                )
            )

            self.update_all_ui()

        except ValueError:

            messagebox.showerror(
                "Invalid Time",
                "Enter a valid time between 1 and 300 seconds."
            )

    # =============================================================
    # RESET CURRENT TIME
    # =============================================================

    def reset_time(self):

        self.remaining_time = 90
        self.phase = "GREEN"

        self.timing_status_label.config(
            text="CURRENT TIMER RESET: 90 sec",
            fg=self.yellow
        )

        self.processor_decision_label.config(
            text="CURRENT TIME RESET",
            fg=self.yellow
        )

        self.update_all_ui()

    # =============================================================
    # RESET SYSTEM
    # =============================================================

    def reset_system(self):

        self.running = False
        self.auto_traffic = False

        self.current_signal = "NORTH"
        self.phase = "GREEN"
        self.remaining_time = 90

        self.manual_time = None
        self.next_signal_time = None

        self.total_cycles = 0
        self.total_vehicles_served = 0
        self.signal_changes = 0

        for direction in self.DIRECTIONS:

            self.input_registers[direction] = 5

            self.applied_traffic[direction] = 5

            self.predicted_traffic[direction] = random.randint(
                5,
                45
            )

            self.traffic_velocity[direction] = random.uniform(
                -0.7,
                0.7
            )

            self.current_trend[direction] = 0

            self.wait_cycles[direction] = 0

            self.traffic_history[direction].clear()

            for _ in range(5):

                self.traffic_history[direction].append(5)

            self.sliders[direction].set(5)

        self.auto_button.config(
            text="AUTO TRAFFIC: OFF",
            fg=self.cyan
        )

        self.register_mode_label.config(
            text="MANUAL",
            fg=self.yellow
        )

        self.system_status_label.config(
            text="● SYSTEM READY",
            fg=self.green
        )

        self.timing_status_label.config(
            text="Adaptive timing: 60–90 sec",
            fg=self.muted
        )

        self.processor_decision_label.config(
            text="SYSTEM RESET",
            fg=self.green
        )

        self.processor_detail_label.config(
            text=(
                "All registers reset to default values.\n"
                "System is ready for new traffic input."
            )
        )

        self.update_all_ui()

    # =============================================================
    # SIGNAL UI
    # =============================================================

    def update_signal_ui(self):

        for direction in self.DIRECTIONS:

            widgets = self.signal_widgets[direction]

            if direction == self.current_signal:

                widgets["card"].config(
                    highlightbackground=self.signal_colors[direction],
                    highlightthickness=2
                )

                if self.phase == "GREEN":

                    widgets["red"].config(
                        fg="#35151d"
                    )

                    widgets["yellow"].config(
                        fg="#3b3014"
                    )

                    widgets["green"].config(
                        fg=self.green
                    )

                    widgets["status"].config(
                        text="GREEN",
                        fg=self.green
                    )

                else:

                    widgets["red"].config(
                        fg="#35151d"
                    )

                    widgets["yellow"].config(
                        fg=self.yellow
                    )

                    widgets["green"].config(
                        fg="#123a2c"
                    )

                    widgets["status"].config(
                        text="YELLOW",
                        fg=self.yellow
                    )

            else:

                widgets["card"].config(
                    highlightbackground=self.border,
                    highlightthickness=1
                )

                widgets["red"].config(
                    fg=self.red
                )

                widgets["yellow"].config(
                    fg="#3b3014"
                )

                widgets["green"].config(
                    fg="#123a2c"
                )

                widgets["status"].config(
                    text="RED",
                    fg=self.red
                )

            widgets["density"].config(
                text=(
                    f"Density: "
                    f"{self.input_registers[direction]}"
                )
            )

    # =============================================================
    # INTELLIGENCE UI
    # =============================================================

    def update_intelligence_ui(self):

        for direction in self.DIRECTIONS:

            current = self.input_registers[direction]

            trend = self.current_trend[direction]

            predicted = self.predicted_traffic[direction]

            level = self.congestion_level(
                predicted
            )

            color = self.congestion_color(
                predicted
            )

            if trend > 0.15:

                arrow = "↑"

            elif trend < -0.15:

                arrow = "↓"

            else:

                arrow = "→"

            row = self.intelligence_rows[direction]

            row["current"].config(
                text=f"C {current:02d}"
            )

            row["trend"].config(
                text=f"{arrow} {trend:+.1f}",
                fg=(
                    self.green
                    if trend > 0.15
                    else self.red
                    if trend < -0.15
                    else self.cyan
                )
            )

            row["predicted"].config(
                text=f"P {predicted:02d}",
                fg=self.green
            )

            row["congestion"].config(
                text=level,
                fg=color
            )

        next_signal = self.select_prediction_only()

        predicted_time = self.calculate_green_time(
            next_signal,
            use_prediction=True
        )

        self.next_signal_prediction_label.config(
            text=f"NEXT: {next_signal}",
            fg=self.signal_colors[next_signal]
        )

        self.predicted_time_label.config(
            text=f"GREEN: {predicted_time}s"
        )

    # =============================================================
    # UPDATE EVERYTHING
    # =============================================================

    def update_all_ui(self):

        self.update_signal_ui()
        self.update_intelligence_ui()

        self.active_signal_label.config(
            text=self.current_signal,
            fg=self.signal_colors[self.current_signal]
        )

        self.timer_label.config(
            text=str(
                max(
                    0,
                    self.remaining_time
                )
            )
        )

        if self.phase == "GREEN":

            self.phase_label.config(
                text="GREEN PHASE",
                fg=self.green
            )

        else:

            self.phase_label.config(
                text="YELLOW PHASE",
                fg=self.yellow
            )

        # Statistics
        self.stat_labels["cycles"].config(
            text=str(
                self.total_cycles
            )
        )

        self.stat_labels["served"].config(
            text=str(
                self.total_vehicles_served
            )
        )

        self.stat_labels["changes"].config(
            text=str(
                self.signal_changes
            )
        )

        self.stat_labels["mode"].config(
            text=(
                "AUTO"
                if self.auto_traffic
                else "MANUAL"
            ),
            fg=(
                self.green
                if self.auto_traffic
                else self.yellow
            )
        )

        # Applied traffic
        self.applied_label.config(
            text=(
                f"N {self.applied_traffic['NORTH']:02d}   "
                f"S {self.applied_traffic['SOUTH']:02d}   "
                f"E {self.applied_traffic['EAST']:02d}   "
                f"W {self.applied_traffic['WEST']:02d}"
            )
        )

        # Register values
        for direction in self.DIRECTIONS:

            self.register_value_labels[direction].config(
                text=str(
                    self.input_registers[direction]
                )
            )

        # Status
        if self.running:

            if self.auto_traffic:

                self.system_status_label.config(
                    text="● RUNNING • AUTO PREDICTIVE",
                    fg=self.green
                )

            else:

                self.system_status_label.config(
                    text="● RUNNING • MANUAL",
                    fg=self.cyan
                )

        # Timing status priority
        if self.next_signal_time is not None:

            self.timing_status_label.config(
                text=(
                    f"NEXT SIGNAL OVERRIDE: "
                    f"{self.next_signal_time} sec"
                ),
                fg=self.yellow
            )

        elif self.manual_time is not None:

            self.timing_status_label.config(
                text=(
                    f"MANUAL TIME ACTIVE: "
                    f"{self.manual_time} sec"
                ),
                fg=self.cyan
            )


# =============================================================
# RUN APPLICATION
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AdaptiveTrafficSignal(root)

    root.mainloop()