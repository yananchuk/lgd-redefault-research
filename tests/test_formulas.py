import numpy as np

from lgd_sim.formulas import lgd_basic, lgd_lgc, lgd_new, lgd_new_adj, lgd_prd


def test_lgd_prd_collapses_to_basic_when_prd_is_zero():
    pc, rr = 0.2, 0.4
    assert lgd_prd(pc, rr, prd=0.0) == lgd_basic(pc, rr)


def test_lgd_new_collapses_to_basic_when_prd_is_zero():
    pc, rr, rr_brd = 0.2, 0.4, 0.5
    assert lgd_new(pc, rr, prd=0.0, rr_brd=rr_brd) == lgd_basic(pc, rr)


def test_lgd_lgc_collapses_to_basic_when_lgc_is_zero():
    pc, rr = 0.2, 0.4
    assert lgd_lgc(pc, rr, lgc=0.0) == lgd_basic(pc, rr)


def test_lgd_new_matches_lgd_prd_when_rr_brd_is_zero():
    pc, rr, prd = 0.2, 0.4, 0.1
    assert lgd_new(pc, rr, prd, rr_brd=0.0) == lgd_prd(pc, rr, prd)


def test_lgd_new_adj_collapses_to_lgd_new_when_rr_ard_equals_rr():
    pc, rr, prd, rr_brd = 0.2, 0.4, 0.1, 0.3
    assert lgd_new_adj(pc, rr, prd, rr_brd, rr_ard=rr) == lgd_new(pc, rr, prd, rr_brd)


def test_lgd_new_adj_collapses_to_lgd_prd_when_rr_ard_equals_rr_and_rr_brd_is_zero():
    pc, rr, prd = 0.2, 0.4, 0.1
    assert lgd_new_adj(pc, rr, prd, rr_brd=0.0, rr_ard=rr) == lgd_prd(pc, rr, prd)


def test_lgd_new_adj_collapses_to_basic_when_prd_is_zero():
    pc, rr, rr_brd, rr_ard = 0.2, 0.4, 0.5, 0.1
    assert lgd_new_adj(pc, rr, prd=0.0, rr_brd=rr_brd, rr_ard=rr_ard) == lgd_basic(pc, rr)


def test_formulas_accept_numpy_arrays():
    pc = np.array([0.1, 0.2, 0.3])
    rr = np.array([0.4, 0.5, 0.6])
    result = lgd_basic(pc, rr)
    expected = (1 - pc) * (1 - rr)
    np.testing.assert_array_equal(result, expected)
