from graphe import *
import argparse
import os
from copy import deepcopy
import random
import glob

def charger_donnees(graphe, fichier):
    "fonction qui charges les données des fichier texts données"
    nom = fichier.split('.')[0]
    with open(fichier,'r') as fil:
        for lines in fil:
            if lines[0] == "#":
                mode = lines[2:-1]
            elif mode == "stations":
                lines = lines.split(':')
                graphe.ajouter_sommet((int(lines[0]), lines[1][:-1]))
            elif mode == "connexions":
                lines = lines.split('/')
                graphe.ajouter_arete(int(lines[0]), int(lines[1]), nom)

def Numerotations(graphe):
    debut = dict()
    parent = dict()
    ancetre = dict()
    instant = 0
    for sommet in graphe.sommets():
        parent[sommet] = None
        debut[sommet] = 0
        ancetre[sommet] = 0
        
    def aux(s):
        nonlocal instant
        instant = instant + 1
        debut[s] = ancetre[s] = instant
        for voisin, tmp in sorted(graphe.voisins(s)):
            if debut[voisin] != 0:
                if parent[s] != voisin :
                    ancetre[s] = min(ancetre[s], debut[voisin])
            else:
                parent[voisin] = s
                aux(voisin)
                ancetre[s] = min(ancetre[s], ancetre[voisin])

    for sommet in sorted(graphe.sommets()):
        if debut[sommet] == 0:
            aux(sommet)
    return debut, parent, ancetre

def racine(reseau, parent):
    res = []
    for element in reseau.sommets():
        if parent[element] == None:
            res.append(element)
    return res

def points_articulation(graphe):
    debut, parent, ancetre = Numerotations(graphe)
    articulations = set()
    rac = set() 

    [rac.add(v) for v in parent if parent[v] == None]
    for depart in rac:
        degre = graphe.degre(depart)

        for voisin, _ in graphe.voisins(depart):
            if parent[voisin] != depart:
                degre -= 1

        if degre >= 2:
            articulations.add(depart)

    rac.add(None)
    for som in graphe.sommets() :
        if (parent[som] not in rac) and ancetre[som] >= debut[parent[som]]:
            articulations.add(parent[som]) 
    return articulations

def ponts(reseau):
    debut, parent, ancetre = Numerotations(reseau)
    res = set()
    for sommet in parent:
        if  parent[sommet] != None and ancetre[sommet] > debut[parent[sommet]]  :
            res.add((parent[sommet], sommet))
    return res

def verifie(sommet,graphe):
    pont = ponts(graphe)
    for sommet1, sommet2 in pont:
        if sommet1 == sommet or sommet2 == sommet:
            return True
    return False

def trouve_csp(sommet, ponts, reseau):
    def aux(sommet, ponts, reseau):
        nonlocal deja_visite
        deja_visite.append(sommet)
        for voisin in reseau.voisins(sommet):
            if (sorted([sommet, voisin]) not in ponts) and (voisin not in deja_visite):
                aux(voisin, ponts, reseau)

    deja_visite = []
    aux(sommet, ponts, reseau)
    return sorted(deja_visite)

def rech_lst(element, lst):
    for ss_lst in lst:
        if element in ss_lst:
            return True
    return False

def const_csp(reseau, res_ponts):
    res = []
    for couple in res_ponts:
        for sommet in couple:
            if rech_lst(sommet, res) != True:
                res.append(trouve_csp(sommet, res_ponts, reseau))
    return res

def trouve_feuille(csp, ponts):
    res = []
    x = 0
    for lst in csp:
        for element in lst:
            for lst2 in ponts:
                if element in lst2:
                    x += 1
        if x < 2:
            res.append(lst)
        x = 0
    return res


    
def amelioration_points_articulation(graphe):
    articulations = list(points_articulation(graphe))
    initial = articulations.copy()
    debut, parent, ancetre = Numerotations(graphe)
    visites = dict()
    voisins = list()
    racine = None

    def racine_sommet(sommet):
        def indice(sommet):
            i = 0
            for point, _ in graphe.voisins(sommet):
                i += 1 if parent[point] == sommet and ancetre[point] >= debut[sommet] else 0
            return i

        nonlocal racine
        if parent[sommet] == None:
            racine = sommet
        else:
            if sommet in articulations and indice(sommet) < 2:
                visites[sommet] = True
                articulations.remove(sommet)
            racine_sommet(parent[sommet])

    aretes = set()
    for point in articulations:
        visites[point] = False

    while not all(point for point in visites.values()):
        point = articulations[0]
        for sommet in articulations:
            if debut[sommet] > debut[point]:
                point = sommet
        if parent[point] is None:
            for voisin, _ in graphe.voisins(point):
                if  parent[voisin] == point:
                    voisins.append(voisin)
            for i in range(len(voisins) - 1):
                aretes.add((voisins[i],voisins[i + 1]))
            visites[point] = True
            articulations.remove(point)
        else :
            racine_sommet(point)
            for voisin, _ in graphe.voisins(point):
                if not voisin in initial and parent[voisin] == point and ancetre[voisin] >= debut[point]:
                    aretes.add((voisin, racine))
                if point in articulations:
                    visites[point] = True
    return aretes


