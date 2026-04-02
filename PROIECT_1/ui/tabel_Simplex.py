import customtkinter as ctk
from utils.conversie_Fractie import transformaraFractie

class tabelSimplex(ctk.CTkFrame):
    def __init__(self, container, titlu, matrice, coloana_xb, costuri, deltas, baza, nume_variabile, pivot=None):
        super().__init__(container, border_width=2, border_color="#9bcfff", fg_color="#ffffff")
        self.pack(pady=8, padx=10, fill="x")

        # titlul tabelului (ex: iteratia curenta sau solutie finala)
        ctk.CTkLabel(
            self,
            text=titlu,
            font=("Montserrat", 14, "bold"),
            text_color="#294280",
            fg_color="transparent"
        ).pack(pady=2)

        # zona unde desenam tabelul simplex
        f_grila = ctk.CTkFrame(self, fg_color="transparent")
        f_grila.pack(pady=5)

        nr_linii, nr_coloane = len(baza), len(costuri)

        # culori folosite in tabel (doar pentru evidentiere)
        CULOARE_CRUCE = "#9bcfff"
        CULOARE_PIVOT = "#5284ff"
        CULOARE_NEGATIV = "#FF5252"
        CULOARE_POZITIV = "#2ECC71"

        # afisam numele variabilelor sus in tabel
        for j in range(nr_coloane):
            ctk.CTkLabel(
                f_grila,
                text=nume_variabile[j],
                width=75,
                font=("Montserrat", 12, "bold"),
                text_color="#ffffff",
                fg_color="#6d91b3"
            ).grid(row=0, column=3 + j)

        # linia cu costurile Cj
        ctk.CTkLabel(f_grila, text="Cj", width=75, fg_color="#cde7ff").grid(row=1, column=2)

        for j, val in enumerate(costuri):
            # daca suntem pe coloana pivot, o evidentiem
            fundal = CULOARE_CRUCE if (pivot and j == pivot[1]) else "#cde7ff"
            ctk.CTkLabel(f_grila, text=transformaraFractie(val), width=75, fg_color=fundal).grid(row=1, column=3 + j)

        # anteturile coloanelor principale
        for j, text_antet in enumerate(["CB", "B", "XB"]):
            ctk.CTkLabel(
                f_grila,
                text=text_antet,
                width=75,
                font=("Montserrat", 12, "bold"),
                text_color="#ffffff",
                fg_color="#6d91b3"
            ).grid(row=2, column=j)

        # construim tabelul pe randuri
        for i in range(nr_linii):
            idx_variabila_baza = baza[i]

            # evidentiem linia pivot daca exista
            fundal_linie = CULOARE_CRUCE if (pivot and i == pivot[0]) else "transparent"

            # CB, B si XB (partea din stanga a tabelului)
            ctk.CTkLabel(f_grila, text=transformaraFractie(costuri[idx_variabila_baza]), width=75, fg_color=fundal_linie).grid(row=3 + i, column=0)
            ctk.CTkLabel(f_grila, text=nume_variabile[idx_variabila_baza], width=75, fg_color=fundal_linie).grid(row=3 + i, column=1)
            ctk.CTkLabel(f_grila, text=transformaraFractie(coloana_xb[i]), width=75, fg_color=fundal_linie).grid(row=3 + i, column=2)

            # valorile din matricea simplex
            for j in range(nr_coloane):
                culoare_celula = "transparent"

                # daca avem pivot, coloram linia si coloana lui
                if pivot:
                    if i == pivot[0] and j == pivot[1]:
                        culoare_celula = CULOARE_PIVOT
                    elif i == pivot[0] or j == pivot[1]:
                        culoare_celula = CULOARE_CRUCE

                # font mai gros doar pe pivot
                if pivot and i == pivot[0] and j == pivot[1]:
                    font_celula = ("Montserrat", 12, "bold")
                else:
                    font_celula = ("Montserrat", 12)

                ctk.CTkLabel(
                    f_grila,
                    text=transformaraFractie(matrice[i, j]),
                    width=75,
                    fg_color=culoare_celula,
                    font=font_celula
                ).grid(row=3 + i, column=3 + j)

        # linia Delta (costuri reduse)
        ctk.CTkLabel(
            f_grila,
            text="Delta_j",
            font=("Montserrat", 12, "bold")
        ).grid(row=3 + nr_linii, column=2, pady=5)

        for j, d_val in enumerate(deltas):
            # coloram valorile in functie de semn
            culoare_text = CULOARE_POZITIV if d_val >= -0.0001 else CULOARE_NEGATIV

            # evidentiem coloana pivot daca exista
            fundal_delta = CULOARE_CRUCE if (pivot and j == pivot[1]) else "transparent"

            ctk.CTkLabel(
                f_grila,
                text=transformaraFractie(d_val),
                font=("Montserrat", 12, "bold"),
                text_color=culoare_text,
                fg_color=fundal_delta,
                width=75
            ).grid(row=3 + nr_linii, column=3 + j)
