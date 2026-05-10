from __future__ import annotations

from ..grafuri.graf_date import construieste_fluxuri_zero
from ..modele.modele import EtichetaNod, Graf, PasAlgoritm, RezultatRulare


def ruleaza_mod_seminar(graf: Graf) -> RezultatRulare:
    fluxuri = construieste_fluxuri_zero(graf)
    pasi: list[PasAlgoritm] = []

    flux_initial = {
        ("x1", "x2"): 15,
        ("x1", "x3"): 12,
        ("x1", "x4"): 28,
        ("x2", "x7"): 15,
        ("x2", "x5"): 0,
        ("x3", "x5"): 5,
        ("x3", "x8"): 5,
        ("x3", "x6"): 2,
        ("x4", "x6"): 2,
        ("x4", "x9"): 26,
        ("x5", "x7"): 10,
        ("x5", "x8"): 0,
        ("x6", "x8"): 0,
        ("x6", "x9"): 2,
        ("x7", "x10"): 25,
        ("x8", "x10"): 5,
        ("x9", "x10"): 25,
    }
    fluxuri.update(flux_initial)

    pasi.append(
        PasAlgoritm(
            iteratie=0,
            titlu="Flux initial f0 = 55",
            flux_inainte=55,
            flux_dupa=55,
            fluxuri_dupa_pas=dict(fluxuri),
            explicatie=(
                "Mod seminar: pornim de la fluxul initial prezentat in curs, f0 = 55.\n"
                "De aici urmarim strict demonstratia ghidata, cu lanturi de crestere, etichetare si saturarea arcelor."
            ),
            arce_saturate=[("x5", "x7"), ("x8", "x10")],
        )
    )

    pasi.append(
        construieste_pas_seminar(
            iteratie=1,
            titlu="Pasul 1 - crestere cu 7",
            fluxuri_curente=fluxuri,
            drum=["x1", "x4", "x9", "x10"],
            arce_actualizate=[("x1", "x4"), ("x4", "x9"), ("x9", "x10")],
            increment=7,
            capacitati_reziduale=[12, 7, 17],
            etape_etichetare=[
                "Etichetam x4 cu [+] din x1.",
                "Etichetam x9 cu [+] din x4.",
                "Etichetam x10 cu [+] din x9.",
                "Am determinat un lant de crestere pana la destinatie.",
            ],
            etichete={
                "x4": EtichetaNod("x4", "+", "x1", 12, "x4 este accesibil direct din x1."),
                "x9": EtichetaNod("x9", "+", "x4", 7, "x9 este etichetat din x4."),
                "x10": EtichetaNod("x10", "+", "x9", 17, "x10 este atins prin x9."),
            },
            explicatie_scurta=(
                "Determinam un lant: x1 -> x4 -> x9 -> x10.\n"
                "min(12, 7, 17) = 7, deci crestem fluxul cu 7.\n"
                "Arcul x4->x9 devine saturat in demonstratia seminarului."
            ),
        )
    )

    pasi.append(
        construieste_pas_seminar(
            iteratie=2,
            titlu="Pasul 2 - crestere cu 4",
            fluxuri_curente=fluxuri,
            drum=["x1", "x2", "x7", "x10"],
            arce_actualizate=[("x1", "x2"), ("x2", "x7"), ("x7", "x10")],
            increment=4,
            capacitati_reziduale=[6, 8, 4],
            etape_etichetare=[
                "Reluam etichetarea din x1.",
                "Etichetam x2 cu [+] din x1.",
                "Etichetam x7 cu [+] din x2.",
                "Etichetam x10 cu [+] din x7.",
            ],
            etichete={
                "x2": EtichetaNod("x2", "+", "x1", 6, "Mai exista loc pe arcul x1->x2."),
                "x7": EtichetaNod("x7", "+", "x2", 8, "x7 se eticheteaza din x2."),
                "x10": EtichetaNod("x10", "+", "x7", 4, "Destinatia este etichetata din x7."),
            },
            explicatie_scurta=(
                "Determinam un nou lant: x1 -> x2 -> x7 -> x10.\n"
                "min(6, 8, 4) = 4, deci fluxul creste cu 4 si obtinem f2 = 66."
            ),
        )
    )

    pasi.append(
        construieste_pas_seminar(
            iteratie=3,
            titlu="Pasul 3 - crestere cu 6",
            fluxuri_curente=fluxuri,
            drum=["x1", "x3", "x6", "x9", "x10"],
            arce_actualizate=[("x1", "x3"), ("x3", "x6"), ("x6", "x9"), ("x9", "x10")],
            increment=6,
            capacitati_reziduale=[18, 6, 6, 11],
            etape_etichetare=[
                "Etichetam x3 cu [+] din x1.",
                "Etichetam x6 cu [+] din x3.",
                "Etichetam x9 cu [+] din x6.",
                "Etichetam x10 cu [+] din x9.",
            ],
            etichete={
                "x3": EtichetaNod("x3", "+", "x1", 18, "x3 este accesibil direct din x1."),
                "x6": EtichetaNod("x6", "+", "x3", 6, "x6 este etichetat din x3."),
                "x9": EtichetaNod("x9", "+", "x6", 6, "x9 este etichetat din x6."),
                "x10": EtichetaNod("x10", "+", "x9", 11, "x10 este atins din nou."),
            },
            explicatie_scurta=(
                "Determinam un lant: x1 -> x3 -> x6 -> x9 -> x10.\n"
                "min(18, 6, 6, 11) = 6, deci crestem fluxul cu 6.\n"
                "Arcul x6->x9 devine saturat."
            ),
        )
    )

    pas_4 = construieste_pas_seminar(
        iteratie=4,
        titlu="Pasul 4 - crestere cu 2",
        fluxuri_curente=fluxuri,
        drum=["x1", "x2", "x7", "x10"],
        arce_actualizate=[("x1", "x2"), ("x2", "x7"), ("x7", "x10")],
        increment=2,
        capacitati_reziduale=[2, 2, 2],
        etape_etichetare=[
            "Etichetam x2 cu [+] din x1.",
            "Etichetam x7 cu [+] din x2.",
            "Etichetam x10 cu [+] din x7.",
        ],
        etichete={
            "x2": EtichetaNod("x2", "+", "x1", 2, "Mai raman 2 unitati disponibile."),
            "x7": EtichetaNod("x7", "+", "x2", 2, "x7 primeste eticheta finala."),
            "x10": EtichetaNod("x10", "+", "x7", 2, "Ultima crestere spre destinatie."),
        },
        explicatie_scurta=(
            "Determinam ultimul lant de crestere: x1 -> x2 -> x7 -> x10.\n"
            "min(2, 2, 2) = 2, deci fluxul devine f4 = 74."
        ),
    )
    pas_4.arce_saturate = pas_4.arce_saturate + [("x7", "x10")]
    pasi.append(pas_4)

    pasi.append(
        PasAlgoritm(
            iteratie=5,
            titlu="STOP - verificare cu taietura minima",
            flux_inainte=74,
            flux_dupa=74,
            fluxuri_dupa_pas=dict(fluxuri),
            explicatie=(
                "Reluam etichetarea si observam ca x10 nu se mai poate eticheta.\n"
                "In modul seminar, verificarea finala se face cu taietura minima:\n"
                "CT = 31 + 5 + 8 + 30 = 74.\n"
                "Concluzie: fluxul maxim este 74 si este egal cu capacitatea taieturii."
            ),
            formula_taietura="CT = 31 + 5 + 8 + 30 = 74",
            multime_s=["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"],
            multime_t=["x9", "x10"],
            arce_saturate=[("x4", "x9"), ("x6", "x9"), ("x7", "x10"), ("x8", "x10")],
            etape_etichetare=[
                "Etichetarea se opreste.",
                "Nu se mai poate eticheta x10.",
                "Aplicam teorema flux maxim = taietura minima.",
            ],
            este_pas_final=True,
        )
    )

    return RezultatRulare(
        mod_rulare="seminar",
        pasi=pasi,
        flux_maxim=74,
        formula_taietura="CT = 31 + 5 + 8 + 30 = 74",
        multime_s=["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8"],
        multime_t=["x9", "x10"],
    )


