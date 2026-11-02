import random
from typing import Optional, Union
from .exception import PlateauError, CaseError #pointage des erreurs dans leur propre classe d'exception
from .Jeton import JetonRuine, PileJeton, Forme


"classe pour regrouper toutes les attributs et méthodes qui vont aider à la création de jeu"


class Case :
  def __init__(self,contenu :Optional[Union[PileJeton, JetonRuine]]) -> None:  #contenu prend comme valeur soit None (Optinal)soit PileJetons soit JetonRuine 

    if contenu is not None and not isinstance(contenu, (JetonRuine, PileJeton)):
        raise CaseError("Le contenu de la case doit être un JetonRuine, une PileJeton ou None.")

    self._contenu=contenu
    self._jeton_blanc=False 
    self._occupe=False   #pour identifier si une case est occupé ou non par un joueur
    self._sous_marin= False #pour pouvoir séparer la case sous-marin des autres 

  def definir_sous_marin(self):
    self._sous_marin=True


  "pouvoir savoir quel type de case on pointe"

  def contient_jeton(self) -> bool:
    return self._contenu is not None

  def contient_pile(self) -> bool:
    return isinstance(self._contenu, PileJeton)

  def contient_ruine(self) -> bool:
    return isinstance(self._contenu, JetonRuine)
  
  def contient_jeton_blanc(self) -> bool:
    return self._jeton_blanc
  

  "changer le contenu d'une case"

  def poser_contenu(self, contenu: Union[PileJeton, JetonRuine]) -> None:
    if not isinstance(contenu, (JetonRuine, PileJeton)):
        raise CaseError("Le contenu doit être un JetonRuine ou une PileJeton.")
    self._contenu = contenu

  def retirer_contenu(self) :
    contenu = self._contenu
    self._contenu = None
    return contenu

  def poser_jeton_blanc(self) -> None:
    self.retirer_contenu()
    self._jeton_blanc = True

  def retirer_jeton_blanc(self) -> None:
    self._jeton_blanc = False


  @property
  def contenu(self) :
    return self._contenu

  @property
  def jeton_blanc(self) -> bool:
    return self._jeton_blanc

  @property
  def occupe(self) -> bool:
    return self._occupe
  @property
  def sous_marin(self):
     return self._sous_marin
  @occupe.setter
  def occupe(self, occupe:bool) -> None:
    self._occupe=occupe

  def __str__(self) -> str:
    return f"contenu {self._contenu} /jeton_blanc {self._jeton_blanc}"

  def reveler(self):
    if self._contenu:
      self._contenu.reveler()



#création du plateau en début de partie avec le sous marin, les 32 jetons de différentes formes et de différentes valeurs
class Plateau:


  #les valeurs sont celles cachées sous les cases 
  Valeurs_par_niveau: dict[int, list[int] ] = {
      1:[0,1,2,3],
      2:[4,5,6,7],
      3:[8,9,10,11],
      4:[12,13,14,15]
  }

  def __init__(self, cases:list[Case]) -> None: #on initialise des jetons avce des niveaux mais sans les valeurs. Celles ci sont ajouté dans cette classe.
    if not cases:
      raise PlateauError("Le plateau doit contenir au moins une case.")

    if not all(isinstance(case, Case) for case in cases):
      raise PlateauError("Toutes les cases du plateau doivent être de type Case.")

    self._cases=list(cases)


  @property
  def nb_cases(self) -> int:
      return len(self._cases)

  @property
  def cases(self) -> list[Case]:
    return self._cases

  
  @classmethod
  def creer_plateau_initial(cls) -> "Plateau": #création du plateau en début de partie
        jetons = cls._generer_jetons_depart()
        case_sous_marin=Case(None) #création d'une case vide 
        case_sous_marin.definir_sous_marin() #la case devient le sous marin
        case_sous_marin.occupe=True
        cases = [case_sous_marin] #le plateau a pour première case la case sous marin
        cases.extend([Case(j) for j in jetons]) #on ajoute les cases par niveau
        return cls(cases) #Plateau(cases)  ou cases est une liste de case


  #on prend les cases qui ont été initalisé et on leur ajoute leur valeur
  @classmethod
  def _generer_jetons_depart(cls) -> list[JetonRuine]: 
        jetons: list[JetonRuine] = []

        for niveau, valeurs in cls.Valeurs_par_niveau.items(): #on défile dans niveau puis dans les valeurs 
            jetons_niveau: list[JetonRuine] = []

            for v in valeurs:
                # On crée deux jetons de cette valeur
                jetons_niveau.append(JetonRuine(Forme(niveau), v))
                jetons_niveau.append(JetonRuine(Forme(niveau), v))

            random.shuffle(jetons_niveau) #on mélange les jetons par niveau pour avoir un chemin avec des valeurs qui ne se suivent pas ex: premier jeton = 3, deuxième jeton =1, etc.
            jetons.extend(jetons_niveau)# On les ajoute à la liste globale, dans l’ordre des niveaux

        return jetons



  def get_case(self, position: int) -> Case:
    if position < 0 or position >= self.nb_cases:
        raise IndexError(f"Position {position} hors du plateau (0..{self.nb_cases - 1}).")
    return self._cases[position]

  def ajouter_case(self, case: Case) -> None:
    if not isinstance(case, Case):
        raise PlateauError("On ne peut ajouter que des objets de type Case au plateau.")
    self._cases.append(case)

  #pour connaître la valeur d'une case
  def reveler(self): 
      for case in self._cases:
        case.reveler()

  def __str__(self) -> str:
    return "\n".join(str(case) for case in self._cases)

