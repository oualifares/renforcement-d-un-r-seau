#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class Graphe(object):
    def __init__(self):
        """
        """
        self.dic_a = dict()
        self.dic_s = dict()

    def noms_stations_str(self):

        res = []
        for sommet in self.noms:
            res.append(self.noms[sommet] + " (" + str(sommet) + ')')
        return '\n'.join(sorted(res))

    def ajouter_sommet(self, sommet):
        """
        """
        lst = list(sommet)
        self.dic_s[lst[0]] = lst[1]

    def ajouter_sommets(self, iterable):
        """.
        """
        for s in iterable:
            self.ajouter_sommet(s)

    def ajouter_arete(self, u, v, ligne):
        """ 
        """
        if u not in self.dic_a:
            self.dic_a[u] = set()

        if v not in self.dic_a:
            self.dic_a[v] = set()

        self.dic_a[u].add((v, ligne))
        self.dic_a[v].add((u, ligne))

    def ajouter_aretes(self, iterable):
        """
        """
        for (u, v , nom) in iterable:
            self.ajouter_arete(u, v, nom)

    def aretes(self):
        """
        """
        aretes = set()
        for arr in self.dic_a:
            for v in self.dic_a[arr]:
                mx = max(arr, v[0])
                mn = min(arr, v[0])
                aretes.add((mn, mx, v[1]))
        return aretes

    def degre(self, sommet):
        """
        """
        return len(self.dic_a[sommet])

    def sommets(self):
        """
        """
        return self.dic_s.keys()

    def nb_aretes(self):
        """
        """
        nombre_arretes = 0
        for v in self.dic_a.values():
            nombre_arretes += len(v)
        return nombre_arretes// 2

    def nb_sommets(self):
        """
        """
        return len(self.dic_s)

    def nom_sommet(self, sommet):
        return self.dic_s[sommet]

    def voisins(self, sommet):
        """
        """
        return set([v for v in self.dic_a[sommet]])
        
    def Degre(self, id_s):
        return len(self.graphe[id_s])

