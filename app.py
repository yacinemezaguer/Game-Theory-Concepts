from Main import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(250, 50, 800, 580)
        self.setWindowTitle("Game Theory applications")
        self.setStyleSheet(open('style.css').read())
        self.initUI()

    def initUI(self):
        #Initialisation des éléments de l'interface

        #Table Widget (affichage des gains)
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 500, 300))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        #TextBrowser (affichage des résultats)
        self.textBrowser = QtWidgets.QTextBrowser(self)
        self.textBrowser.setGeometry(QtCore.QRect(10, 325, 740, 250))
        self.textBrowser.setObjectName("textBrowser")

        #Boutons

        self.importButton = QtWidgets.QPushButton(self)
        self.importButton.setText("Importer")
        self.importButton.setGeometry(QtCore.QRect(590, 15, 130, 40))
        self.importButton.clicked.connect(self.importClicked)

        self.nashButton = QtWidgets.QPushButton(self)
        self.nashButton.setText("équilibre Nash")
        self.nashButton.setGeometry(QtCore.QRect(590, 65, 130, 40))
        self.nashButton.clicked.connect(self.calculerNashClicked)

        self.dominanceButton = QtWidgets.QPushButton(self)
        self.dominanceButton.setText("Dominance")
        self.dominanceButton.setGeometry(QtCore.QRect(590, 115, 130, 40))
        self.dominanceButton.clicked.connect(self.calculerDominanceClicked)

        self.securiteButton = QtWidgets.QPushButton(self)
        self.securiteButton.setText("Niveaux de sécurité")
        self.securiteButton.setGeometry(QtCore.QRect(590, 165, 130, 40))
        self.securiteButton.clicked.connect(self.calculerSecuriteClicked)

        self.valeurButton = QtWidgets.QPushButton(self)
        self.valeurButton.setText("Valeur (Jeu à somme Nulle)")
        self.valeurButton.setGeometry(QtCore.QRect(575, 215, 160, 40))
        self.valeurButton.clicked.connect(self.calculerValeurClicked)

        
    def calculerNashClicked(self):
        equilibresNash = nash(self.gains)
        if len(equilibresNash) > 0:
            self.textBrowser.append("Les équilibres de Nash de ce jeu sont:\n" + str(equilibresNash))
        else: self.textBrowser.append("Il n'existe pas d'équilibre de Nash pour ce jeu.")

        if len(self.strategies) == 2:
            mNash = mixedNash(self.gains)
            if mNash is not None:
                self.textBrowser.append(f"équilibre mixte de Nash: {mNash}")
            else: self.textBrowser.append("Impossible de trouver l'équilibre de nash mixte pour ce jeu.")

    def calculerDominanceClicked(self):
        #Dominance strice et faible
        for i in range(len(self.gains)):
            self.textBrowser.append(f"Joueur {i+1}:")
            strictement, faiblement, strats = stratDominante(self.gains, i)
            if strictement:
                self.textBrowser.append(f"Stratégie strictement dominante: {strats}")
            elif faiblement:
                self.textBrowser.append(f"Stratégie(s) faiblement dominante(s): {strats}")
            else: self.textBrowser.append("Ce joueur ne possède pas de stratégie dominante")
        
        #Profils pareto optimums
        paretoList = paretoOptimums(self.filedata)
        if len(paretoList) > 0:
            self.textBrowser.append(f"Liste des profils pareto optimums: {paretoList}")
        else: print("Il n'existe pas de profil pareto optimum pour ce jeu")

    def calculerSecuriteClicked(self):
        self.textBrowser.append("Niveaux de sécurité: ")
        for i in range(len(self.gains)):
            self.textBrowser.append(f"Joueur {i+1}:")
            self.textBrowser.append(f"Niveau de sécurité: {niveauSecurite(self.filedata, self.gains[0].shape[i], i)}")
        

    def calculerValeurClicked(self):
        valeur = valeurJeu(self.gains)
        if len(self.strategies) == 2:
            if valeur is not None:
                self.textBrowser.append(f"Valeure du jeu: {valeur}")
            else: self.textBrowser.append("Ce jeu ne possède pas de valeur")
        else: self.textBrowser.append("Impossible de calculer la valeur du jeu, Veuillez entrer un jeu à 2 joueurs")

    def importClicked(self):
        #Importation du fichier de données
        self.filedata = np.genfromtxt('data.csv', delimiter = ',', dtype = 'int32')
        print(self.filedata)
        self.strategies = tuple(self.filedata[0, 0:int(len(self.filedata[0])/2)]) #lecture de la forme de la matrice de gain (nombre de stratégies par joueur)
        self.gains = genMatGains(self.filedata, self.strategies)
        
        #remplissage du tableau
        self.tableWidget.setColumnCount(len(self.filedata[0]))
        self.tableWidget.setRowCount(len(self.filedata) - 1)

        """Header"""
        for i in range(len(self.strategies)):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem("Joueur" + str(i+1)))

        for i in range(len(self.strategies)):
            self.tableWidget.setHorizontalHeaderItem(i+len(self.strategies), QTableWidgetItem("Gains J" + str(i+1)))

        """Data"""
        for i in range(1, len(self.filedata)):
            for j in range(len(self.filedata[i])):
                self.tableWidget.setItem(i-1,j, QTableWidgetItem(str(self.filedata[i][j])))




def window():
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec_())

window()