def construieste_pas_seminar(
    iteratie: int,
    titlu: str,
    fluxuri_curente: dict[tuple[str, str], int],
    drum: list[str],
    arce_actualizate: list[tuple[str, str]],
    increment: int,
    capacitati_reziduale: list[int],
    etape_etichetare: list[str],
    etichete: dict[str, EtichetaNod],
    explicatie_scurta: str,
) -> PasAlgoritm:
    flux_inainte = sum(fluxuri_curente[cheie] for cheie in fluxuri_curente if cheie[0] == "x1")
    for cheie in arce_actualizate:
        fluxuri_curente[cheie] += increment
    flux_dupa = sum(fluxuri_curente[cheie] for cheie in fluxuri_curente if cheie[0] == "x1")
    arce_saturate = []
    if ("x4", "x9") in fluxuri_curente and fluxuri_curente[("x4", "x9")] >= 30:
        arce_saturate.append(("x4", "x9"))
    if ("x6", "x9") in fluxuri_curente and fluxuri_curente[("x6", "x9")] >= 8:
        arce_saturate.append(("x6", "x9"))
    if fluxuri_curente[("x8", "x10")] >= 5:
        arce_saturate.append(("x8", "x10"))
    return PasAlgoritm(
        iteratie=iteratie,
        titlu=titlu,
        drum_crestere=drum,
        arce_drum=[(drum[index], drum[index + 1]) for index in range(len(drum) - 1)],
        capacitati_reziduale=capacitati_reziduale,
        valoare_minima=increment,
        flux_inainte=flux_inainte,
        flux_dupa=flux_dupa,
        fluxuri_dupa_pas=dict(fluxuri_curente),
        etichete_noduri=etichete,
        explicatie=explicatie_scurta,
        arce_saturate=arce_saturate,
        etape_etichetare=etape_etichetare,
    )
