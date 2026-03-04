# ruff: noqa: N802, N803, ANN001, ANN202, D400, D415, D205, RET504, B020, PLR1704

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from mxlpy import Derived, Model, fns
from mxlpy.surrogates import qss

__all__ = [
    "Fluorescence",
    "K_ATPsynth",
    "K_QAPQ",
    "K_cytb6f",
    "PSII",
    "Quencher",
    "four_divided_value",
    "get_matuszynska_2016",
    "include_derived_quantities",
    "include_rates",
    "neg_divided_value",
    "neg_fourteenthirds_divided_value",
    "pH",
    "pHinv",
    "two_divided_value",
    "v_ATPact",
    "v_ATPcons",
    "v_ATPsynth",
    "v_Leak",
    "v_PQ",
    "v_PSII",
    "v_PsbSP",
    "v_Xcyc",
]

if TYPE_CHECKING:
    from collections.abc import Iterable


def two_divided_value(x: float) -> float:
    return 2 / x


def four_divided_value(x: float) -> float:
    return 4 / x


def neg_fourteenthirds_divided_value(x: float) -> float:
    return -(14 / 3) / x


def neg_divided_value(x: float) -> float:
    return -1 / x


def pH(H):
    return -np.log10(H * 2.5e-4)


def pHinv(pH):
    return 3.2e4 * 10**-pH


def K_QAPQ(F, E0_QA, E0_PQ, pH_st, R, T):
    RT = R * T
    DG1 = -F * E0_QA
    DG2 = -2 * F * E0_PQ + 2 * pH_st * np.log(10) * RT
    DG0 = -2 * DG1 + DG2
    Keq = np.exp(-DG0 / RT)
    return Keq


def K_cytb6f(pH_lu, F, E0_PQ, R, T, E0_PC, pH_st):
    """Equilibriu constant of Cytochrome b6f"""
    RT = R * T
    DG1 = -2 * F * E0_PQ + 2 * RT * np.log(10) * pH_lu
    DG2 = -F * E0_PC
    DG3 = RT * np.log(10) * (pH_st - pH_lu)
    DG = -DG1 + 2 * DG2 + 2 * DG3
    Keq = np.exp(-DG / RT)
    return Keq


def K_ATPsynth(pH_lu, DG_ATP, pH_st, R, T, Pi):
    """Equilibrium constant of ATP synthase. For more
    information see Matuszynska et al 2016 or Ebenhöh et al. 2011,2014
    """
    RT = R * T
    DG = DG_ATP - np.log(10) * (pH_st - pH_lu) * (14 / 3) * RT
    Keq = Pi * np.exp(-DG / RT)
    return Keq


def Quencher(psbS, Zx, PsbSP, K_ZSat, gamma_0, gamma_1, gamma_2, gamma_3):
    """Quencher mechanism

    accepts:
    psbS: fraction of non-protonated PsbS protein
    Vx: fraction of Violaxanthin
    """
    Zs = Zx / (Zx + K_ZSat)

    Q = (
        gamma_0 * (1 - Zs) * psbS
        + gamma_1 * (1 - Zs) * PsbSP
        + gamma_2 * Zs * PsbSP
        + gamma_3 * Zs * psbS
    )
    return Q


def PSII(PQ, PQH_2, Q, pfd, k_PQH2, K_QAPQ, k_H, k_F, k_P, PSII_tot) -> Iterable[float]:
    # light = np.ones(len(P)) * light
    b0 = pfd + k_PQH2 * PQH_2 / K_QAPQ
    b1 = k_H * Q + k_F
    b2 = k_H * Q + k_F + k_P

    if any(
        not isinstance(i, np.ndarray) for i in [b0, b1, k_PQH2, PQ, pfd, b2, PSII_tot]
    ):
        M = np.array(
            [
                [-b0, b1, k_PQH2 * PQ, 0],  # B0
                [pfd, -b2, 0, 0],  # B1
                [0, 0, pfd, -b1],  # B3
                [1, 1, 1, 1],
            ]
        )

        A = np.array([0, 0, 0, PSII_tot])
        B0, B1, B2, B3 = np.linalg.solve(M, A)
        return B0, B1, B2, B3

    B0 = []
    B1 = []
    B2 = []
    B3 = []

    for b0, b1, k_PQH2, PQ, pfd, b2, PSII_tot in zip(
        b0, b1, k_PQH2, PQ, pfd, b2, PSII_tot, strict=False
    ):
        M = np.array(
            [
                [-b0, b1, k_PQH2 * PQ, 0],  # B0
                [pfd, -b2, 0, 0],  # B1
                [0, 0, pfd, -b1],  # B3
                [1, 1, 1, 1],
            ]
        )

        A = np.array([0, 0, 0, PSII_tot])
        B0_, B1_, B2_, B3_ = np.linalg.solve(M, A)
        B0.append(B0_)
        B1.append(B1_)
        B2.append(B2_)
        B3.append(B3_)

    return np.array(B0), np.array(B1), np.array(B2), np.array(B3)  # type: ignore


