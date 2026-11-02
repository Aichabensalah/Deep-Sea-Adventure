from .engine.partie import Partie
from .engine.joueur import Joueur

# Créer une partie avec 2 joueurs
partie = Partie([Joueur("rouge"), Joueur("bleu")])

# Lancer la partie version console
partie.jouer()
