from __future__ import annotations


SURSA_IMPLICITA = "x1"
DESTINATIE_IMPLICITA = "x2"
NUMAR_NODURI_IMPLICIT = 6
NUMAR_ARCE_IMPLICIT = 7

DECALAJE_ETICHETE_GENERALE = [-22, -10, 12, 24, -30, 30]

EXEMPLU_SEMINAR_NODURI = [f"x{i}" for i in range(1, 11)]
EXEMPLU_SEMINAR_SURSA = "x1"
EXEMPLU_SEMINAR_DESTINATIA = "x10"

DEFINITII_ARCE_SEMINAR = [
    {"sursa": "x1", "destinatie": "x2", "capacitate": 20, "eticheta": "e1"},
    {"sursa": "x1", "destinatie": "x3", "capacitate": 30, "eticheta": "e2"},
    {"sursa": "x1", "destinatie": "x4", "capacitate": 40, "eticheta": "e3"},
    {"sursa": "x2", "destinatie": "x7", "capacitate": 27, "eticheta": "e4"},
    {"sursa": "x2", "destinatie": "x5", "capacitate": 19, "eticheta": "e5"},
    {"sursa": "x3", "destinatie": "x5", "capacitate": 15, "eticheta": "e6"},
    {"sursa": "x3", "destinatie": "x8", "capacitate": 30, "eticheta": "e7"},
    {"sursa": "x3", "destinatie": "x6", "capacitate": 6, "eticheta": "e8"},
    {"sursa": "x4", "destinatie": "x6", "capacitate": 20, "eticheta": "e9"},
    {"sursa": "x4", "destinatie": "x9", "capacitate": 15, "eticheta": "e10"},
    {"sursa": "x5", "destinatie": "x7", "capacitate": 10, "eticheta": "e11"},
    {"sursa": "x5", "destinatie": "x8", "capacitate": 9, "eticheta": "e12"},
    {"sursa": "x6", "destinatie": "x8", "capacitate": 12, "eticheta": "e13"},
    {"sursa": "x6", "destinatie": "x9", "capacitate": 8, "eticheta": "e14"},
    {"sursa": "x7", "destinatie": "x10", "capacitate": 31, "eticheta": "e15"},
    {"sursa": "x8", "destinatie": "x10", "capacitate": 5, "eticheta": "e16"},
    {"sursa": "x9", "destinatie": "x10", "capacitate": 42, "eticheta": "e17"},
]
