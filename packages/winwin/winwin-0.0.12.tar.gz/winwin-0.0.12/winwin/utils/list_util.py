# -*- coding: utf-8 -*-
# @Time    : 2022-07-20 21:00
# @Author  : zbmain

def reverse(arr: list) -> list:
    return arr.reverse() or arr


def append(arr, element):
    return arr.append(element) or arr


def push(arr, element):
    return append(arr, element)


def extend(arr1, arr2):
    return arr1.extend(arr2) or arr1