def Fluorescence(Q, B0, B2, k_H, k_F, k_P):
    """Fluorescence function"""
    Fluo = k_F / (k_H * Q + k_F + k_P) * B0 + k_F / (k_H * Q + k_F) * B2
    return Fluo


def include_derived_quantities(m: Model) -> Model:
    m.add_derived(name="pH_lu", fn=pH, args=["H_lu"])
    m.add_derived(name="H_st", fn=pHinv, args=["pH_st"])
    m.add_derived(name="K_pHSat_inv", fn=pHinv, args=["K_pHSat"])
    m.add_derived(name="K_pHSatLHC_inv", fn=pHinv, args=["K_pHSatLHC"])
    m.add_derived(
        name="K_QAPQ", fn=K_QAPQ, args=["F", "E0_QA", "E0_PQ", "pH_st", "R", "T"]
    )
    m.add_derived(
        name="K_cytb6f",
        fn=K_cytb6f,
        args=["pH_lu", "F", "E0_PQ", "R", "T", "E0_PC", "pH_st"],
    )
    m.add_derived(
        name="K_ATPsynth",
        fn=K_ATPsynth,
        args=["pH_lu", "DG_ATP", "pH_st", "R", "T", "Pi"],
    )
    m.add_derived(name="PQ", fn=fns.moiety_1s, args=["PQH_2", "PQ_tot"])
    m.add_derived(name="ADP_st", fn=fns.moiety_1s, args=["ATP_st", "AP_tot"])
    m.add_derived(name="PsbSP", fn=fns.moiety_1s, args=["psbS", "PsbS_tot"])
    m.add_derived(name="Zx", fn=fns.moiety_1s, args=["Vx", "X_tot"])
    m.add_derived(
        name="Q",
        fn=Quencher,
        args=[
            "psbS",
            "Zx",
            "PsbSP",
            "K_ZSat",
            "gamma_0",
            "gamma_1",
            "gamma_2",
            "gamma_3",
        ],
    )
    m.add_surrogate(
        name="psii",
        surrogate=qss.Surrogate(
            model=PSII,
            args=[
                "PQ",
                "PQH_2",
                "Q",
                "pfd",
                "k_PQH2",
                "K_QAPQ",
                "k_H",
                "k_F",
                "k_P",
                "PSII_tot",
            ],
            outputs=["B0", "B1", "B2", "B3"],
        ),
    )
    m.add_derived(
        name="Fluo", fn=Fluorescence, args=["Q", "B0", "B2", "k_H", "k_F", "k_P"]
    )
    return m


def v_PSII(B1, k_P):
    """Reduction of PQ due to ps2"""
    v = k_P * 0.5 * B1
    return v


def v_PQ(PQH_2, pfd, k_Cytb6f, k_PTOX, O2_ex, PQ_tot, K_cytb6f):
    """Oxidation of the PQ pool through cytochrome and PTOX"""
    kPFD = k_Cytb6f * pfd
    k_PTOX = k_PTOX * O2_ex
    a1 = kPFD * K_cytb6f / (K_cytb6f + 1)
    a2 = kPFD / (K_cytb6f + 1)
    v = (a1 + k_PTOX) * PQH_2 - a2 * (PQ_tot - PQH_2)
    return v


def v_ATPsynth(ATP_st, ATPase_ac, k_ATPsynth, K_ATPsynth, AP_tot):
    """Production of ATP by ATPsynthase"""
    v = ATPase_ac * k_ATPsynth * (AP_tot - ATP_st - ATP_st / K_ATPsynth)
    return v


def v_ATPact(ATPase_ac, pfd, k_ActATPase, k_DeactATPase):
    """Activation of ATPsynthase by light"""
    switch = pfd > 0
    v = (
        k_ActATPase * switch * (1 - ATPase_ac)
        - k_DeactATPase * (1 - switch) * ATPase_ac
    )
    return v


def v_Leak(H_lu, k_leak, H_st):
    """Transmembrane proton leak"""
    v = k_leak * (H_lu - H_st)
    return v


def v_ATPcons(ATP_st, k_ATPconsum):
    """ATP consuming reaction"""
    v = k_ATPconsum * ATP_st
    return v


def v_Xcyc(Vx, H_lu, nhx, K_pHSat_inv, k_DV, k_EZ, X_tot):
    """Xanthophyll cycle"""
    a = H_lu**nhx / (H_lu**nhx + K_pHSat_inv**nhx)
    v = k_DV * a * Vx - k_EZ * (X_tot - Vx)
    return v


def v_PsbSP(psbS, H_lu, nhl, K_pHSatLHC_inv, k_prot, k_deprot, PsbS_tot):
    """Protonation of PsbS protein"""
    a = H_lu**nhl / (H_lu**nhl + K_pHSatLHC_inv**nhl)
    v = k_prot * a * psbS - k_deprot * (PsbS_tot - psbS)
    return v


