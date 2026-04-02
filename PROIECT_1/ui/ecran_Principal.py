import customtkinter as ctk
from tkinter import messagebox
import numpy as np
from ui.tabel_Simplex import tabelSimplex
from core.transformare_PLS import transformarePLS
from core.validare import validare_metoda_I, validare_feazibilitate
from tkinter import font

class ecranPrincipal(ctk.CTk):

    # seteaza iconita ferestrei
    def seteaza_iconita(self):
        self.iconbitmap("fsa.ico")

    def __init__(self):
        super().__init__()

        # titlu si dimensiune fereastra
        self.title("PROGRAMARE LINIARA - Optimizarea alocării serverelor într-un data center")
        self.geometry("900x700")

        # tema aplicatiei
        ctk.set_appearance_mode("light")

        # incarcare iconita dupa pornire
        self.after(200, self.seteaza_iconita)

        # panou sus cu setari
        self.panou_config = ctk.CTkFrame(self, fg_color="transparent")
        self.configure(fg_color="#dceeff")
        self.panou_config.pack(pady=10, padx=20, fill="x")

        # alegere MIN / MAX
        self.meniu_tip = ctk.CTkOptionMenu(
            self.panou_config,
            values=["MIN", "MAX"],
            width=80,
            text_color="#ffffff",
            dropdown_fg_color="#ffffff",
            dropdown_hover_color="#dceeff",
            fg_color="#759dff",
            button_color="#6390ff",
            button_hover_color="#5284ff",
            dropdown_text_color="#294280",
            font=("Montserrat", 12, "bold"),
            dropdown_font=("Montserrat", 12)
        )
        self.meniu_tip.grid(row=0, column=0, padx=5)

        # input numar variabile
        self.input_nr_var = ctk.CTkEntry(
            self.panou_config,
            width=130,
            placeholder_text="Nr. Variabile",
            font=("Montserrat", 12),
            placeholder_text_color="#a4b9cc",
            fg_color="#ffffff",
            border_width=2,
            border_color="#b9ddff",
            text_color="#294280"
        )
        self.input_nr_var.grid(row=0, column=1, padx=5)

        # input numar restrictii
        self.input_nr_restr = ctk.CTkEntry(
            self.panou_config,
            width=130,
            placeholder_text="Nr. Restrictii",
            font=("Montserrat", 12),
            placeholder_text_color="#a4b9cc",
            fg_color="#ffffff",
            border_width=2,
            border_color="#b9ddff",
            text_color="#294280"
        )
        self.input_nr_restr.grid(row=0, column=2, padx=5)

        # buton generare problema
        ctk.CTkButton(
            self.panou_config,
            text="GENEREAZA P.L.",
            font=("Montserrat", 12, "bold"),
            text_color="#ffffff",
            fg_color="#5284ff",
            hover_color="#4a77e6",
            command=self.genereazaInput
        ).grid(row=0, column=3, padx=10)

        # zona unde introducem datele
        self.zona_date_intrare = ctk.CTkFrame(self, fg_color="#ffffff")
        self.zona_date_intrare.pack(pady=10, padx=20, fill="x")

        # zona unde se afiseaza pasii rezolvarii
        self.zona_rezolvare = ctk.CTkScrollableFrame(
            self,
            label_text="PASI REZOLVARE",
            fg_color="#93c5f2",
            label_font=("Montserrat", 14, "bold"),
            label_fg_color="#afd9ff",
            label_text_color="#ffffff",
            scrollbar_button_color="#6d91b3",
            scrollbar_button_hover_color="#4e6880"
        )
        self.zona_rezolvare.pack(pady=5, padx=20, fill="both", expand=True)

        # buton calcul simplex
        self.buton_calcul = ctk.CTkButton(
            self,
            text="CALCULEAZA OPTIM",
            text_color="#ffffff",
            fg_color="#5284ff",
            font=("Montserrat", 12, "bold"),
            hover_color="#4a77e6",
            command=self.ASP
        )
        self.buton_calcul.pack_forget()

        # buton validare rezultat
        self.buton_validare = ctk.CTkButton(
            self,
            text="VALIDARE SOLUTIE",
            text_color="#ffffff",
            fg_color="#5284ff",
            font=("Montserrat", 12, "bold"),
            hover_color="#4a77e6",
            command=self.valideaza_solutia
        )
        self.buton_validare.pack_forget()

        # liste unde tin datele introduse
        self.lista_coef_A, self.lista_coef_C, self.lista_termeni_B = [], [], []
        self.lista_semne_restr, self.lista_cond_semn = [], []

        # pentru navigare intre campuri
        self.grid_entries = []

    # muta focusul intre campuri cu sageti
    def muta_focus(self, entry_curent, directie):
        for i, rand in enumerate(self.grid_entries):
            for j, entry in enumerate(rand):
                if entry == entry_curent:
                    ni, nj = i, j

                    # directia apasata
                    if directie == "stanga": nj -= 1
                    elif directie == "dreapta": nj += 1
                    elif directie == "sus": ni -= 1
                    elif directie == "jos": ni += 1

                    # daca e valid, mutam focusul
                    if 0 <= ni < len(self.grid_entries) and 0 <= nj < len(self.grid_entries[ni]):
                        self.grid_entries[ni][nj].focus_set()
                    return

    # genereaza campurile de input
    def genereazaInput(self):
        # resetam listele vechi
        self.lista_coef_A.clear()
        self.lista_coef_C.clear()
        self.lista_termeni_B.clear()
        self.lista_semne_restr.clear()
        self.lista_cond_semn.clear()
        self.grid_entries.clear()

        # stergem UI vechi
        for elem in self.zona_date_intrare.winfo_children():
            elem.destroy()
        for elem in self.zona_rezolvare.winfo_children():
            elem.destroy()

        try:
            nr_var = int(self.input_nr_var.get())
            nr_restr = int(self.input_nr_restr.get())
        except:
            messagebox.showerror("Eroare", "Introdu numere valide!")
            return

        # functie obiectiv
        ctk.CTkLabel(
            self.zona_date_intrare,
            text="1. Coeficienti functia obiectiv f(x):",
            text_color="#294280",
            font=("Montserrat", 12, "bold")
        ).pack(anchor="w", pady=(5, 2))

        rand_f_ob = ctk.CTkFrame(self.zona_date_intrare, fg_color="transparent")
        rand_f_ob.pack(anchor="w")

        rand_entries = []

        # campuri pentru functia obiectiv
        for j in range(nr_var):
            e = ctk.CTkEntry(rand_f_ob, width=70, placeholder_text=f"x{j+1}",
                             placeholder_text_color="#a4b9cc",
                             fg_color="#ffffff",
                             border_width=2,
                             border_color="#b9ddff",
                             text_color="#294280",
                             font=("Montserrat", 12))

            e.pack(side="left", padx=2)

            # navigare cu sageti
            e.bind("<Left>", lambda ev, ent=e: self.muta_focus(ent, "stanga"))
            e.bind("<Right>", lambda ev, ent=e: self.muta_focus(ent, "dreapta"))
            e.bind("<Up>", lambda ev, ent=e: self.muta_focus(ent, "sus"))
            e.bind("<Down>", lambda ev, ent=e: self.muta_focus(ent, "jos"))

            self.lista_coef_C.append(e)
            rand_entries.append(e)

        self.grid_entries.append(rand_entries)

        # restrictii
        ctk.CTkLabel(
            self.zona_date_intrare,
            text="2. Coeficienti restrictii:",
            text_color="#294280",
            font=("Montserrat", 12, "bold")
        ).pack(anchor="w", pady=(15, 2))

        for i in range(nr_restr):
            rand_restr = ctk.CTkFrame(self.zona_date_intrare, fg_color="transparent")
            rand_restr.pack(anchor="w", pady=1)

            coef_linie = []
            rand_entries = []

            # coeficienti restrictii
            for j in range(nr_var):
                e = ctk.CTkEntry(rand_restr, width=70, placeholder_text=f"x{j+1}",
                                 placeholder_text_color="#a4b9cc",
                                 fg_color="#ffffff",
                                 border_width=2,
                                 border_color="#b9ddff",
                                 text_color="#294280",
                                 font=("Montserrat", 12))

                e.pack(side="left", padx=2)

                e.bind("<Left>", lambda ev, ent=e: self.muta_focus(ent, "stanga"))
                e.bind("<Right>", lambda ev, ent=e: self.muta_focus(ent, "dreapta"))
                e.bind("<Up>", lambda ev, ent=e: self.muta_focus(ent, "sus"))
                e.bind("<Down>", lambda ev, ent=e: self.muta_focus(ent, "jos"))

                coef_linie.append(e)
                rand_entries.append(e)

            self.lista_coef_A.append(coef_linie)
            self.grid_entries.append(rand_entries)

            # semn restrictie
            s = ctk.CTkOptionMenu(rand_restr, values=["≤", "≥", "="],
                                  width=75,
                                  text_color="#ffffff",
                                  dropdown_fg_color="#ffffff",
                                  dropdown_hover_color="#dceeff",
                                  fg_color="#759dff",
                                  button_color="#6390ff",
                                  button_hover_color="#5284ff",
                                  dropdown_text_color="#294280",
                                  font=("Montserrat", 12, "bold"),
                                  dropdown_font=("Montserrat", 12))
            s.pack(side="left", padx=10)
            self.lista_semne_restr.append(s)

            # termen liber b
            eb = ctk.CTkEntry(rand_restr, width=70, placeholder_text=f"b{i+1}",
                              placeholder_text_color="#a4b9cc",
                              fg_color="#ffffff",
                              border_width=2,
                              border_color="#b9ddff",
                              text_color="#294280",
                              font=("Montserrat", 12))

            eb.pack(side="left", padx=2)

            self.lista_termeni_B.append(eb)
            self.grid_entries.append([eb])

        # conditii semn variabile
        ctk.CTkLabel(
            self.zona_date_intrare,
            text="3. Conditii de semn:",
            text_color="#294280",
            font=("Montserrat", 12, "bold")
        ).pack(anchor="w", pady=(15, 2))

        rand_conditii = ctk.CTkFrame(self.zona_date_intrare, fg_color="transparent")
        rand_conditii.pack(anchor="w")

        # fiecare variabila are conditie
        for j in range(nr_var):
            cond = ctk.CTkOptionMenu(rand_conditii,
                                     values=[f"x{j+1} ≥ 0", f"x{j+1} ≤ 0", f"x{j+1} ∈ R"],
                                     width=100,
                                     text_color="#ffffff",
                                     dropdown_fg_color="#ffffff",
                                     dropdown_hover_color="#dceeff",
                                     fg_color="#759dff",
                                     button_color="#6390ff",
                                     button_hover_color="#5284ff",
                                     dropdown_text_color="#294280",
                                     font=("Montserrat", 12, "bold"),
                                     dropdown_font=("Montserrat", 12))
            cond.pack(side="left", padx=2)
            self.lista_cond_semn.append(cond)

        # afisam butonul de calcul
        self.buton_calcul.pack(pady=10)

    # aici ruleaza simplex
    def ASP(self):
        # stergem rezultatele vechi
        for elem in self.zona_rezolvare.winfo_children():
            elem.destroy()

        try:
            tip = self.meniu_tip.get()

            # salvam datele introduse
            nr_var_orig = len(self.lista_coef_C)

            c_vals = [float(e.get().replace(',', '.')) for e in self.lista_coef_C]
            a_vals = [[float(e.get().replace(',', '.')) for e in rand] for rand in self.lista_coef_A]
            b_vals = [float(e.get().replace(',', '.')) for e in self.lista_termeni_B]

            # salvam pentru validare
            self.A_orig_valid = np.array(a_vals, dtype=float)
            self.b_orig_valid = np.array(b_vals, dtype=float)
            self.c_orig_valid = np.array(c_vals, dtype=float)

            # transformam problema in forma standard
            mat_p, cost_p, b_p, bz_p, nume_p = transformarePLS(
                c_vals, a_vals, b_vals,
                self.lista_semne_restr,
                self.lista_cond_semn,
                tip
            )

            # salvam coloane initiale
            self.coloane_init_dict = {}
            for j in range(mat_p.shape[1]):
                self.coloane_init_dict[nume_p[j]] = mat_p[:, j].copy()

            tab, xb = mat_p.copy(), b_p.copy()

            # iteratii simplex
            for it in range(10):

                cb_l = cost_p[bz_p]

                delte = np.array([cost_p[j] - np.dot(cb_l, tab[:, j]) for j in range(tab.shape[1])])

                cp = np.argmin(delte) if tip == "MIN" else np.argmax(delte)

                # verificam optimul
                if (tip == "MIN" and delte[cp] >= -1e-4) or (tip == "MAX" and delte[cp] <= 1e-4):

                    self.xb_final_valid = xb.copy()
                    self.bz_final_valid = bz_p.copy()
                    self.nume_final_valid = nume_p.copy()

                    tabelSimplex(self.zona_rezolvare, "SOLUTIE OPTIMA GASITA",
                                 tab, xb, cost_p, delte, bz_p, nume_p)

                    self.afiseazaSolutie(xb, bz_p, nume_p, nr_var_orig,
                                          np.dot(cb_l, xb), tip)

                    self.buton_validare.pack(pady=5)
                    return

                raps = [xb[i] / tab[i, cp] if tab[i, cp] > 1e-9 else np.inf for i in range(len(xb))]
                rp = np.argmin(raps)

                if raps[rp] == np.inf:
                    messagebox.showwarning("Atentie", "Problema nu este marginita!")
                    return

                tabelSimplex(self.zona_rezolvare, f"Iteratia {it}",
                             tab, xb, cost_p, delte, bz_p, nume_p, (rp, cp))

                # pivot
                v_p = tab[rp, cp]
                tab[rp, :] /= v_p
                xb[rp] /= v_p

                for i in range(len(xb)):
                    if i != rp:
                        f = tab[i, cp]
                        tab[i, :] -= f * tab[rp, :]
                        xb[i] -= f * xb[rp]

                bz_p[rp] = cp

        except Exception as ex:
            messagebox.showerror("Eroare", f"Date invalide!\n{ex}")

    # verificam solutia obtinuta
    def valideaza_solutia(self):
        try:
            nr_orig = len(self.lista_coef_C)
            semne_originale = [s.get() for s in self.lista_semne_restr]

            # refacem matricea bazei
            S = []
            for idx_nume in self.bz_final_valid:
                nume_v = self.nume_final_valid[idx_nume]
                S.append(self.coloane_init_dict[nume_v])
            S = np.array(S).T

            X_sol = np.zeros(nr_orig)

            # reconstruim solutia finala
            for i, idx in enumerate(self.bz_final_valid):
                nm = self.nume_final_valid[idx]
                val = self.xb_final_valid[i]

                for k in range(1, nr_orig + 1):
                    px = f"x{k}"

                    if nm == px:
                        X_sol[k - 1] = val
                    elif nm == px + "'":
                        X_sol[k - 1] = -val
                    elif nm == px + "+":
                        X_sol[k - 1] += val
                    elif nm == px + "-":
                        X_sol[k - 1] -= val

            ok1, msg1 = validare_metoda_I(self.b_orig_valid, self.xb_final_valid, S)

            ok2, msg2 = validare_feazibilitate(
                X_sol,
                self.A_orig_valid,
                self.b_orig_valid,
                semne_originale,
                self.c_orig_valid,
                np.dot(self.c_orig_valid, X_sol)
            )

            messagebox.showinfo("Rezultat Validare", f"Metoda I: {msg1}\n\nMetoda II: {msg2}")

        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare validare: {e}")

    # afisare rezultat final
    def afiseazaSolutie(self, xb_f, baza_f, nume_f, nr_var_orig, valoare_f, tip):
        cadru_final = ctk.CTkFrame(self.zona_rezolvare,
                                   border_width=2,
                                   border_color="#9bcfff",
                                   fg_color="#ffffff")
        cadru_final.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(cadru_final,
                     text=" REZULTAT FINAL ",
                     font=("Montserrat", 14, "bold"),
                     text_color="#3645a4").pack(pady=5)

        solutie_variabile = {f"x{i+1}": 0.0 for i in range(nr_var_orig)}

        # reconstruim valorile variabilelor
        for i, idx in enumerate(baza_f):
            nm = nume_f[idx]

            for k in range(1, nr_var_orig + 1):
                pk = f"x{k}"

                if nm.startswith(pk):
                    if "+" in nm:
                        solutie_variabile[pk] += xb_f[i]
                    elif "-" in nm:
                        solutie_variabile[pk] -= xb_f[i]
                    elif "'" in nm:
                        solutie_variabile[pk] = -xb_f[i]
                    else:
                        solutie_variabile[pk] = xb_f[i]

        mesaj = f"Valoare Optima: f({tip}) = {valoare_f:.2f}\n"

        for var_nume, valoare in solutie_variabile.items():
            mesaj += f"  {var_nume} = {valoare:.2f}\n"

        ctk.CTkLabel(cadru_final,
                     text=mesaj,
                     font=("Montserrat", 12),
                     justify="left").pack(pady=10, padx=20)