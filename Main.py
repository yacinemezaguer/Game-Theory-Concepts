import numpy as np
import math


def mReponses(gains, indices, dimActuelle, dimCible, strategies, currAnswers, lastAnswers = None):
    #Retourne les meilleures réponses du joueur 'dimActuelle' selon la matrice 'gains'
    #Le premier appel doit être fait avec indices = [], dimActuelle = 0, currAnswers = []
    """
        Paramètres
        ----------
        gains : n dimensional array
            la matrice de gains du joueur
        indices : int list
            les indices d'accès à la matrices (construite au fur à mesure)
        dimActuelle: int
            l'indice de la dimension actuellement itérée
        dimCible : int
            l'indice du joueur cible
        strategies : int tuple
            le nombre de stratégie de chaque joueur
        currAnswers : list of int lists
            les meilleures réponses du joueur actuelle, elle est remplies par cette fonction même
        lastAnswers : list of int lists
            les meilleures réponses du joueur précédent, utilisées seulement pour l'intersection des ensembles, peut être None (null)
        """
    if(dimActuelle < len(strategies)): #Construction des indices d'accès à la matrice de gains
        if dimActuelle != dimCible:
            indices.append(0) #ajout d'une dimensions dans la liste d'indices
            for i in range(strategies[dimActuelle]):
                indices[dimActuelle] = i
                mReponses(gains, indices, dimActuelle+1, dimCible, strategies, currAnswers, lastAnswers)
            indices.pop()
        else:
            indices.append(0) 
            mReponses(gains, indices, dimActuelle+1, dimCible, strategies, currAnswers, lastAnswers)
            indices.pop()
    else: #parcours des stratégies du joueur cible pour trouver les meilleures réponses à ce profil de stratégies
        max = -math.inf
        bestAnswers = []

        for i in range(strategies[dimCible]):
            indices[dimCible] = i
            gain = gains[tuple(indices)]
            #print(f"{indices} = {gain}")

            if gain == max:
                bestAnswers.append(indices.copy())
            elif gain > max:
                max = gain
                bestAnswers.clear()
                bestAnswers.append(indices.copy())

        if lastAnswers is None: #Ajoute toute les meilleures réponses trouvées
            currAnswers.extend(bestAnswers)
        else: #N'ajoute que les éléments d'intersection avec le joueur précédent
            for element in bestAnswers:
                if element in lastAnswers:
                    currAnswers.append(element)

    return currAnswers


def genMatGains(data, strategies):
    #Retourne la matrice qui contient les gains de tous les joueurs. 
    #gains[0, 2, 1] représente le gain du joueur 0 pour le profil (2, 1)

    strategies = list(strategies)
    nbJoueurs = len(strategies)
    strategies.insert(0, len(strategies))
    gains = np.zeros(strategies, dtype='int32')

    for i in range(1, len(data)):
        for j in range(nbJoueurs):
            indice = list(data[i][0:nbJoueurs])
            indice.insert(0, j)
            gains[tuple(indice)] = data[i][nbJoueurs + j]

    return gains


def nash(gains):
    #Calcul et retourne la liste d'équilibres de nash du jeu associé à la matrice 'gains'
    lastAnswers = None
    for i in range(len(gains)):
        lastAnswers = mReponses(gains[i], [], 0, i, gains[0].shape, [], lastAnswers)

    return lastAnswers


def stratDominante(gains, joueur):
    #Détermine si il existe des stratégies strictement (resp. faiblement) dominante et les retourne
    """
    joueur : int
        indice du joueur pour lequel on cherche des stratégies dominantes
    La valeur de retour est un tuple (strictement, faiblement, list)
    strictement : boolean
        Vrai s'il existe une stratégie strictement dominante
    faiblement : boolean
        Vrai s'il existe une ou plusieurs stratégie faiblement dominante
    list : int list
        La liste de(s) stratégie(s) dominantes
    """
    #Recherche de stratégie strictement dominante
    reponses = mReponses(gains[joueur], [], 0, joueur, gains[0].shape, [], None)
    dominant = reponses[0][joueur]
    strictement = True
    for profil in reponses:
        if profil[joueur] != dominant:
            strictement = False
            break

    if strictement:
        return True, False, dominant

    #calcul du nombre de profils adverses
    profilsAdverses = 1
    for i in gains[0].shape:
        profilsAdverses *= i

    profilsAdverses //= gains[0].shape[joueur]

    #Recherche des stratégies faiblement dominante
    listStrats = np.zeros(gains[0].shape[joueur], dtype = 'int32')
    for profil in reponses:
        listStrats[profil[joueur]] += 1 #incrémenter la stratégie utilisée dans ce profil
    
    faiblement = False
    stratsDominantes = []
    for strategie in range(len(listStrats)):
        if listStrats[strategie] == profilsAdverses: #Si le nombre d'apparation de la stratégie est égal au nombre de profils adverse alors elle est dominante
            stratsDominantes.append(strategie)
            faiblement = True

    return False, faiblement, stratsDominantes


def paretoDomine(A, B):
    #Retourne Vrai si A domine B au sens de pareto, Retourne Faux pour tous les autres cas
    pareto = False
    for i in range(len(A)):
        if A[i] < B[i]:
            return False
        elif A[i] > B[i]:
            pareto = True
    
    return pareto

