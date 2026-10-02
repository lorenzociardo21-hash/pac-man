from mazegenerator import MazeGenerator

generatore = MazeGenerator(size=(20, 21), perfect=False, seed=42)
griglia = generatore.maze

print(len(griglia))     # how many rows
print(len(griglia[0]))  # how many columns
print(griglia[0])       # the first row


"""importo maze package, dico che deve essere 20 21 con seed 42
griglio = ... prende maze da  generatore cioe lista di 21 rows
e ogni row e' alta 21 colonne.
ogni numero che printo descrive come e' la cella in base a muri
aperti e chiusi N-S-O-E"""