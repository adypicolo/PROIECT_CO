from fractions import Fraction

def transformaraFractie(numar):
    if abs(numar) >= 10000:
        return "M" if numar > 0 else "-M"

    # Transforma numarul in fractie(0.5 -> 1/2)
    fractie = Fraction(numar).limit_denominator(100)
    return str(fractie)
