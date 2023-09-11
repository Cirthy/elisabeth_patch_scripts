import random
import copy
from math import comb
from bisect import bisect_left
import sys
import pickle
sys.path.append("../lib/DahuHunting")
from BF import BF


def hw(x):
    x -= (x >> 1) & 0x5555555555555555
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    return ((x * 0x0101010101010101) & 0xffffffffffffffff ) >> 56

def clear_bits(x, bits):
    ret = x
    for bit in bits:
        ret = clear_bit(ret, bit)
    return ret

def clear_bit(x, bit):
    return x & ~(1<<bit)


def create_deg_partition(n):
    deg_partition = [[] for _ in range(n + 1)]
    for i in range(1<<n):
        deg_partition[hw(i)].append(i)
    return deg_partition

def deg(f, deg_partition=None):
    if(deg_partition == None):
        deg_partition = create_deg_partition(f.l)
    f.update_ANF()
    n = f.l
    for d in range(n, -1, -1):
        for i in deg_partition[d]:
            if(f.ANF[i] == 1):
                return d


def create_deg_partition(n):
    deg_partition = [[] for _ in range(n + 1)]
    for i in range(1<<n):
        deg_partition[hw(i)].append(i)
    return deg_partition

def deg(f, deg_partition=None):
    if(deg_partition == None):
        deg_partition = create_deg_partition(f.l)
    f.update_ANF()
    n = f.l
    for d in range(n, -1, -1):
        for i in deg_partition[d]:
            if(f.ANF[i] == 1):
                return d


def update_anf_sorted(anf_sorted, new_monom, shift):
    d = hw(new_monom) - shift
    i = bisect_left(anf_sorted[d], new_monom)
    if(i != len(anf_sorted[d]) and anf_sorted[d][i] == new_monom):
        anf_sorted[d].pop(i)
    else:
        anf_sorted[d].insert(i, new_monom)
        

def deg_subfonctions(f, deg_f=None):  # Limited to 2 guesses (yet)
    deg_subfonctions = [[] for _ in range(7)]
    n = f.l
    deg_partition = create_deg_partition(n)
    if(deg_f == None):
        deg_f = deg(f, deg_partition)
    deg_subfonctions[0].append(deg_f)
    anf_size = min(deg_f + 1, 4)
    shift = deg_f - anf_size + 1 if anf_size == 4 else 0
    anf_sorted = [[i for i in sub_deg_partition if f.ANF[i] == 1] for sub_deg_partition in deg_partition[deg_f - anf_size + 1:deg_f + 1]]
    break_flag = 0
    for i in range(n): # 1st guess
        for i_value in range(2): # Value of the guess
            anf_cp = copy.deepcopy(anf_sorted)
            for k in range(anf_size - 1, -1, -1):
                while(len(anf_cp[k]) != 0):
                    if(anf_cp[k][0]>>i & 0x1 == 1): # if X_i is a factor of the monomial
                        if(i_value == 1):
                            update_anf_sorted(anf_cp, clear_bit(anf_cp[k][0], i), deg_f - anf_size + 1)
                        anf_cp[k].pop(0)
                    else:
                        deg_subfonctions[3 * i_value + 1].append(k + deg_f - anf_size + 1)
                        break_flag = 1
                        break
                if(break_flag == 1):
                    break_flag = 0
                    break
            if(k == 0 and len(anf_cp[0]) == 0):
                deg_subfonctions[3 * i_value + 1].append(-1) # error code
            anf_buf = copy.deepcopy(anf_cp)
            for j in range(i + 1, n): # 2nd guess
                for j_value in range(2): # Value of the guess
                    anf_cp = copy.deepcopy(anf_buf)
                    for k in range(anf_size - 1, -1, -1):
                        while(len(anf_cp[k]) != 0):
                            i_in_mon, j_in_mon = anf_cp[k][0]>>i & 0x1 == 1, anf_cp[k][0]>>j & 0x1 == 1
                            if(i_in_mon or j_in_mon):
                                if(not(i_in_mon and i_value == 0) and not(j_in_mon and j_value == 0)):
                                    update_anf_sorted(anf_cp, clear_bits(anf_cp[k][0], (i, j)), deg_f - anf_size + 1)
                                anf_cp[k].pop(0)
                            else:
                                deg_subfonctions[3 * i_value + 2 + j_value].append(k + deg_f - anf_size + 1)
                                break_flag = 1
                                break
                        if(break_flag == 1):
                            break_flag = 0
                            break
                    if(k == 0 and len(anf_cp[0]) == 0):
                        deg_subfonctions[3 * i_value + 2 + j_value].append(-1)
    return deg_subfonctions


def analysis_deg(n, path_tt="../data/tts", path_results="../data/results"):
    # n could be found when reading the tt
    f = BF(n)
    results = {"deg_subfonctions": [], "nb_monomials": []}
    cnt = 0
    with open(path_tt, 'r') as fd:
        char = fd.read(1)
        while(char):
            tt = []
            while(char != '\n'):
                tt.append(int(char))
                char = fd.read(1)
            print(cnt, ": tt loaded", end='', flush=True)
            f.set_TT(tt)
            f.update_ANF()
            results["nb_monomials"].append(sum(f.ANF))
            print(" - nb_monomials ok", end='', flush=True)
            results["deg_subfonctions"].append(deg_subfonctions(f))
            print(" - deg_subfonctions ok")
            cnt += 1
            char = fd.read(1)
    with open(path_results, 'wb') as fd:
        pickle.dump(results, fd)


# analysis_deg(18, path_tt="../data/margrethe/tts", path_results="../data/margrethe/results")
