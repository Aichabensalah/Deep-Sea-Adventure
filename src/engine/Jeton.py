from __future__ import annotations
from .exception import CaseError, PileCompleteError
from enum import Enum

"classe pour regrouper toutes les attributs et méthodes qui vont aider à la création des jetons"

class Forme(Enum):
  #on rerésente les formes avec des niveaux
  TRIANGLE = 1
  CARRE = 2
  PENTAGONE = 3
  HEXAGONE = 4

class JetonRuine:
    def __init__(self, forme: Forme, valeur: int):

        if not isinstance(forme, Forme):
            raise TypeError("forme doit être une instance de Forme")

        if valeur < 0:
            raise ValueError("La valeur d'un jeton doit être positive")

        self._forme = forme
        self._valeur = valeur
        self._revele = False

    @property
    def revele(self) -> bool:
        return self._revele

    @property
    def niveau(self) -> int:
        return self._forme.value

    @property
    def valeur(self) -> int:
        return self._valeur

    def reveler(self):
        self._revele = True


    def __str__(self):
        if self._revele:
            etat = f"valeur={self._valeur}"
        else:
            etat = "valeur inconnue"
        return f"<Jeton {self._forme.name} | niv={self.niveau} | {etat}>"
    


class PileJeton:

  def __init__(self, jetons:list[JetonRuine]) -> None:
    if not jetons:
      raise ValueError("La pile doit contenir au moins un jeton")

    if not all(isinstance(jeton, JetonRuine) for jeton in jetons):
      raise TypeError("Tous les éléments de la pile doivent être des JetonRuine")

    if len(jetons)>3:
      raise ValueError("La pile ne peut pas contenir plus de 3 jetons")

    self._jetons=list(jetons) #une copie pour eviter qu'on puisse la modifier à l'exterieur

  def ajouter_jeton(self, jeton:JetonRuine):
    if not isinstance(jeton, JetonRuine):
      raise TypeError("on peut empiler que des jetons")

    if len(self._jetons)>=3:
      raise PileCompleteError("La pile ne peut pas contenir plus de 3 jetons")

    self._jetons.append(jeton)

  def reveler(self) -> None:
    for j in self._jetons:
        j.reveler()

  def est_complete(self) -> bool:
    return len(self._jetons) == 3

  def peut_ajouter(self) -> bool:
    return len(self._jetons) < 3

  @property
  def jetons(self) -> list[JetonRuine]:
    return self._jetons



  def  __str__(self) -> str:
     return "["+",".join(str(j) for j in self._jetons)+"]"