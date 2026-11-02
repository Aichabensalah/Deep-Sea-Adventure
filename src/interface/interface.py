import pygame
import sys
import os

from ..engine.joueur import Joueur, JoueurIA
from ..engine.plateau import Plateau
from ..engine.manche import Manche
from .jeu import ecran_manche   #on importe l'écran de jeu
from .bouton import Bouton, IconButton

pygame.init()

#fenêtre
LARGEUR, HAUTEUR = 1000, 800
FENETRE = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Deep Sea Adventure")

#chemin des assets et des fonds
INTERFACE_DIR = os.path.dirname(__file__)
SRC_DIR       = os.path.dirname(INTERFACE_DIR)
RACINE_PROJET = os.path.dirname(SRC_DIR)
ASSETS_DIR    = os.path.join(RACINE_PROJET, "assets")

IMAGE_FOND   = os.path.join(ASSETS_DIR, "fond_accueil.png")
POLICE_PATH  = os.path.join(ASSETS_DIR, "Longline.ttf")
IMAGE_FLECHE = os.path.join(ASSETS_DIR, "fleche.png")

try:
    FOND = pygame.image.load(IMAGE_FOND)
    FOND = pygame.transform.scale(FOND, (LARGEUR, HAUTEUR))
except Exception:
    print("Impossible de charger le fond.")
    FOND = pygame.Surface((LARGEUR, HAUTEUR))
    FOND.fill((22, 75, 120))

# flèche
try:
    FLECHE_IMG = pygame.image.load(IMAGE_FLECHE).convert_alpha()
    FLECHE_IMG = pygame.transform.smoothscale(FLECHE_IMG, (50, 50))
except Exception:
    FLECHE_IMG = None
    print("Impossible de charger fleche.png, utilisation du texte '←'.")

#couleur et police
BLEU_BOUTON       = (16, 63, 111)
BLEU_SURVOL       = (22, 92, 150)
BLEU_SELECTED     = (40, 130, 190)
BLEU_SELECTED_HOV = (60, 150, 210)

BLANC  = (240, 240, 240)
GRIS   = (48,53,54)

try:
    POLICE_TITRE  = pygame.font.Font(POLICE_PATH, 180)
    POLICE_BOUTON = pygame.font.Font(POLICE_PATH, 60)
    POLICE_TEXTE  = pygame.font.Font(POLICE_PATH, 70)
except Exception as e:
    print("Police introuvable :", e)
    POLICE_TITRE  = pygame.font.Font(None, 80)
    POLICE_BOUTON = pygame.font.Font(None, 50)
    POLICE_TEXTE  = pygame.font.Font(None, 40)


