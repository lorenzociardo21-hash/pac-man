from mazegenerator import MazeGenerator


generatore = MazeGenerator(size=(21, 21), perfect=False, seed=42)

mappa = generatore.maze

print(mappa)