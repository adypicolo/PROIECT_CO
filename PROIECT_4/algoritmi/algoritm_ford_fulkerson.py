from __future__ import annotations

from collections import deque

from ..grafuri.graf_date import calculeaza_flux_total, construieste_fluxuri_zero, dictionar_capacitati, lista_arce_saturate
from ..modele.modele import EtichetaNod, Graf, PasAlgoritm, RezultatRulare


def ruleaza_ford_fulkerson(graf: Graf) -> RezultatRulare:
    capacitati = dictionar_capacitati(graf)
    fluxuri = construieste_fluxuri_zero(graf)
    pasi: list[PasAlgoritm] = [
        PasAlgoritm(
            iteratie=0,
            titlu="Flux initial f0 = 0",
            flux_inainte=0,
            flux_dupa=0,
            fluxuri_dupa_pas=dict(fluxuri),
            explicatie=(
                "Pornim cu flux nul pe toate arcele. In fiecare iteratie cautam un drum de crestere "
                "in graful rezidual, determinam minimul de pe acel drum si actualizam fluxul."
            ),
            arce_saturate=[],
        )
    ]

    iteratie = 1
    while True:
        rezultat_bfs = cauta_drum_cu_bfs(graf, capacitati, fluxuri)
        if rezultat_bfs["drum_crestere"] is None:
            multime_s, multime_t = determina_taietura_minima(graf, capacitati, fluxuri)
            formula = construieste_formula_taietura(graf, multime_s)
            flux_maxim = calculeaza_flux_total(graf, fluxuri)
            explicatie_finala = (
                "Nu se mai poate eticheta x10 in graful rezidual, deci algoritmul se opreste.\n"
                f"Taietura minima este S = {{{', '.join(multime_s)}}}, T = {{{', '.join(multime_t)}}}.\n"
                f"Verificare: flux maxim = capacitatea taieturii minime = {formula}"
            )
            pasi.append(
                PasAlgoritm(
                    iteratie=iteratie,
                    titlu="STOP - x10 nu mai poate fi etichetat",
                    flux_inainte=flux_maxim,
                    flux_dupa=flux_maxim,
                    fluxuri_dupa_pas=dict(fluxuri),
                    explicatie=explicatie_finala,
                    arce_saturate=lista_arce_saturate(graf, fluxuri),
                    formula_taietura=formula,
                    multime_s=multime_s,
                    multime_t=multime_t,
                    etichete_noduri=rezultat_bfs["etichete_noduri"],
                    etape_etichetare=rezultat_bfs["etape_etichetare"],
                    este_pas_final=True,
                )
            )
            return RezultatRulare(
                mod_rulare="automat",
                pasi=pasi,
                flux_maxim=flux_maxim,
                formula_taietura=formula,
                multime_s=multime_s,
                multime_t=multime_t,
            )

        flux_inainte = calculeaza_flux_total(graf, fluxuri)
        drum_crestere = rezultat_bfs["drum_crestere"]
        capacitati_reziduale = rezultat_bfs["capacitati_reziduale"]
        arce_parcurse = rezultat_bfs["arce_parcurse"]
        valoare_minima = min(capacitati_reziduale)

        arce_inverse: list[tuple[str, str]] = []
        for sursa, destinatie, sens in arce_parcurse:
            if sens == 1:
                fluxuri[(sursa, destinatie)] += valoare_minima
            else:
                fluxuri[(destinatie, sursa)] -= valoare_minima
                arce_inverse.append((destinatie, sursa))

        flux_dupa = calculeaza_flux_total(graf, fluxuri)
        explicatie = construieste_explicatie_pas(
            iteratie=iteratie,
            drum_crestere=drum_crestere,
            capacitati_reziduale=capacitati_reziduale,
            valoare_minima=valoare_minima,
            flux_inainte=flux_inainte,
            flux_dupa=flux_dupa,
            etape_etichetare=rezultat_bfs["etape_etichetare"],
            arce_inverse=arce_inverse,
            arce_saturate=lista_arce_saturate(graf, fluxuri),
        )

        pasi.append(
            PasAlgoritm(
                iteratie=iteratie,
                titlu=f"Iteratia {iteratie}",
                drum_crestere=drum_crestere,
                arce_drum=[(drum_crestere[index], drum_crestere[index + 1]) for index in range(len(drum_crestere) - 1)],
                arce_inverse=arce_inverse,
                capacitati_reziduale=capacitati_reziduale,
                valoare_minima=valoare_minima,
                flux_inainte=flux_inainte,
                flux_dupa=flux_dupa,
                fluxuri_dupa_pas=dict(fluxuri),
                etichete_noduri=rezultat_bfs["etichete_noduri"],
                explicatie=explicatie,
                arce_saturate=lista_arce_saturate(graf, fluxuri),
                etape_etichetare=rezultat_bfs["etape_etichetare"],
            )
        )
        iteratie += 1