def paretoOptimums(data):
    listOptimums = []
    nbJoueurs = len(data[0])//2

    for i in range(1,len(data)):
        domine = True
        for j in range(1, len(data)):
            if paretoDomine(data[j, nbJoueurs:], data[i, nbJoueurs:]):
                domine = False
                break
        
        if domine:
            listOptimums.append(list(data[i, 0:nbJoueurs]))

    return listOptimums


def niveauSecurite(data, nbStrategies, joueur):
    strategies = np.full(nbStrategies, np.inf)
    nbJoueurs = len(data[0])//2
    for i in range(1, len(data)):
        if data[i, nbJoueurs+joueur] < strategies[data[i, joueur]]:
            strategies[data[i, joueur]] = data[i, nbJoueurs+joueur]

    return int(np.max(strategies))

def mixedNash2x2(gains):
    nash = []

    #Si 2 stratégie par joueur:  (Les probabilités sont p et 1-p)
    if len(gains[0]) == 2:
        for i in range(2):
            numerateur = gains[i, 1, 1] - gains[i, i, 1-i]
            denomi = gains[i, 0, 0] + gains[i, 1, 1] - gains[i, 1, 0] - gains[i, 0, 1]
            if denomi == 0:
                return None
            p = numerateur/denomi
            if p < 0 or p > 1:
                return None

            nash.append([p, (1-p)])

        return nash

def mixedNash(gains):
    nash = []

    #Si 2 stratégie par joueur:  (Les probabilités sont p et 1-p)
    if len(gains[0]) == 2:
        return mixedNash2x2(gains)
        
    elif len(gains[0]) == 3: #Si 3 stratégie par joueur:  (p1, p2 probabilité de J1 et q1, q2 probabilité de J2)
        failure = False
        A1 = np.array([ [ gains[1, 0, 0] - gains[1, 0, 1] - gains[1, 2, 0] + gains[1, 2, 1], #matrice d'équations pour J1 (inégalité du support du J2)
            gains[1, 1, 0] - gains[1, 1, 1] - gains[1, 2, 0] + gains[1, 2, 1] ], 
        [ gains[1, 0, 1] - gains[1, 2, 1] - gains[1, 0, 2] + gains[1, 2, 2], 
            gains[1, 1, 1] - gains[1, 2, 1] - gains[1, 1, 2] + gains[1, 2, 2] ] ])
        B1 = np.array([gains[1, 2, 1] - gains[1, 2, 0], gains[1, 2, 2] - gains[1, 2, 1]]) #matrice de résultats pour J1 (inégalité du support du J2)
        
        try:
            X = np.linalg.solve(A1, B1)
        except np.LinAlgError:
            failure = True 

        if X[0] < 0 or X[1] < 0 or X[0]+X[1] > 1:
            failure = True

        if not failure:
            nash.append([X[0], X[1], 1-X[0]-X[1]])
        
        #Calcul de la stratégie de J2
        A2 = np.array([ [ gains[0, 0, 0] - gains[0, 0, 2] + gains[0, 1, 2] - gains[0, 1, 0], #matrice d'équations pour J2 (inégalité du support du J1)
            gains[0, 0, 1] - gains[0, 0, 2] + gains[0, 1, 2] - gains[0, 1, 1] ], 
        [ gains[0, 1, 0] - gains[0, 1, 2] -gains[0, 2, 0] + gains[0, 2, 2], 
            gains[0, 1, 1] - gains[0, 1, 2] - gains[0, 2, 1] + gains[0, 2, 2] ] ])
        B2 = np.array([gains[0, 1, 2] - gains[0, 0, 2], gains[0, 2, 2] - gains[0, 1, 2]]) #matrice de résultats pour J2 (inégalité du support du J1)
        
        try:
            X = np.linalg.solve(A2, B2)
        except np.LinAlgError:
            failure = True 

        if X[0] < 0 or X[1] < 0 or X[0]+X[1] > 1:
            failure = True

        if not failure:
            nash.append([X[0], X[1], 1-X[0]-X[1]])
            return nash
            
        else: #Tester toutes les combinaisons de supports
            supportsJ1 = [[0, 1], [0, 2], [1, 2]]
            supportsJ2 = [[0, 1], [0, 2], [1, 2]]
            for stratJ1 in supportsJ1:
                for stratJ2 in supportsJ2:
                    nash = mixedNash2x2(gains[np.ix_([0, 1], stratJ1, stratJ2)])
                    if nash is not None:
                        result = np.zeros((2, 3))
                        result[0][[stratJ1[0], stratJ1[1]]] = nash[0]
                        result[1][[stratJ2[0], stratJ2[1]]] = nash[1]
                        return result
            
            #Si aucun des cas n'a aboutit à un équilibre de nash alors erreur:
            return None
                    
    else: raise Exception("Nombre de joueurs invalide, veuillez entrer un jeu à 2 joueurs")
    


def valeurJeu(gains):
    #Trouve la valeur d'un jeu à somme nulle si elle existe

    nbCols = len(gains[0][0]) #nombre de colonnes
    nbRows = len(gains[0])    #nombre de lignes

    #Trouver le maxMin pour le Joueur 1
    maxMin = np.amax(np.amin(gains[0], axis=1))
    #Trouver le minMax pour le Joueur 2
    minMax = np.amin(np.amax(gains[0], axis=0)) 

    if(minMax == maxMin):
        return minMax
    
    return None
