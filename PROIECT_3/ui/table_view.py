# --- ui/table_view.py ---

import tkinter as tk
import customtkinter as ctk


class TableView(ctk.CTkFrame):
    def __init__(self, master, stare, title="Iteratia", **kwargs):
        super().__init__(master, **kwargs)

        self.stare = stare
        self.m = stare['m']
        self.n = stare['n']

        self.cost = stare['cost']
        self.alocari = stare['alocari']
        self.u = stare['u']
        self.v = stare['v']
        self.delta = stare['delta']
        self.circuit = stare['circuit']
        self.pivot = stare['pivot']
        self.disp = stare['disp']
        self.nec = stare['nec']

        # Paleta Tema Circulatorie
        self.color_bg = "#F8F3E6"  # Crem (Fundal canvas)
        self.color_cell = "#FFFFFF"  # Celule albe
        self.color_header = "#9C3032"  # Rosu visiniu pentru u, v
        self.color_sum_bg = "#6D2022"  # Rosu mai inchis pt sume

        self.color_text_dark = "#6D2022"
        self.color_text_light = "#F8F3E6"

        self.color_pivot = "#5C6BC0"  # Albastru
        self.color_cycle = "#D48383"  # Roz
        self.color_negative = "#E53935"  # Rosu aprins
        self.color_success = "#43A047"  # Verde pt optim

        lbl_title = ctk.CTkLabel(self, text=title, font=("Helvetica", 18, "bold"), text_color=self.color_text_dark)
        lbl_title.pack(pady=(0, 10))

        # --- Caseta de text formatata frumos pentru explicatii ---
        explicatie = stare.get('mesaj_explicativ', '')
        if explicatie:
            textbox = ctk.CTkTextbox(
                self,
                fg_color="#FFEBEB",  # Un fundal rozaliu deschis
                text_color=self.color_text_dark,
                font=("Helvetica", 14),
                wrap="word",
                height=110,
                corner_radius=8,
                border_width=1,
                border_color="#D48383"
            )
            textbox.pack(pady=5, padx=10, fill="x")
            textbox.insert("0.0", explicatie)
            textbox.configure(state="disabled")  # O facem read-only
        # ---------------------------------------------------------

        if stare['este_optim']:
            lbl_opt = ctk.CTkLabel(self, text="SOLUTIE OPTIMA ATINSA", font=("Helvetica", 16, "bold"),
                                   text_color=self.color_success)
            lbl_opt.pack(pady=10)

        self.cell_w = 85
        self.cell_h = 65

        canvas_width = (self.n + 2) * self.cell_w
        canvas_height = (self.m + 2) * self.cell_h

        canvas_wrapper = ctk.CTkFrame(self, fg_color="transparent")
        canvas_wrapper.pack(pady=15)

        self.canvas = tk.Canvas(canvas_wrapper, width=canvas_width, height=canvas_height,
                                bg=self.color_bg, highlightthickness=0)
        self.canvas.pack()

        self._draw_table()

    def _draw_table(self):
        cw = self.cell_w
        ch = self.cell_h

        font_math = ("Helvetica", 13, "bold")
        font_cost = ("Helvetica", 11, "bold")
        font_main = ("Helvetica", 15, "bold")

        pad = 2

        def draw_cell(x, y, w, h, bg_col, text, t_font, t_col, anchor="center", text_x_offset=0, text_y_offset=0):
            self.canvas.create_rectangle(x + pad, y + pad, x + w - pad, y + h - pad, fill=bg_col, outline="", width=0)
            tx = x + w / 2 if anchor == "center" else x + text_x_offset
            ty = y + h / 2 if anchor == "center" else y + text_y_offset
            self.canvas.create_text(tx, ty, text=text, font=t_font, fill=t_col, anchor=anchor)

        draw_cell(0, 0, cw, ch, self.color_header, "u \\ v", font_math, self.color_text_light)

        for j in range(self.n):
            v_val = f"{self.v[j]:g}" if self.v[j] is not None else "-"
            draw_cell((j + 1) * cw, 0, cw, ch, self.color_header, v_val, font_math, self.color_text_light)

        for i in range(self.m):
            u_val = f"{self.u[i]:g}" if self.u[i] is not None else "-"
            draw_cell(0, (i + 1) * ch, cw, ch, self.color_header, u_val, font_math, self.color_text_light)

        x_sum = (self.n + 1) * cw
        y_sum = (self.m + 1) * ch
        draw_cell(x_sum, 0, cw, ch, self.color_sum_bg, "Σ (D)", font_math, self.color_text_light)
        draw_cell(0, y_sum, cw, ch, self.color_sum_bg, "ΣC (N)", font_math, self.color_text_light)

        for i in range(self.m):
            # self.disp[i] este obiect Epsilon; str() il converteste corect pentru afisare
            draw_cell(x_sum, (i + 1) * ch, cw, ch, self.color_sum_bg, str(self.disp[i]), font_math,
                      self.color_text_light)
        for j in range(self.n):
            draw_cell((j + 1) * cw, y_sum, cw, ch, self.color_sum_bg, str(self.nec[j]), font_math,
                      self.color_text_light)

        total_sum = sum(self.disp, start=type(self.disp[0])(0))
        draw_cell(x_sum, y_sum, cw, ch, self.color_success, str(total_sum), font_math, "#FFFFFF")

        for i in range(self.m):
            for j in range(self.n):
                x = (j + 1) * cw
                y = (i + 1) * ch

                fill_color = self.color_cell
                text_color = self.color_text_dark

                if self.pivot == (i, j):
                    fill_color = self.color_pivot
                    text_color = "#FFFFFF"
                elif self.circuit and (i, j) in self.circuit:
                    fill_color = self.color_cycle
                    text_color = "#FFFFFF"

                self.canvas.create_rectangle(x + pad, y + pad, x + cw - pad, y + ch - pad, fill=fill_color, outline="")

                c_col = "#9C3032" if fill_color == self.color_cell else "#FFEBEB"
                self.canvas.create_text(x + 8, y + 8, text=f"{self.cost[i][j]:g}", font=font_cost, fill=c_col,
                                        anchor="nw")

                if (i, j) in self.alocari:
                    val_str = str(self.alocari[(i, j)])
                    if self.circuit and (i, j) in self.circuit:
                        idx = self.circuit.index((i, j))
                        sign = "(+)" if idx % 2 == 0 else "(-)"
                        val_str += f" {sign}"
                    self.canvas.create_text(x + cw / 2, y + ch / 2, text=val_str, font=font_main, fill=text_color)
                else:
                    d_val = self.delta.get((i, j), 0)
                    if d_val < 0:
                        self.canvas.create_text(x + cw / 2, y + ch / 2, text=f"({d_val:g})", font=font_math,
                                                fill=self.color_negative)