import numpy as np


def validare_metoda_I(XB0, XBf, S, eps=1e-2):
    XB0 = np.array(XB0, dtype=float)
    XBf = np.array(XBf, dtype=float)
    S = np.array(S, dtype=float)
    XB0_estimat = S @ XBf
    if np.allclose(XB0, XB0_estimat, atol=eps):
        return True, "Relatia XB0 = S * XBf este verificata"
    else:
        return False, "Relatia NU se verifica"


def validare_feazibilitate(X, A, b, semne, c, z_final, eps=1e-2):
    """
    X - doar x1, x2, x3 optimi
    A - matricea originala
    b - vectorul b original
    semne - lista cu semnele ["<=", ">=", "="] luate din OptionMenu
    """
    X = np.array(X, dtype=float)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    erori = []
    for i in range(len(b)):
        rezultat_stanga = np.dot(A[i], X)
        semn = semne[i]

        if semn == "≤":
            if not (rezultat_stanga <= b[i] + eps):
                erori.append(f"R{i + 1}: {rezultat_stanga:.2f} nu este <= {b[i]}")
        elif semn == "≥":
            if not (rezultat_stanga >= b[i] - eps):
                erori.append(f"R{i + 1}: {rezultat_stanga:.2f} nu este >= {b[i]}")
        elif semn == "=":
            if not np.isclose(rezultat_stanga, b[i], atol=eps):
                erori.append(f"R{i + 1}: {rezultat_stanga:.2f} nu este egal cu {b[i]}")

    if len(erori) == 0:
        return True, "Solutia respecta toate restrictiile originale (AX ~ b)!"
    else:
        return False, "Erori: " + ", ".join(erori)