def include_rates(m: Model):
    m.add_reaction(
        name="v_PSII",
        fn=v_PSII,
        args=["B1", "k_P"],
        stoichiometry={
            "PQH_2": 1,
            "H_lu": Derived(fn=two_divided_value, args=["b_H"]),
        },
    )

    m.add_reaction(
        name="v_PQ",
        fn=v_PQ,
        args=["PQH_2", "pfd", "k_Cytb6f", "k_PTOX", "O2_ex", "PQ_tot", "K_cytb6f"],
        stoichiometry={
            "PQH_2": -1,
            "H_lu": Derived(fn=four_divided_value, args=["b_H"]),
        },
    )

    m.add_reaction(
        name="v_ATPsynth",
        fn=v_ATPsynth,
        args=["ATP_st", "ATPase_ac", "k_ATPsynth", "K_ATPsynth", "AP_tot"],
        stoichiometry={
            "ATP_st": 1,
            "H_lu": Derived(fn=neg_fourteenthirds_divided_value, args=["b_H"]),
        },
    )

    m.add_reaction(
        name="v_ATPact",
        fn=v_ATPact,
        args=["ATPase_ac", "pfd", "k_ActATPase", "k_DeactATPase"],
        stoichiometry={"ATPase_ac": 1},
    )

    m.add_reaction(
        name="v_Leak",
        fn=v_Leak,
        args=["H_lu", "k_leak", "H_st"],
        stoichiometry={"H_lu": Derived(fn=neg_divided_value, args=["b_H"])},
    )

    m.add_reaction(
        name="v_ATPcons",
        fn=v_ATPcons,
        args=["ATP_st", "k_ATPconsum"],
        stoichiometry={"ATP_st": -1},
    )

    m.add_reaction(
        name="v_Xcyc",
        fn=v_Xcyc,
        args=["Vx", "H_lu", "nhx", "K_pHSat_inv", "k_DV", "k_EZ", "X_tot"],
        stoichiometry={"Vx": -1},
    )

    m.add_reaction(
        name="v_PsbSP",
        fn=v_PsbSP,
        args=[
            "psbS",
            "H_lu",
            "nhl",
            "K_pHSatLHC_inv",
            "k_prot",
            "k_deprot",
            "PsbS_tot",
        ],
        stoichiometry={"psbS": -1},
    )

    return m


def get_matuszynska_2016() -> Model:
    m = Model()

    m.add_parameters(
        {
            # Pool sizes
            "PSII_tot": 2.5,  # PSII reaction centres
            "PQ_tot": 20,  # PQ + PQH2
            "AP_tot": 50,  # total adenosine phosphate pool (ATP + ADP)
            "PsbS_tot": 1,  # LHCII normalized
            "X_tot": 1,  # toal xanthophylls
            "O2_ex": 8,  # external oxygen
            "Pi": 0.01,  # internal pool of phosphates
            # Rate constants and key parameters
            "k_Cytb6f": 0.104,
            "k_ActATPase": 0.01,
            "k_DeactATPase": 0.002,
            "k_ATPsynth": 20.0,
            "k_ATPconsum": 10.0,
            "k_PQH2": 250.0,
            "k_H": 5e9,
            "k_F": 6.25e8,
            "k_P": 5e9,
            "k_PTOX": 0.01,
            "pH_st": 7.8,
            "k_leak": 1000,
            "b_H": 100,
            "hpr": 14.0 / 3.0,
            # Parameter associated with xanthophyll cycle
            "k_DV": 0.0024,
            "k_EZ": 0.00024,
            "K_pHSat": 5.8,
            "nhx": 5.0,
            "K_ZSat": 0.12,
            # Parameter associated with PsbS protonation
            "nhl": 3,
            "k_deprot": 0.0096,
            "k_prot": 0.0096,
            "K_pHSatLHC": 5.8,
            # Fitted quencher contribution factors
            "gamma_0": 0.1,
            "gamma_1": 0.25,
            "gamma_2": 0.6,
            "gamma_3": 0.15,
            # Physical constants
            "F": 96.485,
            "R": 8.3e-3,  # J in KJ
            "T": 298,
            # Standard potentials
            "E0_QA": -0.140,
            "E0_PQ": 0.354,
            "E0_PC": 0.380,
            "DG_ATP": 30.6,
            # pfd
            "pfd": 100,
        }
    )

    m.add_variables(
        {
            "PQH_2": 0,  # reduced Plastoquinone
            "H_lu": 6.32975752e-05,  # luminal Protons
            "ATPase_ac": 0,  # ATPactivity
            "ATP_st": 25.0,  # ATP
            "psbS": 1,  # fraction of non-protonated PsbS
            "Vx": 1,  # fraction of Violaxanthin
        }
    )

    m = include_derived_quantities(m)
    m = include_rates(m)

    return m