def amelioration_ponts(graphe):
    aretes = set()
    visite = dict()
    feuilles = set()
    lst_feuilles = list()
    pont = ponts(graphe)
    nbr = 0
    def aux(depart, extremite):
        visite[depart] = True
        feuille.add(depart)
        for voisin in graphe.voisins(depart):
            if not visite[voisin[0]] and voisin[0] != extremite :
                if not verifie(voisin[0],graphe):
                    aux(voisin[0],extremite)
                else:
                    feuille.add(voisin[0])
    for a, b in pont:
        for k in range(2):
            feuille = set()
            for sommet in graphe.sommets():
                visite[sommet] = False
            aux(a,b)
            for sommet in feuille :
                if verifie(sommet,graphe): 
                    nbr += 1
            if nbr < 2:
                feuilles.add(tuple(feuille))
            nbr = 0
            tmp = a
            a = b
            b = tmp 

    for e in feuilles:
        lst_feuilles.append(e)
    for i in range(len(lst_feuilles) - 1):
        r1 = random.choice(lst_feuilles[i])
        r2 = random.choice(lst_feuilles[i + 1])
        aretes.add((r1, r2))
    return aretes

  
def affiche_liste_stations(reseau):
    sommets = reseau.sommets()
    stations = []
    for s in sommets:
        stations.append((reseau.nom_sommet(s), s))
    for station in sorted(stations):
        print("{0} ({1})".format(station[0], station[1]))
    print()


def affiche_ameliorer_articulations(reseau):
    liste= list()
    liste = amelioration_points_articulation(reseau)
    print("On peut éliminer tous les pints articulations du réseau en rajoutant les "+str(len(liste))+  " arêtes suivantes:" )
    print()
    for a,b in    liste:  
        print(reseau.nom_sommet(a) +" -- "+reseau.nom_sommet(b))

def affiche_articulations(reseau):
    points = list(points_articulation(reseau))

    print("Le reseau contient les {0} points articulations suivants :".format(len(points)))
    print()
    for i, sommet in enumerate(points):
        points[i] = reseau.nom_sommet(sommet)
    for i, nom in enumerate(sorted(points)):
        print("{0} : {1}".format(i + 1, nom))
    print()

def affiche_ameliorer_ponts(reseau):
    liste= list()
    liste = amelioration_ponts(reseau)
    print("On peut éliminer tous les ponts du réseau en rajoutant les "+str(len(liste))+  " arêtes suivantes:")
    print()
    for a, b in liste:
        print(reseau.nom_sommet(a) +" -- "+reseau.nom_sommet(b))

def affiche_ponts(reseau):
    lst = list(ponts(reseau))
    print("Le reseau contient {0} ponts suivants :".format(len(lst)))
    print()

    for nbr, sommets in enumerate(lst):
        sommets = sorted([reseau.nom_sommet(sommets[0]), reseau.nom_sommet(sommets[1])])
        lst[nbr] = "- {0} -- {1}".format(sommets[0], sommets[1])

    for e in sorted(lst):
        print(e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ponts",action ='store_true')
    p.add_argument("--ameliorer-articulations",action ='store_true')
    p.add_argument("--ameliorer-ponts",action ='store_true')
   
    p.add_argument("--metro",nargs='*')
    p.add_argument("--rer",nargs='*')
    p.add_argument("--liste-stations",action ='store_true')
    p.add_argument("--articulations",action ='store_true')
    
    args = p.parse_args()
    reseau = Graphe()

    if args.rer or args.metro:
        if args.metro:
            print("Chargement des lignes {0} de metro ... terminé.".format(args.metro))
            for ligne in args.metro:
                charger_donnees(reseau, "METRO_{0}.txt".format(ligne))
        if args.rer:
            print("Chargement des lignes {0} de rer ... terminé.".format(args.metro))
            for ligne in args.rer:
                charger_donnees(reseau, "RER_{0}.txt".format(ligne))
    else:
        if args.metro == []:
            print("Chargement de toutes les lignes de metro ...")
            for fichier in glob.iglob('données/METRO*.txt'):
                charger_donnees(reseau, fichier.split('/')[-1])
            print("terminé.")

        if args.rer == []:
            print("Chargement de toutes les lignes de rer ...")
            for fichier in glob.iglob('données/RER*.txt'):
                charger_donnees(reseau, fichier.split('/')[-1])
            print("terminé.")
    nbr_a = reseau.nb_aretes()
    nbr_s = reseau.nb_sommets()

    print("Le réseau contient {0} sommets et {1} aretes".format(nbr_s, nbr_a))
    print()

    fonctions = globals()

    for argument in vars(args):
        if getattr(args, argument):
            fonct = 'affiche_' + argument
            if fonct in fonctions:
                fonctions[fonct](reseau)

if __name__ == "__main__":
    main()





