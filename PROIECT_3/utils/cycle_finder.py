# --- utils/cycle_finder.py ---

def find_cycle(celula_start: tuple[int, int], celule_baza: set[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Gaseste un circuit care incepe si se termina in celula_start,
    folosind DOAR elemente din celule_baza ca "pivoti" unde isi schimba directia.
    Circuitul trebuie sa alterneze liniile si coloanele.

    Returneaza lista ordonata de celule care formeaza circuitul.
    """
    # Adaugam celula de start in "baza" temporar pentru a putea reveni la ea
    celule_valide = set(celule_baza)
    celule_valide.add(celula_start)

    def dfs(curent: tuple[int, int], directie: str, vizitate: set, drum: list) -> list | None:
        if len(drum) >= 4 and curent == celula_start:
            return drum

        r, c = curent

        # Daca venim pe orizontala (H), trebuie sa plecam pe verticala (V) (aceeasi coloana, rand diferit)
        if directie == 'H' or directie is None:
            # Cautam celule in aceeasi coloana (directia viitoare e V)
            for nr, nc in celule_valide:
                if nc == c and nr != r:
                    if (nr, nc) == celula_start and len(drum) >= 3:
                        return drum + [(nr, nc)]
                    if (nr, nc) not in vizitate:
                        vizitate.add((nr, nc))
                        res = dfs((nr, nc), 'V', vizitate, drum + [(nr, nc)])
                        if res:
                            return res
                        vizitate.remove((nr, nc))

        # Daca venim pe verticala (V), trebuie sa plecam pe orizontala (H) (acelasi rand, coloana diferita)
        if directie == 'V' or directie is None:
            # Cautam celule in acelasi rand (directia viitoare e H)
            for nr, nc in celule_valide:
                if nr == r and nc != c:
                    if (nr, nc) == celula_start and len(drum) >= 3:
                        return drum + [(nr, nc)]
                    if (nr, nc) not in vizitate:
                        vizitate.add((nr, nc))
                        res = dfs((nr, nc), 'H', vizitate, drum + [(nr, nc)])
                        if res:
                            return res
                        vizitate.remove((nr, nc))

        return None

    # Pornim DFS. De la start putem pleca fie pe 'H', fie pe 'V'.
    # directie is None initial.
    set_vizitate = {celula_start}
    circuit = dfs(celula_start, None, set_vizitate, [celula_start])

    if circuit:
        # Pastram circuitul fara celula de final (care e la fel ca prima)
        # returneaza lista celulelor: [celula_start, cell2, cell3, cell4]
        return circuit[:-1]

    return []