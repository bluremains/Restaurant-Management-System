from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from services.restaurant_service import RestaurantService
from models.discount import NoDiscount, PercentageDiscount, FixedAmountDiscount
from exceptions import RestaurantError


class RestaurantApp(tk.Tk):
    """Lilium restaurant POS interface.

    GUI layer only. Business rules and data operations are delegated to
    RestaurantService and the existing model classes.
    """

    BG = "#F5EEE6"
    SURFACE = "#FFFDFC"
    SURFACE_2 = "#EFE3D5"
    SIDEBAR = "#3D2B22"
    SIDEBAR_2 = "#50382C"
    BROWN = "#7B513A"
    BROWN_DARK = "#5E3C2C"
    GOLD = "#B88A58"
    TEXT = "#2D211B"
    MUTED = "#806F63"
    BORDER = "#E3D5C7"
    GREEN = "#5C7A62"
    RED = "#A65A50"
    AMBER = "#B9844D"
    WHITE = "#FFFFFF"

    BRAND = "LILIUM"
    SUBTITLE = "Dining • Coffee • Moments"

    def __init__(self) -> None:
        super().__init__()

        self.title("Lilium • Restaurant Management")
        self.geometry("1380x820")
        self.minsize(1120, 700)
        self.configure(bg=self.BG)

        self.service = RestaurantService()
        self.restaurant = self.service.load()

        self.current_page = "Dashboard"
        self.pages = {}
        self.nav_buttons = {}
        self.selected_order_id = None

        self._configure_style()
        self._build_shell()
        self._build_pages()
        self.show_page("Dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ================================================================
    # STYLE
    # ================================================================
    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            rowheight=42,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=self.SURFACE_2,
            foreground=self.BROWN_DARK,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(12, 11),
        )
        style.map(
            "Treeview",
            background=[("selected", "#E8D5C2")],
            foreground=[("selected", self.TEXT)],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.SURFACE,
            background=self.SURFACE,
            foreground=self.TEXT,
            padding=8,
        )
        style.configure(
            "TEntry",
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            padding=8,
        )

    # ================================================================
    # SHELL
    # ================================================================
    def _build_shell(self) -> None:
        self.sidebar = tk.Frame(self, bg=self.SIDEBAR, width=245)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_brand()

        nav_title = tk.Label(
            self.sidebar,
            text="RESTAURANT",
            bg=self.SIDEBAR,
            fg="#BCA99B",
            font=("Segoe UI", 8, "bold"),
        )
        nav_title.pack(anchor="w", padx=24, pady=(0, 8))

        nav = [
            ("Dashboard", "⌂"),
            ("POS / New Order", "＋"),
            ("Menu", "✦"),
            ("Tables", "▦"),
            ("Customers", "♙"),
            ("Orders", "▤"),
        ]

        for name, icon in nav:
            self._create_nav_button(name, icon)

        bottom = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        bottom.pack(side="bottom", fill="x", padx=20, pady=20)

        tk.Frame(bottom, bg="#62483A", height=1).pack(fill="x", pady=(0, 14))
        tk.Label(
            bottom,
            text="●  System online",
            bg=self.SIDEBAR,
            fg="#AFC4A8",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            bottom,
            text="Lilium • Local data",
            bg=self.SIDEBAR,
            fg="#9C887B",
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(4, 0))

        self.topbar = tk.Frame(self.content, bg=self.SURFACE, height=78)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = tk.Label(
            self.topbar,
            text="Dashboard",
            bg=self.SURFACE,
            fg=self.TEXT,
            font=("Georgia", 21, "bold"),
        )
        self.page_title.pack(side="left", padx=30)

        self.clock_label = tk.Label(
            self.topbar,
            text="",
            bg=self.SURFACE,
            fg=self.MUTED,
            font=("Segoe UI", 9),
        )
        self.clock_label.pack(side="right", padx=30)
        self._update_clock()

        self.page_area = tk.Frame(self.content, bg=self.BG)
        self.page_area.pack(fill="both", expand=True, padx=28, pady=24)

    def _build_brand(self) -> None:
        brand = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(23, 30))

        canvas = tk.Canvas(
            brand, width=58, height=58, bg=self.SIDEBAR,
            highlightthickness=0
        )
        canvas.pack(side="left")
        self._draw_lily(canvas, 29, 30, 1.0, "#D8B79B", "#E8D4C2")

        text_box = tk.Frame(brand, bg=self.SIDEBAR)
        text_box.pack(side="left", padx=11)

        tk.Label(
            text_box, text=self.BRAND, bg=self.SIDEBAR, fg="#FFF9F3",
            font=("Georgia", 18, "bold")
        ).pack(anchor="w")
        tk.Label(
            text_box, text=self.SUBTITLE, bg=self.SIDEBAR, fg="#BCA99B",
            font=("Segoe UI", 7)
        ).pack(anchor="w", pady=(2, 0))

    def _draw_lily(self, canvas, cx, cy, scale=1.0, petal="#D8B79B", center="#E8D4C2"):
        r = 15 * scale
        for angle in range(0, 360, 60):
            import math
            a = math.radians(angle)
            px = cx + math.cos(a) * r * 0.52
            py = cy + math.sin(a) * r * 0.52
            canvas.create_oval(
                px-r*0.45, py-r*0.75, px+r*0.45, py+r*0.75,
                fill=petal, outline=""
            )
        canvas.create_oval(
            cx-r*0.28, cy-r*0.28, cx+r*0.28, cy+r*0.28,
            fill=center, outline=""
        )

    def _create_nav_button(self, name: str, icon: str) -> None:
        button = tk.Button(
            self.sidebar,
            text=f"  {icon}   {name}",
            command=lambda n=name: self.show_page(n),
            anchor="w",
            bd=0,
            relief="flat",
            bg=self.SIDEBAR,
            fg="#CBBBAF",
            activebackground=self.SIDEBAR_2,
            activeforeground="#FFF9F3",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=13,
            cursor="hand2",
        )
        button.pack(fill="x", padx=12, pady=3)
        self.nav_buttons[name] = button

    def _update_clock(self) -> None:
        self.clock_label.config(
            text=datetime.now().strftime("%A, %d %B %Y   •   %I:%M %p")
        )
        self.after(1000, self._update_clock)

    # ================================================================
    # PAGE MANAGEMENT
    # ================================================================
    def _build_pages(self) -> None:
        self.pages["Dashboard"] = tk.Frame(self.page_area, bg=self.BG)
        self.pages["POS / New Order"] = tk.Frame(self.page_area, bg=self.BG)
        self.pages["Menu"] = tk.Frame(self.page_area, bg=self.BG)
        self.pages["Tables"] = tk.Frame(self.page_area, bg=self.BG)
        self.pages["Customers"] = tk.Frame(self.page_area, bg=self.BG)
        self.pages["Orders"] = tk.Frame(self.page_area, bg=self.BG)

        self._build_dashboard()
        self._build_pos()
        self._build_menu()
        self._build_tables()
        self._build_customers()
        self._build_orders()

    def show_page(self, name: str) -> None:
        for page in self.pages.values():
            page.pack_forget()

        self.pages[name].pack(fill="both", expand=True)
        self.current_page = name

        display_name = "Point of Sale" if name == "POS / New Order" else name
        self.page_title.config(text=display_name)

        for page_name, button in self.nav_buttons.items():
            if page_name == name:
                button.config(bg=self.BROWN, fg="#FFF9F3")
            else:
                button.config(bg=self.SIDEBAR, fg="#CBBBAF")

        self.refresh_all()

    # ================================================================
    # COMMON UI
    # ================================================================
    def _clear(self, frame: tk.Widget) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _card(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=self.SURFACE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
            **kwargs,
        )

    def _button(self, parent, text, command, primary=False, danger=False,
                width=None, compact=False):
        if primary:
            bg, fg, active = self.BROWN, self.WHITE, self.BROWN_DARK
        elif danger:
            bg, fg, active = "#F4E2DF", self.RED, "#EBD0CC"
        else:
            bg, fg, active = self.SURFACE, self.TEXT, self.SURFACE_2

        button = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=active,
            activeforeground=fg if not primary else self.WHITE,
            bd=0, relief="flat",
            font=("Segoe UI", 9, "bold"),
            padx=13 if not compact else 9,
            pady=9 if not compact else 6,
            cursor="hand2",
        )
        if width:
            button.config(width=width)
        return button

    def _section_title(self, parent, title, subtitle=""):
        tk.Label(
            parent, text=title, bg=self.BG, fg=self.TEXT,
            font=("Georgia", 18, "bold")
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                parent, text=subtitle, bg=self.BG, fg=self.MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=(4, 0))

    def _pill(self, parent, text, bg, fg, padx=9):
        return tk.Label(
            parent, text=text, bg=bg, fg=fg,
            font=("Segoe UI", 8, "bold"), padx=padx, pady=4
        )

    def _stat_card(self, parent, title, value, symbol):
        card = self._card(parent)
        card.pack(side="left", fill="both", expand=True, padx=5)

        inner = tk.Frame(card, bg=self.SURFACE)
        inner.pack(fill="both", expand=True, padx=17, pady=15)

        icon = tk.Label(
            inner, text=symbol, bg=self.SURFACE_2, fg=self.BROWN,
            font=("Georgia", 16, "bold"), width=3, pady=7
        )
        icon.pack(side="left")

        text = tk.Frame(inner, bg=self.SURFACE)
        text.pack(side="left", padx=13)

        tk.Label(
            text, text=title.upper(), bg=self.SURFACE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        tk.Label(
            text, text=value, bg=self.SURFACE, fg=self.TEXT,
            font=("Georgia", 17, "bold")
        ).pack(anchor="w", pady=(3, 0))

    def _info(self, message):
        messagebox.showinfo("Lilium", message)

    def _error(self, message):
        messagebox.showerror("Lilium", message)

    def _confirm(self, message):
        return messagebox.askyesno("Lilium", message)

    def _selected_id(self, tree):
        selection = tree.selection()
        if not selection:
            self._error("Please select a row first.")
            return None
        return int(selection[0])

    # ================================================================
    # DASHBOARD
    # ================================================================
    def _build_dashboard(self):
        page = self.pages["Dashboard"]

        hero = tk.Frame(page, bg=self.BG)
        hero.pack(fill="x", pady=(0, 18))

        left = tk.Frame(hero, bg=self.BG)
        left.pack(side="left")
        tk.Label(
            left, text="WELCOME TO LILIUM", bg=self.BG, fg=self.BROWN,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        tk.Label(
            left, text="A beautiful day to serve.", bg=self.BG, fg=self.TEXT,
            font=("Georgia", 23, "bold")
        ).pack(anchor="w", pady=(3, 0))
        tk.Label(
            left, text="Your restaurant at a glance.", bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))

        self.dashboard_cards = tk.Frame(page, bg=self.BG)
        self.dashboard_cards.pack(fill="x", pady=(0, 20))

        lower = tk.Frame(page, bg=self.BG)
        lower.pack(fill="both", expand=True)

        self.dashboard_left = self._card(lower)
        self.dashboard_left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.dashboard_right = self._card(lower, width=325)
        self.dashboard_right.pack(side="right", fill="y", padx=(8, 0))
        self.dashboard_right.pack_propagate(False)

    def _refresh_dashboard(self):
        self._clear(self.dashboard_cards)
        stats = self.restaurant.dashboard_stats()

        cards = [
            ("Revenue", f"${stats['Total Revenue']:,.2f}", "₤"),
            ("Open Orders", str(stats["Open Orders"]), "◌"),
            ("Available Tables", str(stats["Available Tables"]), "⌂"),
            ("Customers", str(stats["Total Customers"]), "♙"),
        ]
        for data in cards:
            self._stat_card(self.dashboard_cards, *data)

        self._clear(self.dashboard_left)
        tk.Label(
            self.dashboard_left, text="Today at Lilium",
            bg=self.SURFACE, fg=self.TEXT, font=("Georgia", 15, "bold")
        ).pack(anchor="w", padx=22, pady=(21, 3))
        tk.Label(
            self.dashboard_left, text="A quick view of your restaurant activity.",
            bg=self.SURFACE, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=22)

        activity = [
            ("Tables occupied", stats["Occupied Tables"], stats["Total Tables"]),
            ("Menu available", stats["Available Menu Items"], stats["Total Menu Items"]),
            ("Paid orders", stats["Paid Orders"],
             stats["Paid Orders"] + stats["Open Orders"]),
        ]

        for label, value, total in activity:
            row = tk.Frame(self.dashboard_left, bg=self.SURFACE)
            row.pack(fill="x", padx=22, pady=(19, 0))
            tk.Label(
                row, text=label, bg=self.SURFACE, fg=self.TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left")
            tk.Label(
                row, text=str(value), bg=self.SURFACE, fg=self.BROWN,
                font=("Georgia", 12, "bold")
            ).pack(side="right")

            bar = tk.Frame(self.dashboard_left, bg=self.SURFACE_2, height=8)
            bar.pack(fill="x", padx=22, pady=(8, 0))
            ratio = min(1, value / total) if total else 0
            fill = tk.Frame(bar, bg=self.BROWN, height=8)
            fill.place(relwidth=ratio, relheight=1)

        self._clear(self.dashboard_right)
        tk.Label(
            self.dashboard_right, text="QUICK ACTIONS", bg=self.SURFACE,
            fg=self.BROWN, font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=22, pady=(21, 5))
        tk.Label(
            self.dashboard_right, text="Keep service moving",
            bg=self.SURFACE, fg=self.TEXT, font=("Georgia", 15, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self._button(
            self.dashboard_right, "＋  Start a new order",
            lambda: self._new_order_dialog(), primary=True
        ).pack(fill="x", padx=22, pady=5)

        self._button(
            self.dashboard_right, "✦  Open menu",
            lambda: self.show_page("Menu")
        ).pack(fill="x", padx=22, pady=5)

        self._button(
            self.dashboard_right, "▦  View tables",
            lambda: self.show_page("Tables")
        ).pack(fill="x", padx=22, pady=5)

        self._button(
            self.dashboard_right, "♙  Add customer",
            lambda: self._add_customer_dialog()
        ).pack(fill="x", padx=22, pady=5)

    # ================================================================
    # POS
    # ================================================================
    def _build_pos(self):
        page = self.pages["POS / New Order"]

        top = tk.Frame(page, bg=self.BG)
        top.pack(fill="x", pady=(0, 15))

        left = tk.Frame(top, bg=self.BG)
        left.pack(side="left")
        tk.Label(
            left, text="POINT OF SALE", bg=self.BG, fg=self.BROWN,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        tk.Label(
            left, text="Create an order", bg=self.BG, fg=self.TEXT,
            font=("Georgia", 21, "bold")
        ).pack(anchor="w", pady=(2, 0))

        self.pos_order_var = tk.StringVar(value="No open order selected")
        self._pill(
            top, self.pos_order_var.get(), self.SURFACE_2, self.BROWN
        ).pack(side="right", pady=8)

        body = tk.Frame(page, bg=self.BG)
        body.pack(fill="both", expand=True)

        self.pos_left = tk.Frame(body, bg=self.BG)
        self.pos_left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.pos_right = self._card(body, width=355)
        self.pos_right.pack(side="right", fill="y")
        self.pos_right.pack_propagate(False)

        # Order selector
        selector = self._card(self.pos_left)
        selector.pack(fill="x", pady=(0, 10))

        tk.Label(
            selector, text="CURRENT ORDER", bg=self.SURFACE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=15, pady=12)

        self.pos_order_combo_var = tk.StringVar()
        self.pos_order_combo = ttk.Combobox(
            selector, textvariable=self.pos_order_combo_var,
            state="readonly", width=28
        )
        self.pos_order_combo.pack(side="left", padx=5, pady=8)
        self.pos_order_combo.bind("<<ComboboxSelected>>", self._pos_select_order)

        self._button(
            selector, "＋ New", self._new_order_dialog, primary=True, compact=True
        ).pack(side="right", padx=10, pady=7)

        # Search and categories
        tools = tk.Frame(self.pos_left, bg=self.BG)
        tools.pack(fill="x", pady=(0, 10))

        search = self._card(tools)
        search.pack(side="left", fill="x", expand=True)

        tk.Label(
            search, text="⌕", bg=self.SURFACE, fg=self.BROWN,
            font=("Georgia", 17)
        ).pack(side="left", padx=(12, 4))
        self.pos_search_var = tk.StringVar()
        entry = tk.Entry(
            search, textvariable=self.pos_search_var, bd=0,
            bg=self.SURFACE, fg=self.TEXT, insertbackground=self.TEXT,
            font=("Segoe UI", 10)
        )
        entry.pack(side="left", fill="x", expand=True, ipady=9)
        entry.bind("<KeyRelease>", lambda e: self._refresh_pos_menu())

        self.pos_category_var = tk.StringVar(value="All")
        self.pos_categories = tk.Frame(self.pos_left, bg=self.BG)
        self.pos_categories.pack(fill="x", pady=(0, 10))

        # Scrollable menu area
        menu_shell = self._card(self.pos_left)
        menu_shell.pack(fill="both", expand=True)

        self.pos_canvas = tk.Canvas(
            menu_shell, bg=self.SURFACE, highlightthickness=0
        )
        scroll = ttk.Scrollbar(
            menu_shell, orient="vertical", command=self.pos_canvas.yview
        )
        self.pos_canvas.configure(yscrollcommand=scroll.set)
        self.pos_canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.pos_menu_frame = tk.Frame(self.pos_canvas, bg=self.SURFACE)
        self.pos_window = self.pos_canvas.create_window(
            (0, 0), window=self.pos_menu_frame, anchor="nw"
        )
        self.pos_menu_frame.bind(
            "<Configure>",
            lambda e: self.pos_canvas.configure(
                scrollregion=self.pos_canvas.bbox("all")
            )
        )
        self.pos_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.pos_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            if self.current_page == "POS / New Order" else None
        )
        self.pos_canvas.bind(
            "<Configure>",
            lambda e: self.pos_canvas.itemconfigure(
                self.pos_window, width=e.width
            )
        )

        self._build_pos_cart()

    def _build_pos_cart(self):
        self._clear(self.pos_right)

        header = tk.Frame(self.pos_right, bg=self.SURFACE)
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            header, text="YOUR ORDER", bg=self.SURFACE, fg=self.BROWN,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w")
        self.pos_cart_title = tk.Label(
            header, text="Select an open order", bg=self.SURFACE,
            fg=self.TEXT, font=("Georgia", 16, "bold")
        )
        self.pos_cart_title.pack(anchor="w", pady=(3, 0))

        self.pos_cart_info = tk.Label(
            header, text="", bg=self.SURFACE, fg=self.MUTED,
            font=("Segoe UI", 8)
        )
        self.pos_cart_info.pack(anchor="w", pady=(3, 0))

        self.pos_cart_items = tk.Frame(self.pos_right, bg=self.SURFACE)
        self.pos_cart_items.pack(fill="both", expand=True, padx=20)

        summary = tk.Frame(self.pos_right, bg=self.SURFACE_2)
        summary.pack(fill="x", padx=15, pady=15)

        self.pos_subtotal_label = tk.Label(
            summary, text="Subtotal   $0.00", bg=self.SURFACE_2,
            fg=self.MUTED, font=("Segoe UI", 9)
        )
        self.pos_subtotal_label.pack(anchor="w", padx=15, pady=(12, 3))

        self.pos_discount_label = tk.Label(
            summary, text="Discount   —", bg=self.SURFACE_2,
            fg=self.MUTED, font=("Segoe UI", 9)
        )
        self.pos_discount_label.pack(anchor="w", padx=15, pady=3)

        self.pos_total_label = tk.Label(
            summary, text="TOTAL   $0.00", bg=self.SURFACE_2,
            fg=self.BROWN_DARK, font=("Georgia", 17, "bold")
        )
        self.pos_total_label.pack(anchor="w", padx=15, pady=(5, 13))

        self.pos_checkout = self._button(
            self.pos_right, "CHECKOUT  →", self._checkout_pos,
            primary=True
        )
        self.pos_checkout.pack(fill="x", padx=20, pady=(0, 20), ipady=5)

    def _menu_symbol(self, item):
        category = item.category.lower()
        name = item.name.lower()
        if "drink" in category or "juice" in name or "coffee" in name:
            return "☕"
        if "dessert" in category or "cake" in name or "sweet" in name:
            return "🍰"
        if "pizza" in name:
            return "◉"
        if "burger" in name or "sandwich" in name:
            return "◈"
        if "salad" in category:
            return "❋"
        return "✦"

    def _refresh_pos_categories(self):
        self._clear(self.pos_categories)
        categories = sorted({i.category for i in self.restaurant.menu.values()})
        values = ["All"] + categories
        for category in values:
            selected = category == self.pos_category_var.get()
            button = tk.Button(
                self.pos_categories, text=category,
                command=lambda c=category: self._set_pos_category(c),
                bg=self.BROWN if selected else self.SURFACE,
                fg=self.WHITE if selected else self.MUTED,
                activebackground=self.BROWN_DARK if selected else self.SURFACE_2,
                activeforeground=self.WHITE if selected else self.TEXT,
                bd=0, relief="flat", padx=14, pady=7,
                font=("Segoe UI", 8, "bold"), cursor="hand2"
            )
            button.pack(side="left", padx=(0, 7))

    def _set_pos_category(self, category):
        self.pos_category_var.set(category)
        self._refresh_pos_menu()

    def _refresh_pos_menu(self):
        self._refresh_pos_categories()
        self._clear(self.pos_menu_frame)

        keyword = self.pos_search_var.get().strip().lower()
        category = self.pos_category_var.get()

        items = [
            i for i in self.restaurant.menu.values()
            if i.available
            and (category == "All" or i.category == category)
            and (not keyword or keyword in i.name.lower()
                 or keyword in i.category.lower())
        ]

        if not items:
            tk.Label(
                self.pos_menu_frame,
                text="No dishes found",
                bg=self.SURFACE, fg=self.MUTED,
                font=("Georgia", 14)
            ).pack(pady=60)
            return

        columns = 3
        for index, item in enumerate(items):
            card = tk.Frame(
                self.pos_menu_frame, bg="#FFFAF5",
                highlightbackground=self.BORDER, highlightthickness=1
            )
            row, col = divmod(index, columns)
            card.grid(
                row=row, column=col, sticky="nsew",
                padx=(12 if col == 0 else 6, 6),
                pady=(12 if row == 0 else 6, 6)
            )

            visual = tk.Canvas(
                card, width=74, height=74, bg=self.SURFACE_2,
                highlightthickness=0
            )
            visual.pack(pady=(12, 7))
            self._draw_lily(visual, 37, 37, 0.72, "#C9A88D", "#A77A58")
            visual.create_text(
                37, 39, text=self._menu_symbol(item),
                fill=self.BROWN_DARK, font=("Segoe UI", 18, "bold")
            )

            tk.Label(
                card, text=item.name, bg="#FFFAF5", fg=self.TEXT,
                font=("Georgia", 11, "bold")
            ).pack(anchor="w", padx=12)

            tk.Label(
                card, text=item.category, bg="#FFFAF5", fg=self.MUTED,
                font=("Segoe UI", 8)
            ).pack(anchor="w", padx=12, pady=(2, 5))

            bottom = tk.Frame(card, bg="#FFFAF5")
            bottom.pack(fill="x", padx=12, pady=(2, 12))

            tk.Label(
                bottom, text=f"${item.price:,.2f}", bg="#FFFAF5",
                fg=self.BROWN, font=("Georgia", 11, "bold")
            ).pack(side="left")

            add = self._button(
                bottom, "+ Add", lambda i=item.item_id: self._pos_add_item(i),
                primary=True, compact=True
            )
            add.pack(side="right")

        for col in range(columns):
            self.pos_menu_frame.columnconfigure(col, weight=1)

    def _open_orders(self):
        return [o for o in self.restaurant.filter_orders("Open")]

    def _refresh_pos_order_choices(self):
        orders = self._open_orders()
        values = [
            f"#{o.order_id} • Table {o.table_id}"
            for o in orders
        ]
        self.pos_order_combo["values"] = values

        if self.selected_order_id is not None:
            found = next(
                (o for o in orders if o.order_id == self.selected_order_id), None
            )
            if found:
                self.pos_order_combo_var.set(
                    f"#{found.order_id} • Table {found.table_id}"
                )
            else:
                self.selected_order_id = None

        if self.selected_order_id is None and values:
            self.selected_order_id = orders[0].order_id
            self.pos_order_combo_var.set(values[0])

    def _pos_select_order(self, event=None):
        text = self.pos_order_combo_var.get()
        if text:
            try:
                self.selected_order_id = int(text.split("#")[1].split()[0])
            except (ValueError, IndexError):
                self.selected_order_id = None
        self._refresh_pos_cart()

    def _pos_add_item(self, item_id):
        if self.selected_order_id is None:
            self._error("Create or select an open order first.")
            return
        try:
            self.restaurant.add_item_to_order(
                self.selected_order_id, item_id, 1
            )
            self._refresh_pos_cart()
            self._refresh_orders()
            self._refresh_dashboard()
        except RestaurantError as e:
            self._error(str(e))

    def _refresh_pos_cart(self):
        self._refresh_pos_order_choices()
        self._clear(self.pos_cart_items)

        if self.selected_order_id is None:
            self.pos_cart_title.config(text="Select an open order")
            self.pos_cart_info.config(text="Your selected items will appear here.")
            self.pos_subtotal_label.config(text="Subtotal   $0.00")
            self.pos_discount_label.config(text="Discount   —")
            self.pos_total_label.config(text="TOTAL   $0.00")
            return

        try:
            order = self.restaurant.get_order(self.selected_order_id)
        except RestaurantError:
            self.selected_order_id = None
            return

        customer = "Walk-in"
        if order.customer_id and order.customer_id in self.restaurant.customers:
            customer = self.restaurant.customers[order.customer_id].name

        self.pos_cart_title.config(text=f"Order #{order.order_id}")
        self.pos_cart_info.config(
            text=f"Table {order.table_id}  •  {customer}  •  {order.status}"
        )

        if not order.items:
            tk.Label(
                self.pos_cart_items,
                text="Your order is empty",
                bg=self.SURFACE, fg=self.MUTED,
                font=("Georgia", 12)
            ).pack(pady=45)
        else:
            for line in order.items:
                row = tk.Frame(
                    self.pos_cart_items, bg=self.SURFACE,
                    highlightbackground=self.BORDER, highlightthickness=1
                )
                row.pack(fill="x", pady=4)

                left = tk.Frame(row, bg=self.SURFACE)
                left.pack(side="left", fill="x", expand=True, padx=10, pady=9)

                tk.Label(
                    left, text=line.menu_item.name, bg=self.SURFACE,
                    fg=self.TEXT, font=("Segoe UI", 9, "bold")
                ).pack(anchor="w")
                tk.Label(
                    left, text=f"{line.quantity} × ${line.menu_item.price:.2f}",
                    bg=self.SURFACE, fg=self.MUTED, font=("Segoe UI", 8)
                ).pack(anchor="w", pady=(2, 0))

                tk.Label(
                    row, text=f"${line.subtotal:.2f}", bg=self.SURFACE,
                    fg=self.BROWN, font=("Georgia", 10, "bold")
                ).pack(side="right", padx=(5, 3))

                remove = tk.Button(
                    row, text="×",
                    command=lambda i=line.menu_item.item_id:
                    self._pos_remove_item(i),
                    bg=self.SURFACE, fg=self.RED,
                    activebackground="#F4E2DF", bd=0,
                    font=("Segoe UI", 11, "bold"), cursor="hand2"
                )
                remove.pack(side="right", padx=5)

        subtotal = order.calculate_subtotal()
        total = order.calculate_total()
        discount_text = order.discount.describe()

        self.pos_subtotal_label.config(text=f"Subtotal   ${subtotal:,.2f}")
        self.pos_discount_label.config(text=f"Discount   {discount_text}")
        self.pos_total_label.config(text=f"TOTAL   ${total:,.2f}")

    def _pos_remove_item(self, item_id):
        if self.selected_order_id is None:
            return
        try:
            self.restaurant.remove_item_from_order(
                self.selected_order_id, item_id
            )
            self._refresh_pos_cart()
            self._refresh_orders()
        except RestaurantError as e:
            self._error(str(e))

    def _checkout_pos(self):
        if self.selected_order_id is None:
            self._error("Select an open order first.")
            return
        self._checkout_dialog(self.selected_order_id)

    # ================================================================
    # MENU MANAGEMENT
    # ================================================================
    def _build_menu(self):
        page = self.pages["Menu"]

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 15))
        self._section_title(
            header, "Menu Collection",
            "Manage the dishes and drinks available at Lilium."
        )
        self._button(
            header, "＋ Add Menu Item", self._add_menu_item_dialog, primary=True
        ).pack(side="right")

        toolbar = self._card(page)
        toolbar.pack(fill="x", pady=(0, 10))

        tk.Label(
            toolbar, text="⌕", bg=self.SURFACE, fg=self.BROWN,
            font=("Georgia", 16)
        ).pack(side="left", padx=(13, 4))

        self.menu_search_var = tk.StringVar()
        entry = tk.Entry(
            toolbar, textvariable=self.menu_search_var, bd=0,
            bg=self.SURFACE, fg=self.TEXT, font=("Segoe UI", 10)
        )
        entry.pack(side="left", fill="x", expand=True, ipady=9)
        entry.bind("<KeyRelease>", lambda e: self._refresh_menu())

        self.menu_avail_var = tk.StringVar(value="All")
        ttk.Combobox(
            toolbar, textvariable=self.menu_avail_var,
            values=["All", "Available", "Unavailable"],
            state="readonly", width=15
        ).pack(side="left", padx=10)
        self.menu_avail_var.trace_add("write", lambda *_: self._refresh_menu())

        self._button(
            toolbar, "Toggle availability", self._toggle_menu_item, compact=True
        ).pack(side="right", padx=8, pady=7)
        self._button(
            toolbar, "Delete", self._delete_menu_item, danger=True, compact=True
        ).pack(side="right", padx=(0, 8), pady=7)

        card = self._card(page)
        card.pack(fill="both", expand=True)
        self.menu_tree = self._tree(
            card,
            [("id", "ID", 60), ("name", "Item", 270), ("category", "Category", 160),
             ("price", "Price", 120), ("available", "Status", 150)]
        )

    def _refresh_menu(self):
        if not hasattr(self, "menu_tree"):
            return
        self.menu_tree.delete(*self.menu_tree.get_children())
        keyword = self.menu_search_var.get().strip()
        items = self.restaurant.search_menu(keyword) if keyword else list(
            self.restaurant.menu.values()
        )

        filt = self.menu_avail_var.get()
        if filt == "Available":
            items = [i for i in items if i.available]
        elif filt == "Unavailable":
            items = [i for i in items if not i.available]

        for item in items:
            self.menu_tree.insert(
                "", "end", iid=item.item_id,
                values=(
                    item.item_id, item.name, item.category,
                    f"${item.price:.2f}",
                    "●  Available" if item.available else "●  Unavailable"
                ),
                tags=("available" if item.available else "unavailable",)
            )

        self.menu_tree.tag_configure("available", foreground=self.GREEN)
        self.menu_tree.tag_configure("unavailable", foreground=self.RED)

    # ================================================================
    # TABLES
    # ================================================================
    def _build_tables(self):
        page = self.pages["Tables"]

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 15))
        self._section_title(
            header, "Tables",
            "See the dining room at a glance."
        )
        self._button(
            header, "＋ Add Table", self._add_table_dialog, primary=True
        ).pack(side="right")

        self.tables_grid = tk.Frame(page, bg=self.BG)
        self.tables_grid.pack(fill="both", expand=True)

    def _refresh_tables(self):
        if not hasattr(self, "tables_grid"):
            return
        self._clear(self.tables_grid)

        tables = list(self.restaurant.tables.values())
        if not tables:
            tk.Label(
                self.tables_grid, text="No tables yet",
                bg=self.BG, fg=self.MUTED, font=("Georgia", 16)
            ).pack(pady=80)
            return

        for index, table in enumerate(tables):
            row, col = divmod(index, 4)
            card = self._card(self.tables_grid)
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

            canvas = tk.Canvas(
                card, width=100, height=82, bg=self.SURFACE,
                highlightthickness=0
            )
            canvas.pack(pady=(15, 2))
            occupied = not table.is_available
            canvas.create_oval(
                23, 13, 77, 67,
                fill="#E7D7C7" if not occupied else "#E6C6C0",
                outline=""
            )
            canvas.create_text(
                50, 40, text=str(table.table_id),
                fill=self.BROWN_DARK if not occupied else self.RED,
                font=("Georgia", 20, "bold")
            )

            tk.Label(
                card, text=f"TABLE {table.table_id}",
                bg=self.SURFACE, fg=self.TEXT,
                font=("Segoe UI", 8, "bold")
            ).pack()
            tk.Label(
                card, text=f"{table.capacity} seats",
                bg=self.SURFACE, fg=self.MUTED,
                font=("Segoe UI", 9)
            ).pack(pady=(2, 4))

            if occupied:
                self._pill(card, "OCCUPIED", "#F4E2DF", self.RED).pack(pady=(0, 8))
                actions = tk.Frame(card, bg=self.SURFACE)
                actions.pack(pady=(0, 13))
                self._button(
                    actions, "Free",
                    lambda i=table.table_id: self._free_table_by_id(i),
                    compact=True
                ).pack(side="left", padx=3)
                self._button(
                    actions, "Delete",
                    lambda i=table.table_id: self._delete_table_by_id(i),
                    danger=True, compact=True
                ).pack(side="left", padx=3)
            else:
                self._pill(card, "AVAILABLE", "#E2ECE1", self.GREEN).pack(pady=(0, 8))

        for col in range(4):
            self.tables_grid.columnconfigure(col, weight=1)

    def _free_table_by_id(self, table_id):
        try:
            self.restaurant.get_table(table_id).free()
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    def _delete_table_by_id(self, table_id):
        if not self._confirm(f"Delete Table {table_id}?"):
            return
        try:
            self.restaurant.delete_table(table_id)
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    # ================================================================
    # CUSTOMERS
    # ================================================================
    def _build_customers(self):
        page = self.pages["Customers"]

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 15))
        self._section_title(
            header, "Guests",
            "Keep your Lilium customer list organized."
        )
        self._button(
            header, "＋ Add Customer", self._add_customer_dialog, primary=True
        ).pack(side="right")

        toolbar = self._card(page)
        toolbar.pack(fill="x", pady=(0, 10))
        tk.Label(
            toolbar, text="⌕", bg=self.SURFACE, fg=self.BROWN,
            font=("Georgia", 16)
        ).pack(side="left", padx=(13, 4))

        self.customer_search_var = tk.StringVar()
        entry = tk.Entry(
            toolbar, textvariable=self.customer_search_var, bd=0,
            bg=self.SURFACE, fg=self.TEXT, font=("Segoe UI", 10)
        )
        entry.pack(side="left", fill="x", expand=True, ipady=9)
        entry.bind("<KeyRelease>", lambda e: self._refresh_customers())

        self._button(
            toolbar, "Delete selected", self._delete_customer,
            danger=True, compact=True
        ).pack(side="right", padx=8, pady=7)

        card = self._card(page)
        card.pack(fill="both", expand=True)
        self.customers_tree = self._tree(
            card, [("id", "ID", 70), ("name", "Customer", 280), ("phone", "Phone", 240)]
        )

    def _refresh_customers(self):
        if not hasattr(self, "customers_tree"):
            return
        self.customers_tree.delete(*self.customers_tree.get_children())
        keyword = self.customer_search_var.get().strip()
        customers = (
            self.restaurant.search_customers(keyword)
            if keyword else list(self.restaurant.customers.values())
        )
        for customer in customers:
            self.customers_tree.insert(
                "", "end", iid=customer.customer_id,
                values=(
                    customer.customer_id, customer.name,
                    customer.phone or "—"
                )
            )

    # ================================================================
    # ORDERS
    # ================================================================
    def _build_orders(self):
        page = self.pages["Orders"]

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 15))
        self._section_title(
            header, "Orders",
            "Review orders, discounts and payments."
        )
        self._button(
            header, "＋ New Order", self._new_order_dialog, primary=True
        ).pack(side="right")

        filters = self._card(page)
        filters.pack(fill="x", pady=(0, 10))

        tk.Label(
            filters, text="STATUS", bg=self.SURFACE, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(15, 6), pady=12)

        self.order_status_var = tk.StringVar(value="All")
        combo = ttk.Combobox(
            filters, textvariable=self.order_status_var,
            values=["All", "Open", "Paid", "Cancelled"],
            state="readonly", width=13
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_orders())

        self._button(
            filters, "Add item", self._add_item_dialog, compact=True
        ).pack(side="right", padx=4, pady=7)
        self._button(
            filters, "Discount", self._apply_discount_dialog, compact=True
        ).pack(side="right", padx=4, pady=7)
        self._button(
            filters, "Checkout", self._checkout_dialog, primary=True, compact=True
        ).pack(side="right", padx=4, pady=7)
        self._button(
            filters, "Cancel", self._cancel_order, danger=True, compact=True
        ).pack(side="right", padx=4, pady=7)

        card = self._card(page)
        card.pack(fill="both", expand=True)
        self.orders_tree = self._tree(
            card,
            [("id", "Order", 90), ("table", "Table", 100),
             ("customer", "Customer", 200), ("status", "Status", 130),
             ("total", "Total", 130), ("created", "Created", 190)]
        )
        self.orders_tree.bind("<Double-1>", lambda e: self._show_order_details())

    def _refresh_orders(self):
        if not hasattr(self, "orders_tree"):
            return
        self.orders_tree.delete(*self.orders_tree.get_children())
        status = self.order_status_var.get()
        status = None if status == "All" else status

        for order in self.restaurant.filter_orders(status):
            customer_name = "Walk-in"
            if order.customer_id and order.customer_id in self.restaurant.customers:
                customer_name = self.restaurant.customers[order.customer_id].name

            self.orders_tree.insert(
                "", "end", iid=order.order_id,
                values=(
                    f"#{order.order_id}", f"Table {order.table_id}",
                    customer_name, order.status,
                    f"${order.calculate_total():.2f}", order.created_at
                ),
                tags=(order.status.lower(),)
            )

        self.orders_tree.tag_configure("open", foreground=self.BROWN)
        self.orders_tree.tag_configure("paid", foreground=self.GREEN)
        self.orders_tree.tag_configure("cancelled", foreground=self.RED)

    # ================================================================
    # TREEVIEW
    # ================================================================
    def _tree(self, parent, columns):
        frame = tk.Frame(parent, bg=self.SURFACE)
        frame.pack(fill="both", expand=True, padx=1, pady=1)

        names = [x[0] for x in columns]
        tree = ttk.Treeview(
            frame, columns=names, show="headings", selectmode="browse"
        )

        for key, heading, width in columns:
            tree.heading(key, text=heading)
            tree.column(key, width=width, minwidth=60, anchor="w")

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=10)
        return tree

    # ================================================================
    # DIALOGS
    # ================================================================
    def _dialog(self, title, width=480, height=340):
        win = tk.Toplevel(self)
        win.title(f"Lilium • {title}")
        win.geometry(f"{width}x{height}")
        win.resizable(False, False)
        win.configure(bg=self.BG)
        win.transient(self)
        win.grab_set()
        return win

    def _field(self, parent, label, row, default=""):
        tk.Label(
            parent, text=label, bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=row, column=0, sticky="w", padx=28, pady=(8, 4))

        entry = tk.Entry(
            parent, bd=0, bg=self.SURFACE, fg=self.TEXT,
            font=("Segoe UI", 10),
            highlightbackground=self.BORDER, highlightthickness=1,
            insertbackground=self.TEXT
        )
        entry.grid(
            row=row, column=1, sticky="ew",
            padx=(0, 28), pady=(8, 4), ipady=7
        )
        if default:
            entry.insert(0, default)
        return entry

    def _dialog_header(self, win, title, subtitle=""):
        tk.Label(
            win, text="LILIUM", bg=self.BG, fg=self.BROWN,
            font=("Segoe UI", 8, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=28, pady=(22, 0))
        tk.Label(
            win, text=title, bg=self.BG, fg=self.TEXT,
            font=("Georgia", 18, "bold")
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=28, pady=(2, 3))
        if subtitle:
            tk.Label(
                win, text=subtitle, bg=self.BG, fg=self.MUTED,
                font=("Segoe UI", 9)
            ).grid(row=2, column=0, columnspan=2, sticky="w", padx=28, pady=(0, 10))

    def _dialog_buttons(self, parent, save_command, cancel_command=None):
        bar = tk.Frame(parent, bg=self.BG)
        bar.grid(
            row=99, column=0, columnspan=2,
            sticky="ew", padx=28, pady=22
        )
        if cancel_command is None:
            cancel_command = parent.destroy
        self._button(bar, "Cancel", cancel_command).pack(side="right", padx=(8, 0))
        self._button(bar, "Save", save_command, primary=True).pack(side="right")

    # ================================================================
    # MENU ACTIONS
    # ================================================================
    def _add_menu_item_dialog(self):
        win = self._dialog("Add Menu Item", 520, 370)
        self._dialog_header(
            win, "New menu item",
            "Add a dish or drink to the Lilium collection."
        )
        name = self._field(win, "Item name", 3)
        category = self._field(win, "Category", 4, "Main")
        price = self._field(win, "Price", 5)

        def save():
            try:
                self.restaurant.add_menu_item(
                    name.get(), category.get(), float(price.get())
                )
                win.destroy()
                self._info("Menu item added successfully.")
                self.refresh_all()
            except (ValueError, TypeError):
                self._error("Please enter a valid price.")
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _delete_menu_item(self):
        item_id = self._selected_id(self.menu_tree)
        if item_id is None:
            return
        if not self._confirm("Delete the selected menu item?"):
            return
        try:
            self.restaurant.delete_menu_item(item_id)
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    def _toggle_menu_item(self):
        item_id = self._selected_id(self.menu_tree)
        if item_id is None:
            return
        try:
            item = self.restaurant.get_menu_item(item_id)
            if item.available:
                item.mark_unavailable()
            else:
                item.mark_available()
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    # ================================================================
    # TABLE ACTIONS
    # ================================================================
    def _add_table_dialog(self):
        win = self._dialog("Add Table", 480, 300)
        self._dialog_header(
            win, "Add restaurant table",
            "Choose how many guests this table can seat."
        )
        capacity = self._field(win, "Seating capacity", 3)

        def save():
            try:
                self.restaurant.add_table(int(capacity.get()))
                win.destroy()
                self.refresh_all()
            except (ValueError, TypeError):
                self._error("Capacity must be a whole number.")
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _delete_table(self):
        table_id = self._selected_id(self.tables_tree)
        if table_id is None:
            return
        if not self._confirm("Delete the selected table?"):
            return
        try:
            self.restaurant.delete_table(table_id)
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    def _free_table(self):
        table_id = self._selected_id(self.tables_tree)
        if table_id is None:
            return
        self._free_table_by_id(table_id)

    # ================================================================
    # CUSTOMER ACTIONS
    # ================================================================
    def _add_customer_dialog(self):
        win = self._dialog("Add Customer", 500, 330)
        self._dialog_header(
            win, "New customer",
            "Save a guest profile for faster future orders."
        )
        name = self._field(win, "Full name", 3)
        phone = self._field(win, "Phone", 4)

        def save():
            try:
                self.restaurant.add_customer(name.get(), phone.get())
                win.destroy()
                self.refresh_all()
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _delete_customer(self):
        customer_id = self._selected_id(self.customers_tree)
        if customer_id is None:
            return
        if not self._confirm("Delete the selected customer?"):
            return
        try:
            self.restaurant.delete_customer(customer_id)
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    # ================================================================
    # ORDER ACTIONS
    # ================================================================
    def _new_order_dialog(self):
        win = self._dialog("New Order", 520, 410)
        self._dialog_header(
            win, "Create new order",
            "Choose a table and, optionally, a returning guest."
        )

        table = self._field(win, "Table ID", 3)

        tk.Label(
            win, text="Customer", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=4, column=0, sticky="w", padx=28, pady=8)

        customer_var = tk.StringVar(value="Walk-in customer")
        choices = ["Walk-in customer"] + [
            f"{c.customer_id} — {c.name}"
            for c in self.restaurant.customers.values()
        ]
        customer_box = ttk.Combobox(
            win, textvariable=customer_var,
            values=choices, state="readonly"
        )
        customer_box.grid(
            row=4, column=1, sticky="ew",
            padx=(0, 28), pady=8
        )

        def save():
            try:
                customer_id = None
                selected = customer_var.get()
                if selected != "Walk-in customer":
                    customer_id = int(selected.split("—")[0].strip())

                order = self.restaurant.create_order(
                    int(table.get()), customer_id
                )
                self.selected_order_id = order.order_id
                win.destroy()
                self.show_page("POS / New Order")
            except (ValueError, TypeError):
                self._error("Table ID must be a whole number.")
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _add_item_dialog(self):
        order_id = self._selected_id(self.orders_tree)
        if order_id is None:
            return

        order = self.restaurant.get_order(order_id)
        if order.status != "Open":
            self._error("Only open orders can be changed.")
            return

        win = self._dialog("Add Item to Order", 540, 400)
        self._dialog_header(
            win, f"Add to Order #{order_id}",
            "Select an available menu item and quantity."
        )

        tk.Label(
            win, text="Menu item", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=3, column=0, sticky="w", padx=28, pady=10)

        available = [i for i in self.restaurant.menu.values() if i.available]
        item_var = tk.StringVar()
        values = [
            f"{i.item_id} — {i.name} (${i.price:.2f})"
            for i in available
        ]
        item_box = ttk.Combobox(
            win, textvariable=item_var,
            values=values, state="readonly"
        )
        item_box.grid(
            row=3, column=1, sticky="ew",
            padx=(0, 28), pady=10
        )

        qty = self._field(win, "Quantity", 4, "1")

        def save():
            try:
                item_id = int(item_var.get().split("—")[0].strip())
                self.restaurant.add_item_to_order(
                    order_id, item_id, int(qty.get())
                )
                win.destroy()
                self.refresh_all()
            except (ValueError, TypeError, IndexError):
                self._error(
                    "Please choose an item and enter a valid quantity."
                )
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _apply_discount_dialog(self):
        order_id = self._selected_id(self.orders_tree)
        if order_id is None:
            return

        order = self.restaurant.get_order(order_id)
        if order.status != "Open":
            self._error("Only open orders can receive a discount.")
            return

        win = self._dialog("Apply Discount", 520, 390)
        self._dialog_header(
            win, f"Discount • Order #{order_id}",
            "Apply one of the existing discount strategies."
        )

        kind_var = tk.StringVar(value="Percentage")
        tk.Label(
            win, text="Discount type", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=3, column=0, sticky="w", padx=28, pady=8)

        kind_box = ttk.Combobox(
            win, textvariable=kind_var,
            values=["No discount", "Percentage", "Fixed amount"],
            state="readonly"
        )
        kind_box.grid(
            row=3, column=1, sticky="ew",
            padx=(0, 28), pady=8
        )
        value = self._field(win, "Value", 4)

        def save():
            try:
                kind = kind_var.get()
                if kind == "No discount":
                    discount = NoDiscount()
                elif kind == "Percentage":
                    discount = PercentageDiscount(float(value.get()))
                else:
                    discount = FixedAmountDiscount(float(value.get()))

                self.restaurant.apply_discount(order_id, discount)
                win.destroy()
                self.refresh_all()
            except (ValueError, TypeError):
                self._error("Please enter a valid discount value.")
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, save)
        win.columnconfigure(1, weight=1)

    def _checkout_dialog(self, order_id=None):
        if order_id is None:
            order_id = self._selected_id(self.orders_tree)
        if order_id is None:
            return

        order = self.restaurant.get_order(order_id)
        if order.status != "Open":
            self._error("Only open orders can be checked out.")
            return

        total = order.calculate_total()
        win = self._dialog("Checkout", 520, 390)

        self._dialog_header(
            win, f"Checkout • Order #{order_id}",
            "Confirm payment to close the order."
        )

        tk.Label(
            win, text=f"${total:,.2f}", bg=self.BG, fg=self.BROWN,
            font=("Georgia", 29, "bold")
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=28, pady=(7, 0))

        tk.Label(
            win,
            text=f"Subtotal: ${order.calculate_subtotal():,.2f}  •  {order.discount.describe()}",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).grid(
            row=4, column=0, columnspan=2,
            sticky="w", padx=28, pady=(2, 14)
        )

        tk.Label(
            win, text="Payment method", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=5, column=0, sticky="w", padx=28, pady=5)

        method_var = tk.StringVar(value="Cash")
        ttk.Combobox(
            win, textvariable=method_var,
            values=["Cash", "Card"], state="readonly"
        ).grid(
            row=5, column=1, sticky="ew",
            padx=(0, 28), pady=5
        )

        def confirm():
            try:
                payment = self.restaurant.checkout_order(
                    order_id, method_var.get()
                )
                self.selected_order_id = None
                win.destroy()
                self._info(
                    f"Payment of ${payment.amount:,.2f} received by {payment.method}."
                )
                self.refresh_all()
            except RestaurantError as e:
                self._error(str(e))

        self._dialog_buttons(win, confirm)
        win.columnconfigure(1, weight=1)

    def _cancel_order(self):
        order_id = self._selected_id(self.orders_tree)
        if order_id is None:
            return
        if not self._confirm(f"Cancel Order #{order_id}?"):
            return
        try:
            self.restaurant.cancel_order(order_id)
            if self.selected_order_id == order_id:
                self.selected_order_id = None
            self.refresh_all()
        except RestaurantError as e:
            self._error(str(e))

    def _show_order_details(self):
        order_id = self._selected_id(self.orders_tree)
        if order_id is None:
            return

        order = self.restaurant.get_order(order_id)
        win = self._dialog(f"Order #{order_id}", 680, 560)

        tk.Label(
            win, text="LILIUM", bg=self.BG, fg=self.BROWN,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=28, pady=(23, 0))

        header = tk.Frame(win, bg=self.BG)
        header.pack(fill="x", padx=28, pady=(2, 10))

        tk.Label(
            header, text=f"Order #{order.order_id}",
            bg=self.BG, fg=self.TEXT,
            font=("Georgia", 20, "bold")
        ).pack(side="left")

        status_bg = self.GREEN if order.status == "Paid" else (
            self.RED if order.status == "Cancelled" else self.BROWN
        )
        self._pill(header, order.status.upper(), status_bg, self.WHITE).pack(
            side="right", pady=4
        )

        customer = "Walk-in"
        if order.customer_id and order.customer_id in self.restaurant.customers:
            customer = self.restaurant.customers[order.customer_id].name

        tk.Label(
            win, text=f"Table {order.table_id}   •   {customer}",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=28, pady=(0, 8))

        tree_frame = tk.Frame(win, bg=self.SURFACE)
        tree_frame.pack(fill="both", expand=True, padx=28, pady=8)

        tree = self._tree(
            tree_frame,
            [("item", "Item", 260), ("qty", "Qty", 70),
             ("price", "Unit Price", 110), ("subtotal", "Subtotal", 120)]
        )

        for line in order.items:
            tree.insert(
                "", "end",
                values=(
                    line.menu_item.name, line.quantity,
                    f"${line.menu_item.price:.2f}",
                    f"${line.subtotal:.2f}"
                )
            )

        summary = tk.Frame(win, bg=self.BG)
        summary.pack(fill="x", padx=28, pady=(0, 12))

        tk.Label(
            summary, text=f"Subtotal   ${order.calculate_subtotal():,.2f}",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="e")
        tk.Label(
            summary, text=order.discount.describe(),
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="e", pady=2)
        tk.Label(
            summary, text=f"TOTAL   ${order.calculate_total():,.2f}",
            bg=self.BG, fg=self.BROWN,
            font=("Georgia", 16, "bold")
        ).pack(anchor="e")

        self._button(
            win, "Close", win.destroy
        ).pack(anchor="e", padx=28, pady=(0, 20))

    # ================================================================
    # REFRESH / CLOSE
    # ================================================================
    def refresh_all(self):
        if hasattr(self, "menu_tree"):
            self._refresh_menu()
        if hasattr(self, "tables_grid"):
            self._refresh_tables()
        if hasattr(self, "customers_tree"):
            self._refresh_customers()
        if hasattr(self, "orders_tree"):
            self._refresh_orders()
        if hasattr(self, "dashboard_cards"):
            self._refresh_dashboard()
        if hasattr(self, "pos_menu_frame"):
            self._refresh_pos_menu()
        if hasattr(self, "pos_cart_items"):
            self._refresh_pos_cart()

    def _on_close(self):
        try:
            self.service.save(self.restaurant)
        finally:
            self.destroy()


def run() -> None:
    app = RestaurantApp()
    app.mainloop()
