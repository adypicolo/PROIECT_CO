from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..algoritmi.algoritm_ford_fulkerson import ruleaza_ford_fulkerson
from ..algoritmi.algoritm_seminar import ruleaza_mod_seminar
from ..configurare.constante import (
    DEFINITII_ARCE_SEMINAR,
    EXEMPLU_SEMINAR_DESTINATIA,
    EXEMPLU_SEMINAR_NODURI,
    EXEMPLU_SEMINAR_SURSA,
)
from ..grafuri.desen_graf import deseneaza_graf
from ..grafuri.graf_date import (
    construieste_graf_din_exemplu,
    construieste_graf_generic,
    genereaza_nume_noduri,
    valideaza_numar_intreg,
)
from ..modele.modele import Graf, PasAlgoritm, RezultatRulare
from ..configurare.stil import DIMENSIUNI, FONTURI, PALETA_LUMINOASA, VITEZE_ANIMATIE


class AplicatieFordFulkerson(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ford-Fulkerson - aplicatie generala")
        self.geometry("1460x860")
        self.minsize(DIMENSIUNI["latime_minima"], DIMENSIUNI["inaltime_minima"])

        self.rezultat_var = tk.StringVar(value="Flux maxim: -")
        self.status_var = tk.StringVar(value="Completeaza manual reteaua, apoi genereaza campurile.")
        self.numar_noduri_var = tk.StringVar(value="")
        self.numar_arce_var = tk.StringVar(value="")
        self.sursa_var = tk.StringVar(value="")
        self.destinatie_var = tk.StringVar(value="")

        self.paleta = PALETA_LUMINOASA
        self.graf_curent: Graf | None = None
        self.rezultat_curent: RezultatRulare | None = None
        self.index_pas_curent = 0
        self.animatie_programata: str | None = None
        self.redesenare_programata: str | None = None
        self.actualizare_layout_programata: str | None = None
        self.inaltime_explicatii_curenta = 160
        self.drag_separator_activ = False
        self.text_verificare_finala = ""
        self.noduri_curente: list[str] = []
        self.linii_arce: list[dict[str, object]] = []
        self.mod_seminar_disponibil = False

        ctk.set_appearance_mode("light")
        self.configure(fg_color=self.paleta["fundal"])
        self._construieste_layout()
        self._pregateste_stare_initiala()
        self._configureaza_redimensionare()

    def _construieste_layout(self) -> None:
        self.grid_columnconfigure(0, weight=3, minsize=380)
        self.grid_columnconfigure(1, weight=7, minsize=760)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.panou_stanga = ctk.CTkFrame(self, fg_color=self.paleta["panou"], corner_radius=20)
        self.panou_stanga.grid(row=0, column=0, sticky="nswe", padx=(16, 10), pady=16)
        self.panou_stanga.grid_rowconfigure(1, weight=1)

        self.panou_dreapta = ctk.CTkFrame(self, fg_color="transparent")
        self.panou_dreapta.grid(row=0, column=1, sticky="nswe", padx=(0, 16), pady=16)
        self.panou_dreapta.grid_columnconfigure(0, weight=1)
        self.panou_dreapta.grid_rowconfigure(0, weight=1)

        self._construieste_panou_stanga(self.panou_stanga)
        self._construieste_panou_dreapta(self.panou_dreapta)
        self._construieste_legenda(self.panou_stanga)

    def _pregateste_stare_initiala(self) -> None:
        self.noduri_curente = []
        self.selector_sursa.configure(values=[""])
        self.selector_destinatie.configure(values=[""])
        self.sursa_var.set("")
        self.destinatie_var.set("")
        self._reface_tabel_arce(0)
        self.scrie_explicatii(
            "Aplicatia a pornit cu campurile goale.\n"
            "Completeaza numarul de noduri si numarul de arce, apoi apasa pe butonul de generare."
        )

    def _construieste_panou_stanga(self, parinte: ctk.CTkFrame) -> None:
        self.hero = ctk.CTkFrame(parinte, fg_color=self.paleta["panou_moale"], corner_radius=18)
        self.hero.pack(fill="x", padx=14, pady=(14, 10))
        self.titlu_hero = ctk.CTkLabel(self.hero, text="Retea generala", font=FONTURI["titlu"], text_color=self.paleta["text"])
        self.titlu_hero.pack(anchor="w", padx=16, pady=(14, 2))
        self.text_hero = ctk.CTkLabel(
            self.hero,
            text="Introduci din tastatura numarul de noduri, numarul de arce, sursa, destinatia si fiecare arc orientat.",
            wraplength=340,
            justify="left",
            font=FONTURI["normal"],
            text_color=self.paleta["text"],
        )
        self.text_hero.pack(anchor="w", padx=16, pady=(0, 12))

        self.cadru_control = ctk.CTkScrollableFrame(
            parinte,
            fg_color=self.paleta["panou"],
            corner_radius=18,
            border_width=1,
            border_color=self.paleta["bordura"],
        )
        self.cadru_control.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.cadru_control.grid_columnconfigure(0, weight=1)
        self.cadru_control.grid_columnconfigure(1, weight=1)

        self._adauga_config_retea()
        self._adauga_panou_arce()
        self._adauga_butoane_actiune()

    def _adauga_config_retea(self) -> None:
        ctk.CTkLabel(self.cadru_control, text="Configurare retea", font=FONTURI["subtitlu"], text_color=self.paleta["text"]).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(14, 8)
        )

        ctk.CTkLabel(self.cadru_control, text="Numar noduri", font=FONTURI["normal_bold"], text_color=self.paleta["text"]).grid(
            row=1, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        self.camp_numar_noduri = ctk.CTkEntry(
            self.cadru_control,
            textvariable=self.numar_noduri_var,
            fg_color=self.paleta["fundal_secundar"],
            border_color=self.paleta["bordura"],
            text_color=self.paleta["text"],
            font=FONTURI["normal"],
        )
        self.camp_numar_noduri.grid(row=2, column=0, padx=14, pady=(0, 8), sticky="we")

        ctk.CTkLabel(self.cadru_control, text="Numar arce", font=FONTURI["normal_bold"], text_color=self.paleta["text"]).grid(
            row=1, column=1, sticky="w", padx=14, pady=(0, 4)
        )
        self.camp_numar_arce = ctk.CTkEntry(
            self.cadru_control,
            textvariable=self.numar_arce_var,
            fg_color=self.paleta["fundal_secundar"],
            border_color=self.paleta["bordura"],
            text_color=self.paleta["text"],
            font=FONTURI["normal"],
        )
        self.camp_numar_arce.grid(row=2, column=1, padx=14, pady=(0, 8), sticky="we")

        self.buton_genereaza = ctk.CTkButton(
            self.cadru_control,
            text="Genereaza campurile retelei",
            command=self.genereaza_formular_retea,
            fg_color=self.paleta["accent_calduros"],
            hover_color=self.paleta["accent_calduros_hover"],
            font=FONTURI["normal_bold"],
        )
        self.buton_genereaza.grid(row=3, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="we")

        ctk.CTkLabel(self.cadru_control, text="Sursa", font=FONTURI["normal_bold"], text_color=self.paleta["text"]).grid(
            row=4, column=0, sticky="w", padx=14, pady=(0, 4)
        )
        ctk.CTkLabel(self.cadru_control, text="Destinatie", font=FONTURI["normal_bold"], text_color=self.paleta["text"]).grid(
            row=4, column=1, sticky="w", padx=14, pady=(0, 4)
        )
        self.selector_sursa = ctk.CTkOptionMenu(
            self.cadru_control,
            values=["x1", "x2"],
            variable=self.sursa_var,
            fg_color=self.paleta["accent_principal"],
            button_color=self.paleta["accent_principal"],
            button_hover_color=self.paleta["accent_principal_hover"],
            text_color=self.paleta["panou"],
        )
        self.selector_sursa.grid(row=5, column=0, padx=14, pady=(0, 10), sticky="we")
        self.selector_destinatie = ctk.CTkOptionMenu(
            self.cadru_control,
            values=["x1", "x2"],
            variable=self.destinatie_var,
            fg_color=self.paleta["accent_principal"],
            button_color=self.paleta["accent_principal"],
            button_hover_color=self.paleta["accent_principal_hover"],
            text_color=self.paleta["panou"],
        )
        self.selector_destinatie.grid(row=5, column=1, padx=14, pady=(0, 10), sticky="we")

    def _adauga_panou_arce(self) -> None:
        self.titlu_arce = ctk.CTkLabel(self.cadru_control, text="Date arce orientate", font=FONTURI["subtitlu"], text_color=self.paleta["text"])
        self.titlu_arce.grid(row=6, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 8))

        self.cadru_tabel_arce = ctk.CTkScrollableFrame(
            self.cadru_control,
            fg_color=self.paleta["fundal_secundar"],
            border_width=1,
            border_color=self.paleta["bordura"],
            height=280,
        )
        self.cadru_tabel_arce.grid(row=7, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="we")
        self.cadru_tabel_arce.grid_columnconfigure(0, weight=1)
        self.cadru_tabel_arce.grid_columnconfigure(1, weight=1)
        self.cadru_tabel_arce.grid_columnconfigure(2, weight=1)
        self.cadru_tabel_arce.grid_columnconfigure(3, weight=1)
        self.cadru_tabel_arce.grid_columnconfigure(0, minsize=88)
        self.cadru_tabel_arce.grid_columnconfigure(1, minsize=88)
        self.cadru_tabel_arce.grid_columnconfigure(2, minsize=92)
        self.cadru_tabel_arce.grid_columnconfigure(3, minsize=84)

    def _adauga_butoane_actiune(self) -> None:
        baza = 8
        self.buton_exemplu = ctk.CTkButton(
            self.cadru_control,
            text="Incarca exemplu seminar",
            command=self.incarca_exemplu_seminar,
            fg_color=self.paleta["panou_moale"],
            hover_color=self.paleta["accent_calduros"],
            text_color=self.paleta["text"],
        )
        self.buton_exemplu.grid(row=baza, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="we")

        self.buton_construieste = ctk.CTkButton(
            self.cadru_control,
            text="Construieste graful",
            command=self.construieste_graf_din_input,
            fg_color=self.paleta["accent_calduros"],
            hover_color=self.paleta["accent_calduros_hover"],
            font=FONTURI["normal_bold"],
        )
        self.buton_construieste.grid(row=baza + 1, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="we")

        self.buton_ruleaza = ctk.CTkButton(
            self.cadru_control,
            text="Ruleaza algoritmul",
            command=self.ruleaza_automat,
            fg_color=self.paleta["accent_principal"],
            hover_color=self.paleta["accent_principal_hover"],
            font=FONTURI["normal_bold"],
        )
        self.buton_ruleaza.grid(row=baza + 2, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="we")

        self.buton_pas_inapoi = ctk.CTkButton(
            self.cadru_control,
            text="Pas inapoi",
            command=self.pas_inapoi,
            fg_color=self.paleta["panou_moale"],
            hover_color=self.paleta["accent_calduros"],
            text_color=self.paleta["text"],
        )
        self.buton_pas_inapoi.grid(row=baza + 3, column=0, padx=(14, 7), pady=(0, 8), sticky="we")

        self.buton_pas_inainte = ctk.CTkButton(
            self.cadru_control,
            text="Pas inainte",
            command=self.pas_inainte,
            fg_color=self.paleta["panou_moale"],
            hover_color=self.paleta["accent_calduros"],
            text_color=self.paleta["text"],
        )
        self.buton_pas_inainte.grid(row=baza + 3, column=1, padx=(7, 14), pady=(0, 8), sticky="we")

        self.buton_reset = ctk.CTkButton(
            self.cadru_control,
            text="Reset",
            command=self.reseteaza_stare,
            fg_color=self.paleta["panou_moale"],
            hover_color=self.paleta["accent_calduros"],
            text_color=self.paleta["text"],
        )
        self.buton_reset.grid(row=baza + 4, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="we")

        self.buton_export = ctk.CTkButton(
            self.cadru_control,
            text="Export raport",
            command=self.exporta_raport,
            fg_color=self.paleta["accent_calduros"],
            hover_color=self.paleta["accent_calduros_hover"],
            font=FONTURI["normal_bold"],
        )
        self.buton_export.grid(row=baza + 5, column=0, columnspan=2, padx=14, pady=(0, 14), sticky="we")

    def _construieste_panou_dreapta(self, parinte: ctk.CTkFrame) -> None:
        continut = ctk.CTkFrame(parinte, fg_color="transparent")
        continut.grid(row=0, column=0, sticky="nswe")
        continut.grid_columnconfigure(0, weight=1)
        continut.grid_rowconfigure(0, weight=1)
        continut.grid_rowconfigure(1, weight=0, minsize=10)
        continut.grid_rowconfigure(2, weight=0, minsize=self.inaltime_explicatii_curenta)

        self.cadru_canvas = ctk.CTkFrame(continut, fg_color=self.paleta["panou"], corner_radius=18)
        self.cadru_canvas.grid(row=0, column=0, sticky="nswe")
        self.cadru_canvas.grid_rowconfigure(1, weight=1)
        self.cadru_canvas.grid_columnconfigure(0, weight=1)

        self.cadru_header_graf = ctk.CTkFrame(self.cadru_canvas, fg_color="transparent")
        self.cadru_header_graf.grid(row=0, column=0, sticky="we", padx=16, pady=(14, 6))
        self.cadru_header_graf.grid_columnconfigure(0, weight=1)
        self.cadru_header_graf.grid_columnconfigure(1, weight=0)

        self.label_rezultat = ctk.CTkLabel(
            self.cadru_header_graf,
            textvariable=self.rezultat_var,
            font=FONTURI["titlu"],
            text_color=self.paleta["accent_calduros"],
        )
        self.label_rezultat.grid(row=0, column=0, sticky="w")
        self.label_status = ctk.CTkLabel(
            self.cadru_header_graf,
            textvariable=self.status_var,
            font=FONTURI["normal"],
            text_color=self.paleta["text_secundar"],
            justify="left",
        )
        self.label_status.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.buton_verificare_finala = ctk.CTkButton(
            self.cadru_header_graf,
            text="Verificare finala",
            command=self.afiseaza_casuta_verificare,
            state="disabled",
            fg_color=self.paleta["accent_principal"],
            hover_color=self.paleta["accent_principal_hover"],
            font=FONTURI["normal_bold"],
            width=150,
        )
        self.buton_verificare_finala.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

        self.canvas_graf = ctk.CTkCanvas(self.cadru_canvas, highlightthickness=0)
        self.canvas_graf.grid(row=1, column=0, sticky="nswe", padx=14, pady=(0, 14))

        self.bara_separator = ctk.CTkFrame(continut, fg_color=self.paleta["fundal"], height=10, corner_radius=8)
        self.bara_separator.grid(row=1, column=0, sticky="ew", pady=(6, 6))
        self.bara_separator.bind("<ButtonPress-1>", self._incepe_redimensionarea_separatorului)
        self.bara_separator.bind("<ButtonRelease-1>", self._opreste_redimensionarea_separatorului)
        self.bara_separator.bind("<B1-Motion>", self._redimensioneaza_separatorul)
        self.bara_separator.bind("<Enter>", lambda _event: self.configure(cursor="sb_v_double_arrow"))
        self.bara_separator.bind("<Leave>", lambda _event: self.configure(cursor=""))

        self.cadru_explicatii = ctk.CTkFrame(continut, fg_color=self.paleta["panou"], corner_radius=18, height=160)
        self.cadru_explicatii.grid(row=2, column=0, sticky="ew")
        self.cadru_explicatii.pack_propagate(False)
        self.titlu_explicatii = ctk.CTkLabel(self.cadru_explicatii, text="Explicatii pas cu pas", font=FONTURI["subtitlu"], text_color=self.paleta["text"])
        self.titlu_explicatii.pack(anchor="w", padx=16, pady=(16, 6))
        self.text_explicatii = ctk.CTkTextbox(
            self.cadru_explicatii,
            wrap="word",
            font=FONTURI["normal"],
            fg_color=self.paleta["fundal_secundar"],
            text_color=self.paleta["text"],
            border_width=1,
            border_color=self.paleta["bordura"],
        )
        self.text_explicatii.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.text_explicatii.configure(state="disabled")

    def _construieste_legenda(self, parinte: ctk.CTkFrame) -> None:
        self.cadru_legenda = ctk.CTkFrame(parinte, fg_color=self.paleta["panou"], corner_radius=18)
        self.cadru_legenda.pack(fill="x", padx=14, pady=(0, 14))
        ctk.CTkLabel(self.cadru_legenda, text="Legenda:", font=FONTURI["normal_bold"], text_color=self.paleta["text"]).pack(side="left", padx=(14, 10), pady=10)
        self.legenda_puncte = []
        for text, culoare in [
            ("Arc normal", self.paleta["arc_normal"]),
            ("Arc saturat", self.paleta["arc_saturat"]),
            ("Drum curent", self.paleta["arc_drum"]),
            ("Arc invers", self.paleta["arc_invers"]),
        ]:
            label = ctk.CTkLabel(self.cadru_legenda, text=f"  {text}  ", fg_color=culoare, corner_radius=8, text_color="#FFFFFF")
            label.pack(side="left", padx=8, pady=10)
            self.legenda_puncte.append(label)

    def _configureaza_redimensionare(self) -> None:
        self.bind("<Configure>", self._la_redimensionare_fereastra)
        self.canvas_graf.bind("<Configure>", self._la_redimensionare_canvas)
        self.after(50, self._actualizeaza_layout_responsiv)

    def _la_redimensionare_fereastra(self, event: tk.Event) -> None:
        if event.widget is not self:
            return
        if self.actualizare_layout_programata is not None:
            self.after_cancel(self.actualizare_layout_programata)
        self.actualizare_layout_programata = self.after(80, self._actualizeaza_layout_responsiv)

    def _la_redimensionare_canvas(self, event: tk.Event) -> None:
        if event.widget is not self.canvas_graf:
            return
        if self.redesenare_programata is not None:
            self.after_cancel(self.redesenare_programata)
        self.redesenare_programata = self.after(80, self._redeseneaza_stare_curenta)

    def _actualizeaza_layout_responsiv(self) -> None:
        self.actualizare_layout_programata = None
        latime = max(self.winfo_width(), DIMENSIUNI["latime_minima"])
        inaltime = max(self.winfo_height(), DIMENSIUNI["inaltime_minima"])

        latime_stanga = max(380, min(520, int(latime * 0.30)))
        latime_dreapta = max(760, latime - latime_stanga - 52)
        inaltime_explicatii = max(140, min(240, int(inaltime * 0.18)))
        wrap_hero = max(280, latime_stanga - 110)

        self.grid_columnconfigure(0, minsize=latime_stanga)
        self.grid_columnconfigure(1, minsize=latime_dreapta)
        self.hero.configure(width=latime_stanga - 28)
        self.text_hero.configure(wraplength=wrap_hero)
        if not self.drag_separator_activ:
            self.inaltime_explicatii_curenta = inaltime_explicatii
        self.cadru_explicatii.configure(height=self.inaltime_explicatii_curenta)
        self.cadru_explicatii.master.grid_rowconfigure(2, minsize=self.inaltime_explicatii_curenta)

        if self.redesenare_programata is not None:
            self.after_cancel(self.redesenare_programata)
        self.redesenare_programata = self.after(50, self._redeseneaza_stare_curenta)

    def _incepe_redimensionarea_separatorului(self, _event: tk.Event) -> None:
        self.drag_separator_activ = True
        self.configure(cursor="sb_v_double_arrow")

    def _opreste_redimensionarea_separatorului(self, _event: tk.Event) -> None:
        self.drag_separator_activ = False
        self.configure(cursor="")

    def _redimensioneaza_separatorul(self, event: tk.Event) -> None:
        continut = self.cadru_canvas.master
        inaltime_totala = continut.winfo_height()
        pozitie_locala = event.y_root - continut.winfo_rooty()
        inaltime_noua_explicatii = inaltime_totala - pozitie_locala
        inaltime_noua_explicatii = max(120, min(300, inaltime_noua_explicatii))
        self.inaltime_explicatii_curenta = inaltime_noua_explicatii
        continut.grid_rowconfigure(2, minsize=self.inaltime_explicatii_curenta)
        self.cadru_explicatii.configure(height=self.inaltime_explicatii_curenta)
        if self.redesenare_programata is not None:
            self.after_cancel(self.redesenare_programata)
        self.redesenare_programata = self.after(30, self._redeseneaza_stare_curenta)

    def _redeseneaza_stare_curenta(self) -> None:
        self.redesenare_programata = None
        if self.graf_curent is None:
            return
        if self.rezultat_curent is None:
            self.afiseaza_graf_fara_pasi()
            return
        self.afiseaza_pas_curent()

    def genereaza_formular_retea(self) -> None:
        self.opreste_animatia()
        try:
            numar_noduri = valideaza_numar_intreg(self.numar_noduri_var.get(), "numar noduri", 2)
            numar_arce = valideaza_numar_intreg(self.numar_arce_var.get(), "numar arce", 1)
        except ValueError as exc:
            messagebox.showerror("Date invalide", str(exc))
            return

        self.noduri_curente = genereaza_nume_noduri(numar_noduri)
        self.sursa_var.set(self.noduri_curente[0])
        self.destinatie_var.set(self.noduri_curente[-1])
        self.selector_sursa.configure(values=self.noduri_curente)
        self.selector_destinatie.configure(values=self.noduri_curente)
        self.mod_seminar_disponibil = False
        self.text_verificare_finala = ""
        self.buton_verificare_finala.configure(state="disabled")
        self._reface_tabel_arce(numar_arce)
        self.status_var.set("Completeaza sursa, destinatia si fiecare arc al retelei.")
        self.rezultat_var.set("Flux maxim: -")
        self.scrie_explicatii(
            "Reteaua generala a fost pregatita.\n"
            "Pentru fiecare arc completezi: nod sursa, nod destinatie, capacitate si o eticheta optionala."
        )

    def _reface_tabel_arce(self, numar_arce: int, valori_implicite: list[dict[str, str]] | None = None) -> None:
        for widget in self.cadru_tabel_arce.winfo_children():
            widget.destroy()
        self.linii_arce.clear()

        antete = [("Start", 84), ("Final", 84), ("Capacitate", 90), ("Eticheta", 82)]
        for coloana, (text, latime) in enumerate(antete):
            ctk.CTkLabel(
                self.cadru_tabel_arce,
                text=text,
                width=latime,
                anchor="w",
                font=FONTURI["normal_bold"],
                text_color=self.paleta["text"],
            ).grid(
                row=0,
                column=coloana,
                sticky="w",
                padx=(10, 6),
                pady=(8, 4),
            )

        for index in range(numar_arce):
            valoare = valori_implicite[index] if valori_implicite and index < len(valori_implicite) else {}
            variabila_start = tk.StringVar(value=valoare.get("sursa", self.noduri_curente[0]))
            variabila_final = tk.StringVar(value=valoare.get("destinatie", self.noduri_curente[-1]))
            selector_start = ctk.CTkOptionMenu(
                self.cadru_tabel_arce,
                values=self.noduri_curente,
                variable=variabila_start,
                fg_color=self.paleta["accent_principal"],
                button_color=self.paleta["accent_principal"],
                button_hover_color=self.paleta["accent_principal_hover"],
                text_color=self.paleta["panou"],
                width=84,
            )
            selector_final = ctk.CTkOptionMenu(
                self.cadru_tabel_arce,
                values=self.noduri_curente,
                variable=variabila_final,
                fg_color=self.paleta["accent_principal"],
                button_color=self.paleta["accent_principal"],
                button_hover_color=self.paleta["accent_principal_hover"],
                text_color=self.paleta["panou"],
                width=84,
            )
            camp_capacitate = ctk.CTkEntry(
                self.cadru_tabel_arce,
                fg_color=self.paleta["panou"],
                border_color=self.paleta["bordura"],
                text_color=self.paleta["text"],
                width=88,
            )
            camp_capacitate.insert(0, valoare.get("capacitate", "0"))
            camp_eticheta = ctk.CTkEntry(
                self.cadru_tabel_arce,
                fg_color=self.paleta["panou"],
                border_color=self.paleta["bordura"],
                text_color=self.paleta["text"],
                width=82,
            )
            camp_eticheta.insert(0, valoare.get("eticheta", f"e{index + 1}"))

            selector_start.grid(row=index + 1, column=0, padx=(10, 6), pady=4, sticky="we")
            selector_final.grid(row=index + 1, column=1, padx=(10, 6), pady=4, sticky="we")
            camp_capacitate.grid(row=index + 1, column=2, padx=(10, 6), pady=4, sticky="we")
            camp_eticheta.grid(row=index + 1, column=3, padx=(10, 6), pady=4, sticky="we")

            self.linii_arce.append(
                {
                    "start_var": variabila_start,
                    "final_var": variabila_final,
                    "selector_start": selector_start,
                    "selector_final": selector_final,
                    "camp_capacitate": camp_capacitate,
                    "camp_eticheta": camp_eticheta,
                }
            )

    def citeste_arce_din_tabel(self) -> list[dict[str, str]]:
        date_arce: list[dict[str, str]] = []
        for linie in self.linii_arce:
            date_arce.append(
                {
                    "sursa": linie["start_var"].get(),
                    "destinatie": linie["final_var"].get(),
                    "capacitate": linie["camp_capacitate"].get(),
                    "eticheta": linie["camp_eticheta"].get(),
                }
            )
        return date_arce

    def construieste_graf_din_input(self) -> None:
        self.opreste_animatia()
        if not self.noduri_curente:
            self.genereaza_formular_retea()
            if not self.noduri_curente:
                return

        try:
            self.graf_curent = construieste_graf_generic(
                nume_noduri=self.noduri_curente,
                sursa=self.sursa_var.get(),
                destinatie=self.destinatie_var.get(),
                linii_arce=self.citeste_arce_din_tabel(),
                titlu="Retea generala - Ford-Fulkerson",
            )
        except ValueError as exc:
            messagebox.showerror("Date invalide", str(exc))
            return

        self.rezultat_curent = None
        self.index_pas_curent = 0
        self.mod_seminar_disponibil = False
        self.text_verificare_finala = ""
        self.buton_verificare_finala.configure(state="disabled")
        self.rezultat_var.set("Flux maxim: -")
        self.status_var.set(
            f"Graful a fost construit. Noduri: {len(self.graf_curent.noduri)} | Arce: {len(self.graf_curent.arce)}."
        )
        self.afiseaza_graf_fara_pasi()
        self.scrie_explicatii(
            "Graful este acum complet general.\n"
            "Nu mai depinde de a, b, c ... si poate fi construit pentru orice numar de noduri si arce."
        )

    def incarca_exemplu_seminar(self) -> None:
        self.opreste_animatia()
        self.noduri_curente = list(EXEMPLU_SEMINAR_NODURI)
        self.numar_noduri_var.set(str(len(EXEMPLU_SEMINAR_NODURI)))
        self.numar_arce_var.set(str(len(DEFINITII_ARCE_SEMINAR)))
        self.sursa_var.set(EXEMPLU_SEMINAR_SURSA)
        self.destinatie_var.set(EXEMPLU_SEMINAR_DESTINATIA)
        self.selector_sursa.configure(values=self.noduri_curente)
        self.selector_destinatie.configure(values=self.noduri_curente)
        self._reface_tabel_arce(
            len(DEFINITII_ARCE_SEMINAR),
            [
                {
                    "sursa": arc["sursa"],
                    "destinatie": arc["destinatie"],
                    "capacitate": str(arc["capacitate"]),
                    "eticheta": str(arc["eticheta"]),
                }
                for arc in DEFINITII_ARCE_SEMINAR
            ],
        )
        self.graf_curent = construieste_graf_din_exemplu(
            noduri_exemplu=EXEMPLU_SEMINAR_NODURI,
            sursa=EXEMPLU_SEMINAR_SURSA,
            destinatie=EXEMPLU_SEMINAR_DESTINATIA,
            arce_exemplu=DEFINITII_ARCE_SEMINAR,
            titlu="Exemplu seminar - retea preincarcata",
        )
        self.mod_seminar_disponibil = True
        self.rezultat_curent = None
        self.index_pas_curent = 0
        self.text_verificare_finala = ""
        self.buton_verificare_finala.configure(state="disabled")
        self.rezultat_var.set("Flux maxim: -")
        self.status_var.set("Exemplul de seminar a fost incarcat. Poti rula automat sau, separat, modul seminar.")
        self.afiseaza_graf_fara_pasi()
        self.scrie_explicatii(
            "Exemplul de seminar este doar o incarcare rapida.\n"
            "Fluxul general al aplicatiei ramane acum unul generic, bazat pe numar de noduri si arce."
        )

    def afiseaza_graf_fara_pasi(self) -> None:
        if self.graf_curent is None:
            return
        pas_gol = PasAlgoritm(
            iteratie=0,
            titlu="Graful initial",
            fluxuri_dupa_pas={(arc.sursa, arc.destinatie): 0 for arc in self.graf_curent.arce},
        )
        deseneaza_graf(self.canvas_graf, self.graf_curent, pas_gol, self.paleta)

    def ruleaza_automat(self) -> None:
        self.opreste_animatia()
        self.construieste_graf_din_input()
        if self.graf_curent is None:
            return
        self.rezultat_curent = ruleaza_ford_fulkerson(self.graf_curent)
        self.index_pas_curent = 0
        self._pregateste_verificare_finala()
        self.rezultat_var.set(f"Flux maxim: {self.rezultat_curent.flux_maxim}")
        self.status_var.set("Mod automat activ: reteaua este rezolvata general cu BFS in graful rezidual.")
        self.afiseaza_pas_curent()

    def ruleaza_seminar(self) -> None:
        self.opreste_animatia()
        if not self.mod_seminar_disponibil or self.graf_curent is None:
            messagebox.showinfo(
                "Mod seminar indisponibil",
                "Modul seminar ramane disponibil doar dupa incarcarea exemplului de seminar.",
            )
            return
        self.rezultat_curent = ruleaza_mod_seminar(self.graf_curent)
        self.index_pas_curent = 0
        self._pregateste_verificare_finala()
        self.rezultat_var.set(f"Flux maxim: {self.rezultat_curent.flux_maxim}")
        self.status_var.set("Mod seminar activ: demonstratia ghidata este afisata separat de modul automat.")
        self.afiseaza_pas_curent()

    def afiseaza_pas_curent(self) -> None:
        if self.graf_curent is None:
            return
        if self.rezultat_curent is None:
            self.afiseaza_graf_fara_pasi()
            return
        pas = self.rezultat_curent.pasi[self.index_pas_curent]
        deseneaza_graf(self.canvas_graf, self.graf_curent, pas, self.paleta)
        self.scrie_explicatii(pas.explicatie)
        self.rezultat_var.set(f"Flux maxim: {self.rezultat_curent.flux_maxim} | Pas curent: {pas.iteratie}")
        if pas.este_pas_final and pas.formula_taietura:
            self.status_var.set("Algoritmul s-a incheiat. Apasa pe butonul de verificare finala.")

    def scrie_explicatii(self, text: str) -> None:
        self.text_explicatii.configure(state="normal")
        self.text_explicatii.delete("1.0", "end")
        self.text_explicatii.insert("end", text)
        self.text_explicatii.configure(state="disabled")

    def pas_inainte(self) -> None:
        self.opreste_animatia()
        if self.rezultat_curent is None:
            self.scrie_explicatii("Nu exista pasi salvati. Ruleaza mai intai unul dintre moduri.")
            return
        if self.index_pas_curent < len(self.rezultat_curent.pasi) - 1:
            self.index_pas_curent += 1
            self.afiseaza_pas_curent()

    def pas_inapoi(self) -> None:
        self.opreste_animatia()
        if self.rezultat_curent is None:
            self.scrie_explicatii("Nu exista pasi salvati. Ruleaza mai intai unul dintre moduri.")
            return
        if self.index_pas_curent > 0:
            self.index_pas_curent -= 1
            self.afiseaza_pas_curent()

    def ruleaza_animat(self) -> None:
        if self.rezultat_curent is None:
            self.scrie_explicatii("Nu exista pasi de animat. Ruleaza mai intai o metoda.")
            return
        self.opreste_animatia()
        self._pas_animat()

    def _pas_animat(self) -> None:
        self.afiseaza_pas_curent()
        if self.rezultat_curent is None:
            return
        if self.index_pas_curent >= len(self.rezultat_curent.pasi) - 1:
            self.animatie_programata = None
            return
        self.index_pas_curent += 1
        self.animatie_programata = self.after(VITEZE_ANIMATIE["Mediu"], self._pas_animat)

    def opreste_animatia(self) -> None:
        if self.animatie_programata is not None:
            self.after_cancel(self.animatie_programata)
            self.animatie_programata = None

    def reseteaza_stare(self) -> None:
        self.opreste_animatia()
        self.rezultat_curent = None
        self.index_pas_curent = 0
        self.text_verificare_finala = ""
        self.buton_verificare_finala.configure(state="disabled")
        self.rezultat_var.set("Flux maxim: -")
        if self.graf_curent is not None:
            self.afiseaza_graf_fara_pasi()
        self.status_var.set("Fluxurile au fost resetate. Graful ramane incarcat.")
        self.scrie_explicatii("Reset reusit. Poti rula din nou pe aceeasi retea sau o poti modifica.")

    def exporta_raport(self) -> None:
        if self.rezultat_curent is None:
            messagebox.showwarning("Nimic de exportat", "Ruleaza mai intai o metoda.")
            return
        cale = filedialog.asksaveasfilename(
            title="Salveaza raportul",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
        )
        if not cale:
            return

        linii = [
            "# Raport Ford-Fulkerson",
            "",
            f"- Mod de rulare: {self.rezultat_curent.mod_rulare}",
            f"- Flux maxim: {self.rezultat_curent.flux_maxim}",
            f"- Numar noduri: {len(self.graf_curent.noduri) if self.graf_curent else 0}",
            f"- Numar arce: {len(self.graf_curent.arce) if self.graf_curent else 0}",
            f"- Sursa: {self.graf_curent.sursa if self.graf_curent else '-'}",
            f"- Destinatie: {self.graf_curent.destinatie if self.graf_curent else '-'}",
            f"- Formula taieturii: {self.rezultat_curent.formula_taietura or '-'}",
            "",
            "## Pasi",
            "",
        ]
        for pas in self.rezultat_curent.pasi:
            linii.append(f"### {pas.titlu}")
            linii.append(f"- Iteratie: {pas.iteratie}")
            linii.append(f"- Flux: {pas.flux_inainte} -> {pas.flux_dupa}")
            if pas.drum_crestere:
                linii.append(f"- Drum de crestere: {' -> '.join(pas.drum_crestere)}")
            if pas.capacitati_reziduale:
                linii.append(f"- Capacitatile reziduale: {pas.capacitati_reziduale}")
            if pas.formula_taietura:
                linii.append(f"- Taietura minima: {pas.formula_taietura}")
            linii.append("")
            linii.append(pas.explicatie)
            linii.append("")
        with open(cale, "w", encoding="utf-8") as fisier:
            fisier.write("\n".join(linii))
        messagebox.showinfo("Export reusit", f"Raportul a fost salvat in:\n{cale}")

    def actualizeaza_culori(self) -> None:
        self.hero.configure(fg_color=self.paleta["panou_moale"])
        self.cadru_control.configure(fg_color=self.paleta["panou"], border_color=self.paleta["bordura"])
        self.cadru_tabel_arce.configure(fg_color=self.paleta["fundal_secundar"], border_color=self.paleta["bordura"])
        self.bara_separator.configure(fg_color=self.paleta["fundal"])
        self.cadru_canvas.configure(fg_color=self.paleta["panou"])
        self.cadru_explicatii.configure(fg_color=self.paleta["panou"])
        self.cadru_legenda.configure(fg_color=self.paleta["panou"])
        self.text_explicatii.configure(fg_color=self.paleta["fundal_secundar"], border_color=self.paleta["bordura"], text_color=self.paleta["text"])
        self.titlu_hero.configure(text_color=self.paleta["text"])
        self.text_hero.configure(text_color=self.paleta["text"])
        self.label_rezultat.configure(text_color=self.paleta["accent_calduros"])
        self.label_status.configure(text_color=self.paleta["text_secundar"])
        self.titlu_explicatii.configure(text_color=self.paleta["text"])
        self.buton_verificare_finala.configure(
            fg_color=self.paleta["accent_principal"],
            hover_color=self.paleta["accent_principal_hover"],
        )
        for label, culoare in zip(
            self.legenda_puncte,
            [self.paleta["arc_normal"], self.paleta["arc_saturat"], self.paleta["arc_drum"], self.paleta["arc_invers"]],
        ):
            label.configure(fg_color=culoare)

    def _pregateste_verificare_finala(self) -> None:
        if self.rezultat_curent is None or not self.rezultat_curent.pasi:
            self.text_verificare_finala = ""
            self.buton_verificare_finala.configure(state="disabled")
            return

        pas_final = self.rezultat_curent.pasi[-1]
        if pas_final.formula_taietura:
            self.text_verificare_finala = (
                f"Flux maxim: {self.rezultat_curent.flux_maxim}\n"
                f"Formula taieturii minime: {pas_final.formula_taietura}\n"
                f"Multimea S: {', '.join(pas_final.multime_s) or '-'}\n"
                f"Multimea T: {', '.join(pas_final.multime_t) or '-'}\n\n"
                f"{pas_final.explicatie}"
            )
            self.buton_verificare_finala.configure(state="normal")
        else:
            self.text_verificare_finala = ""
            self.buton_verificare_finala.configure(state="disabled")

    def afiseaza_casuta_verificare(self) -> None:
        if not self.text_verificare_finala:
            messagebox.showinfo("Verificare finala", "Nu exista inca o verificare finala disponibila.")
            return

        fereastra = ctk.CTkToplevel(self)
        fereastra.title("Verificare finala")
        fereastra.geometry("620x420")
        fereastra.configure(fg_color=self.paleta["panou"])
        fereastra.attributes("-topmost", True)

        ctk.CTkLabel(
            fereastra,
            text="Verificare finala",
            font=FONTURI["subtitlu"],
            text_color=self.paleta["text"],
        ).pack(anchor="w", padx=18, pady=(18, 8))

        casuta = ctk.CTkTextbox(
            fereastra,
            wrap="word",
            font=FONTURI["normal"],
            fg_color=self.paleta["fundal_secundar"],
            text_color=self.paleta["text"],
            border_width=1,
            border_color=self.paleta["bordura"],
        )
        casuta.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        casuta.insert("1.0", self.text_verificare_finala)
        casuta.configure(state="disabled")
