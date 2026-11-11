"""
Advanced Scientific Calculator — Tkinter

Features:
- Basic arithmetic, parentheses, percentages, powers
- sin, cos, tan, inverse trig, sqrt, ln, log10, factorial, abs, exp
- pi and e constants
- DEG/RAD angle mode
- Memory: MC, MR, M+, M-
- Keyboard input, backspace, history
- Restricted AST-based expression evaluation (does not use eval)
"""

import ast
import math
import operator
import re
import tkinter as tk
from tkinter import ttk


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("900x650")
        self.root.minsize(760, 570)
        self.root.configure(bg="#101522")

        self.expression = ""
        self.last_answer = 0.0
        self.memory = 0.0
        self.angle_mode = tk.StringVar(value="DEG")
        self.display_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="Ready")

        self.colors = {
            "bg": "#101522",
            "panel": "#171e2e",
            "display": "#0b1020",
            "number": "#252f45",
            "function": "#1d2940",
            "operator": "#315efb",
            "danger": "#e05260",
            "equal": "#16a085",
            "text": "#f4f7ff",
            "muted": "#9ca9c7",
            "accent": "#7ea6ff",
        }

        self._setup_style()
        self._build_ui()
        self._bind_keys()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Calc.TCombobox",
            fieldbackground=self.colors["panel"],
            background=self.colors["panel"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["text"],
            borderwidth=0,
        )

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.colors["bg"])
        header.pack(fill="x", padx=22, pady=(18, 12))

        tk.Label(
            header, text="SCIENTIFIC",
            font=("Segoe UI", 19, "bold"),
            fg=self.colors["text"], bg=self.colors["bg"]
        ).pack(side="left")
        tk.Label(
            header, text="CALCULATOR",
            font=("Segoe UI", 19),
            fg=self.colors["accent"], bg=self.colors["bg"]
        ).pack(side="left", padx=(7, 0))

        mode_frame = tk.Frame(header, bg=self.colors["bg"])
        mode_frame.pack(side="right")
        tk.Label(
            mode_frame, text="ANGLE",
            font=("Segoe UI", 9, "bold"),
            fg=self.colors["muted"], bg=self.colors["bg"]
        ).pack(side="left", padx=(0, 8))
        mode_menu = tk.OptionMenu(
            mode_frame, self.angle_mode, "DEG", "RAD",
            command=lambda _value: self.status_var.set(
                f"Angle mode: {self.angle_mode.get()}"
            )
        )
        mode_menu.config(
            bg=self.colors["panel"], fg=self.colors["text"],
            activebackground=self.colors["function"],
            activeforeground=self.colors["text"],
            relief="flat", bd=0, highlightthickness=0,
            font=("Segoe UI", 10, "bold"), padx=10
        )
        mode_menu["menu"].config(
            bg=self.colors["panel"], fg=self.colors["text"],
            activebackground=self.colors["operator"]
        )
        mode_menu.pack(side="left")

        display = tk.Frame(
            self.root, bg=self.colors["display"],
            highlightbackground="#27334d", highlightthickness=1
        )
        display.pack(fill="x", padx=22, pady=(0, 14))

        self.expression_label = tk.Label(
            display, text="",
            font=("Consolas", 12), anchor="e",
            fg=self.colors["muted"], bg=self.colors["display"]
        )
        self.expression_label.pack(fill="x", padx=18, pady=(12, 0))

        entry = tk.Entry(
            display, textvariable=self.display_var,
            font=("Consolas", 29, "bold"), justify="right",
            fg=self.colors["text"], bg=self.colors["display"],
            insertbackground=self.colors["text"],
            relief="flat", bd=0
        )
        entry.pack(fill="x", padx=18, pady=(3, 14), ipady=3)
        entry.focus_set()

        content = tk.Frame(self.root, bg=self.colors["bg"])
        content.pack(fill="both", expand=True, padx=22, pady=(0, 12))

        keypad = tk.Frame(content, bg=self.colors["bg"])
        keypad.pack(side="left", fill="both", expand=True)

        history_panel = tk.Frame(
            content, bg=self.colors["panel"], width=215
        )
        history_panel.pack(side="right", fill="y", padx=(16, 0))
        history_panel.pack_propagate(False)

        tk.Label(
            history_panel, text="HISTORY",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["text"], bg=self.colors["panel"]
        ).pack(anchor="w", padx=12, pady=(13, 8))

        self.history_list = tk.Listbox(
            history_panel, bg=self.colors["panel"],
            fg=self.colors["muted"], selectbackground="#33466c",
            selectforeground=self.colors["text"], relief="flat",
            borderwidth=0, highlightthickness=0,
            font=("Consolas", 10), activestyle="none"
        )
        self.history_list.pack(fill="both", expand=True, padx=8)
        self.history_list.bind("<Double-Button-1>", self._use_history)

        tk.Button(
            history_panel, text="Clear history",
            command=self._clear_history,
            bg="#29344b", fg=self.colors["text"],
            activebackground="#3b4965", activeforeground="white",
            relief="flat", bd=0, pady=8, cursor="hand2"
        ).pack(fill="x", padx=10, pady=10)

        # Each button: visible label, action, visual category.
        rows = [
            [("MC", "MC", "memory"), ("MR", "MR", "memory"),
             ("M+", "M+", "memory"), ("M−", "M-", "memory"),
             ("⌫", "BACK", "danger"), ("AC", "AC", "danger")],
            [("sin", "sin(", "function"), ("cos", "cos(", "function"),
             ("tan", "tan(", "function"), ("√", "sqrt(", "function"),
             ("x²", "^2", "function"), ("÷", "/", "operator")],
            [("asin", "asin(", "function"), ("acos", "acos(", "function"),
             ("atan", "atan(", "function"), ("ln", "ln(", "function"),
             ("log", "log(", "function"), ("×", "*", "operator")],
            [("(", "(", "function"), (")", ")", "function"),
             ("n!", "fact(", "function"), ("xʸ", "^", "function"),
             ("π", "pi", "function"), ("−", "-", "operator")],
            [("7", "7", "number"), ("8", "8", "number"),
             ("9", "9", "number"), ("%", "%", "function"),
             ("e", "e", "function"), ("+", "+", "operator")],
            [("4", "4", "number"), ("5", "5", "number"),
             ("6", "6", "number"), (".", ".", "number"),
             ("Ans", "ANS", "function"), ("=", "EQUALS", "equal")],
            [("1", "1", "number"), ("2", "2", "number"),
             ("3", "3", "number"), ("0", "0", "number"),
             ("1/x", "RECIP", "function"), ("±", "SIGN", "function")],
        ]

        style_map = {
            "number": (self.colors["number"], self.colors["text"]),
            "function": (self.colors["function"], "#c5d7ff"),
            "operator": (self.colors["operator"], "white"),
            "memory": ("#203a36", "#a7f3d0"),
            "danger": (self.colors["danger"], "white"),
            "equal": (self.colors["equal"], "white"),
        }

        for r, row in enumerate(rows):
            keypad.grid_rowconfigure(r, weight=1)
            for c, (label, action, kind) in enumerate(row):
                keypad.grid_columnconfigure(c, weight=1)
                bg, fg = style_map[kind]
                tk.Button(
                    keypad, text=label,
                    command=lambda a=action: self._dispatch(a),
                    font=("Segoe UI", 11, "bold"),
                    bg=bg, fg=fg, activebackground="#53698d",
                    activeforeground="white", relief="flat",
                    bd=0, cursor="hand2"
                ).grid(
                    row=r, column=c, sticky="nsew",
                    padx=3, pady=3, ipadx=2, ipady=8
                )

        footer = tk.Frame(self.root, bg=self.colors["bg"])
        footer.pack(fill="x", padx=23, pady=(0, 10))
        tk.Label(
            footer, textvariable=self.status_var,
            font=("Segoe UI", 9), fg=self.colors["muted"],
            bg=self.colors["bg"], anchor="w"
        ).pack(side="left")
        tk.Label(
            footer, text="Enter = Calculate   •   Esc = Clear   •   Backspace = Delete",
            font=("Segoe UI", 9), fg=self.colors["muted"],
            bg=self.colors["bg"], anchor="e"
        ).pack(side="right")

    def _bind_keys(self):
        self.root.bind("<Key>", self._on_key)
        self.root.bind("<Return>", lambda _e: self.calculate())
        self.root.bind("<KP_Enter>", lambda _e: self.calculate())
        self.root.bind("<Escape>", lambda _e: self.clear())
        self.root.bind("<BackSpace>", lambda _e: self.backspace())

    def _on_key(self, event):
        if event.keysym in {"Return", "KP_Enter", "Escape", "BackSpace"}:
            return
        if event.char and event.char in "0123456789.+-*/()%":
            self.append(event.char)
        elif event.char == "^":
            self.append("^")

    def _dispatch(self, action):
        handlers = {
            "AC": self.clear,
            "BACK": self.backspace,
            "EQUALS": self.calculate,
            "MC": self.memory_clear,
            "MR": self.memory_recall,
            "M+": lambda: self.memory_add(1),
            "M-": lambda: self.memory_add(-1),
            "ANS": self.answer_recall,
            "SIGN": self.toggle_sign,
            "RECIP": self.reciprocal,
        }
        if action in handlers:
            handlers[action]()
        else:
            self.append(action)

    def append(self, value):
        if self.display_var.get() == "Error":
            self.expression = ""
        # If a user enters a new digit after a completed result, start fresh.
        if self.expression == str(self.last_answer) and str(value).isdigit():
            self.expression = ""
        self.expression += str(value)
        self.display_var.set(self.expression or "0")
        self.expression_label.config(text="")
        self.status_var.set("Ready")

    def clear(self):
        self.expression = ""
        self.display_var.set("0")
        self.expression_label.config(text="")
        self.status_var.set("Cleared")

    def backspace(self):
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression or "0")

    @staticmethod
    def _format(value):
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("Result is not finite")
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"

    def calculate(self):
        raw = self.expression.strip()
        if not raw:
            return
        try:
            result = self._evaluate(raw)
            shown = self._format(result)
            self.history_list.insert(0, f"{raw} = {shown}")
            self.expression_label.config(text=f"{raw} =")
            self.expression = shown
            self.display_var.set(shown)
            self.last_answer = float(result)
            self.status_var.set("Calculation complete")
        except Exception as exc:
            self.display_var.set("Error")
            self.expression_label.config(text=raw)
            self.status_var.set(f"Check expression: {exc}")
            self.expression = ""

    def _evaluate(self, raw):
        expr = raw.replace("×", "*").replace("÷", "/")
        expr = expr.replace("−", "-").replace("π", "pi").replace("^", "**")
        # 25% becomes 25/100. For example, 50% = 0.5.
        expr = re.sub(r"(?<=[0-9.)])%", "/100", expr)

        degrees = self.angle_mode.get() == "DEG"

        def angle_in(x):
            return math.radians(x) if degrees else x

        def angle_out(x):
            return math.degrees(x) if degrees else x

        functions = {
            "sin": lambda x: math.sin(angle_in(x)),
            "cos": lambda x: math.cos(angle_in(x)),
            "tan": lambda x: math.tan(angle_in(x)),
            "asin": lambda x: angle_out(math.asin(x)),
            "acos": lambda x: angle_out(math.acos(x)),
            "atan": lambda x: angle_out(math.atan(x)),
            "sqrt": math.sqrt,
            "ln": math.log,
            "log": math.log10,
            "fact": self._factorial,
            "abs": abs,
            "exp": math.exp,
        }
        constants = {"pi": math.pi, "e": math.e}

        tree = ast.parse(expr, mode="eval")

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.Name):
                if node.id in constants:
                    return constants[node.id]
                raise ValueError(f"Unknown name: {node.id}")
            if isinstance(node, ast.BinOp):
                a, b = visit(node.left), visit(node.right)
                ops = {
                    ast.Add: operator.add, ast.Sub: operator.sub,
                    ast.Mult: operator.mul, ast.Div: operator.truediv,
                    ast.Pow: operator.pow, ast.Mod: operator.mod,
                }
                fn = ops.get(type(node.op))
                if fn is None:
                    raise ValueError("Operator not supported")
                if isinstance(node.op, ast.Pow) and abs(b) > 1000:
                    raise ValueError("Exponent too large")
                return fn(a, b)
            if isinstance(node, ast.UnaryOp):
                value = visit(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +value
                if isinstance(node.op, ast.USub):
                    return -value
                raise ValueError("Unary operator not supported")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id
                if name not in functions or node.keywords or len(node.args) != 1:
                    raise ValueError("Function or arguments not supported")
                return functions[name](visit(node.args[0]))
            raise ValueError("Expression not allowed")

        result = visit(tree)
        if isinstance(result, complex) or not math.isfinite(float(result)):
            raise ValueError("Result is outside the supported range")
        return result

    @staticmethod
    def _factorial(value):
        if value < 0 or not float(value).is_integer():
            raise ValueError("Factorial requires a non-negative integer")
        if value > 170:
            raise ValueError("Number too large for factorial")
        return math.factorial(int(value))

    def _current_value(self):
        try:
            return float(self._evaluate(self.expression))
        except Exception:
            try:
                return float(self.display_var.get())
            except ValueError:
                return 0.0

    def memory_clear(self):
        self.memory = 0.0
        self.status_var.set("Memory cleared")

    def memory_recall(self):
        self.append(self._format(self.memory))
        self.status_var.set("Memory recalled")

    def memory_add(self, sign):
        self.memory += sign * self._current_value()
        self.status_var.set(f"Memory: {self._format(self.memory)}")

    def answer_recall(self):
        self.append(self._format(self.last_answer))

    def reciprocal(self):
        """Append the reciprocal function around the current expression."""
        current = self.expression.strip()
        if not current:
            current = self.display_var.get().strip()
        if not current or current == "Error":
            self.status_var.set("Enter a number or expression first")
            return
        self.expression = f"1/({current})"
        self.display_var.set(self.expression)
        self.expression_label.config(text="Reciprocal")
        self.status_var.set("Reciprocal: 1 ÷ expression")

    def toggle_sign(self):
        if not self.expression:
            self.append("-")
        elif self.expression.startswith("-"):
            self.expression = self.expression[1:]
            self.display_var.set(self.expression or "0")
        else:
            self.expression = "-" + self.expression
            self.display_var.set(self.expression)

    def _clear_history(self):
        self.history_list.delete(0, tk.END)

    def _use_history(self, _event):
        selected = self.history_list.curselection()
        if selected:
            item = self.history_list.get(selected[0])
            if " = " in item:
                answer = item.rsplit(" = ", 1)[1]
                self.expression = answer
                self.display_var.set(answer)
                self.expression_label.config(text="Recalled result")


if __name__ == "__main__":
    root = tk.Tk()
    ScientificCalculator(root)
    root.mainloop()
