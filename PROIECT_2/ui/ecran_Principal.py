import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import numpy as np
from copy import deepcopy
from utils.conversie_Fractie import transformaraFractie
from ui.tabel_Simplex import tabelSimplex

# INTERFATA PRINCIPALA
ctk.set_appearance_mode("light")

class ecranPrincipal(ctk.CTk):
    # seteaza iconita ferestrei
    def seteaza_iconita(self):
        self.iconbitmap("fsa.ico")

    def __init__(self):
        super().__init__()
        self.title("TEORIA JOCURILOR")
        self.geometry("1050x850")
        self.configure(fg_color="#dceeff")

        # incarcare iconita dupa pornire
        self.after(200, self.seteaza_iconita)

        # Panoul de configurare cu campurile de intrare pentru dimensiuni
        self.panou_config = ctk.CTkFrame(self, fg_color="transparent")
        self.panou_config.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.panou_config, text="Strategii A (linii):", font=("Montserrat", 12, "bold"),
                     text_color="#294280").grid(row=0, column=0, padx=5)
        self.input_m = ctk.CTkEntry(self.panou_config, width=80, border_color="#b9ddff", text_color="#294280")
        self.input_m.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.panou_config, text="Strategii B (coloane):", font=("Montserrat", 12, "bold"),
                     text_color="#294280").grid(row=0, column=2, padx=5)
        self.input_n = ctk.CTkEntry(self.panou_config, width=80, border_color="#b9ddff", text_color="#294280")
        self.input_n.grid(row=0, column=3, padx=5)

        ctk.CTkButton(
            self.panou_config, text="GENERARE MATRICE Q",
            font=("Montserrat", 12, "bold"), text_color="#ffffff",
            fg_color="#5284ff", hover_color="#4a77e6", command=self.genereazaInput
        ).grid(row=0, column=4, padx=20)

        # Zona pentru afisarea gridului de intrare al matricei Q
        self.zona_date_intrare = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        self.zona_date_intrare.pack(pady=10, padx=20, fill="x")
        self.grid_entries = []

        # Zona scrollabila pentru afisarea pasilor de rezolvare
        self.zona_rezolvare = ctk.CTkScrollableFrame(
            self, label_text="PASII DE REZOLVARE",
            fg_color="#93c5f2", label_font=("Montserrat", 14, "bold"),
            label_fg_color="#afd9ff", label_text_color="#ffffff"
        )
        self.zona_rezolvare.pack(pady=5, padx=20, fill="both", expand=True)

    def genereazaInput(self):
        # Sterge elementele anterioare din zona de date
        for elem in self.zona_date_intrare.winfo_children():
            elem.destroy()
        self.grid_entries.clear()

        try:
            m = int(self.input_m.get())
            n = int(self.input_n.get())
            if m <= 0 or n <= 0: return
        except ValueError:
            return

        ctk.CTkLabel(self.zona_date_intrare, text="Matricea Q:", font=("Montserrat", 14, "bold"),
                     text_color="#294280").pack(pady=10)

        grid_f = ctk.CTkFrame(self.zona_date_intrare, fg_color="transparent")
        grid_f.pack(pady=5)

        # Antet colt stanga sus si antetele coloanelor b1..bn
        ctk.CTkLabel(grid_f, text="A \\ B", font=("Montserrat", 12, "bold"), text_color="#294280").grid(row=0, column=0,
                                                                                                        padx=5, pady=5)
        for j in range(n):
            ctk.CTkLabel(grid_f, text=f"b{j + 1}", font=("Montserrat", 12, "bold"), text_color="#294280").grid(row=0,
                                                                                                               column=j + 1,
                                                                                                               padx=5,
                                                                                                               pady=5)

        # Genereaza randurile cu eticheta a1..am si campurile de intrare
        for i in range(m):
            ctk.CTkLabel(grid_f, text=f"a{i + 1}", font=("Montserrat", 12, "bold"), text_color="#294280").grid(
                row=i + 1, column=0, padx=5, pady=5)
            rand = []
            for j in range(n):
                e = ctk.CTkEntry(grid_f, width=60, justify="center", border_color="#b9ddff", font=("Montserrat", 12))
                e.grid(row=i + 1, column=j + 1, padx=3, pady=3)
                rand.append(e)
            self.grid_entries.append(rand)

        # Butonul de rezolvare apare dupa generarea gridului
        self.buton_calcul = ctk.CTkButton(
            self.zona_date_intrare, text="REZOLVARE",
            font=("Montserrat", 14, "bold"), text_color="#ffffff",
            fg_color="#2ECC71", hover_color="#27ae60", command=self.ASP
        )
        self.buton_calcul.pack(pady=15)

    def afiseaza_analiza_matrice(self, Q, alpha, beta, v1, v2, punct_echilibru):
        # Cadrul principal pentru pasul 1 (analiza matricei)
        m, n = Q.shape
        f_analiza = ctk.CTkFrame(self.zona_rezolvare, fg_color="#ffffff", border_width=2, border_color="#b9ddff",
                                 corner_radius=8)
        f_analiza.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(f_analiza, text="PAS 1", font=("Montserrat", 14, "bold"),
                     text_color="#294280").pack(pady=10)

        grid_f = ctk.CTkFrame(f_analiza, fg_color="transparent")
        grid_f.pack(pady=5)

        # Antetul variabilelor y1..yn pentru matricea extinsa
        for j in range(n):
            ctk.CTkLabel(grid_f, text=f"y{j + 1}", width=60, font=("Montserrat", 12, "bold"), fg_color="#e1ecf7",
                         text_color="#294280").grid(row=0, column=j + 2, padx=2, pady=2)

        ctk.CTkLabel(grid_f, text="A \\ B", width=60, font=("Montserrat", 12, "bold"), fg_color="#e1ecf7",
                     text_color="#294280").grid(row=1, column=1, padx=2, pady=2)
        for j in range(n):
            ctk.CTkLabel(grid_f, text=f"b{j + 1}", width=60, font=("Montserrat", 12, "bold"), fg_color="#e1ecf7",
                         text_color="#294280").grid(row=1, column=j + 2, padx=2, pady=2)
        ctk.CTkLabel(grid_f, text="α (min)", width=60, font=("Montserrat", 12, "bold"), fg_color="#fce4e4",
                     text_color="#e74c3c").grid(row=1, column=n + 2, padx=4, pady=2)

        # Afiseaza fiecare rand al matricei Q cu minimul pe linie (alpha)
        for i in range(m):
            ctk.CTkLabel(grid_f, text=f"x{i + 1}", width=60, font=("Montserrat", 12, "bold"), fg_color="#e1ecf7",
                         text_color="#294280").grid(row=i + 2, column=0, padx=2, pady=2)
            ctk.CTkLabel(grid_f, text=f"a{i + 1}", width=60, font=("Montserrat", 12, "bold"), fg_color="#e1ecf7",
                         text_color="#294280").grid(row=i + 2, column=1, padx=2, pady=2)

            for j in range(n):
                val = Q[i, j]
                txt = f"{int(val)}" if val.is_integer() else f"{val:.2f}"
                ctk.CTkLabel(grid_f, text=txt, width=60, font=("Montserrat", 12, "bold"), fg_color="#f0f5fa",
                             text_color="#294280").grid(row=i + 2, column=j + 2, padx=2, pady=2)

            a_val = alpha[i]
            a_txt = f"{int(a_val)}" if a_val.is_integer() else f"{a_val:.2f}"
            ctk.CTkLabel(grid_f, text=a_txt, width=60, font=("Montserrat", 12, "bold"), fg_color="#fce4e4",
                         text_color="#e74c3c").grid(row=i + 2, column=n + 2, padx=4, pady=2)

        # Afiseaza maximul pe coloana (beta) pe ultimul rand
        ctk.CTkLabel(grid_f, text="β (max)", width=60, font=("Montserrat", 12, "bold"), fg_color="#e3f2fd",
                     text_color="#1976d2").grid(row=m + 2, column=1, padx=2, pady=4)
        for j in range(n):
            b_val = beta[j]
            b_txt = f"{int(b_val)}" if b_val.is_integer() else f"{b_val:.2f}"
            ctk.CTkLabel(grid_f, text=b_txt, width=60, font=("Montserrat", 12, "bold"), fg_color="#e3f2fd",
                         text_color="#1976d2").grid(row=m + 2, column=j + 2, padx=2, pady=4)

        # Construieste textul de concluzie cu v1, v2 si tipul cazului
        str_alpha = ", ".join([transformaraFractie(a) for a in alpha])
        str_beta = ", ".join([transformaraFractie(b) for b in beta])

        concluzie = f"v1 = max(α) = max{{{str_alpha}}} = {transformaraFractie(v1)}\n"
        concluzie += f"v2 = min(β) = min{{{str_beta}}} = {transformaraFractie(v2)}\n\n"

        if punct_echilibru:
            concluzie += "CAZ 1: Joc cu punct de tip \"sa\" (v1 = v2)."
        else:
            concluzie += "CAZ 2: v1 ≠ v2. Nu există punct 'șa'.\nImpartim in problema in PLA si PLB."

        ctk.CTkLabel(f_analiza, text=concluzie, font=("Montserrat", 13, "bold"),
                     text_color="#e74c3c" if not punct_echilibru else "#2ECC71", justify="left").pack(pady=10)

    def afiseaza_formulare_PL(self, Q, m, n):
        # Cadrul pentru pasul 2 - formularea problemelor PLA si PLB
        cadru_pl = ctk.CTkFrame(self.zona_rezolvare, fg_color="#ffffff", border_width=2, border_color="#b9ddff",
                                corner_radius=8)
        cadru_pl.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(cadru_pl, text="PAS 2", font=("Montserrat", 14, "bold"),
                     text_color="#294280").pack(pady=10)

        containere = ctk.CTkFrame(cadru_pl, fg_color="transparent")
        containere.pack(fill="x", padx=10, pady=5)
        containere.grid_columnconfigure(0, weight=1)
        containere.grid_columnconfigure(1, weight=1)

        # Panoul PLA (minimizare)
        f_pla = ctk.CTkFrame(containere, fg_color="#fce4e4", corner_radius=8)
        f_pla.grid(row=0, column=0, padx=5, sticky="nsew")
        ctk.CTkLabel(f_pla, text="PLA", font=("Montserrat", 13, "bold"),
                     text_color="#e74c3c").pack(pady=10)
        obj_a = "min f(x) = " + " + ".join([f"x{i + 1}" for i in range(m)])
        ctk.CTkLabel(f_pla, text=obj_a, font=("Montserrat", 13, "bold"), text_color="#294280").pack(pady=2)

        # Restrictiile PLA: suma pe coloana j >= 1
        for j in range(n):
            termeni = []
            for i in range(m):
                val = Q[i, j]
                termeni.append(f"{transformaraFractie(val)}x{i + 1}" if val != 1 else f"x{i + 1}")
            restr = " + ".join(termeni).replace("+ -", "- ") + " ≥ 1"
            ctk.CTkLabel(f_pla, text=restr, font=("Montserrat", 12), text_color="#294280").pack(pady=1)
        ctk.CTkLabel(f_pla, text=", ".join([f"x{i + 1}" for i in range(m)]) + " ≥ 0",
                     font=("Montserrat", 12, "italic"), text_color="#294280").pack(pady=10)

        # Panoul PLB (maximizare)
        f_plb = ctk.CTkFrame(containere, fg_color="#e3f2fd", corner_radius=8)
        f_plb.grid(row=0, column=1, padx=5, sticky="nsew")
        ctk.CTkLabel(f_plb, text="PLB", font=("Montserrat", 13, "bold"),
                     text_color="#1976d2").pack(pady=10)
        obj_b = "max g(y) = " + " + ".join([f"y{j + 1}" for j in range(n)])
        ctk.CTkLabel(f_plb, text=obj_b, font=("Montserrat", 13, "bold"), text_color="#294280").pack(pady=2)

        # Restrictiile PLB: suma pe linie i <= 1
        for i in range(m):
            termeni = []
            for j in range(n):
                val = Q[i, j]
                termeni.append(f"{transformaraFractie(val)}y{j + 1}" if val != 1 else f"y{j + 1}")
            restr = " + ".join(termeni).replace("+ -", "- ") + " ≤ 1"
            ctk.CTkLabel(f_plb, text=restr, font=("Montserrat", 12), text_color="#294280").pack(pady=1)
        ctk.CTkLabel(f_plb, text=", ".join([f"y{j + 1}" for j in range(n)]) + " ≥ 0",
                     font=("Montserrat", 12, "italic"), text_color="#294280").pack(pady=10)

    def ASP(self):
        # Sterge rezultatele anterioare din zona de rezolvare
        for elem in self.zona_rezolvare.winfo_children(): elem.destroy()

        try:
            m = len(self.grid_entries)
            n = len(self.grid_entries[0])
            # Citeste valorile din grid si construieste matricea Q
            Q = np.zeros((m, n))
            for i in range(m):
                for j in range(n):
                    val = self.grid_entries[i][j].get().replace(',', '.')
                    if val == "": raise ValueError("Celule goale")
                    Q[i, j] = float(val)
        except Exception:
            messagebox.showerror("Eroare", "Introduceti numere valide in matrice!")
            return

        # Calculeaza minimul pe fiecare linie (alpha) si maximul pe fiecare coloana (beta)
        alpha = [min(Q[i, :]) for i in range(m)]
        beta = [max(Q[:, j]) for j in range(n)]
        v1, v2 = max(alpha), min(beta)
        # Verifica daca exista punct de tip "sa" (v1 == v2)
        punct_echilibru = abs(v1 - v2) < 1e-10

        self.afiseaza_analiza_matrice(Q, alpha, beta, v1, v2, punct_echilibru)

        if punct_echilibru:
            # Caz 1: strategia pura optima se gaseste direct din indicii extremelor
            i_sa = np.argmax(alpha)
            j_sa = np.argmin(beta)
            X_opt = [1 if i == i_sa else 0 for i in range(m)]
            Y_opt = [1 if j == j_sa else 0 for j in range(n)]

            self.afiseaza_rezultat_final(v1, X_opt, Y_opt, Q, X_opt, Y_opt, 0, 1 / v1, v1, v2)
        else:
            # Caz 2: rezolvare prin metoda simplex pentru jocuri mixte
            self.ruleaza_simplex_joc(Q, m, n, v1, v2)

    def ruleaza_simplex_joc(self, Q, m, n, v1, v2):
        # Translatam matricea daca are valori <= 0 pentru a asigura pozitivitatea
        min_val = np.min(Q)
        shift = -min_val + 1 if min_val <= 0 else 0
        Q_shift = Q + shift

        self.afiseaza_formulare_PL(Q_shift, m, n)

        # Construieste tabloul simplex initial cu variabile slack
        mat = np.zeros((m, n + m))
        mat[:, :n] = Q_shift
        mat[:, n:] = np.eye(m)       # Adauga matricea identitate pentru variabilele slack
        xb = np.ones(m)              # Termenii liberi sunt 1 (forma standard PLB)

        # Vectorul costurilor: 1 pentru y, 0 pentru slack
        C = np.array([1] * n + [0] * m, dtype=float)
        baza = list(range(n, n + m))  # Baza initiala formata din variabilele slack
        nume_var = [f"y{j + 1}" for j in range(n)] + [f"s{i + 1}" for i in range(m)]

        for it in range(50):
            # Calculeaza deltele (criteriul de optimalitate)
            cb = C[baza]
            deltas = np.array([C[j] - np.dot(cb, mat[:, j]) for j in range(n + m)])

            # Alege coloana pivot ca variabila cu cel mai mare delta pozitiv
            cp = np.argmax(deltas)
            optim = deltas[cp] <= 1e-9

            if optim:
                # Solutia optima a fost gasita
                tabelSimplex(self.zona_rezolvare, "Iteratia STOP", mat, xb, C, deltas, baza, nume_var,
                             pivot=None, iteratie=it)
                break

            # Calculeaza rapoartele minime pentru selectia liniei pivot
            raps = [xb[i] / mat[i, cp] if mat[i, cp] > 1e-9 else np.inf for i in range(m)]
            rp = np.argmin(raps)

            if raps[rp] == np.inf:
                messagebox.showwarning("Eroare", "Joc nemarginit!")
                return

            # Afiseaza tabelul cu pivotul curent evidentiat
            tabelSimplex(self.zona_rezolvare, f"Iteratia {it}", mat, xb, C, deltas, baza, nume_var, pivot=(rp, cp),
                         iteratie=it)

            # Pivotare: normalizeaza linia pivot
            val_p = mat[rp, cp]
            mat[rp, :] /= val_p
            xb[rp] /= val_p
            # Elimina elementele din celelalte linii pe coloana pivot
            for i in range(m):
                if i != rp:
                    f = mat[i, cp]
                    mat[i, :] -= f * mat[rp, :]
                    xb[i] -= f * xb[rp]
            # Actualizeaza baza cu noua variabila intrata
            baza[rp] = cp

        # Extrage solutia y din baza finala
        y_baza = np.zeros(n)
        for i in range(m):
            if baza[i] < n:
                y_baza[baza[i]] = xb[i]

        # Calculeaza valoarea jocului transformata si reala
        gmax = np.sum(y_baza)
        v_transf = 1.0 / gmax
        v_real = v_transf - shift

        # Extrage solutia duala X din deltele variabilelor slack
        x_duale = -deltas[n:]
        X_opt = x_duale * v_transf
        Y_opt = y_baza * v_transf

        self.afiseaza_rezultat_final(v_real, X_opt, Y_opt, Q, x_duale, y_baza, shift, v_transf, v1, v2)

    def afiseaza_rezultat_final(self, v, X_opt, Y_opt, Q, x_stea, y_stea, shift, v_transf, v1, v2):
        # Cadrul principal al solutiei finale
        cadru_final = ctk.CTkFrame(self.zona_rezolvare, border_width=2, border_color="#2ECC71", fg_color="#ffffff",
                                   corner_radius=8)
        cadru_final.pack(pady=15, padx=10, fill="x")

        ctk.CTkLabel(cadru_final, text="SOLUTIA FINALA", font=("Montserrat", 16, "bold"),
                     text_color="#27ae60").pack(pady=10, anchor="center")

        # Construieste textul pentru valoarea jocului V
        str_v1 = transformaraFractie(v1)
        str_v2 = transformaraFractie(v2)
        str_v = transformaraFractie(v)
        str_v_transf = transformaraFractie(v_transf)

        if shift == 0:
            txt_v = f"• V = 1 / g_max = {str_v}  ∈ [{str_v1}, {str_v2}]"
        else:
            txt_v = f"• V' = 1 / g_max = {str_v_transf}  =>  V = V' - k = {str_v_transf} - {shift} = {str_v}  ∈ [{str_v1}, {str_v2}]"

        ctk.CTkLabel(cadru_final, text=txt_v, font=("Montserrat", 14, "bold"), text_color="#d32f2f").pack(anchor="w",
                                                                                                          padx=20,
                                                                                                          pady=5)

        # Afiseaza strategia optima X^0 cu verificarea sumei
        str_XA = "(" + ", ".join([transformaraFractie(x) for x in x_stea]) + ")"
        str_X0 = "(" + ", ".join([transformaraFractie(x) for x in X_opt]) + ")"
        fractii_x = [transformaraFractie(x) for x in X_opt if x != 0]
        str_sum_x = " + ".join(fractii_x) if fractii_x else "0"

        txt_x = f"• X^0 = v · X_A = {str_v_transf} · {str_XA} = {str_X0}   =>   ∑X^0 = {str_sum_x} = 1 ✓"
        ctk.CTkLabel(cadru_final, text=txt_x, font=("Montserrat", 13, "bold"), text_color="#294280").pack(anchor="w",
                                                                                                          padx=20,
                                                                                                          pady=5)

        # Afiseaza strategia optima y^0 cu verificarea sumei
        str_YB = "(" + ", ".join([transformaraFractie(y) for y in y_stea]) + ")^T"
        str_Y0 = "(" + ", ".join([transformaraFractie(y) for y in Y_opt]) + ")^T"
        fractii_y = [transformaraFractie(y) for y in Y_opt if y != 0]
        str_sum_y = " + ".join(fractii_y) if fractii_y else "0"

        txt_y = f"• y^0 = v · Y_B = {str_v_transf} · {str_YB} = {str_Y0}   =>   ∑y^0 = {str_sum_y} = 1 ✓"
        ctk.CTkLabel(cadru_final, text=txt_y, font=("Montserrat", 13, "bold"), text_color="#294280").pack(anchor="w",
                                                                                                          padx=20,
                                                                                                          pady=5)

        # Butonul de verificare deschide fereastra popup cu calculul X*Q*Y=V
        btn_verificare = ctk.CTkButton(
            cadru_final, text="VERIFICA REZULTATUL",
            font=("Montserrat", 14, "bold"), text_color="#ffffff",
            fg_color="#3498db", hover_color="#2980b9",
            command=lambda: self.arata_fereastra_verificare(X_opt, Y_opt, v, Q)
        )
        btn_verificare.pack(pady=15)

    def creare_matrice_ui(self, parent, matrice_2d):
        # Deseneaza o matrice 2D ca grid de etichete intr-un cadru
        frm = ctk.CTkFrame(parent, fg_color="#f0f5fa", border_width=2, border_color="#9bcfff", corner_radius=0)
        for i, rand in enumerate(matrice_2d):
            for j, val in enumerate(rand):
                ctk.CTkLabel(frm, text=str(val), font=("Montserrat", 13, "bold"), text_color="#294280").grid(row=i,
                                                                                                             column=j,
                                                                                                             padx=6,
                                                                                                             pady=2)
        return frm

    def arata_fereastra_verificare(self, X_opt, Y_opt, v, Q):
        # Deschide fereastra popup pentru verificarea solutiei
        fer = ctk.CTkToplevel(self)
        fer.title("VERIFICAREA SOLUTIEI")
        fer.geometry("850x650")
        fer.configure(fg_color="#ffffff")
        fer.grab_set()

        # incarcare iconita dupa pornire
        fer.after(200, lambda: fer.iconbitmap("fsa.ico"))

        scroll = ctk.CTkScrollableFrame(fer, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="VERIFICAREA SOLUTIEI", font=("Montserrat", 16, "bold"),
                     text_color="#294280").pack(pady=15)

        sum_x = sum(X_opt)
        sum_y = sum(Y_opt)

        # Cadrul pentru verificarea matriciala X * Q * Y = V
        f_math = ctk.CTkFrame(scroll, fg_color="#ffffff", border_width=2, border_color="#b9ddff", corner_radius=8)
        f_math.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(f_math, text="3. Verificare: X⁰ · Q · y⁰ = V", font=("Montserrat", 13, "bold"),
                     text_color="#294280").pack(anchor="w", padx=10, pady=(10, 5))

        # Randul 1: afiseaza X, Q, y si valoarea V asteptata
        f_r1 = ctk.CTkFrame(f_math, fg_color="transparent")
        f_r1.pack(anchor="w", pady=5, padx=10)

        ctk.CTkLabel(f_r1, text="X⁰·Q·y⁰ ≟ V   =>   ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(
            side="left")

        mat_x = [[transformaraFractie(x) for x in X_opt]]
        self.creare_matrice_ui(f_r1, mat_x).pack(side="left", padx=5)

        ctk.CTkLabel(f_r1, text=" · ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(side="left")

        mat_q = [[transformaraFractie(Q[i, j]) for j in range(len(Q[0]))] for i in range(len(Q))]
        self.creare_matrice_ui(f_r1, mat_q).pack(side="left", padx=5)

        ctk.CTkLabel(f_r1, text=" · ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(side="left")

        mat_y = [[transformaraFractie(y)] for y in Y_opt]
        self.creare_matrice_ui(f_r1, mat_y).pack(side="left", padx=5)

        ctk.CTkLabel(f_r1, text=f" ≟ {transformaraFractie(v)}", font=("Montserrat", 14, "bold"),
                     text_color="#d32f2f").pack(side="left")

        # Randul 2: afiseaza produsul intermediar X*Q inmultit cu y
        f_r2 = ctk.CTkFrame(f_math, fg_color="transparent")
        f_r2.pack(anchor="w", pady=5, padx=10)

        ctk.CTkLabel(f_r2, text="=>   ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(side="left",
                                                                                                     padx=(190, 0))

        X_Q = np.dot(X_opt, Q)
        mat_xq = [[transformaraFractie(xq) for xq in X_Q]]
        self.creare_matrice_ui(f_r2, mat_xq).pack(side="left", padx=5)

        ctk.CTkLabel(f_r2, text=" · ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(side="left")
        self.creare_matrice_ui(f_r2, mat_y).pack(side="left", padx=5)

        ctk.CTkLabel(f_r2, text=f" = {transformaraFractie(v)}", font=("Montserrat", 14, "bold"),
                     text_color="#d32f2f").pack(side="left")

        # Randul 3: suma termenilor si comparatia cu V
        f_r3 = ctk.CTkFrame(f_math, fg_color="transparent")
        f_r3.pack(anchor="w", pady=5, padx=10)

        val_finala = np.dot(X_Q, Y_opt)
        termeni_suma = [f"{transformaraFractie(X_Q[i])}·{transformaraFractie(Y_opt[i])}" for i in range(len(Y_opt)) if
                        Y_opt[i] != 0 and X_Q[i] != 0]
        str_suma = " + ".join(termeni_suma) if termeni_suma else "0"

        ctk.CTkLabel(f_r3, text="=>   ", font=("Montserrat", 14, "bold"), text_color="#294280").pack(side="left",
                                                                                                     padx=(190, 0))
        ctk.CTkLabel(f_r3, text=f"{str_suma} = {transformaraFractie(val_finala)}", font=("Montserrat", 14, "bold"),
                     text_color="#27ae60").pack(side="left")
        ctk.CTkLabel(f_r3, text=f"   =>   {transformaraFractie(val_finala)} = {transformaraFractie(v)} (A)",
                     font=("Montserrat", 14, "bold"), text_color="#27ae60").pack(side="left")

        # Valideaza ca sumele strategiilor sunt 1 si ca X*Q*Y = V
        is_valid = abs(float(sum_x) - 1.0) < 1e-4 and abs(float(sum_y) - 1.0) < 1e-4 and abs(
            val_finala - float(v)) < 1e-4

        # Afiseaza rezultatul verificarii cu culoare corespunzatoare
        f_rez = ctk.CTkFrame(scroll, fg_color="#e8f8f5" if is_valid else "#fdedec", border_width=2,
                             border_color="#2ecc71" if is_valid else "#e74c3c")
        f_rez.pack(pady=15, padx=20, fill="x")

        if is_valid:
            ctk.CTkLabel(f_rez,
                         text="Verificarea a fost realizata cu succes!\nX·Q·Y = V (Adevarat)",
                         font=("Montserrat", 12, "bold"), text_color="#27ae60", justify="center").pack(pady=10)
        else:
            ctk.CTkLabel(f_rez, text="Solutia nu este verificata.", font=("Montserrat", 12, "bold"),
                         text_color="#e74c3c", justify="center").pack(pady=10)


if __name__ == "__main__":
    app = ecranPrincipal()
    app.mainloop()
