from __future__ import annotations

import math
import tkinter as tk
from collections import deque

from ..configurare.constante import DECALAJE_ETICHETE_GENERALE
from ..modele.modele import EtichetaNod, Graf, PasAlgoritm
from ..configurare.stil import DIMENSIUNI, FONTURI


def curata_canvas(canvas: tk.Canvas) -> None:
    canvas.delete("all")


def deseneaza_graf(canvas: tk.Canvas, graf: Graf, pas: PasAlgoritm | None, paleta: dict[str, str]) -> None:
    curata_canvas(canvas)
    canvas.update_idletasks()
    latime = canvas.winfo_width()
    inaltime = canvas.winfo_height()
    if latime < 240:
        latime = 960
    if inaltime < 240:
        inaltime = 420
    canvas.configure(bg=paleta["fundal_secundar"])
    deseneaza_fundal(canvas, latime, inaltime, paleta)

    pozitii = calculeaza_pozitii_automate(graf, latime, inaltime)
    fluxuri_curente = pas.fluxuri_dupa_pas if pas else {(arc.sursa, arc.destinatie): 0 for arc in graf.arce}
    arce_drum = set(pas.arce_drum if pas else [])
    arce_inverse = set(pas.arce_inverse if pas else [])
    arce_saturate = set(pas.arce_saturate if pas else [])
    etichete_noduri = pas.etichete_noduri if pas else {}

    canvas.create_text(24, 22, anchor="w", text=graf.titlu, fill=paleta["text"], font=FONTURI["subtitlu"])
    canvas.create_text(
        24,
        48,
        anchor="w",
        text=f"Sursa: {graf.sursa}    Destinatie: {graf.destinatie}    Noduri: {len(graf.noduri)}    Arce: {len(graf.arce)}",
        fill=paleta["text_secundar"],
        font=FONTURI["normal"],
    )

    grupuri_etichete = pregateste_decalaje_etichete(graf)

    for index, arc in enumerate(graf.arce):
        cheie = (arc.sursa, arc.destinatie)
        deseneaza_arc(
            canvas=canvas,
            sursa=arc.sursa,
            destinatie=arc.destinatie,
            pozitii=pozitii,
            paleta=paleta,
            este_saturat=cheie in arce_saturate,
            este_in_drum=cheie in arce_drum,
            este_arc_invers=cheie in arce_inverse,
        )
        deseneaza_eticheta_arc(
            canvas=canvas,
            arc=arc,
            flux_curent=fluxuri_curente.get(cheie, 0),
            pozitii=pozitii,
            paleta=paleta,
            decalaj_index=grupuri_etichete[index],
        )

    for nume, nod in graf.noduri.items():
        deseneaza_nod(
            canvas=canvas,
            nume=nume,
            pozitie=pozitii[nume],
            paleta=paleta,
            este_sursa=nume == graf.sursa,
            este_destinatie=nume == graf.destinatie,
            este_evidentiat=nume in etichete_noduri or nume in set(pas.multime_s if pas else []),
        )

    for eticheta in etichete_noduri.values():
        deseneaza_eticheta_nod(canvas, eticheta, pozitii, paleta)


def deseneaza_fundal(canvas: tk.Canvas, latime: int, inaltime: int, paleta: dict[str, str]) -> None:
    canvas.create_rectangle(0, 0, latime, inaltime, fill=paleta["fundal_secundar"], outline=paleta["fundal_secundar"])
    pas_grila = 28
    for x in range(0, latime, pas_grila):
        canvas.create_line(x, 0, x, inaltime, fill=paleta["grila"], width=1)
    for y in range(0, inaltime, pas_grila):
        canvas.create_line(0, y, latime, y, fill=paleta["grila"], width=1)


def calculeaza_pozitii_automate(graf: Graf, latime: int, inaltime: int) -> dict[str, tuple[float, float]]:
    adiacenta: dict[str, list[str]] = {nume: [] for nume in graf.noduri}
    grade_intrare: dict[str, int] = {nume: 0 for nume in graf.noduri}
    for arc in graf.arce:
        adiacenta[arc.sursa].append(arc.destinatie)
        grade_intrare[arc.destinatie] += 1

    niveluri = {graf.sursa: 0}
    coada: deque[str] = deque([graf.sursa])
    while coada:
        nod_curent = coada.popleft()
        for vecin in adiacenta.get(nod_curent, []):
            nivel_nou = niveluri[nod_curent] + 1
            if nivel_nou > niveluri.get(vecin, -1):
                niveluri[vecin] = nivel_nou
                coada.append(vecin)

    nivel_maxim = max(niveluri.values(), default=0)
    for nod in graf.noduri:
        if nod not in niveluri:
            niveluri[nod] = nivel_maxim if grade_intrare[nod] > 0 else 0

    coloane: dict[int, list[str]] = {}
    for nod, nivel in niveluri.items():
        coloane.setdefault(nivel, []).append(nod)

    margine_x = max(72, min(96, int(latime * 0.09)))
    margine_y = max(86, min(108, int(inaltime * 0.22)))
    latime_utila = max(latime - 2 * margine_x, 240)
    pozitii: dict[str, tuple[float, float]] = {}
    nivel_total = max(coloane.keys(), default=0)

    for nivel in sorted(coloane):
        noduri_coloana = sorted(
            coloane[nivel],
            key=lambda nume: (
                nume != graf.sursa,
                nume == graf.destinatie,
                len(adiacenta.get(nume, [])) * -1,
                nume,
            ),
        )
        x = latime / 2 if nivel_total == 0 else margine_x + latime_utila * (nivel / nivel_total)
        pozitii_verticale = distribuie_vertical(noduri_coloana, inaltime, margine_y)
        for nume, y in zip(noduri_coloana, pozitii_verticale):
            pozitii[nume] = (x, y)
    return pozitii


