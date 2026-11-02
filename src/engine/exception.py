#différentes classe d'exception pour chaque classe qui en a besoin

class PileCompleteError(Exception):
  pass

class CaseError(Exception):
  pass

class PlateauError(Exception):
  pass

class JoueurError(Exception):
  pass

class ChangementDirectionError(Exception):
  pass

class MancheError(Exception):
  pass