#écran de configuration
def menu_config():
    nb_joueurs = 1
    nb_ia = 0
    difficulte = "facile"  #paramètre par défaut

    centre_x = LARGEUR // 2
    cadre_largeur = 620

    cadre_joueurs = pygame.Surface((cadre_largeur, 120), pygame.SRCALPHA)
    pygame.draw.rect(cadre_joueurs, (0, 40, 90, 150),
                     pygame.Rect(0, 0, cadre_largeur, 120), border_radius=25)

    cadre_ia = pygame.Surface((cadre_largeur, 260), pygame.SRCALPHA)
    pygame.draw.rect(cadre_ia, (0, 40, 90, 150),
                     pygame.Rect(0, 0, cadre_largeur, 260), border_radius=25)

    bouton_moins_j = Bouton("-", centre_x - 50, 235, 45, 45)
    bouton_plus_j  = Bouton("+", centre_x + 10, 235, 45, 45)

    bouton_moins_ai = Bouton("-", centre_x - 50, 390, 45, 45)
    bouton_plus_ai  = Bouton("+", centre_x + 10, 390, 45, 45)

    if FLECHE_IMG:
        bouton_retour = IconButton(FLECHE_IMG, 25, 25)
    else:
        bouton_retour  = Bouton("←", 25, 25, 50, 45)

    bouton_quitter = Bouton("X", LARGEUR - 75, 25, 50, 45)

    diff_largeur = 140
    diff_esp = 20
    start_x = centre_x - (3 * diff_largeur + 2 * diff_esp) // 2
    y_diff = 510

    bouton_facile = Bouton("Facile",  start_x, y_diff, diff_largeur, 50)
    bouton_medium = Bouton("Medium",  start_x + diff_largeur + diff_esp, y_diff, diff_largeur, 50)
    bouton_expert = Bouton("Expert",  start_x + 2*(diff_largeur + diff_esp), y_diff, diff_largeur, 50)

    bouton_ok = Bouton("Suivant", centre_x - 110, 650, 220, 60)

    while True: #choix des paramètres 
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if bouton_retour.clique(event):
                return None

            if bouton_quitter.clique(event):
                pygame.quit()
                sys.exit()

            if bouton_plus_j.clique(event) and (nb_joueurs + nb_ia) < 6:
                nb_joueurs += 1

            if bouton_moins_j.clique(event) and nb_joueurs > 1:
                nb_joueurs -= 1

            if bouton_plus_ai.clique(event) and (nb_joueurs + nb_ia) < 6:
                nb_ia += 1

            if bouton_moins_ai.clique(event) and nb_ia > 0:
                nb_ia -= 1

            if bouton_facile.clique(event):
                difficulte = "facile"
            if bouton_medium.clique(event):
                difficulte = "medium"
            if bouton_expert.clique(event):
                difficulte = "expert"

            if bouton_ok.clique(event):
                return {
                    "nb_joueurs": nb_joueurs,
                    "nb_ia": nb_ia,
                    "difficulte": difficulte
                }

        FENETRE.blit(FOND, (0, 0))



        bouton_retour.dessiner(FENETRE, POLICE_TEXTE)
        bouton_quitter.dessiner(FENETRE, POLICE_TEXTE)

        FENETRE.blit(cadre_joueurs, (centre_x - cadre_largeur//2, 170))
        txt1 = POLICE_TEXTE.render(f"NOMBRE DE JOUEURS : {nb_joueurs}", True, BLANC)
        FENETRE.blit(txt1, txt1.get_rect(center=(centre_x, 210)))

        bouton_moins_j.dessiner(FENETRE, POLICE_TEXTE)
        bouton_plus_j.dessiner(FENETRE, POLICE_TEXTE)

        FENETRE.blit(cadre_ia, (centre_x - cadre_largeur//2, 330))
        txt2 = POLICE_TEXTE.render(f"NOMBRE DE JOUEURS IA : {nb_ia}", True, BLANC)
        FENETRE.blit(txt2, txt2.get_rect(center=(centre_x, 365)))

        bouton_moins_ai.dessiner(FENETRE, POLICE_TEXTE)
        bouton_plus_ai.dessiner(FENETRE, POLICE_TEXTE)

        txt3 = POLICE_TEXTE.render("DIFFICULTÉ IA :", True, BLANC)
        FENETRE.blit(txt3, txt3.get_rect(center=(centre_x, 450)))

        for bouton, val in [
            (bouton_facile, "facile"),
            (bouton_medium, "medium"),
            (bouton_expert, "expert"),
        ]:
            if difficulte == val:
                bouton.dessiner(FENETRE, POLICE_TEXTE, BLEU_SELECTED, BLEU_SELECTED_HOV)
            else:
                bouton.dessiner(FENETRE, POLICE_TEXTE)

        bouton_ok.dessiner(FENETRE, POLICE_TEXTE)

        pygame.display.flip()

#menu principal de lancement
def menu_accueil():
    bouton_nouvelle = Bouton("NOUVELLE PARTIE", LARGEUR//2 - 180, 330, 360, 80)
    bouton_quitter  = Bouton("QUITTER",         LARGEUR//2 - 150, 430, 300, 70)

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if bouton_nouvelle.clique(event):
                config = menu_config()
                if config:
                    return config

            if bouton_quitter.clique(event):
                pygame.quit()
                sys.exit()

        FENETRE.blit(FOND, (0, 0))

        titre = POLICE_TITRE.render("DEEP SEA ADVENTURE", True, GRIS)
        FENETRE.blit(titre, titre.get_rect(center=(LARGEUR//2, 200)))

        bouton_nouvelle.dessiner(FENETRE, POLICE_BOUTON)
        bouton_quitter.dessiner(FENETRE, POLICE_BOUTON)


        pygame.display.flip()

#dernier affichage avec les résultats et le gagnant
def ecran_resultats(joueurs):
    
    #calcul des scores
    scores = []
    for j in joueurs:
        score = sum(t.valeur for t in j.tresor_valise)
        scores.append((j, score))

    #on pointe le gagnant
    max_score = max(score for _, score in scores)
    gagnants = [j for j, s in scores if s == max_score]

    if len(gagnants) == 1:
        titre_gagnant = f"Gagnant : {gagnants[0].couleur} ({max_score} pts)" #on affiche le gagnant
    else:
        couleurs = ", ".join(g.couleur for g in gagnants)
        titre_gagnant = f"Égalité : {couleurs} ({max_score} pts)"

    # Bouton quitter
    bouton_quitter = Bouton("QUITTER", LARGEUR//2 - 150, HAUTEUR - 140, 300, 70)
    bouton_menu     = Bouton("MENU",     LARGEUR//2 + 50,  HAUTEUR - 140, 300, 70)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if bouton_quitter.clique(event):
                pygame.quit()
                sys.exit()
                        
            if bouton_menu.clique(event):
                return "menu"     

        #fond
        FENETRE.blit(FOND, (0, 0))

        #titre
        titre = POLICE_TITRE.render("FIN DE LA PARTIE", True, BLANC)
        FENETRE.blit(titre, titre.get_rect(center=(LARGEUR//2, 120)))

        #gagnant
        txt_gagnant = POLICE_TEXTE.render(titre_gagnant, True, BLANC)
        FENETRE.blit(txt_gagnant, txt_gagnant.get_rect(center=(LARGEUR//2, 220)))

        #liste des scores
        start_y = 320
        ligne_esp = 60

        for i, (j, score) in enumerate(scores):
            ligne = f"{j.couleur} : {score} points"
            #on met le gagnant en un peu plus clair
            couleur_texte = BLANC if j in gagnants else (200, 200, 200)
            txt = POLICE_TEXTE.render(ligne, True, couleur_texte)
            FENETRE.blit(txt, txt.get_rect(center=(LARGEUR//2, start_y + i * ligne_esp)))

        #bouton quitter/rejouer/revenir au menu
        bouton_quitter.dessiner(FENETRE, POLICE_TEXTE)
        bouton_menu.dessiner(FENETRE, POLICE_TEXTE)

        pygame.display.flip()


#main

def main():
    config = menu_accueil()
    if config is None:
        return

    nb_humains = config["nb_joueurs"]
    nb_ia      = config["nb_ia"]
    difficulte = config["difficulte"]

    couleurs = ["rouge", "bleu", "jaune", "vert", "violet", "orange"]
    joueurs: list[Joueur] = []

    #création des joueurs humains
    for i in range(nb_humains):
        couleur = couleurs[i % len(couleurs)]
        joueurs.append(Joueur(couleur))

    #créations des joueurs IA
    for i in range(nb_ia):
        couleur = couleurs[(nb_humains + i) % len(couleurs)]
        joueurs.append(JoueurIA(couleur, difficulte))

    print("\nJoueurs créés :")
    for j in joueurs:
        type_j = "IA" if isinstance(j, JoueurIA) else "Humain"
        print(f"  - {j.couleur} ({type_j})")

    #plateau unique pour toute la partie
    plateau = Plateau.creer_plateau_initial()

    #on joue 3 manches
    for num_manche in range(3):
        print(f"\n--- Manche {num_manche + 1} ---")
        manche = Manche(joueurs, plateau)

        #écran graphique
        ecran_manche(manche)

        # on ordonne les joueurs pour la manche
        premier = manche.premier_suivant
        idx = joueurs.index(premier)
        joueurs = joueurs[idx:] + joueurs[:idx]

        #on récupère le plateau resserré
        plateau = manche.plateau


    # écran des résultats
    choix = ecran_resultats(joueurs)
    if choix == "menu":
        main()   # retour menu -> menu_accueil() sera relancé
        return



if __name__ == "__main__":
    main()