def cauta_drum_cu_bfs(
    graf: Graf,
    capacitati: dict[tuple[str, str], int],
    fluxuri: dict[tuple[str, str], int],
) -> dict[str, object]:
    coada: deque[str] = deque([graf.sursa])
    vizitat = {graf.sursa}
    parinte: dict[str, tuple[str, tuple[str, str], int, int]] = {}
    etichete_noduri: dict[str, EtichetaNod] = {
        graf.sursa: EtichetaNod(nod=graf.sursa, semn="+", din_nod="-", valoare=None, explicatie="Nodul sursa este etichetat primul.")
    }
    etape_etichetare = [f"Pornim etichetarea din {graf.sursa}."]

    while coada:
        nod_curent = coada.popleft()
        for arc in graf.arce:
            cheie = (arc.sursa, arc.destinatie)
            flux_curent = fluxuri[cheie]

            if arc.sursa == nod_curent:
                capacitate_reziduala = arc.capacitate - flux_curent
                if capacitate_reziduala > 0 and arc.destinatie not in vizitat:
                    vizitat.add(arc.destinatie)
                    coada.append(arc.destinatie)
                    parinte[arc.destinatie] = (nod_curent, cheie, 1, capacitate_reziduala)
                    etichete_noduri[arc.destinatie] = EtichetaNod(
                        nod=arc.destinatie,
                        semn="+",
                        din_nod=nod_curent,
                        valoare=capacitate_reziduala,
                        explicatie=f"{arc.destinatie} primeste eticheta + de la {nod_curent}.",
                    )
                    etape_etichetare.append(
                        f"Etichetam {arc.destinatie} cu [+] din {nod_curent}; disponibil pe {arc.sursa}->{arc.destinatie}: {capacitate_reziduala}."
                    )
                    if arc.destinatie == graf.destinatie:
                        break

            if arc.destinatie == nod_curent and flux_curent > 0 and arc.sursa not in vizitat:
                vizitat.add(arc.sursa)
                coada.append(arc.sursa)
                parinte[arc.sursa] = (nod_curent, cheie, -1, flux_curent)
                etichete_noduri[arc.sursa] = EtichetaNod(
                    nod=arc.sursa,
                    semn="-",
                    din_nod=nod_curent,
                    valoare=flux_curent,
                    explicatie=f"{arc.sursa} primeste eticheta - de la {nod_curent}.",
                )
                etape_etichetare.append(
                    f"Etichetam {arc.sursa} cu [-] din {nod_curent}; putem reduce fluxul pe {arc.sursa}->{arc.destinatie} cu {flux_curent}."
                )
                if arc.sursa == graf.destinatie:
                    break

        if graf.destinatie in vizitat:
            break

    if graf.destinatie not in vizitat:
        etape_etichetare.append("Etichetarea se opreste: x10 nu mai poate fi etichetat.")
        return {
            "drum_crestere": None,
            "capacitati_reziduale": [],
            "arce_parcurse": [],
            "etichete_noduri": etichete_noduri,
            "etape_etichetare": etape_etichetare,
        }

    drum_crestere = [graf.destinatie]
    capacitati_reziduale: list[int] = []
    arce_parcurse_revers: list[tuple[str, str, int]] = []
    nod = graf.destinatie
    while nod != graf.sursa:
        nod_parinte, cheie_arc, sens, capacitate_reziduala = parinte[nod]
        drum_crestere.append(nod_parinte)
        capacitati_reziduale.append(capacitate_reziduala)
        if sens == 1:
            arce_parcurse_revers.append((cheie_arc[0], cheie_arc[1], 1))
        else:
            arce_parcurse_revers.append((cheie_arc[1], cheie_arc[0], -1))
        nod = nod_parinte

    drum_crestere.reverse()
    capacitati_reziduale.reverse()
    arce_parcurse_revers.reverse()
    etape_etichetare.append(f"Am obtinut un lant de crestere: {' -> '.join(drum_crestere)}.")
    return {
        "drum_crestere": drum_crestere,
        "capacitati_reziduale": capacitati_reziduale,
        "arce_parcurse": arce_parcurse_revers,
        "etichete_noduri": etichete_noduri,
        "etape_etichetare": etape_etichetare,
    }


