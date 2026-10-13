import numpy as np
from aurora import estimar_oval_auroral


def test_oval_formula_kp_zero():
    assert abs(estimar_oval_auroral(0) - 64.6) < 1e-9


def test_oval_decresce_com_kp_maior():
    lat_baixo = estimar_oval_auroral(2)
    lat_alto = estimar_oval_auroral(8)
    assert lat_alto < lat_baixo
