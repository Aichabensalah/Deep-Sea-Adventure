import pygame
import sys
import os
import random

from ..engine.Jeton import JetonRuine, PileJeton
from .bouton import Bouton
from ..engine.plateau import Plateau
from ..engine.manche import Manche
from ..engine.joueur import Joueur, JoueurIA
from ..engine.exception import (
    JoueurError,
    PileCompleteError,
    CaseError,
    ChangementDirectionError,
)

pygame.init()


#fenêtre de jeu

LARGEUR, HAUTEUR = 1000, 800
FENETRE = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.setCaption = pygame.display.set_caption
pygame.display.setCaption("Deep Sea Adventure - Jeu")


#assets

INTERFACE_DIR = os.path.dirname(__file__)
SRC_DIR       = os.path.dirname(INTERFACE_DIR)
RACINE_PROJET = os.path.dirname(SRC_DIR)
ASSETS_DIR    = os.path.join(RACINE_PROJET, "assets")

IMAGE_FOND       = os.path.join(ASSETS_DIR, "fond.jpg")
IMAGE_SOUS_MARIN = os.path.join(ASSETS_DIR, "submarine.png")
POLICE_PATH      = os.path.join(ASSETS_DIR, "Longline.ttf")

#Fond
try:
    FOND = pygame.image.load(IMAGE_FOND).convert() #on importe l'image qu'on veut
    FOND = pygame.transform.smoothscale(FOND, (LARGEUR, HAUTEUR))
except Exception:
    FOND = pygame.Surface((LARGEUR, HAUTEUR))
    FOND.fill((0, 80, 150))

#Sous-marin
try:
    SOUS_MARIN_IMG = pygame.image.load(IMAGE_SOUS_MARIN).convert_alpha()
    SOUS_MARIN_IMG = pygame.transform.smoothscale(SOUS_MARIN_IMG, (240, 230))
except Exception:
    SOUS_MARIN_IMG = pygame.Surface((260, 95), pygame.SRCALPHA)
    pygame.draw.ellipse(SOUS_MARIN_IMG, (80, 90, 110), (0, 25, 260, 70))

#couleur et police
BLANC       = (240, 240, 240)
BLEU_BOUTON = (16, 63, 111)
BLEU_SURVOL = (22, 92, 150)
ROUGE_OXY   = (170, 0, 50)

COUL_TRI    = (160, 255, 220)   # triangles
COUL_VERT   = (0, 110, 80)      # carrés
COUL_BLEU   = (20, 70, 170)     # pentagones
COUL_VIO    = (140, 0, 140)     # hexagones
COUL_CHEMIN = (0, 190, 220)     # trait du chemin

COULEUR_PIONS = {
    "rouge":  (220, 70, 70),
    "bleu":   (70, 120, 230),
    "jaune":  (240, 210, 70),
    "vert":   (70, 200, 120),
    "violet": (190, 120, 240),
    "orange": (240, 150, 60),
}

try:
    POLICE_INFO   = pygame.font.Font(POLICE_PATH, 40)
    POLICE_BOUTON = pygame.font.Font(POLICE_PATH, 48)
    POLICE_MSG    = pygame.font.Font(POLICE_PATH, 28)
except Exception:
    POLICE_INFO   = pygame.font.Font(None, 32)
    POLICE_BOUTON = pygame.font.Font(None, 40)
    POLICE_MSG    = pygame.font.Font(None, 28)



#chemin : 8 triangles puis 8 carrés puis 8 pentagones puis 8 hexagones 
# (4 colonnes, 8 cases chacune)

X0    = 360     # x de la première colonne (triangles)
Y0    = 160     # y du premier triangle (en haut)
STEP  = 60      # espacement vertical
HSTEP = 120     # espacement horizontal entre colonnes

cases_coord = []  # 32 positions dans l'ordre

#8 triangles (descendent)
for i in range(8):
    cases_coord.append((X0, Y0 + i * STEP))

