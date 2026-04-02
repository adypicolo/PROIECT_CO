import numpy as np

def transformarePLS(c, a, b, semne, cond_semn, tip_problema):
    # Creeaza matricea restrictiilor si lista coeficientilor functiei obiectiv
    ma, mc = np.array(a, dtype=float), list(c)
    # Numele variabilelor originale (x1, x2, ...)
    nv_orig = [f"x{i + 1}" for i in range(len(c))]

    # Liste pentru matricea finala, costuri si nume variabile
    af, cf, nf = [], [], []

    # Tratam variabilele in functie de conditiile de semn
    for j in range(len(c)):
        reg = cond_semn[j].get()  # Conditia de semn pentru variabila

        # Daca variabila <= 0
        if "≤ 0" in reg:
            af.append(-ma[:, j])            # Inmulteste coloana cu -1
            cf.append(-mc[j])               # Inmulteste coeficientul cu -1
            nf.append(f"{nv_orig[j]}'")     # Marcheaza variabila

        # Daca variabila este libera (∈ R)
        elif "∈ R" in reg:
            af.append(ma[:, j])   # Partea pozitiva
            cf.append(mc[j])
            nf.append(f"{nv_orig[j]}+")

            af.append(-ma[:, j])  # Partea negativa
            cf.append(-mc[j])
            nf.append(f"{nv_orig[j]}-")

        # Daca variabila >= 0 (caz standard)
        else:
            af.append(ma[:, j])
            cf.append(mc[j])
            nf.append(nv_orig[j])

    # Constanta M folosita pentru variabile artificiale
    constanta_M = 10000 if tip_problema == "MIN" else -10000
    # Vectorul termenilor liberi
    bs = np.array(b, dtype=float)

    # Liste pentru variabile slack si artificiale
    slack_cols, slack_costs, slack_names = [], [], []
    art_cols, art_costs, art_names = [], [], []

    # Configuratia bazei initiale
    baza_config, cy, cz = [], 1, 1

    # Parcurge fiecare restrictie
    for i in range(len(bs)):
        s = semne[i].get()  # Tipul restrictiei

        # Restrictie de tip <=
        if s == "≤":
            col = np.zeros(len(bs))
            col[i] = 1  # Adauga variabila slack
            slack_cols.append(col)
            slack_costs.append(0.0)
            slack_names.append(f"y{cy}")

            baza_config.append(('y', len(slack_names) - 1))
            cy += 1

        # Restrictie de tip >=
        elif s == "≥":
            csur, cart = np.zeros(len(bs)), np.zeros(len(bs))
            csur[i], cart[i] = -1, 1  # Variabila surplus si artificiala

            slack_cols.append(csur)
            slack_costs.append(0.0)
            slack_names.append(f"y{cy}")

            art_cols.append(cart)
            art_costs.append(constanta_M)
            art_names.append(f"z{cz}")

            baza_config.append(('z', len(art_names) - 1))
            cy += 1
            cz += 1

        # Restrictie de tip =
        else:
            cart = np.zeros(len(bs))
            cart[i] = 1  # Variabila artificiala

            art_cols.append(cart)
            art_costs.append(constanta_M)
            art_names.append(f"z{cz}")

            baza_config.append(('z', len(art_names) - 1))
            cz += 1

    # Construieste matricea finala (concatenare coloane)
    ms = np.column_stack(af + slack_cols + art_cols)

    # Vectorul costurilor
    cs = cf + slack_costs + art_costs

    # Lista numelor variabilelor
    nf_final = nf + slack_names + art_names

    # Determina indicii bazei initiale
    bz = []
    for tip_v, r_i in baza_config:
        if tip_v == 'y':
            bz.append(len(nf) + r_i)
        else:
            bz.append(len(nf) + len(slack_names) + r_i)

    # Returneaza matricea, costurile, termenii liberi, baza si numele variabilelor
    return ms, np.array(cs), bs, bz, nf_final