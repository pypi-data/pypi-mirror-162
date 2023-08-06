# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.hyperbolic
"""
from test.helper import check_evaluation

# Adapted from symja_android_library/symja_android_library/rules/ArcCosRules.m
def test_ArcCosh():
    for str_expr, str_expected in (
        ("ArcCosh[0]", "I*Pi/2"),
        ("ArcCosh[1/2]", "I*Pi/3"),
        ("ArcCosh[-1/2]", "2/3*I*Pi"),
        ("ArcCosh[Sqrt[2]/2]", "1/4*I*Pi"),
        ("ArcCosh[-Sqrt[2]/2]", "3/4*I*Pi"),
        ("ArcCosh[Sqrt[3]/2]", "1/6*I*Pi"),
        ("ArcCosh[-Sqrt[3]/2]", "5/6*I*Pi"),
        ("ArcCosh[1]", "0"),
        ("ArcCosh[-1]", "Pi I"),
        ("ArcCosh[Infinity]", "Infinity"),
        ("ArcCosh[-Infinity]", "Infinity"),
        # ("ArcCosh[I*Infinity]", "Infinity"),  # Needs fixing; we get ComplexInfinity
        # ("ArcCosh[-I*Infinity]", "Infinity"),  # Needs fixing; we get ComplexInfinity
        # ("ArcCosh[ComplexInfinity]", "Infinity"), # Needs fixing; we get ComplexInfinity
    ):
        check_evaluation(str_expr, str_expected)