def determina_taietura_minima(
    graf: Graf,
    capacitati: dict[tuple[str, str], int],
    fluxuri: dict[tuple[str, str], int],
) -> tuple[list[str], list[str]]:
    coada: deque[str] = deque([graf.sursa])
    vizitat = {graf.sursa}

    while coada:
        nod_curent = coada.popleft()
        for arc in graf.arce:
            cheie = (arc.sursa, arc.destinatie)
            flux_curent = fluxuri[cheie]

            if arc.sursa == nod_curent and capacitati[cheie] - flux_curent > 0 and arc.destinatie not in vizitat:
                vizitat.add(arc.destinatie)
                coada.append(arc.destinatie)

            if arc.destinatie == nod_curent and flux_curent > 0 and arc.sursa not in vizitat:
                vizitat.add(arc.sursa)
                coada.append(arc.sursa)

    multime_s = [nod for nod in graf.noduri if nod in vizitat]
    multime_t = [nod for nod in graf.noduri if nod not in vizitat]
    return multime_s, multime_t


def construieste_formula_taietura(graf: Graf, multime_s: list[str]) -> str:
    termeni: list[str] = []
    suma = 0
    for arc in graf.arce:
        if arc.sursa in multime_s and arc.destinatie not in multime_s:
            termeni.append(str(arc.capacitate))
            suma += arc.capacitate
    if not termeni:
        return "CT = 0"
    return f"CT = {' + '.join(termeni)} = {suma}"


def construieste_explicatie_pas(
    iteratie: int,
    drum_crestere: list[str],
    capacitati_reziduale: list[int],
    valoare_minima: int,
    flux_inainte: int,
    flux_dupa: int,
    etape_etichetare: list[str],
    arce_inverse: list[tuple[str, str]],
    arce_saturate: list[tuple[str, str]],
) -> str:
    text = [
        f"Iteratia {iteratie}",
        "Determinam un lant de crestere in graful rezidual.",
        *etape_etichetare,
        f"Drumul ales este: {' -> '.join(drum_crestere)}",
        f"Capacitati reziduale pe drum: {capacitati_reziduale}",
        f"min({', '.join(str(valoare) for valoare in capacitati_reziduale)}) = {valoare_minima}",
        f"Actualizam fluxul: {flux_inainte} + {valoare_minima} = {flux_dupa}",
    ]
    if arce_inverse:
        text.append(
            "Pe acest lant apar si arce inverse, deci reducem fluxul pe: "
            + ", ".join(f"{sursa}->{destinatie}" for sursa, destinatie in arce_inverse)
            + "."
        )
    if arce_saturate:
        text.append(
            "Arce saturate dupa actualizare: "
            + ", ".join(f"{sursa}->{destinatie}" for sursa, destinatie in arce_saturate)
            + "."
        )
    return "\n".join(text)
