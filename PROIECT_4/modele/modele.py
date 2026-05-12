from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Nod:
    nume: str
    pozitie_x: float
    pozitie_y: float


@dataclass(slots=True)
class Arc:
    sursa: str
    destinatie: str
    capacitate: int
    flux: int = 0
    eticheta: str = ""
    cheie: str = ""


@dataclass(slots=True)
class Graf:
    noduri: dict[str, Nod]
    arce: list[Arc]
    sursa: str
    destinatie: str
    titlu: str


@dataclass(slots=True)
class EtichetaNod:
    nod: str
    semn: str
    din_nod: str
    valoare: int | None
    explicatie: str = ""


@dataclass(slots=True)
class PasAlgoritm:
    iteratie: int
    titlu: str
    drum_crestere: list[str] = field(default_factory=list)
    arce_drum: list[tuple[str, str]] = field(default_factory=list)
    arce_inverse: list[tuple[str, str]] = field(default_factory=list)
    capacitati_reziduale: list[int] = field(default_factory=list)
    valoare_minima: int = 0
    flux_inainte: int = 0
    flux_dupa: int = 0
    fluxuri_dupa_pas: dict[tuple[str, str], int] = field(default_factory=dict)
    etichete_noduri: dict[str, EtichetaNod] = field(default_factory=dict)
    explicatie: str = ""
    arce_saturate: list[tuple[str, str]] = field(default_factory=list)
    formula_taietura: str = ""
    multime_s: list[str] = field(default_factory=list)
    multime_t: list[str] = field(default_factory=list)
    etape_etichetare: list[str] = field(default_factory=list)
    este_pas_final: bool = False


@dataclass(slots=True)
class RezultatRulare:
    mod_rulare: str
    pasi: list[PasAlgoritm] = field(default_factory=list)
    flux_maxim: int = 0
    formula_taietura: str = ""
    multime_s: list[str] = field(default_factory=list)
    multime_t: list[str] = field(default_factory=list)
