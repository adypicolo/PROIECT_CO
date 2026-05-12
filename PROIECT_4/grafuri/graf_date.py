from __future__ import annotations

from ..modele.modele import Arc, Graf, Nod


def genereaza_nume_noduri(numar_noduri: int) -> list[str]:
    if numar_noduri < 2:
        raise ValueError("Trebuie să existe cel puțin 2 noduri!")
    return [f"x{index}" for index in range(1, numar_noduri + 1)]


def valideaza_numar_intreg(text: str, denumire: str, minim: int) -> int:
    text_curat = text.strip()
    if not text_curat:
        raise ValueError(f"Câmpul pentru {denumire} este gol!")
    try:
        valoare = int(text_curat)
    except ValueError as exc:
        raise ValueError(f"Câmpul pentru {denumire} trebuie să fie număr întreg!") from exc
    if valoare < minim:
        raise ValueError(f"Câmpul pentru {denumire} trebuie să fie cel puțin {minim}!")
    return valoare


def construieste_graf_generic(
    nume_noduri: list[str],
    sursa: str,
    destinatie: str,
    linii_arce: list[dict[str, str]],
    titlu: str = "Rețea orientată - Ford-Fulkerson",
) -> Graf:
    if sursa not in nume_noduri:
        raise ValueError("Nodul sursă nu există în lista de noduri!")
    if destinatie not in nume_noduri:
        raise ValueError("Nodul destinație nu există în lista de noduri!")
    if sursa == destinatie:
        raise ValueError("Sursa și destinația trebuie să fie diferite!")

    noduri = {
        nume: Nod(nume=nume, pozitie_x=0.0, pozitie_y=0.0)
        for nume in nume_noduri
    }

    arce: list[Arc] = []
    arce_vazute: set[tuple[str, str]] = set()
    for index, linie in enumerate(linii_arce, start=1):
        start = linie["sursa"].strip()
        final = linie["destinatie"].strip()
        capacitate_text = linie["capacitate"].strip()
        eticheta = linie["eticheta"].strip()

        if not capacitate_text:
            continue
        if start not in noduri or final not in noduri:
            raise ValueError(f"Arcul de pe linia {index} folosește un nod inexistent!")
        if start == final:
            raise ValueError(f"Arcul de pe linia {index} nu poate incepe și termina în același nod!")
        try:
            capacitate = int(capacitate_text)
        except ValueError as exc:
            raise ValueError(f"Capacitatea de pe linia {index} trebuie să fie un număr întreg!") from exc
        if capacitate < 0:
            raise ValueError(f"Capacitatea de pe linia {index} nu poate fi negativă!")
        cheie_arc = (start, final)
        if cheie_arc in arce_vazute:
            raise ValueError(f"Arcul {start}->{final} este introdus de mai multe ori!")
        arce_vazute.add(cheie_arc)
        arce.append(
            Arc(
                sursa=start,
                destinatie=final,
                capacitate=capacitate,
                flux=0,
                eticheta=eticheta or f"e{index}",
                cheie=f"e{index}",
            )
        )

    if not arce:
        raise ValueError("Trebuie introdus cel puțin un arc valid!")

    return Graf(noduri=noduri, arce=arce, sursa=sursa, destinatie=destinatie, titlu=titlu)


def construieste_graf_din_exemplu(
    noduri_exemplu: list[str],
    sursa: str,
    destinatie: str,
    arce_exemplu: list[dict[str, object]],
    titlu: str,
) -> Graf:
    linii_arce = [
        {
            "sursa": str(arc["sursa"]),
            "destinatie": str(arc["destinatie"]),
            "capacitate": str(arc["capacitate"]),
            "eticheta": str(arc["eticheta"]),
        }
        for arc in arce_exemplu
    ]
    return construieste_graf_generic(noduri_exemplu, sursa, destinatie, linii_arce, titlu=titlu)


def construieste_fluxuri_zero(graf: Graf) -> dict[tuple[str, str], int]:
    return {(arc.sursa, arc.destinatie): 0 for arc in graf.arce}


def calculeaza_flux_total(graf: Graf, fluxuri: dict[tuple[str, str], int]) -> int:
    return sum(fluxuri[(arc.sursa, arc.destinatie)] for arc in graf.arce if arc.sursa == graf.sursa)


def lista_arce_saturate(graf: Graf, fluxuri: dict[tuple[str, str], int]) -> list[tuple[str, str]]:
    return [
        (arc.sursa, arc.destinatie)
        for arc in graf.arce
        if fluxuri[(arc.sursa, arc.destinatie)] >= arc.capacitate
    ]


def dictionar_capacitati(graf: Graf) -> dict[tuple[str, str], int]:
    return {(arc.sursa, arc.destinatie): arc.capacitate for arc in graf.arce}


def parseaza_fisier_exemplu(cale_fisier: str) -> dict[str, object]:
    """Citește un fișier text cu formatul:
       Linia 1:  N M        (număr noduri, număr arce)
       Liniile 2..M+1:  sursa destinatie capacitate

    Returnează un dicționar cu cheile:
        noduri   – lista numelor nodurilor
        sursa    – primul nod
        destinatie – ultimul nod
        arce     – lista de dicționare {sursa, destinatie, capacitate, eticheta}
    """
    with open(cale_fisier, "r", encoding="utf-8") as fisier:
        linii = [linie.strip() for linie in fisier if linie.strip()]

    if not linii:
        raise ValueError("Fișierul exemplu este gol!")

    parti_header = linii[0].split()
    if len(parti_header) < 2:
        raise ValueError("Prima linie trebuie să conțină numărul de noduri și numărul de arce!")

    numar_noduri = int(parti_header[0])
    numar_arce = int(parti_header[1])

    if numar_noduri < 2:
        raise ValueError("Trebuie cel puțin 2 noduri!")
    if numar_arce < 1:
        raise ValueError("Trebuie cel puțin 1 arc!")
    if len(linii) < 1 + numar_arce:
        raise ValueError(f"Fișierul declară {numar_arce} arce, dar are doar {len(linii) - 1} linii de date!")

    noduri = [f"x{i}" for i in range(1, numar_noduri + 1)]
    arce: list[dict[str, object]] = []
    for index in range(numar_arce):
        parti = linii[1 + index].split()
        if len(parti) < 3:
            raise ValueError(f"Linia {index + 2} trebuie să conțină: sursa destinatie capacitate!")
        sursa_arc = parti[0]
        destinatie_arc = parti[1]
        capacitate = int(parti[2])
        arce.append({
            "sursa": sursa_arc,
            "destinatie": destinatie_arc,
            "capacitate": capacitate,
            "eticheta": f"e{index + 1}",
        })

    return {
        "noduri": noduri,
        "sursa": noduri[0],
        "destinatie": noduri[-1],
        "arce": arce,
    }
