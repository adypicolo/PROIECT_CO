import customtkinter as ctk
from utils.conversie_Fractie import transformaraFractie

# =====================================================================
# 2. UI: Tabel Simplex
# =====================================================================
class tabelSimplex(ctk.CTkFrame):
    def __init__(self, container, titlu, matrice, coloana_xb, costuri, deltas, baza, nume_variabile, pivot=None,
                 iteratie=0):
        super().__init__(container, border_width=2, border_color="#9bcfff", fg_color="#ffffff")
        self.pack(pady=10, padx=10, fill="x")

        # titlul tabelului
        ctk.CTkLabel(
            self, text=titlu, font=("Montserrat", 14, "bold"),
            text_color="#294280", fg_color="transparent"
        ).pack(pady=5)

        # zona unde desenam tabelul simplex
        f_grila = ctk.CTkFrame(self, fg_color="transparent")
        f_grila.pack(pady=5)

        nr_linii, nr_coloane = len(baza), len(costuri)

        CULOARE_CRUCE = "#9bcfff"
        CULOARE_PIVOT = "#5284ff"
        CULOARE_NEGATIV = "#FF5252"
        CULOARE_POZITIV = "#2ECC71"

        # Eticheta MAX
        ctk.CTkLabel(
            f_grila, text="MAX", width=75,
            font=("Montserrat", 12, "bold"), text_color="#e74c3c", fg_color="#fce4e4"
        ).grid(row=0, column=2, padx=1, pady=1)

        # antet variabile
        for j in range(nr_coloane):
            ctk.CTkLabel(
                f_grila, text=nume_variabile[j], width=75,
                font=("Montserrat", 12, "bold"), text_color="#ffffff", fg_color="#6d91b3"
            ).grid(row=0, column=3 + j, padx=1, pady=1)

        # Cj
        ctk.CTkLabel(f_grila, text="Cj", width=75, font=("Montserrat", 12, "bold"), text_color="#294280",
                     fg_color="#cde7ff").grid(row=1, column=2, padx=1, pady=1)
        for j, val in enumerate(costuri):
            fundal = CULOARE_CRUCE if (pivot and j == pivot[1]) else "#cde7ff"
            ctk.CTkLabel(f_grila, text=transformaraFractie(val), width=75, font=("Montserrat", 12, "bold"),
                         text_color="#294280", fg_color=fundal).grid(row=1, column=3 + j, padx=1, pady=1)

        # antet stanga
        for j, text_antet in enumerate(["CB", "B", "XB"]):
            ctk.CTkLabel(
                f_grila, text=text_antet, width=75,
                font=("Montserrat", 12, "bold"), text_color="#ffffff", fg_color="#6d91b3"
            ).grid(row=2, column=j, padx=1, pady=1)

        # linii tabel
        for i in range(nr_linii):
            idx_variabila_baza = baza[i]
            fundal_linie = CULOARE_CRUCE if (pivot and i == pivot[0]) else "transparent"
            text_color_linie = "#ffffff" if (pivot and i == pivot[0]) else "#294280"

            ctk.CTkLabel(f_grila, text=transformaraFractie(costuri[idx_variabila_baza]), width=75,
                         fg_color=fundal_linie, text_color=text_color_linie).grid(row=3 + i, column=0, padx=1, pady=1)
            ctk.CTkLabel(f_grila, text=nume_variabile[idx_variabila_baza], width=75, fg_color=fundal_linie,
                         text_color=text_color_linie).grid(row=3 + i, column=1, padx=1, pady=1)
            ctk.CTkLabel(f_grila, text=transformaraFractie(coloana_xb[i]), width=75, fg_color=fundal_linie,
                         text_color=text_color_linie).grid(row=3 + i, column=2, padx=1, pady=1)

            for j in range(nr_coloane):
                culoare_celula = "#f0f5fa"
                text_col = "#294280"

                if pivot:
                    if i == pivot[0] and j == pivot[1]:
                        culoare_celula = CULOARE_PIVOT
                        text_col = "#ffffff"
                    elif i == pivot[0] or j == pivot[1]:
                        culoare_celula = CULOARE_CRUCE
                        text_col = "#ffffff"

                font_celula = ("Montserrat", 12, "bold") if (pivot and i == pivot[0] and j == pivot[1]) else (
                    "Montserrat", 12)

                ctk.CTkLabel(
                    f_grila, text=transformaraFractie(matrice[i, j]), width=75,
                    fg_color=culoare_celula, text_color=text_col, font=font_celula
                ).grid(row=3 + i, column=3 + j, padx=1, pady=1)

        # Calcul Zj si Z0
        cb = [costuri[idx] for idx in baza]
        z_j = [sum(cb[i] * matrice[i, j] for i in range(nr_linii)) for j in range(nr_coloane)]
        z_0 = sum(cb[i] * coloana_xb[i] for i in range(nr_linii))

        rand_zj = 3 + nr_linii
        rand_delta = 4 + nr_linii

        text_z = f"Z^{iteratie} = {transformaraFractie(z_0)}"
        ctk.CTkLabel(
            f_grila, text=text_z, font=("Montserrat", 12, "bold"), text_color="#294280"
        ).grid(row=rand_zj, column=1, columnspan=2, padx=1, pady=(5, 1))

        for j, z_val in enumerate(z_j):
            fundal_zj = CULOARE_CRUCE if (pivot and j == pivot[1]) else "transparent"
            text_color_zj = "#ffffff" if (pivot and j == pivot[1]) else "#294280"
            ctk.CTkLabel(
                f_grila, text=transformaraFractie(z_val),
                font=("Montserrat", 12, "bold"), text_color=text_color_zj,
                fg_color=fundal_zj, width=75
            ).grid(row=rand_zj, column=3 + j, padx=1, pady=(5, 1))

        # Delta
        ctk.CTkLabel(
            f_grila, text="Δj", font=("Montserrat", 12, "bold"), text_color="#294280"
        ).grid(row=rand_delta, column=1, columnspan=2, pady=(1, 5))

        for j, d_val in enumerate(deltas):
            culoare_text = CULOARE_POZITIV if d_val <= 1e-9 else CULOARE_NEGATIV
            fundal_delta = CULOARE_CRUCE if (pivot and j == pivot[1]) else "transparent"

            ctk.CTkLabel(
                f_grila, text=transformaraFractie(d_val),
                font=("Montserrat", 12, "bold"), text_color=culoare_text,
                fg_color=fundal_delta, width=75
            ).grid(row=rand_delta, column=3 + j, padx=1, pady=(1, 5))