from fractions import Fraction

# =====================================================================
# 1. UTILITARE: Conversie Fractie
# =====================================================================
def transformaraFractie(numar):
    if abs(numar) >= 10000:
        return "M" if numar > 0 else "-M"
    # Corectam erorile de precizie din float inainte de conversie
    numar_rotunjit = round(float(numar), 6)
    fractie = Fraction(numar_rotunjit).limit_denominator(1000)

    if fractie.denominator == 1:
        return str(fractie.numerator)
    return f"{fractie.numerator}/{fractie.denominator}"