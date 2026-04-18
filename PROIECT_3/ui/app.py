# --- ui/app.py ---

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from core.solver import TransportationSolver
from ui.table_view import TableView

ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    # Paleta de culori "Circulatory System"
    BG_MAIN = "#9C3032"
    BG_CARD = "#F8F3E6"
    TEXT_DARK = "#6D2022"
    TEXT_LIGHT = "#F8F3E6"
    ACCENT_BLUE = "#5C6BC0"
    ACCENT_PINK = "#D48383"

    def __init__(self):
        super().__init__()
        self.title("PROIECT CO - Problema Transporturilor")

        # Rezolutie verticala optima
        self.geometry("800x1000")
        self.eval('tk::PlaceWindow . center')
        self.configure(fg_color=self.BG_MAIN)

        self.intrari_matrice_cost = []
        self.intrari_disponibil = []
        self.intrari_necesar = []
        self.final_state = None

        self._setup_ui()

    def _setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(15, 5), fill="x")
        ctk.CTkLabel(header_frame, text="Problema Transporturilor", font=("Helvetica", 22, "bold"),
                     text_color=self.TEXT_LIGHT).pack()
        ctk.CTkLabel(header_frame, text="Interpretarea Solutiei Optime", font=("Helvetica", 12),
                     text_color=self.ACCENT_PINK).pack()

        # Panou configurare m si n
        self.frame_config = ctk.CTkFrame(self, fg_color=self.BG_CARD, corner_radius=10)
        self.frame_config.pack(pady=5, padx=20, fill="x")
        self.frame_config.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(self.frame_config, text="Surse (m):", font=("Helvetica", 12, "bold"),
                     text_color=self.TEXT_DARK).grid(row=0, column=0, pady=8, sticky="e", padx=5)
        self.entry_m = ctk.CTkEntry(self.frame_config, width=50, height=26, font=("Helvetica", 12), fg_color="#FFFFFF",
                                    text_color=self.TEXT_DARK, border_color=self.ACCENT_PINK)
        self.entry_m.grid(row=0, column=1, pady=8, sticky="w")

        ctk.CTkLabel(self.frame_config, text="Dest. (n):", font=("Helvetica", 12, "bold"),
                     text_color=self.TEXT_DARK).grid(row=0, column=2, pady=8, sticky="e", padx=5)
        self.entry_n = ctk.CTkEntry(self.frame_config, width=50, height=26, font=("Helvetica", 12), fg_color="#FFFFFF",
                                    text_color=self.TEXT_DARK, border_color=self.ACCENT_PINK)
        self.entry_n.grid(row=0, column=3, pady=8, sticky="w")

        btn_generate = ctk.CTkButton(
            self.frame_config, text="Genereaza",
            font=("Helvetica", 12, "bold"), text_color=self.TEXT_LIGHT,
            fg_color=self.ACCENT_BLUE, hover_color="#3F4A8C",
            corner_radius=6, height=28, command=self.generate_input_grid
        )
        btn_generate.grid(row=0, column=4, pady=8, padx=10, sticky="w")

        # Panou pentru introducerea matricei
        self.frame_input = ctk.CTkFrame(self, fg_color=self.BG_CARD, corner_radius=10)
        self.frame_input.pack(pady=5, padx=20, fill="x")

        # --- ZONA DE REZULTATE (Scrollable) ---
        self.frame_results = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=10,
            scrollbar_button_color=self.BG_CARD, scrollbar_button_hover_color=self.ACCENT_PINK
        )
        self.frame_results.pack(pady=5, padx=20, fill="both", expand=True)

        # --- PANOU ACTIUNI FINALE (In afara scroll-ului) ---
        self.frame_actions = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_actions.pack(pady=(5, 15), padx=20, fill="x")

        self.btn_interpretare = ctk.CTkButton(
            self.frame_actions, text="Interpretare Rezultate",
            font=("Helvetica", 15, "bold"), text_color=self.TEXT_LIGHT,
            fg_color=self.ACCENT_BLUE, hover_color="#3F4A8C", corner_radius=8,
            height=45, command=self.arata_interpretarea
        )
        # Il ascundem initial, va aparea doar la final
        self.btn_interpretare.pack_forget()

    def generate_input_grid(self):
        # Resetam starea butonului de interpretare
        self.btn_interpretare.pack_forget()

        for widget in self.frame_input.winfo_children():
            widget.destroy()

        self.intrari_matrice_cost.clear()
        self.intrari_disponibil.clear()
        self.intrari_necesar.clear()

        try:
            m = int(self.entry_m.get())
            n = int(self.entry_n.get())
            if m <= 0 or n <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Eroare", "Introduceti numere intregi pozitive!")
            return

        grid_f = ctk.CTkFrame(self.frame_input, fg_color="transparent")
        grid_f.pack(pady=10)

        font_label = ("Helvetica", 12, "bold")
        font_entry = ("Helvetica", 12)

        for j in range(n):
            ctk.CTkLabel(grid_f, text=f"B{j + 1}", font=font_label, text_color=self.TEXT_DARK).grid(row=0, column=j + 1,
                                                                                                    padx=2, pady=2)
        ctk.CTkLabel(grid_f, text="D", font=font_label, text_color=self.BG_MAIN).grid(row=0, column=n + 1, padx=8,
                                                                                      pady=2)

        for i in range(m):
            ctk.CTkLabel(grid_f, text=f"A{i + 1}", font=font_label, text_color=self.TEXT_DARK).grid(row=i + 1, column=0,
                                                                                                    padx=8, pady=2)
            rand_intrari = []
            for j in range(n):
                e = ctk.CTkEntry(grid_f, width=42, height=24, font=font_entry, justify="center", fg_color="#FFFFFF",
                                 text_color=self.TEXT_DARK, border_color=self.ACCENT_PINK)
                e.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                rand_intrari.append(e)
            self.intrari_matrice_cost.append(rand_intrari)

            e_supp = ctk.CTkEntry(grid_f, width=52, height=24, font=font_entry, justify="center", fg_color="#FFEBEB",
                                  text_color=self.TEXT_DARK, border_width=1, border_color=self.BG_MAIN)
            e_supp.grid(row=i + 1, column=n + 1, padx=8, pady=2)
            self.intrari_disponibil.append(e_supp)

        ctk.CTkLabel(grid_f, text="N", font=font_label, text_color=self.BG_MAIN).grid(row=m + 1, column=0, padx=8,
                                                                                      pady=(5, 2))
        for j in range(n):
            e_dem = ctk.CTkEntry(grid_f, width=42, height=24, font=font_entry, justify="center", fg_color="#FFEBEB",
                                 text_color=self.TEXT_DARK, border_width=1, border_color=self.BG_MAIN)
            e_dem.grid(row=m + 1, column=j + 1, padx=2, pady=(5, 2))
            self.intrari_necesar.append(e_dem)

        btn_solve = ctk.CTkButton(
            self.frame_input, text="Rezolva",
            font=("Helvetica", 13, "bold"), text_color=self.TEXT_LIGHT,
            fg_color=self.BG_MAIN, hover_color="#6D2022", corner_radius=6,
            command=self.solve_problem, width=140, height=30
        )
        btn_solve.pack(pady=(5, 10))

    def solve_problem(self):
        # Curatam rezultatele anterioare si ascundem butonul de interpretare
        for widget in self.frame_results.winfo_children():
            widget.destroy()
        self.btn_interpretare.pack_forget()
        self.final_state = None

        try:
            m = len(self.intrari_disponibil)
            n = len(self.intrari_necesar)
            cost = []
            for i in range(m):
                row = []
                for j in range(n):
                    row.append(float(self.intrari_matrice_cost[i][j].get()))
                cost.append(row)
            disponibil = [float(e.get()) for e in self.intrari_disponibil]
            necesar = [float(e.get()) for e in self.intrari_necesar]
        except ValueError:
            messagebox.showerror("Eroare", "Date invalide in tabel! Verificati toate campurile.")
            return

        solver = TransportationSolver(cost, disponibil, necesar)

        for state in solver.solve():
            it_num = state['iteratie']
            title = f"Iteratia {it_num} (N-V)" if it_num == 0 else f"Iteratia {it_num}"

            card = ctk.CTkFrame(self.frame_results, fg_color=self.BG_CARD, corner_radius=10)
            card.pack(pady=8, fill="x", padx=5)

            tv = TableView(card, state, title=title, fg_color="transparent")
            tv.pack(pady=12, padx=12, fill="x")

            if state['este_optim']:
                self.final_state = state

        # Daca s-a gasit solutia optima, afisam butonul de interpretare IN AFARA scroll-ului
        if self.final_state:
            self.btn_interpretare.pack(pady=5)

    def arata_interpretarea(self):
        if not self.final_state: return

        state = self.final_state
        popup = ctk.CTkToplevel(self)
        popup.title("Interpretarea Rezultatelor")
        popup.geometry("600x550")
        popup.configure(fg_color=self.BG_MAIN)
        popup.attributes("-topmost", True)

        orig_m, orig_n = state['original_m'], state['original_n']
        alocari, cost_matrix = state['alocari'], state['cost']

        real_allocs, leftovers, deficits, cost_total = [], [], [], 0

        # Analizam fiecare alocare din tabelul final
        for (i, j), cant_eps in alocari.items():
            cantitate = cant_eps.real
            if cantitate == 0: continue

            # 1. Alocare Reala (Intre sursa reala si destinatie reala)
            if i < orig_m and j < orig_n:
                cost_total += cantitate * cost_matrix[i][j]
                real_allocs.append(f"-> Din Sursa A{i + 1} la Destinatia B{j + 1} se transporta {cantitate:g} unitati.")

            # 2. Alocare catre destinatie fictiva (Sursa ramane cu stoc)
            elif j >= orig_n and i < orig_m:
                leftovers.append(f"-> Sursa A{i + 1} ramane cu un stoc de {cantitate:g} unitati (excedent).")

            # 3. Alocare din sursa fictiva (Destinatia ramane cu necesar neacoperit)
            elif i >= orig_m and j < orig_n:
                deficits.append(f"-> Destinatia B{j + 1} are un necesar neacoperit de {cantitate:g} unitati (deficit).")

        card = ctk.CTkFrame(popup, fg_color=self.BG_CARD, corner_radius=12)
        card.pack(pady=15, padx=15, fill="both", expand=True)

        ctk.CTkLabel(card, text="CONCLUZII FINALE", font=("Helvetica", 18, "bold"), text_color=self.TEXT_DARK).pack(
            pady=10)
        ctk.CTkLabel(card, text=f"Cost Minim de Transport: {cost_total:g} UM", font=("Helvetica", 16, "bold"),
                     text_color=self.ACCENT_PINK).pack(pady=5)

        text_f = ctk.CTkScrollableFrame(card, fg_color="transparent")
        text_f.pack(pady=10, padx=15, fill="both", expand=True)

        ctk.CTkLabel(text_f, text="Planul de transport optim:", font=("Helvetica", 14, "bold"),
                     text_color=self.TEXT_DARK).pack(anchor="w")
        for ra in real_allocs:
            ctk.CTkLabel(text_f, text=ra, font=("Helvetica", 13), text_color=self.TEXT_DARK, justify="left").pack(
                anchor="w", padx=10, pady=2)

        if leftovers or deficits:
            ctk.CTkLabel(text_f, text="\nObservatii privind dezechilibrul:", font=("Helvetica", 14, "bold"),
                         text_color=self.TEXT_DARK).pack(anchor="w")
            for item in leftovers + deficits:
                ctk.CTkLabel(text_f, text=item, font=("Helvetica", 13), text_color=self.TEXT_DARK, justify="left").pack(
                    anchor="w", padx=10, pady=2)
        else:
            ctk.CTkLabel(text_f,
                         text="\nToate capacitatile surselor au fost epuizate,\niar toate cerintele destinatiilor au fost satisfacute.",
                         font=("Helvetica", 13), text_color=self.TEXT_DARK).pack(anchor="w", padx=10)