#8 carrés (remontent)
X_VERT = X0 + HSTEP
for i in range(8):
    cases_coord.append((X_VERT, Y0 + 7 * STEP - i * STEP))

#8 pentagones (redescendent)
X_BLEU = X_VERT + HSTEP
for i in range(8):
    cases_coord.append((X_BLEU, Y0 + i * STEP))

#8 hexagones (remontent)
X_VIO  = X_BLEU + HSTEP
for i in range(8):
    cases_coord.append((X_VIO, Y0 + 7 * STEP - i * STEP))

#fonctions de dessin des formes
def dessiner_triangle(surface, x, y, taille=40, couleur=COUL_TRI):
    p1 = (x, y - taille//2)
    p2 = (x - taille//2, y + taille//2)
    p3 = (x + taille//2, y + taille//2)
    pygame.draw.polygon(surface, couleur, [p1, p2, p3])

def dessiner_carre(surface, x, y, taille=46, couleur=COUL_VERT):
    rect = pygame.Rect(0, 0, taille, taille)
    rect.center = (x, y)
    pygame.draw.rect(surface, couleur, rect, border_radius=8)

def dessiner_polygone(surface, x, y, rayon, nb_sommets, couleur):
    points = []
    for k in range(nb_sommets):
        angle = 2 * 3.14159265 * k / nb_sommets - 3.14159265 / 2
        v = pygame.math.Vector2(1, 0).rotate_rad(angle)
        px = x + rayon * v.x
        py = y + rayon * v.y
        points.append((px, py))
    pygame.draw.polygon(surface, couleur, points)

def dessiner_pentagone_bleu(surface, x, y):
    dessiner_polygone(surface, x, y, 30, 5, COUL_BLEU)

def dessiner_hexagone_violet(surface, x, y):
    dessiner_polygone(surface, x, y, 30, 6, COUL_VIO)

def dessiner_chemin(surface, coords):
    if len(coords) >= 2:
        pygame.draw.lines(surface, COUL_CHEMIN, False, coords, 6)

#position plateau
def coord_case_depuis_position(position: int):
 
    #position = index plateau (0 = sous-marin, 1 = première case, etc.)
    
    if position <= 0:
        return None

    idx = position - 1
    if idx >= len(cases_coord):
        idx = len(cases_coord) - 1
    return cases_coord[idx]

def dessiner_case_contenu(surface, case, x, y):
   #jeton blanc = rond blanc
   #un jeton = une forme
   #une pile de jeton = un rond gris avec le niveau des jetons 

    #jeton blanc
    if case.contient_jeton_blanc():
        pygame.draw.circle(surface, (255, 255, 255), (x, y), 24)
        pygame.draw.circle(surface, (0, 0, 0),     (x, y), 24, 2)
        return

    contenu = case.contenu
    if contenu is None:
        return

    #pile
    if hasattr(contenu, "jetons") and len(contenu.jetons) > 1:
        pygame.draw.circle(surface, (150, 150, 150), (x, y), 24)   # gris

        #afficher les niveaux de la pile (ex: [1,1,3])
        niveaux = [j.niveau for j in contenu.jetons]
        texte = "[" + ",".join(str(v) for v in niveaux) + "]"

        surf = POLICE_MSG.render(texte, True, (255, 255, 255))
        rect = surf.get_rect(center=(x, y + 32))  
        #texte sous les piles 

        surface.blit(surf, rect)
        return

    #jeton
    if hasattr(contenu, "niveau"):
        niveau = contenu.niveau

        if niveau == 1:
            dessiner_triangle(surface, x, y)
        elif niveau == 2:
            dessiner_carre(surface, x, y)
        elif niveau == 3:
            dessiner_pentagone_bleu(surface, x, y)
        elif niveau == 4:
            dessiner_hexagone_violet(surface, x, y)



def choisir_tresor_a_deposer(FENETRE, joueur) -> int | None:
    
    #affiche une petite fenêtre pour choisir quel trésor déposer.

    clock = pygame.time.Clock()

    #zone centrale
    cadre_largeur = 600
    cadre_hauteur = 80 + 60 * len(joueur.tresor_manche) + 80
    x_cadre = (LARGEUR - cadre_largeur) // 2
    y_cadre = (HAUTEUR - cadre_hauteur) // 2

    #création des boutons pour chaque trésor
    boutons_tresors = []
    start_y = y_cadre + 100
    for idx, t in enumerate(joueur.tresor_manche):
        if isinstance(t,JetonRuine):
            texte = f"Trésor {idx+1} : niv {t.niveau}  "
        elif isinstance(t,PileJeton):
            niveaux = [j.niveau for j in t.jetons]
            niveaux_str = ",".join(str(v) for v in niveaux)
            texte = f"Pile {idx+1} : [{niveaux_str}]"
        btn = Bouton(texte, x_cadre + 50, start_y + idx * 60, cadre_largeur - 100, 50)
        boutons_tresors.append(btn)

    bouton_annuler = Bouton("Annuler", x_cadre + cadre_largeur//2 - 100,
                            y_cadre + cadre_hauteur - 70, 200, 50)

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #clic sur un des trésors pour le choisir
            for idx, btn in enumerate(boutons_tresors):
                if btn.clique(event):
                    return idx

            #clic sur annuler si on ne veut pas poser de trésor
            if bouton_annuler.clique(event):
                return None

    
        #on dessine par-dessus l'écran de jeu actuel
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # noir semi-transparent
        FENETRE.blit(overlay, (0, 0))

        #cadre
        cadre = pygame.Surface((cadre_largeur, cadre_hauteur), pygame.SRCALPHA)
        pygame.draw.rect(cadre, (0, 40, 90, 230),
                         pygame.Rect(0, 0, cadre_largeur, cadre_hauteur),
                         border_radius=25)
        FENETRE.blit(cadre, (x_cadre, y_cadre))

        #titre
        titre = POLICE_MSG.render("Choisissez un trésor à déposer", True, BLANC)
        FENETRE.blit(titre, titre.get_rect(center=(LARGEUR//2, y_cadre + 40)))

        #boutons trésors
        for btn in boutons_tresors:
            btn.dessiner(FENETRE, POLICE_BOUTON)
        #bouton annuler
        bouton_annuler.dessiner(FENETRE, POLICE_BOUTON)
        pygame.display.flip()


#écran de jeu 
def ecran_manche(manche: Manche):
    plateau = manche._plateau
    joueurs = manche._joueurs

    clock = pygame.time.Clock()

    bouton_lancer   = Bouton("LANCER DÉS",        40,  HAUTEUR - 100)
    bouton_dir      = Bouton("CHANGER\nDIRECTION", 320, HAUTEUR - 115, 200, 85)
    bouton_ramasser = Bouton("RAMASSER",         540, HAUTEUR - 100, 140, 60)
    bouton_deposer  = Bouton("DÉPOSER",          700, HAUTEUR - 100, 140, 60)
    bouton_passer   = Bouton("PASSER TOUR",      860, HAUTEUR - 100, 130, 60)

    dernier_lancer = 0
    message        = ""

    #état de tour pour le joueur humain
    phase = "attente_lancer" 
    a_ramasse_ce_tour = False
    case_courante = None

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #changer de direction(pour humain, avant de lancer les dés)
            if bouton_dir.clique(event) and not manche.terminee:
                joueur = manche.joueur_courant()
                if not isinstance(joueur, JoueurIA) and phase == "attente_lancer":
                    try:
                        joueur.changer_direction()
                        message = "Direction changée."
                    except ChangementDirectionError as e:
                        message = str(e)

            #passer au tour suivant (humain)
            if bouton_passer.clique(event) and not manche.terminee:
                joueur = manche.joueur_courant()
                if not isinstance(joueur, JoueurIA) and phase == "choix_action":
                    manche.verifier_fin()
                    if not manche.terminee:
                        manche.avancer_tour()
                    phase = "attente_lancer"
                    a_ramasse_ce_tour = False
                    case_courante = None
                    message = "Tour passé."

            #lancer des dés
            if bouton_lancer.clique(event) and not manche.terminee:
                joueur   = manche.joueur_courant()
                nb_cases = manche._plateau.nb_cases
                message = ""

                #tour IA,  on joue tout d'un coup car aucun choix à demander
                if isinstance(joueur, JoueurIA):
                    a_ramasse = False
                    pos = joueur.position
                    peut_choisir_direction = True

                    if pos == 0:
                        if joueur.direction != 1:
                            joueur.direction = 1
                        peut_choisir_direction = False
                    elif pos == nb_cases - 1:
                        if joueur.direction != -1:
                            joueur.direction = -1
                        peut_choisir_direction = False

                    if getattr(joueur, "_est_rentre", False):
                        #IA déjà rentréealors on passe tout de suite au joueur suivant
                        message = "IA déjà rentrée, on passe au joueur suivant."
                        manche.verifier_fin()
                        if not manche.terminee:
                            manche.avancer_tour()
                    else:
                        if peut_choisir_direction and joueur.choisir_changer_direction(manche):
                            try:
                                joueur.changer_direction()
                            except ChangementDirectionError:
                                pass

                        d1 = random.randint(1, 3)
                        d2 = random.randint(1, 3)
                        dernier_lancer = d1 + d2

                        joueur.avancer(dernier_lancer, manche._plateau, manche)
                        case = manche._plateau.get_case(joueur.position)

                        manche.consommer_oxygene(joueur)
                        if manche.terminee:
                            message = "Plus d'oxygène, fin de la manche."
                        else:
                            #ramasser IA
                            if case.contient_jeton() and joueur.choisir_ramasser(case):
                                try:
                                    joueur.ramasser_tresor(case)
                                    a_ramasse = True
                                except JoueurError:
                                    pass

                            #dépôt sur un jeton blanc IA
                            if case.contient_jeton_blanc() and not a_ramasse and joueur.tresor_manche:
                                idx_dep = joueur.choisir_deposer_tresor(case, manche)
                                if idx_dep is not None:
                                    try:
                                        joueur.deposer_tresor(case, idx_dep)
                                    except (JoueurError, PileCompleteError, CaseError):
                                        pass

                            manche.verifier_fin()
                            if not manche.terminee:
                                manche.avancer_tour()

                    phase = "attente_lancer"
                    a_ramasse_ce_tour = False
                    case_courante = None

                # Tour humain
                else:
                    #si on est en phase "choix_action" alors relancer = passer / fin de tour
                    if phase == "choix_action":
                        manche.verifier_fin()
                        if not manche.terminee:
                            manche.avancer_tour()
                        phase = "attente_lancer"
                        a_ramasse_ce_tour = False
                        case_courante = None
                        message = "Tour terminé."
                    #si on est en phase "attente_lancer" alors on joue
                    else:
                        pos = joueur.position
                        peut_choisir_direction = True

                        #direction imposée
                        if pos == 0:
                            if joueur.direction != 1:
                                joueur.direction = 1
                            peut_choisir_direction = False
                        elif pos == nb_cases - 1:
                            if joueur.direction != -1:
                                joueur.direction = -1
                            peut_choisir_direction = False

                        if getattr(joueur, "_est_rentre", False):
                            #joueur déjà revenu au sous matin alors on ne joue pas et on passe au suivant
                            message = "Vous êtes déjà rentré, on passe au joueur suivant."
                            manche.verifier_fin()
                            if not manche.terminee:
                                manche.avancer_tour()
                            phase = "attente_lancer"
                            a_ramasse_ce_tour = False
                            case_courante = None
                        else:
                            #on ne gère pas ici le changement de direction
                            d1 = random.randint(1, 3)
                            d2 = random.randint(1, 3)
                            dernier_lancer = d1 + d2

                            joueur.avancer(dernier_lancer, manche._plateau, manche)
                            case = manche._plateau.get_case(joueur.position)
                            case_courante = case

                            manche.consommer_oxygene(joueur)
                            if manche.terminee:
                                message = "Plus d'oxygène, fin de la manche."
                                phase = "attente_lancer"
                                case_courante = None
                            else:
                                phase = "choix_action"
                                a_ramasse_ce_tour = False
                                message = "Choisissez : RAMASSER, DÉPOSER, ou relancer pour passer."

            #ramasser humain
            if bouton_ramasser.clique(event) and not manche.terminee:
                joueur = manche.joueur_courant()
                if not isinstance(joueur, JoueurIA) and phase == "choix_action":
                    if case_courante is not None and case_courante.contient_jeton():
                        try:
                            joueur.ramasser_tresor(case_courante)
                            a_ramasse_ce_tour = True
                            message = "Trésor ramassé."
                        except JoueurError as e:
                            message = f"Impossible de ramasser : {e}"
                    else:
                        message = "Aucun trésor à ramasser ici."

            
            #déposer humain
            if bouton_deposer.clique(event) and not manche.terminee:
                joueur = manche.joueur_courant()
                if not isinstance(joueur, JoueurIA) and phase == "choix_action":
                    if a_ramasse_ce_tour:
                        message = "Vous avez déjà ramassé ce tour : impossible de déposer."
                    elif case_courante is None or not case_courante.contient_jeton_blanc():
                        message = "Vous devez être sur un jeton blanc pour déposer."
                    elif not joueur.tresor_manche:
                        message = "Vous n'avez aucun trésor à déposer."
                    else:
                        #fenêtre de choix
                        idx_dep = choisir_tresor_a_deposer(FENETRE, joueur)

                        if idx_dep is None:
                            message = "Dépôt annulé."
                        else:
                            try:
                                joueur.deposer_tresor(case_courante, idx_dep)
                                message = "Trésor déposé."
                            except (JoueurError, PileCompleteError, CaseError) as e:
                                message = f"Impossible de déposer : {e}"



        #affichage
        FENETRE.blit(FOND, (0, 0))

        #sous marin
        sous_rect = SOUS_MARIN_IMG.get_rect()
        x_tri0, y_tri0 = cases_coord[0]
        sous_rect.midbottom = (x_tri0 - 20, y_tri0 + 35)
        FENETRE.blit(SOUS_MARIN_IMG, sous_rect)
        sous_x, sous_y = sous_rect.center

        #chemin
        dessiner_chemin(FENETRE, cases_coord)

        #oxygène
        pygame.draw.circle(FENETRE, ROUGE_OXY, (90, 110), 55)
        txt_oxy = POLICE_BOUTON.render(str(manche.oxygene), True, BLANC)
        FENETRE.blit(txt_oxy, txt_oxy.get_rect(center=(90, 110)))


        #texte joueur
        if manche.terminee:
            info_str = "Manche terminée"
        else:
            j_courant = manche.joueur_courant()
            info_str = f"Joueur {j_courant.couleur}  |  Dernier lancer : {dernier_lancer}"

        info_txt = POLICE_INFO.render(info_str, True, BLANC)
        
        info_rect = info_txt.get_rect(midright=(LARGEUR - 40, 50))
        FENETRE.blit(info_txt, info_rect)

        #message
        if message:
            msg_surf = POLICE_MSG.render(message, True, BLANC)
            msg_rect = msg_surf.get_rect(midright=(LARGEUR - 40, 95))
            FENETRE.blit(msg_surf, msg_rect)
        
        #cadre: trésors ramassés par les joueurs durant la manche
        
        
        panel_x = LARGEUR - 205
        panel_y = 140
        panel_w = 200
        panel_h = 40 + len(joueurs) * 50

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 150), pygame.Rect(0, 0, panel_w, panel_h), border_radius=20)
        FENETRE.blit(panel, (panel_x, panel_y))

        #titre du cadre
        titre_panel = POLICE_MSG.render("Trésors ", True, BLANC)
        FENETRE.blit(titre_panel, titre_panel.get_rect(midtop=(panel_x + panel_w // 2, panel_y + 8)))

        #pour chaque joueur: petit rond de couleur + résumé des niveaux
        for i, j in enumerate(joueurs):
            #position de la ligne
            ligne_y = panel_y + 40 + i * 50
            ligne_x = panel_x + 15

            #rond de couleur du joueur
            coul = COULEUR_PIONS.get(j.couleur, (255, 255, 255))
            pygame.draw.circle(FENETRE, coul, (ligne_x + 10, ligne_y + 10), 8)
            pygame.draw.circle(FENETRE, (0, 0, 0), (ligne_x + 10, ligne_y + 10), 8, 2)

            #comptage des niveaux dans tresor_manche
            c_niv = [0, 0, 0, 0]  # niv1, niv2, niv3, niv4

            for t in j.tresor_manche:
                if isinstance(t, JetonRuine):
                    niv = t.niveau
                    if 1 <= niv <= 4:
                        c_niv[niv - 1] += 1
                elif isinstance(t, PileJeton):
                    for jt in t.jetons:
                        niv = jt.niveau
                        if 1 <= niv <= 4:
                            c_niv[niv - 1] += 1

            #texte résumé (T = triangle, C = carré, P = pentagone, H = hexagone)
            txt = f"T:{c_niv[0]}  C:{c_niv[1]}  P:{c_niv[2]}  H:{c_niv[3]}"
            txt_surf = POLICE_MSG.render(txt, True, BLANC)
            FENETRE.blit(txt_surf, (ligne_x + 30, ligne_y))

        #fusion des jetons perdus en piles
    
        index_debut = manche.index_debut_jetons_perdus
        piles_affichage = []

        if index_debut is not None:

            jetons_perdus = []

            #récupère les jetons perdus (après resserrage)
            for pos in range(index_debut, plateau.nb_cases):
                case_temp = plateau.get_case(pos)
                contenu = case_temp.contenu
                if hasattr(contenu, "niveau"): #jeton
                    jetons_perdus.append(contenu)

            #regroupe par piles de 3
            pile = []
            for j in jetons_perdus:
                pile.append(j)
                if len(pile) == 3:
                    piles_affichage.append(list(pile))
                    pile = []

            if pile:
                piles_affichage.append(list(pile))

        #formes et jeton blanc
        for idx, (x, y) in enumerate(cases_coord):
            #on ne dessine que si la case existe sur le plateau
            if idx + 1 >= manche._plateau.nb_cases:
                continue
            case = manche._plateau.get_case(idx + 1)
            dessiner_case_contenu(FENETRE, case, x, y)




        #pions des joueurs
        for idx_j, j in enumerate(joueurs):
            c = COULEUR_PIONS.get(j.couleur, (255, 255, 255))
            if j.position == 0:
                offset_x = (idx_j - len(joueurs) / 2) * 20
                pion_x = int(sous_x + offset_x)
                pion_y = int(sous_y + 10)
            else:
                coord = coord_case_depuis_position(j.position)
                if coord is None:
                    continue
                pion_x, pion_y = int(coord[0]), int(coord[1])

            pygame.draw.circle(FENETRE, c, (pion_x, pion_y), 12)
            pygame.draw.circle(FENETRE, (0, 0, 0), (pion_x, pion_y), 12, 2)

        #boutons
        bouton_lancer.dessiner(FENETRE, POLICE_BOUTON)
        bouton_dir.dessiner(FENETRE, POLICE_BOUTON)
        bouton_ramasser.dessiner(FENETRE, POLICE_BOUTON)
        bouton_deposer.dessiner(FENETRE, POLICE_BOUTON)
        bouton_passer.dessiner(FENETRE, POLICE_BOUTON)


        pygame.display.flip()
        if manche.terminee:
            running = False

