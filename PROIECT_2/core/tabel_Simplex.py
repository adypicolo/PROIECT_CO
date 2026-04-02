import tkinter as tk
from tkinter import ttk
from fractions import Fraction
from copy import deepcopy
import numpy as np


class SimplexFrame(tk.Frame):
    def __init__(self, parent, Q, v1=None, v2=None):
        super().__init__(parent)
        self.Q = np.array(Q, dtype=float)
        self.m, self.n = self.Q.shape
        self.v1, self.v2 = v1, v2
        self.afiseaza_solutie()

    def afiseaza_solutie(self):
        X_optim, Y_optim, v_frac, punct_echilibru, iter_tables, pivot_info = self.rezolva_joc()

        # Container cu scroll
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Titlu
        tk.Label(scrollable, text="REZOLVARE JOC MATRICEAL",
                 font=("Arial", 18, "bold"), fg="navy").pack(pady=15)

        # Informatii joc
        info_frame = tk.LabelFrame(scrollable, text="Datele problemei",
                                   font=("Arial", 12, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(info_frame, text=f"Dimensiune joc: {self.m} x {self.n}",
                 font=("Arial", 11)).pack(anchor="w")

        # Matricea jocului
        tk.Label(info_frame, text="Matricea plăților:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        mat_frame = tk.Frame(info_frame)
        mat_frame.pack()
        for i in range(self.m):
            for j in range(self.n):
                val = self.Q[i][j]
                text = f"{int(val)}" if val.is_integer() else f"{val:.2f}"
                tk.Label(mat_frame, text=text, width=6, relief=tk.RIDGE,
                         font=("Courier", 10)).grid(row=i, column=j, padx=1, pady=1)

        # Calcul valori
        alpha = [min(self.Q[i, :]) for i in range(self.m)]
        beta = [max(self.Q[:, j]) for j in range(self.n)]
        v1_calc, v2_calc = max(alpha), min(beta)

        tk.Label(info_frame, text=f"\nαᵢ (min pe linie): {[round(float(a), 2) for a in alpha]}",
                 font=("Arial", 10)).pack(anchor="w")
        tk.Label(info_frame, text=f"βⱼ (max pe coloană): {[round(float(b), 2) for b in beta]}",
                 font=("Arial", 10)).pack(anchor="w")
        tk.Label(info_frame, text=f"v₁ = max(αᵢ) = {v1_calc} (maximin)",
                 font=("Arial", 10, "bold"), fg="blue").pack(anchor="w")
        tk.Label(info_frame, text=f"v₂ = min(βⱼ) = {v2_calc} (minimax)",
                 font=("Arial", 10, "bold"), fg="blue").pack(anchor="w")

        # Cazul determinat
        caz_frame = tk.LabelFrame(scrollable, text="Analiza jocului",
                                  font=("Arial", 12, "bold"), padx=10, pady=10)
        caz_frame.pack(fill=tk.X, padx=10, pady=5)

        if punct_echilibru:
            tk.Label(caz_frame, text="✓ CAZUL 1: Joc cu punct 'șa'",
                     font=("Arial", 11, "bold"), fg="green").pack(anchor="w")
            tk.Label(caz_frame, text=f"v₁ = v₂ = {v1_calc} → jocul admite punct de echilibru în strategii pure",
                     font=("Arial", 10)).pack(anchor="w")
        else:
            tk.Label(caz_frame, text="✗ CAZUL 2: Joc fără punct 'șa'",
                     font=("Arial", 11, "bold"), fg="orange").pack(anchor="w")
            tk.Label(caz_frame, text=f"v₁ = {v1_calc} < v₂ = {v2_calc} → se determină strategii mixte optime",
                     font=("Arial", 10)).pack(anchor="w")

        # Solutia jocului
        sol_frame = tk.LabelFrame(scrollable, text="Soluția optimă",
                                  font=("Arial", 12, "bold"), padx=10, pady=10, bg="lightyellow")
        sol_frame.pack(fill=tk.X, padx=10, pady=5)

        v_str = f"{v_frac.numerator}/{v_frac.denominator}" if v_frac.denominator != 1 else str(v_frac.numerator)
        v_float = float(v_frac)
        tk.Label(sol_frame, text=f"VALOAREA JOCULUI: v = {v_str} ≈ {v_float:.4f}",
                 font=("Arial", 13, "bold"), fg="red", bg="lightyellow").pack(anchor="w", pady=5)

        if not punct_echilibru:
            tk.Label(sol_frame,
                     text=f"Verificare apartenență: v ∈ [{v1_calc}, {v2_calc}] → {v1_calc} ≤ {v_float:.4f} ≤ {v2_calc}",
                     font=("Arial", 9), bg="lightyellow").pack(anchor="w")

        # Strategii A
        tk.Label(sol_frame, text="\nSTRATEGII OPTIME PENTRU JUCĂTORUL A (MINIMIZATOR):",
                 font=("Arial", 11, "bold"), bg="lightyellow").pack(anchor="w")
        for i, x in enumerate(X_optim):
            prob = float(x)
            frac_str = f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
            tk.Label(sol_frame, text=f"  • a{i + 1} → {frac_str}  ({prob * 100:.2f}%)",
                     font=("Arial", 10), bg="lightyellow").pack(anchor="w")

        # Strategii B
        tk.Label(sol_frame, text="\nSTRATEGII OPTIME PENTRU JUCĂTORUL B (MAXIMIZATOR):",
                 font=("Arial", 11, "bold"), bg="lightyellow").pack(anchor="w")
        for j, y in enumerate(Y_optim):
            prob = float(y)
            frac_str = f"{y.numerator}/{y.denominator}" if y.denominator != 1 else str(y.numerator)
            tk.Label(sol_frame, text=f"  • b{j + 1} → {frac_str}  ({prob * 100:.2f}%)",
                     font=("Arial", 10), bg="lightyellow").pack(anchor="w")

        # Verificari
        sum_X = sum(float(x) for x in X_optim)
        sum_Y = sum(float(y) for y in Y_optim)
        v_check = sum(float(X_optim[i]) * self.Q[i][j] * float(Y_optim[j])
                      for i in range(self.m) for j in range(self.n))

        tk.Label(sol_frame, text="\nVERIFICĂRI:", font=("Arial", 11, "bold"),
                 bg="lightyellow").pack(anchor="w")

        status_X = "VERIFICAT" if abs(sum_X - 1) < 0.0001 else "NEVERIFICAT"
        tk.Label(sol_frame, text=f"✓ ∑X = {'1' if abs(sum_X - 1) < 0.0001 else f'{sum_X:.6f}'} → {status_X}",
                 font=("Arial", 10), bg="lightyellow").pack(anchor="w")

        status_Y = "VERIFICAT" if abs(sum_Y - 1) < 0.0001 else "NEVERIFICAT"
        tk.Label(sol_frame, text=f"✓ ∑Y = {'1' if abs(sum_Y - 1) < 0.0001 else f'{sum_Y:.6f}'} → {status_Y}",
                 font=("Arial", 10), bg="lightyellow").pack(anchor="w")

        status_v = "VERIFICAT" if abs(v_check - v_float) < 0.0001 else "NEVERIFICAT"
        tk.Label(sol_frame, text=f"✓ v = X·Q·Y = {v_check:.6f} ≈ {v_float:.6f} → {status_v}",
                 font=("Arial", 10), bg="lightyellow").pack(anchor="w")

        # Interpretare
        interp_frame = tk.LabelFrame(scrollable, text="Interpretarea rezultatelor",
                                     font=("Arial", 12, "bold"), padx=10, pady=10, bg="lightblue")
        interp_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(interp_frame, text=f"Jucătorul A (MINIMIZATOR) va câștiga CEL PUȚIN {v_str} unități,",
                 font=("Arial", 10), bg="lightblue").pack(anchor="w")
        tk.Label(interp_frame, text=f"aplicând strategiile mixte cu probabilitățile specificate mai sus.",
                 font=("Arial", 10), bg="lightblue").pack(anchor="w")
        tk.Label(interp_frame, text=f"\nJucătorul B (MAXIMIZATOR) va pierde CEL MULT {v_str} unități,",
                 font=("Arial", 10), bg="lightblue").pack(anchor="w")
        tk.Label(interp_frame, text=f"aplicând strategiile mixte cu probabilitățile specificate mai sus.",
                 font=("Arial", 10), bg="lightblue").pack(anchor="w")

        # Tabele simplex
        if iter_tables and not punct_echilibru:
            simplex_frame = tk.LabelFrame(scrollable, text="Algoritmul Simplex - Iterații",
                                          font=("Arial", 12, "bold"), padx=10, pady=10)
            simplex_frame.pack(fill=tk.X, padx=10, pady=5)

            for it, (table, pivot_row, pivot_col) in enumerate(zip(iter_tables, pivot_info[0], pivot_info[1])):
                it_frame = tk.Frame(simplex_frame, relief=tk.RIDGE, bd=2, padx=5, pady=5)
                it_frame.pack(fill=tk.X, pady=5)

                header = f"Iterația {it}"
                if pivot_row is not None and pivot_col is not None:
                    header += f" | Pivot: linia {pivot_row + 1}, coloana {pivot_col + 1}"
                tk.Label(it_frame, text=header, font=("Arial", 10, "bold"),
                         fg="navy", bg="lightgray").pack(anchor="w", fill=tk.X, pady=2)

                if table:
                    rows, cols = len(table), len(table[0])
                    tbl_frame = tk.Frame(it_frame)
                    tbl_frame.pack(pady=5)

                    for j in range(min(cols, 12)):
                        if j == cols - 1:
                            text = "b"
                        elif j < self.n:
                            text = f"y{j + 1}"
                        else:
                            text = f"s{j - self.n + 1}"
                        tk.Label(tbl_frame, text=text, width=8, relief=tk.RIDGE,
                                 bg="lightgray", font=("Arial", 8, "bold")).grid(row=0, column=j, padx=1, pady=1)

                    for i in range(min(rows, 15)):
                        for j in range(min(cols, 12)):
                            val = table[i][j]
                            if val.denominator == 1:
                                val_str = str(val.numerator)
                            else:
                                val_str = f"{val.numerator}/{val.denominator}"
                            if len(val_str) > 8:
                                val_str = val_str[:6] + ".."

                            bg_color = "yellow" if (pivot_row is not None and pivot_col is not None and
                                                    i == pivot_row and j == pivot_col) else "white"
                            font_style = ("Courier", 8, "bold") if bg_color == "yellow" else ("Courier", 8)

                            tk.Label(tbl_frame, text=val_str, width=8, relief=tk.RIDGE,
                                     bg=bg_color, font=font_style).grid(row=i + 1, column=j, padx=1, pady=1)

                    for i in range(min(rows, 15)):
                        if i < self.m:
                            text = f"s{i + 1}"
                        else:
                            text = "g"
                        tk.Label(tbl_frame, text=text, width=4, relief=tk.RIDGE,
                                 bg="lightgray", font=("Arial", 8, "bold")).grid(row=i + 1, column=cols, padx=1, pady=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def rezolva_joc(self):
        alpha = [min(self.Q[i, :]) for i in range(self.m)]
        beta = [max(self.Q[:, j]) for j in range(self.n)]
        v1, v2 = max(alpha), min(beta)

        if abs(v1 - v2) < 1e-10:
            i_sa = None
            for i in range(self.m):
                if abs(min(self.Q[i, :]) - v1) < 1e-10:
                    i_sa = i
                    break
            j_sa = None
            for j in range(self.n):
                if abs(max(self.Q[:, j]) - v2) < 1e-10:
                    j_sa = j
                    break
            X = [Fraction(1) if i == i_sa else Fraction(0) for i in range(self.m)]
            Y = [Fraction(1) if j == j_sa else Fraction(0) for j in range(self.n)]
            return X, Y, Fraction(v1), True, None, None

        return self.solve_PLB_ASP()

    def solve_PLB_ASP(self):
        m, n = self.m, self.n

        # Determinare shift
        min_val = np.min(self.Q)
        if min_val <= 0:
            shift = -min_val + 1
        else:
            shift = 0

        C = self.Q + shift

        # Construim tabelul
        table = []
        for i in range(m):
            row = []
            for j in range(n):
                row.append(Fraction(C[i, j]))
            for k in range(m):
                row.append(Fraction(1) if k == i else Fraction(0))
            row.append(Fraction(1))
            table.append(row)

        # Rândul funcției obiectiv
        obj_row = [Fraction(-1) for _ in range(n)] + [Fraction(0) for _ in range(m)] + [Fraction(0)]
        table.append(obj_row)

        basic = list(range(n, n + m))

        iter_tables = [deepcopy(table)]
        pivot_rows = [None]
        pivot_cols = [None]

        # Algoritmul Simplex
        for _ in range(100):
            obj = table[-1][:-1]
            min_obj = min(obj)

            if min_obj >= 0:
                break

            j = obj.index(min_obj)

            ratios = []
            for i in range(m):
                if table[i][j] > 0:
                    ratios.append(table[i][-1] / table[i][j])
                else:
                    ratios.append(float('inf'))

            if all(r == float('inf') for r in ratios):
                break

            i = ratios.index(min(ratios))

            pivot_rows.append(i)
            pivot_cols.append(j)

            pivot_val = table[i][j]
            table[i] = [x / pivot_val for x in table[i]]

            for k in range(len(table)):
                if k != i:
                    factor = table[k][j]
                    if factor != 0:
                        table[k] = [table[k][l] - factor * table[i][l] for l in range(len(table[0]))]

            basic[i] = j
            iter_tables.append(deepcopy(table))

        # Extragem soluțiile
        # y - variabilele de decizie pentru B
        y = [Fraction(0) for _ in range(n)]
        for i in range(m):
            if basic[i] < n:
                y[basic[i]] = table[i][-1]

        gmax = sum(y)
        v_transformed = Fraction(1, gmax)

        # Shift
        shift_frac = Fraction(int(shift), 1)
        v = v_transformed - shift_frac

        # x - variabilele duale (pentru A) se extrag din coloanele variabilelor de egalizare
        x = [Fraction(0) for _ in range(m)]
        for j in range(m):
            # Coloanele variabilelor de egalizare sunt la indexul n + j
            x[j] = -table[-1][n + j]

        # Soluțiile finale conform formulelor: X_optim = v * x, Y_optim = y / gmax
        X_optim = [xi * v for xi in x]
        Y_optim = [yj / gmax for yj in y]

        return X_optim, Y_optim, v, False, iter_tables, (pivot_rows, pivot_cols)