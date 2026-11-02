from __future__ import annotations

from .joueur import Joueur

from .plateau import Plateau, Case
from .exception import MancheError
from .Jeton import JetonRuine, PileJeton

"classe pour regrouper toutes les attributs et méthodes qui vont aider à dérouler une manche"

class Manche:
    Oxygene_depart = 25

    def __init__(self, joueurs: list[Joueur], plateau: "Plateau"):
        self._joueurs = joueurs
        self._plateau = plateau
        self._oxygene = self.Oxygene_depart
        self._tour = 0
        self._terminee = False
        self._dernier_rentre = None
        self._premier_suivant = None
        self._index_debut_jetons_perdus = None 


        for j in joueurs: #on met tous les joueurs en position pour commencer la manche
            if not hasattr(j,"reinitialiser_pour_manche"):
              raise MancheError("La classe Joueur doit implémenter la méthode reinitialiser_pour_manche")
            j.reinitialiser_pour_manche()

        #mettre à jour les cases occupées en fonction des positions des joueurs
        for case in self._plateau.cases:
            case.occupe = False

        for j in self._joueurs:
            
            if j.position != 0:#la case (sous marin) est la seule case à pouvoir être occupé par plusieurs joueurs
                self._plateau.get_case(j.position).occupe = True


    def joueur_courant(self) -> Joueur:
        return self._joueurs[self._tour]

    def avancer_tour(self):
        self._tour = (self._tour + 1) % len(self._joueurs) #pour être sûre qu'on passe bien au joueur d'après modulo le nombre de joueur)


    def consommer_oxygene(self, joueur: "Joueur"):
        self._oxygene -= joueur.penalite_oxygene()
        if self._oxygene <= 0:
            self._oxygene = 0
            self.fin_manche()

    @property
    def oxygene(self):
        return self._oxygene


    @property
    def terminee(self):
        return self._terminee

    def verifier_fin(self): #condition spécial d'arrêt
        if all(j.position == 0 for j in self._joueurs) or self._oxygene==0: #si tout le monde au sous-marin on arrête la manche
            self.fin_manche()


    def fin_manche(self): #quand plus d'oxygène on stop la manche et on arrange les joueurs, le plateau, les jetons
        self._terminee = True
        jetons_perdus: list[JetonRuine | PileJeton] = []

        anciennes_cases = self._plateau.cases

        #on mémorise la position de fin des joueurs
        positions_fin = {j: j.position for j in self._joueurs}

        #gestion des trésors : qui est rentré ou qui est dehors
        for j in self._joueurs:
            if positions_fin[j] != 0:
                #joueurs dehors du sous marin perd ses trésors
                jetons_perdus.extend(j.tresor_manche)
                j.mourir()
            else:
                #joueurs au sous marin dépose ses trésors dans sa valise
                j.deposer_tous_au_sous_marin()

        #acutalisation des positions
        # si le joueur est sur un jeton blanc il recule jusqu'à la case non blanche la plus proche derrière
        # sinon il reste sur sa case
        positions_apres_blanc: dict[Joueur, int] = {}
        nb_anciennes = len(anciennes_cases)

        for j, pos in positions_fin.items():
            if pos == 0:
                positions_apres_blanc[j] = 0
                continue

            #bornes de sécurité
            if pos < 0:
                pos = 0
            if pos >= nb_anciennes:
                pos = nb_anciennes - 1

            case_mort = anciennes_cases[pos]

            if case_mort.jeton_blanc:
                p = pos - 1
                # on recule tant qu'on trouve des jetons blancs, mais on ne va pas avant la case 1
                while p >= 1 and anciennes_cases[p].jeton_blanc:
                    p -= 1

                if p >= 1:
                    positions_apres_blanc[j] = p
                else:
                    #pas de case non blanche derrière : on le laisse à sa position de fin
                    positions_apres_blanc[j] = pos
            else:
                positions_apres_blanc[j] = pos

        #resserrer le plateau, on supprime toutes les cases avec un jeton blanc
        sous_marin = anciennes_cases[0]
        sous_marin.occupe = False
        nouvelles_cases: list[Case] = [sous_marin]

        for case in anciennes_cases[1:]:
            if case.jeton_blanc:
                case.retirer_jeton_blanc()
            else:
                case.occupe = False
                nouvelles_cases.append(case)

        #on positionne les joueurs
        for j, old_pos in positions_apres_blanc.items():
            if old_pos == 0:
                j._position = 0
            else:
                old_case = anciennes_cases[old_pos]
                try:
                    new_pos = nouvelles_cases.index(old_case)
                except ValueError:
                    #sécurité : si la case a disparu, on renvoie le joueur au sous-marin
                    new_pos = 0
                j._position = new_pos

        # les jetons perdus :
        # si c'est un JetonRuine, on le garde sans y toucher
        # si c'est une PileJeton, on défais la pile pour s'occuper des jetons un à un
        jetons_perdus_plats: list[JetonRuine] = []
        for elem in jetons_perdus:
            if isinstance(elem, PileJeton):
                jetons_perdus_plats.extend(elem.jetons)
            else:
                jetons_perdus_plats.append(elem)

        #ajouter ces jetons en piles de 3 à la fin du nouveau plateau
        index_debut = len(nouvelles_cases)
        self._index_debut_jetons_perdus = index_debut

        i = 0
        n = len(jetons_perdus_plats)
        while i < n:
            groupe = jetons_perdus_plats[i:i+3]  # 1, 2 ou 3 jetons
            if len(groupe) == 1:
                nouvelles_cases.append(Case(groupe[0]))
            else:
                pile = PileJeton(groupe)
                nouvelles_cases.append(Case(pile))
            i += 3

        #remplacer définitivement les cases du plateau
        self._plateau._cases = nouvelles_cases

        #détermination du premier joueur pour la prochaine manche
        j_eloigne = max(self._joueurs, key=lambda j: j.position)
        self._premier_suivant = j_eloigne




    @property
    def premier_suivant(self):
        return self._premier_suivant
    @property
    def plateau(self):
        return self._plateau
    
    @property
    def index_debut_jetons_perdus(self):
        return self._index_debut_jetons_perdus

