from __future__ import annotations
import random
from .Jeton import JetonRuine, PileJeton
from .plateau import Plateau, Case
from .exception import (
    JoueurError,
    ChangementDirectionError,
    PileCompleteError,
    CaseError,
)

"classe pour regrouper toutes les attributs et méthodes qui vont aider à la création d'un joueur"

class Joueur: #joueur humain

    def __init__(self, couleur: str) -> None:
        self._couleur = couleur
        self._position = 0
        self._tresor_manche: list[JetonRuine] = []
        self._tresor_valise: list[JetonRuine] = []
        self._direction = 1
        self._en_vie = True
        self._nb_changement_direction_par_manche = 0
        self._est_rentre = False   #pour empêcher de repartir après retour au sous-marin
        self._offset = (0, 0) # pour l'affichage /interface 

    "méthode de décision"

    def choisir_changer_direction(self, manche) -> bool:
        choix = input("Changer de direction ? (o/n) : ").strip().lower()
        return choix == "o"

    def choisir_ramasser(self, case: "Case") -> bool:
        choix = input("Ramasser ? (o/n) : ").strip().lower()
        return choix == "o"

    def choisir_deposer_tresor(self, case: "Case") -> int | None:
        if not self._tresor_manche:
            return None

        choix = input("Voulez-vous lâcher un trésor ici ? (o/n) : ").strip().lower()
        if choix != "o":
            return None

        print("Quel trésor voulez-vous lâcher ?")
        for i, t in enumerate(self._tresor_manche):
            print(f"  {i} : {t}")

        try:
            idx = int(input(f"Choisir (0-{len(self._tresor_manche)-1}) : "))
            if 0 <= idx < len(self._tresor_manche):
                return idx
        except ValueError:
            pass

        return None

    "méthode de jeu"

    def changer_direction(self):
        if self._nb_changement_direction_par_manche == 1:
            raise ChangementDirectionError("Vous avez déjà changé de direction cette manche.")


        self._direction *= -1
        self._nb_changement_direction_par_manche += 1

    def avancer(self, pas: int, plateau: "Plateau", manche: "Manche") -> None:
        if not self._en_vie:
            return

        #revenu au sous marin on ne repart pas 
        if self._est_rentre:
            return

        if not isinstance(pas, int):
            raise JoueurError("pas doit être un entier")
        if pas < 0:
            raise JoueurError("pas doit être >= 0")

        nb_cases = plateau.nb_cases

        #pas - pénalités
        steps = pas - len(self._tresor_manche)
        if steps <= 0:
            return

        position_depart = self._position
        direction = self._direction

        #on libère la case de départ si ce n'est pas le sous marin
        if position_depart != 0:
            plateau.get_case(position_depart).occupe = False

        pos = position_depart

        #condition pour avancer
        # saute les cases occupées (sauf sous-marin)
        # si bloc jusqu'au bord alors on reste avant
        # interdit d'entrer au sous-marin sans trésor
        for _ in range(steps):
            pos_avant = pos  # case sûre et libre avant ce pas

            #on calcule une première case cible( comme s'il n'y avait personne devant)
            cible = pos + direction

            # bornes
            if cible < 0:
                cible = 0
            elif cible >= nb_cases:
                cible = nb_cases - 1

            #on cherche la prochaine case libre dans la même direction, en sautant les cases occupées (sauf le sous-marin)
            search = cible
            no_free = False

            if search != 0:
                while plateau.get_case(search).occupe:
                    search += direction

                    # si on sort du plateau alors pas de case libre dans ce sens
                    if search < 0 or search >= nb_cases:
                        no_free = True
                        break

            if no_free:
                #bloc jusqu'au bord alors on reste sur la case précédente
                pos = pos_avant
                break

            #gestion du sous-marin
            if search == 0:
                #pas de trésor alors interdit d'entrer au sous-marin
                if len(self._tresor_manche) == 0:
                    pos = pos_avant
                    break
                else:
                    # il a au moins un trésor alors il rentre et on termine le mouvement
                    pos = 0
                    break

            pos = search

        #position finale
        self._position = pos
        if pos != 0:
            plateau.get_case(pos).occupe = True
        else:
            # ici, il a forcément au moins un trésor (sinon on serait resté avant)
            self._est_rentre = True
            manche._dernier_rentre = self

    def ramasser_tresor(self, case: "Case"):
        if not case.contient_jeton():
            raise JoueurError("La case ne contient pas de jeton.")
        self._tresor_manche.append(case.retirer_contenu())
        case.poser_jeton_blanc()

    def deposer_tresor(self, case: "Case", num_jeton: int) -> None:
        if num_jeton < 0 or num_jeton >= len(self._tresor_manche):
            raise JoueurError("Indice de trésor invalide.")

        jeton = self._tresor_manche.pop(num_jeton)

        #Si on est sur un jeton blanc, on le retire
        if case.contient_jeton_blanc():
            case.retirer_jeton_blanc()

        if not case.contient_jeton():
            # Case vide alors on pose simplement le jeton
            case.poser_contenu(jeton)
        else:
            contenu = case.contenu
            if isinstance(contenu, JetonRuine):
                #on transforme en pile
                pile = PileJeton([contenu, jeton])
                case.poser_contenu(pile)
            else:
                #déjà une pile
                if contenu.peut_ajouter():
                    contenu.ajouter_jeton(jeton)
                else:
                    # pile pleine alors on remet le jeton au joueur
                    self._tresor_manche.append(jeton)
                    raise PileCompleteError("La pile est complète.")


    def deposer_tous_au_sous_marin(self):
        self._tresor_valise.extend(self._tresor_manche)
        self._tresor_manche.clear()

    def penalite_oxygene(self) -> int:
        return len(self._tresor_manche)

    def mourir(self):
        self._en_vie = False
        self._tresor_manche.clear()

    def reinitialiser_pour_manche(self):
        self._direction = 1
        self._en_vie = True
        self._tresor_manche.clear()
        self._nb_changement_direction_par_manche = 0
        self._est_rentre = False


    "propriété"

    @property
    def couleur(self) -> str:
        return self._couleur

    @property
    def position(self) -> int:
        return self._position

    @property
    def tresor_manche(self) -> list[JetonRuine]:
        return self._tresor_manche

    @property
    def tresor_valise(self) -> list[JetonRuine]:
        return self._tresor_valise

    @property
    def direction(self) -> int:
        return self._direction

    @direction.setter
    def direction(self, value: int) -> None:
        self._direction = value

    @property
    def en_vie(self) -> bool:
        return self._en_vie

    @property
    def nb_changement_direction_par_manche(self) -> int:
        return self._nb_changement_direction_par_manche
    
    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, val):
        self._offset = val


    def __str__(self):
        return (f"Joueur {self.couleur} à la case {self.position}. "
                f"{'Descend' if self.direction == 1 else 'Remonte'}. "
                f"{len(self.tresor_manche)} trésors.")
    




