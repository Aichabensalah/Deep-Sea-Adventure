import pygame

BLANC       = (240, 240, 240)
BLEU_BOUTON = (16, 63, 111)
BLEU_SURVOL = (22, 92, 150)

"classe pour pouvoir gérer les boutons dans les différentes fenêtres"

class Bouton:
    def __init__(self, texte, x, y, largeur=260, hauteur=70):
        self.texte = texte
        self.rect = pygame.Rect(x, y, largeur, hauteur)

    def dessiner(self, surface, police, couleur=BLEU_BOUTON, couleur_hover=BLEU_SURVOL): #dessin des boutons
        mx, my = pygame.mouse.get_pos()
        col = couleur_hover if self.rect.collidepoint(mx, my) else couleur

        pygame.draw.rect(surface, col, self.rect, border_radius=25)

        rendu = police.render(self.texte, True, BLANC)
        surface.blit(rendu, rendu.get_rect(center=self.rect.center))



    def clique(self, event): #pouvoir cliquer sur un bouton
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class IconButton:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    def dessiner(self, surface, *args, **kwargs):
        surface.blit(self.image, self.rect)

    def clique(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

