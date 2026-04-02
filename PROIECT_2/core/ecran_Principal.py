# core/ecran_Principal.py
import customtkinter as ctk
import numpy as np
from core.tabel_Simplex import SimplexFrame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ecranPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Teoria jocurilor matriceale")
        self.geometry("900x700")

        # Frame principal pentru input
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10, padx=10, fill="x")

        # Dimensiuni joc
        ctk.CTkLabel(self.input_frame, text="Număr strategii jucător A (m):", font=("Arial", 12)).grid(row=0, column=0,
                                                                                                       padx=5, pady=5,
                                                                                                       sticky="e")
        self.m_entry = ctk.CTkEntry(self.input_frame, width=80)
        self.m_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.input_frame, text="Număr strategii jucător B (n):", font=("Arial", 12)).grid(row=1, column=0,
                                                                                                       padx=5, pady=5,
                                                                                                       sticky="e")
        self.n_entry = ctk.CTkEntry(self.input_frame, width=80)
        self.n_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buton generare matrice
        self.generate_button = ctk.CTkButton(self.input_frame, text="Generează matricea Q",
                                             command=self.genereaza_Q, width=200)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame pentru matricea Q
        self.q_frame = ctk.CTkFrame(self)
        self.q_frame.pack(pady=10, padx=10, fill="x")
        self.q_entries = []

        # Buton rezolvare
        self.solve_button = ctk.CTkButton(self, text="Rezolvă jocul",
                                          command=self.determina_solutia,
                                          width=200, height=40,
                                          font=("Arial", 14, "bold"))
        self.solve_button.pack(pady=15)

        # Frame pentru rezultate
        self.result_frame = None

    def genereaza_Q(self):
        # Șterge conținutul vechi
        for widget in self.q_frame.winfo_children():
            widget.destroy()
        self.q_entries.clear()

        try:
            m = int(self.m_entry.get())
            n = int(self.n_entry.get())

            if m <= 0 or n <= 0:
                return
        except:
            return

        # Adaugă titlu
        ctk.CTkLabel(self.q_frame, text="Introduceți matricea plăților:",
                     font=("Arial", 12, "bold")).pack(pady=5)

        # Creează grid pentru matrice
        grid_frame = ctk.CTkFrame(self.q_frame)
        grid_frame.pack(pady=5)

        for i in range(m):
            row_entries = []
            for j in range(n):
                entry = ctk.CTkEntry(grid_frame, width=60, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(entry)
            self.q_entries.append(row_entries)

    def determina_solutia(self):
        # Extrage matricea Q
        try:
            if not self.q_entries:
                return

            m = len(self.q_entries)
            n = len(self.q_entries[0])

            Q = np.zeros((m, n))
            for i in range(m):
                for j in range(n):
                    val = self.q_entries[i][j].get()
                    if val == "":
                        return
                    Q[i, j] = float(val)
        except:
            return

        # Calculează v1 și v2
        alpha = np.min(Q, axis=1)  # minim pe linii
        beta = np.max(Q, axis=0)  # maxim pe coloane
        v1 = np.max(alpha)  # maximin
        v2 = np.min(beta)  # minimax

        # Elimină frame-ul vechi de rezultate
        if self.result_frame:
            self.result_frame.destroy()

        # Creează noul frame cu rezultatele
        self.result_frame = SimplexFrame(self, Q, v1, v2)
        self.result_frame.pack(pady=10, padx=10, fill="both", expand=True)