class JoueurIA(Joueur): #joueur IA

    def __init__(self, couleur: str, niveau: str):
        super().__init__(couleur)
        self._niveau = niveau.lower()  # "facile", "medium", "expert"

    "choix de direction"

    def choisir_changer_direction(self, manche) -> bool:
        oxy = manche.oxygene
        pos = self.position
        charge = len(self.tresor_manche)

        if self._niveau == "facile":
            return random.random() < 0.15

        if self._niveau == "medium":
            if oxy <= 4 + charge:
                return True
            return random.random() < 0.1

        if self._niveau == "expert":
            distance = pos
            if oxy <= distance + charge + 1:
                return True
            return False

        return False

    "ramasser"

    def choisir_ramasser(self, case: "Case") -> bool:
        contenu = case.contenu

        # Si la case n'a rien (ou seulement jeton blanc), l'IA ne ramasse pas
        if contenu is None:
            return False

        # Cas du Jeton simple
        if isinstance(contenu, JetonRuine):
            niveau = contenu.niveau     # 1 à 4
        else:
            #dans une pile regarde le niveau du jeton du dessus 
            niveau = contenu.jetons[-1].niveau

        
        if self._niveau == "facile":
            return True

        
        if self._niveau == "medium":
            return niveau >= 2   # évite les triangles

        
        if self._niveau == "expert":
            #si le jeton est loin et que c'est trop bas, le joueur évite
            if niveau == 1 and self.position > 6:
                return False
            #sinon ramasse si >= carré
            return niveau >= 2

        return True


    "déposer"

    def choisir_deposer_tresor(self, case: "Case", manche: "Manche") -> int | None:

        if not self.tresor_manche:
            return None

        if self._niveau == "facile":
            if random.random() < 0.20:
                return random.randint(0, len(self.tresor_manche) - 1)
            return None

        if self._niveau == "medium":
            valeurs = [t.valeur for t in self.tresor_manche]
            mini = min(valeurs)
            if mini <= 1:
                return valeurs.index(mini)
            return None

        if self._niveau == "expert":
            valeurs = [t.valeur for t in self.tresor_manche]
            if manche.oxygene <= len(self.tresor_manche) * 2:
                return valeurs.index(min(valeurs))

            return None

        return None

