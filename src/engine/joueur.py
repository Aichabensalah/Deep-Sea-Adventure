from __future__ import annotations
import random
from typing import TYPE_CHECKING

from .Jeton import JetonRuine, PileJeton
from .plateau import Plateau, Case
from .exception import (
    JoueurError,
    ChangementDirectionError,
    PileCompleteError,
    CaseError,
)

if TYPE_CHECKING:
    from .manche import Manche

"classe pour regrouper toutes les attributs et méthodes qui vont aider à la création d'un joueur"

class Joueur: #joueur humain

    def __init__(self, couleur: str) -> None:
        self._couleur = couleur
        self._position = 0
        self._tresor_manche: list[JetonRuine | PileJeton] = []
        self._tresor_valise: list[JetonRuine | PileJeton] = []
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

        # Le dépôt est autorisé uniquement sur une case blanche
        if not case.contient_jeton_blanc():
            raise JoueurError("Le dépôt est autorisé uniquement sur une case blanche.")

        jeton = self._tresor_manche[num_jeton]

        # Vérification du type de trésor
        if not isinstance(jeton, (JetonRuine, PileJeton)):
            raise JoueurError("Type de trésor invalide.")

        # On vérifie d'abord que la case est vide
        if case.contient_jeton():
            raise JoueurError("La case contient déjà un trésor.")

        # Case vide alors on pose simplement le jeton
        case.poser_contenu(jeton)

        #Si on est sur un jeton blanc, on le retire
        case.retirer_jeton_blanc()

        # On retire le trésor du joueur après le dépôt
        self._tresor_manche.pop(num_jeton)
    
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
    def tresor_manche(self) -> list[JetonRuine | PileJeton]:
        return self._tresor_manche

    @property
    def tresor_valise(self) -> list[JetonRuine | PileJeton]:
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

        # On ne change pas de direction si on remonte déjà
        if self.direction == -1:
            return False

        # On ne change pas de direction si on l'a déjà fait
        if self.nb_changement_direction_par_manche >= 1:
            return False

        # On évite de remonter immédiatement au début
        if pos <= 1:
            return False

        # Estimation approximative du retour selon la charge
        distance_retour = pos * (1 + charge / 3)

        if self._niveau == "facile":
            # L'IA facile prend en compte l'oxygène, sa position et sa charge
            # mais elle anticipe moins bien le trajet de retour

            if oxy <= 5 + charge:
                return True

            if pos >= 10:
                return True

            if charge >= 3 and pos >= 5:
                return True

            if pos >= 6 and charge >= 1:
                return random.random() < 0.65

            return False

        if self._niveau == "medium":
            # L'IA medium adapte sa décision à sa charge
            if oxy <= distance_retour + 3:
                return True

            if charge >= 3 and pos >= 5:
                return True

            if pos >= 10:
                return random.random() < 0.65

            if pos >= 6 and charge >= 1:
                return random.random() < 0.35

            return False

        if self._niveau == "expert":
            # L'IA experte anticipe son retour
            marge_securite = 4 + charge

            if oxy <= distance_retour + marge_securite:
                return True

            if charge >= 4:
                return True

            if pos >= 12 and charge >= 2:
                return True

            if pos >= 16:
                return True

            return False

        return False

    "ramasser"

    def choisir_ramasser(self, case: "Case") -> bool:
        contenu = case.contenu

        # Si la case n'a rien (ou seulement jeton blanc), l'IA ne ramasse pas
        if not isinstance(contenu, (JetonRuine, PileJeton)):
            return False

        # Cas du Jeton simple
        if isinstance(contenu, JetonRuine):
            niveau = contenu.niveau
            nb_jetons = 1
        else:
            #dans une pile regarde le niveau du jeton du dessus
            # On prend aussi en compte le nombre de jetons de la pile
            niveau = contenu.jetons[-1].niveau
            nb_jetons = len(contenu.jetons)

        charge = len(self.tresor_manche)
        pos = self.position

        if self._niveau == "facile":
            # L'IA facile privilégie les trésors de niveau élevé
            # mais ne prend pas toujours la meilleure décision

            if charge >= 4:
                return False

            if niveau >= 3:
                return True

            if nb_jetons >= 2:
                return True

            if niveau == 2:
                return charge <= 2

            if niveau == 1:
                return charge == 0 and pos <= 5

            return False

        if self._niveau == "medium":
            # L'IA medium privilégie les trésors intéressants
            if charge >= 4:
                return False

            if niveau >= 3:
                return True

            if nb_jetons >= 2:
                return True

            if niveau == 2:
                return random.random() < 0.60

            return charge <= 1 and random.random() < 0.30

        if self._niveau == "expert":
            # L'IA experte compare le gain potentiel au risque
            if charge >= 4:
                return False

            if niveau == 4 or nb_jetons >= 3:
                return True

            if niveau >= 3 and charge <= 2:
                return True

            if niveau == 2 and charge <= 1 and pos <= 8:
                return True

            return False

        return False

    "déposer"

    def choisir_deposer_tresor(self, case: "Case", manche: "Manche") -> int | None:

        if not self.tresor_manche:
            return None

        # On utilise uniquement les niveaux visibles, jamais les valeurs réelles
        niveaux = []

        for t in self.tresor_manche:
            if isinstance(t, JetonRuine):
                niveaux.append(t.niveau)

            elif isinstance(t, PileJeton):
                # Une pile est évaluée selon ses niveaux visibles
                niveaux.append(sum(j.niveau for j in t.jetons))

            else:
                niveaux.append(float("inf"))

        # Une pile ou un jeton est considéré comme un seul trésor transporté
        charge = len(self.tresor_manche)

        # On cherche le trésor le moins intéressant selon les niveaux
        indice_moins_interessant = niveaux.index(min(niveaux))

        if self._niveau == "facile":
            # L'IA facile dépose un trésor peu intéressant
            # lorsqu'elle commence à être trop chargée

            if charge >= 3 and min(niveaux) <= 2:
                return indice_moins_interessant

            if manche.oxygene <= 5 and charge >= 2:
                return indice_moins_interessant

            return None

        if self._niveau == "medium":
            # L'IA medium dépose surtout les trésors peu intéressants
            if charge >= 3 and min(niveaux) <= 2:
                return indice_moins_interessant

            if manche.oxygene <= 6 and charge >= 3:
                return indice_moins_interessant

            return None

        if self._niveau == "expert":
            # L'IA experte réduit sa charge lorsque le retour devient risqué
            distance_retour = self.position * (1 + charge / 3)

            if manche.oxygene <= distance_retour + 3 and charge >= 2:
                return indice_moins_interessant

            if charge >= 4 and min(niveaux) <= 3:
                return indice_moins_interessant

            return None

        return None