def distribuie_vertical(noduri: list[str], inaltime: int, margine_y: int) -> list[float]:
    if len(noduri) == 1:
        return [inaltime / 2]
    distanta_minima = max(62, min(88, int(inaltime * 0.16)))
    spatiu_util = max(inaltime - 2 * margine_y, distanta_minima * (len(noduri) - 1))
    start = max(margine_y, (inaltime - spatiu_util) / 2)
    return [start + index * (spatiu_util / max(len(noduri) - 1, 1)) for index in range(len(noduri))]


def pregateste_decalaje_etichete(graf: Graf) -> list[int]:
    aparitii_pe_sursa: dict[str, int] = {}
    decalaje: list[int] = []
    for arc in graf.arce:
        aparitie = aparitii_pe_sursa.get(arc.sursa, 0)
        decalaje.append(DECALAJE_ETICHETE_GENERALE[aparitie % len(DECALAJE_ETICHETE_GENERALE)])
        aparitii_pe_sursa[arc.sursa] = aparitie + 1
    return decalaje


def deseneaza_nod(
    canvas: tk.Canvas,
    nume: str,
    pozitie: tuple[float, float],
    paleta: dict[str, str],
    este_sursa: bool,
    este_destinatie: bool,
    este_evidentiat: bool,
) -> None:
    raza = DIMENSIUNI["raza_nod"]
    x, y = pozitie
    culoare_fundal = paleta["nod_normal"]
    if este_sursa:
        culoare_fundal = paleta["nod_sursa"]
    elif este_destinatie:
        culoare_fundal = paleta["nod_destinatie"]
    elif este_evidentiat:
        culoare_fundal = paleta["nod_evidentiat"]

    grosime = 4 if este_evidentiat else 2
    canvas.create_oval(x - raza, y - raza, x + raza, y + raza, fill=culoare_fundal, outline=paleta["accent_principal"], width=grosime)
    canvas.create_text(x, y, text=nume, fill=paleta["text"], font=FONTURI["graf_nod"])


def deseneaza_arc(
    canvas: tk.Canvas,
    sursa: str,
    destinatie: str,
    pozitii: dict[str, tuple[float, float]],
    paleta: dict[str, str],
    este_saturat: bool,
    este_in_drum: bool,
    este_arc_invers: bool,
) -> None:
    x1, y1 = pozitii[sursa]
    x2, y2 = pozitii[destinatie]
    dx = x2 - x1
    dy = y2 - y1
    distanta = math.hypot(dx, dy)
    if distanta == 0:
        return

    raza = DIMENSIUNI["raza_nod"] + 4
    start_x = x1 + dx / distanta * raza
    start_y = y1 + dy / distanta * raza
    end_x = x2 - dx / distanta * raza
    end_y = y2 - dy / distanta * raza

    culoare = paleta["arc_normal"]
    grosime = 2
    if este_saturat:
        culoare = paleta["arc_saturat"]
        grosime = 3
    if este_arc_invers:
        culoare = paleta["arc_invers"]
        grosime = 3
    if este_in_drum:
        culoare = paleta["arc_drum"]
        grosime = 4

    canvas.create_line(
        start_x,
        start_y,
        end_x,
        end_y,
        arrow=tk.LAST,
        arrowshape=(16, 18, 5),
        fill=culoare,
        width=grosime,
        smooth=True,
    )


def deseneaza_eticheta_arc(
    canvas: tk.Canvas,
    arc,
    flux_curent: int,
    pozitii: dict[str, tuple[float, float]],
    paleta: dict[str, str],
    decalaj_index: int,
) -> None:
    x1, y1 = pozitii[arc.sursa]
    x2, y2 = pozitii[arc.destinatie]
    mijloc_x = (x1 + x2) / 2
    mijloc_y = (y1 + y2) / 2
    dx = x2 - x1
    dy = y2 - y1
    distanta = max(math.hypot(dx, dy), 1)
    normal_x = -dy / distanta
    normal_y = dx / distanta
    decalaj_x = normal_x * decalaj_index
    decalaj_y = normal_y * decalaj_index

    text = f"{flux_curent}/{arc.capacitate}"
    if arc.eticheta:
        text = f"{arc.eticheta}: {text}"

    latime = max(74, 7 * len(text))
    canvas.create_rectangle(
        mijloc_x + decalaj_x - latime / 2,
        mijloc_y + decalaj_y - 12,
        mijloc_x + decalaj_x + latime / 2,
        mijloc_y + decalaj_y + 12,
        fill=paleta["panou"],
        outline=paleta["bordura"],
    )
    canvas.create_text(mijloc_x + decalaj_x, mijloc_y + decalaj_y, text=text, fill=paleta["text"], font=FONTURI["graf_eticheta"])


def deseneaza_eticheta_nod(
    canvas: tk.Canvas,
    eticheta_nod: EtichetaNod,
    pozitii: dict[str, tuple[float, float]],
    paleta: dict[str, str],
) -> None:
    x, y = pozitii[eticheta_nod.nod]
    text = f"[{eticheta_nod.semn}]"
    if eticheta_nod.din_nod not in {"", "-"}:
        text += f" din {eticheta_nod.din_nod}"
    if eticheta_nod.valoare is not None:
        text += f" ({eticheta_nod.valoare})"
    canvas.create_text(
        x + 62,
        y - 24,
        text=text,
        fill=paleta["accent_calduros"] if eticheta_nod.semn == "+" else paleta["arc_invers"],
        font=FONTURI["mic"],
    )
