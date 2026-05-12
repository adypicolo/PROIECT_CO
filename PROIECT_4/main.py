from __future__ import annotations

import importlib
import pathlib
import sys

import customtkinter as ctk

if __package__ in {None, ""}:
    director_pachet = pathlib.Path(__file__).resolve().parent
    director_parinte = director_pachet.parent
    if str(director_parinte) not in sys.path:
        sys.path.insert(0, str(director_parinte))
    nume_pachet = director_pachet.name
    AplicatieFordFulkerson = importlib.import_module(f"{nume_pachet}.ui.interfata").AplicatieFordFulkerson
else:
    from .ui.interfata import AplicatieFordFulkerson


def main() -> None:
    ctk.set_default_color_theme("blue")
    aplicatie = AplicatieFordFulkerson()
    aplicatie.mainloop()


if __name__ == "__main__":
    main()
