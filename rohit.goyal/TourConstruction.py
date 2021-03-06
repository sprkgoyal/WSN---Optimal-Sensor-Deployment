from cmath import inf
import numpy as np
from collections import defaultdict
from reliability import Reliability

alpha = 2
beta = 3
Target_under = defaultdict(lambda :[])

def dist(a: tuple, b: tuple) -> float:
    return np.sqrt(np.power(a[0]-b[0], 2) + np.power(a[1]-b[1], 2))


def equal(T_cov: list, T: list) -> bool:
    for item in T:
        if item not in T_cov:
            return False
    return True


def find_Target_under(D: list, T: list, r_c: int) -> None:
    for d in D:
        for t in T:
            if dist(d, t) <= r_c:
                Target_under[d].append(t)


def find_N_ifull(S_k: list, node_points: list, r_c: int) -> list:

    N_ifull = set()
    
    for node1 in S_k:
        for node in node_points:
            if dist(node, node1) <= r_c:
                N_ifull.add(node)

    return list(N_ifull)


def find_N_ieff(node_points: list, T_cov: list) -> list:
    
    N_ieff = set()
    T_cov_tmp = T_cov.copy()

    for node in node_points:
        for target in Target_under[node]:
            if target not in T_cov_tmp:
                T_cov_tmp.append(target)
                N_ieff.add(node)
    
    return list(N_ieff)


def find_coverage_gain(N: list, T_cov: list) -> int:
    
    ret = 0
    for node in N:
        for target in Target_under[node]:
            if target not in T_cov:
                ret += 1

    return ret


def next_best_node(d_o: tuple, tau: list, N_i: list, r_c: int, alpha: float, beta: float) -> tuple:
    
    phermone_vals = defaultdict(lambda :0)

    deno_sum = 0
    for node in N_i:
        if d_o != node:
            eta = 1 / dist(d_o, node)
            deno_sum += np.power(tau[d_o][node], alpha) * np.power(eta, beta)

    for node in N_i:
        if d_o != node:
            eta = 1 / dist(d_o, node)
            phermone_vals[node] = (np.power(tau[d_o][node], alpha) * np.power(eta, beta)) / deno_sum

    ret = d_o
    phermone_vals[d_o] = 0

    for node, p_val in phermone_vals.items():
        if p_val > phermone_vals[ret]:
            ret = node

    return ret

def Tour_Construction(D: list, T: list, d_o: tuple, R_min: float, tau_mat: list,
                r_c: int, alpha: float = 2, beta: float = 3) -> list:
    '''
        D: set of possible node positions (x, y)
        T: set of target points (x, y)
        d_o: starting point belongs to D
        R_min: min reliability lie in [0, 1]
        _lambda: failure probabilty of node
        tau_mat: phermone value of each path
        r_c: communication range of each node
    '''

    # initialization of variables

    S = []
    S_reliability = 0
    k = 0
    D_minus = D.copy()
    find_Target_under(D, T, r_c)
    
    #finding a reliable connected cover
    while S_reliability < R_min:
        # print('xxxx')
        #initializaion variables for this iteration
        k += 1
        S_k, T_cov = [[] for i in range(2)]

        # covering all target points
        while not equal(T_cov, T):
            # print('mmmm')
            N_ifull = find_N_ifull(S_k, D_minus, r_c)
            N_ieff = find_N_ieff(N_ifull, T_cov)
            N_i = N_ieff if len(N_ieff) != 0 else N_ifull
            converage_gain_i = find_coverage_gain(N_i, T_cov)
            S_k.append(d_o)
            # print(N_i)
            for target in Target_under[d_o]:
                if target not in T_cov:
                    T_cov.append(target)
            d_o = next_best_node(d_o, tau_mat, N_i, r_c, alpha, beta)
        
        # Updating the variables after covering all arget points
        S.append(S_k)
        S_reliability += Reliability(S_k, T)
        for node in S_k:
            if node in D_minus:
                D_minus.remove(node)
    
    Sret = []
    for lst in S:
        s = set()
        for item in lst:
            s.add(item)
        Sret.append(list(s))

    return Sret