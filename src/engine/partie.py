import random
from .exception import (
    CaseError,
    ChangementDirectionError,
    JoueurError,
    PileCompleteError,
) #pointage des erreurs dans leur propre classe d'exception

from .joueur import Joueur
from .manche import Manche
from .plateau import Plateau


"classe pour regrouper toutes les attributs et méthodes qui vont aiderà jouer une partie"

class Partie:

    def __init__(self, joueurs:list[Joueur]):
        self._joueurs = joueurs
        self._manches:list[Manche] = []
        self._plateau = Plateau.creer_plateau_initial()

    def jouer(self):
        for i in range(3): #on joue 3 manches
            print(f"\n Manche {i+1} ")
            print(f" Le plateau est le suivant {len(self._plateau._cases)}")
            manche = Manche(self._joueurs, self._plateau)
            self._manches.append(manche)
            self._jouer_manche(manche)
            premier = manche._premier_suivant # Réordonner les joueurs selon les règles officielles
            index = self._joueurs.index(premier)
            self._joueurs = self._joueurs[index:] + self._joueurs[:index]

            print("\nNouvel ordre des joueurs pour la prochaine manche :")
            for j in self._joueurs:
              print(f" - {j.couleur}")

        self.afficher_resultats() #à la fin de la partie on affiche les résultats


    #déroulement d'une manche
    def _jouer_manche(self, manche: Manche): 

      plateau = manche._plateau 
      nb_cases = plateau.nb_cases

      while not manche.terminee:
          joueur = manche.joueur_courant()
          print("\n_________")
          print(f"Tour de {joueur.couleur}")
          print(f"Position : {joueur.position}")
          print(f"Direction : {'descente' if joueur.direction == 1 else 'remontée'}")
          print(f"Oxygène : {manche.oxygene}")
          print(f"Trésors portés : {len(joueur.tresor_manche)}")

          
          a_ramasse_ce_tour = False 

          #Choix (ou non) de la direction. descente = avancer , remonté = reculer
          pos = joueur.position
          peut_choisir_direction = True

          #cas 1 : si on est au sous marin on descend forcément
          if pos == 0:
              if joueur.direction != 1:
                  joueur.direction = 1
              peut_choisir_direction = False

          #cas 2 : à la dernière case -> direction forcément remontée
          elif pos == nb_cases - 1:
              if joueur.direction != -1:
                  joueur.direction = -1
              peut_choisir_direction = False
            #cas où le joueur est revenu au sous marin  
          if joueur._est_rentre:
              print("(Vous êtes déjà rentré, vous ne repartez plus.)")
          elif peut_choisir_direction:
              #cas où le joeur n'a pas de trésor et essaie de remonter
              if joueur.direction == 1 and len(joueur.tresor_manche) == 0:
                  print("(Impossible de remonter : vous n'avez pas encore ramassé de trésor.)")
              else:
                  if joueur.choisir_changer_direction(manche):
                    try:
                      joueur.changer_direction()

                    except ChangementDirectionError as e:
                      print(e)
          else:
              print("(Direction imposée, pas de choix possible)")

          #lancer les dés
          d1, d2 = random.randint(1, 3), random.randint(1, 3)
          de = d1 + d2
          print(f"Total des dés: {de}")

          #déplacement
          joueur.avancer(de, plateau, manche)
          case = plateau.get_case(joueur.position)
          print(f"Arrivé sur case {joueur.position}")

          manche.consommer_oxygene(joueur)
          if manche.terminee:
              print("Plus d'oxygène, fin de la manche.")
              break

          #ramasser un jeton
          if case.contient_jeton():
              print("Un trésor est ici.")
              if joueur.choisir_ramasser(case):
                try:
                    joueur.ramasser_tresor(case)
                    a_ramasse_ce_tour = True   #pour ne pas ramasser plusieurs fois
                    print("Trésor ramassé.")
                except JoueurError as e:
                      print(f"Impossible de ramasser : {e}")
          else:
              print("Aucun trésor sur cette case.")

          #poser un jeton sur une case blanche
          if case.contient_jeton_blanc():
              if a_ramasse_ce_tour:
                  #on ne peut pas ramasser et déposer dans le même tour
                  print("Vous êtes sur un jeton blanc, mais vous avez déjà ramassé un trésor ce tour :")
                  print("vous ne pouvez pas lâcher de trésor ce tour-ci.")
              else:
                  print("Vous êtes sur un jeton blanc : vous pouvez lâcher un trésor ici.")
                  if joueur.tresor_manche:
                      print("Trésors que vous portez :")
                      for idx, t in enumerate(joueur.tresor_manche): 
                          print(f"  {idx} : {t}") #pour voir les trésors dans notre main et choisir lequel on pose
                      indice = joueur.choisir_deposer_tresor(case)
                      if indice is not None:
                          try:
                              joueur.deposer_tresor(case, indice)
                              print("Trésor déposé.")
                          except (ValueError, JoueurError, PileCompleteError, CaseError) as e:
                              print(f"Impossible de déposer ce trésor : {e}")
                  else:
                      print("Vous n'avez aucun trésor à lâcher.")

          manche.verifier_fin() #on vérifie si la manche respecte les conditions de fin ou non
          manche.avancer_tour()#joueur suivant


    def afficher_resultats(self):
        print("\n Les résultats:")
        for j in self._joueurs:
            score = sum(t.valeur for t in j.tresor_valise)
            print(f"{j.couleur} a {score} points")