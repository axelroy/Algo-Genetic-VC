import pygame
from pygame.locals import *
from pygame.math import Vector2
from itertools import cycle
import sys, getopt
import random
from math import sqrt
from time import time
from math import hypot

# Contient le tableau de villes. Une fois instancié, il n'est plus modifié.
cities = None
# Nombre de chromosomes formant la population
population_size = 20
# Pourcentage de la population qui va subir une mutation
mutation_rate = 40
# Constantes pour PyGame
WHITE = (255,255,255)
BLACK = (0,0,0)
# Taille des points pour représenter les villes
POINTSIZE = 2
# Temps que l'on laisse à disposition pour retourner la solution. Avec 0.05s on est très très large, cela prend en général 0.005s
TIMELIMIT = 0.1
starting_time = 0
selection_rate = 60
DEFAULTMAXTIME = 20

################################################################################
#  Algorithme génétique
################################################################################

def populate(count):
    """Crée une population de n individus selon la liste de ville auparavant déterminée"""
    population = []

    available_indexes = []

    # Pour chaque échantillon de la population à créer
    for _ in range(0,count):
        indexes_list = []

        available_indexes = list(range(len(cities)))

        # On utilise ici une liste d'index afin de minimiser les appels au random
        # Tant qu'il reste encore des index (attention, ils ne sont pas forcément consécutifs)
        while (len(available_indexes) > 0):
            # On tire au hasard un index entre 0 et la longueur de la chaine
            index = random.randrange(0, len(available_indexes))
            # On ajoute la valeur contenue à l'index à la séquence de villes
            indexes_list.append(available_indexes[index])
            # On retire l'index de la ville
            del available_indexes[index]
        population.append(Chromosome(indexes_list))

    return population

def selection(population):
    population = sorted(population, key=lambda chromosome: chromosome.cost)
    population = population[:(int)(len(population)/100 * selection_rate)]

    return population

def crossing(population, size):
    start_xo_index = int(len(population[0].genes) / 2 - len(population[0].genes) / 4)
    end_xo_index = int(len(population[0].genes) / 2 + len(population[0].genes) / 4)

    nb_to_create = size - len(population)

    for chromosome_index in range(0, nb_to_create):
        chromosome_x = random.choice(population)
        chromosome_y = random.choice(population)

        new_genes_list = xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index)

        # Ajout du nouveau chromosome à la population
        population.append(Chromosome(new_genes_list))

    return population

def xo_cross(chromosome_x, chromosome_y, start_xo_index, end_xo_index):
    """ Principe global de mutation : Mutation XO.
        On selectionne deux Chromosomes x et y parmis la population.
        On détermine une section où on va insérer la section de y dans le même endroit de x.
        Il faut pour ceci préparer x à recevoir les gènes de y en :
            Déterminant les valeurs de la portion de y qui sera insérée.
            Remplacer ces valeurs dans x par un marqueur.
            Mettre en place ces marqueurs à la position de la section que l'on échange.
            Pour ceci, on condense tous les indexes sans les marqueurs, que l'on décale
            par n rotations à droite, où n est le nombre de marqueurs entre la fin de la section
            et la fin des gênes.
            A la fin, on insère la section de y.

            exemple complet :

            Chromosomes retenus
            [8, 7, 2, 3, 0, 5, 1, 6, 4, 9]] : Cost : 2433.6255091876656
            [4, 9, 0, 3, 5, 6, 2, 7, 1, 8]] : Cost : 2468.848455299176

            Section (valeurs) à échanger (choisie arbitrairement, indexs 3 à 5)
            [3, 5, 6]

            X sans les valeurs de la section
            [8, 7, 2, None, 0, None, 1, None, 4, 9]

            Nombre de None après l'index 5
            1

            Liste sans les None, avant décalage
            [8, 7, 2, 0, 1, 4, 9]
            Liste sans les None, après décalage
            [7, 2, 0, 1, 4, 9, 8]

            Portion à insérer
            [3, 5, 6]

            Nouveaux gênes après croisements
            [7, 2, 0, 3, 5, 6, 1, 4, 9, 8]

    """

    # Détermination des valeurs à supprimer dans x, tirées de la portion y
    list_to_replace = chromosome_y.genes[start_xo_index:end_xo_index+1]

    # Remplacement de ces valeurs dans x avec des None
    new_genes_list = [value if value not in list_to_replace else None for value in chromosome_x.genes]

    # Comptage du nombre de None à droite de la section (pour le décalage)
    nb_none_right = new_genes_list[end_xo_index+1:].count(None)

    # Suppression des None dans la liste pour les rotations
    new_genes_list = [value for value in new_genes_list if not value == None]

    # Rotation à droite des éléments
    for _ in range(0,nb_none_right):
        new_genes_list.insert(len(new_genes_list), new_genes_list.pop(0))
    list_to_insert = chromosome_y.genes[start_xo_index:end_xo_index+1]

    # Insertion des valeurs de y dans la section préparée
    new_genes_list[start_xo_index:start_xo_index] = list_to_insert

    return new_genes_list

def mutate(population):
    """Pour l'instant, la mutation est un simple swap d'indexes au hasard"""
    for _ in range(0, int(len(population) / 100 * mutation_rate)):
        chromosome = random.choice(population)
        population.append(chromosome.mutate())

    return population

def solve(cities_list, window = None, maxtime = DEFAULTMAXTIME, gui = False):
    global cities
    global starting_time
    global TIMELIMIT
    global selection_rate
    global mutation_rate

    # Second seuil de mutation pour tenter de faire sortir d'un minimum local
    second_mutation_rate = 60
    # Détermine si on est dans le second seuil de mutation
    augmentation_up = False
    # Pourcentage d'erreur pour le calcul du temps écoulé entre deux cycles.
    # Il est très grand pour ne pas prendre de risque pour l'évaluation via PVC-tester
    time_error_rate = 0.02

    if gui:
        font = pygame.font.Font(None, 30)

    cities = tuple(cities_list)
    population = populate(population_size)

    # Calcul du temps écoulé depuis le lancement du programme
    elapsed_time = time() - starting_time
    time_left = maxtime - elapsed_time
    time_left -= time_left * time_error_rate

    while time_left > TIMELIMIT:
        time1 = time()
        population = selection(population)

        if gui:
            draw_best_path(population, window)

        population = crossing(population, population_size)
        population = mutate(population)

        if time_left < maxtime/4 and not augmentation_up:
            mutation_rate = second_mutation_rate
            augmentation_up = True

        time2 = time()
        elapsed_time = time2 - time1
        elapsed_time = elapsed_time + elapsed_time * time_error_rate
        time_left -= elapsed_time

    population = sorted(population, key=lambda chromosome: chromosome.cost)
    best_solution = population[0]
    best_cost = best_solution.cost
    best_path = [cities_list[city].name for city in best_solution.genes]

    if window != None:
        draw_best_path(population, window)
        text = font.render("Coût : " + str(population[0].cost), True, WHITE)
        textRect = text.get_rect()
        window.blit(text, textRect)


    print("Meilleur cout", best_cost )

    return best_cost, best_path

################################################################################
#  Fin Algorithme génétique
################################################################################

def ga_solve(file = None, gui=True, maxtime=DEFAULTMAXTIME):
     return parametre(file,gui,maxtime)

def parametre(file = None, gui=True, maxtime=DEFAULTMAXTIME):
    window = None
    cities_list = None
    global starting_time
    starting_time = time()

    if(file):
        cities_list = []
        with open(file, "r") as fichier :
            for line in fichier :
                data = line.split()
                cities_list.append(City((int(data[1]),int(data[2])), data[0]))
    if(gui):
        window = pygame.display.set_mode((500, 500))

    if (gui and not file):
        maxtime = DEFAULTMAXTIME
        return display(cities_list, maxtime,gui,window)
    elif(not gui and file):
        return solve(cities_list, window, maxtime, gui)
    elif(gui and file):
        return display(cities_list,maxtime,gui,window)


def main(argv):
    """
        NAME
            TSP : Solve the travelling salesman problem using genetic algorithm
        SYNOPSIS
            python DroxlerRoy.py [--nogui] [--maxtime s] [filename]

        PARAMETERS
            [--nogui] : disable the gui, default to true
            [--maxtime s] : diffine the maximum time of exectution in seconds , default at 1000 s
            [filename] : Format expected :
                                        City_Name X_Position Y_Position
                                        i.e :
                                        v0 54 391
                                        v1 77 315
                                        It uses the /data/pb010.txt path

    """
    optlist, args = getopt.getopt(argv, '' ,['nogui', 'maxtime=','help'])

    file = None
    gui = True
    maxtime = DEFAULTMAXTIME

    if len(args) == 1:
        file = args[0]

    for o,a in optlist :
        if o == "--maxtime":
            maxtime = int(a)
        if o == "--nogui":
            gui = False
        if o == "--help":
             print(main.__doc__)
             sys.exit()

    parametre(file,gui,maxtime)

################################################################################
#  Affichage
################################################################################

def clear_window(window):
    window.fill(BLACK)

    for point in cities:
        pygame.draw.rect(window, WHITE, [point.pos.x, point.pos.y, POINTSIZE, POINTSIZE])

def draw_best_path(population, window):
    clear_window(window)

    list_points = []
    best_genes_list = population[0].genes
    for gene in best_genes_list:
        list_points.append(cities[gene].pos)

    list_points.append(cities[best_genes_list[0]].pos)
    pygame.draw.lines(window, WHITE, False, list_points, 1)
    pygame.display.update()


def display(cities_list = None, maxtime = DEFAULTMAXTIME, gui = True, window = None):
    LEFTCLICK = 1                     # Défini ainsi dans pygame
    global starting_time

    pygame.init()
    pygame.display.set_caption('Problème du voyageur commercial')
    font = pygame.font.Font(None, 30)
    text = font.render("Temps : " + str(maxtime) +  "secondes. Pressez enter pour lancer", True, WHITE)
    textRect = text.get_rect()
    window.blit(text, textRect)
    cost = -1
    best_path = []
    max_time_relauch = maxtime

    if cities_list == None:
        cities_list = []
    else:
        for point in cities_list:
            pygame.draw.rect(window, WHITE, [point.pos.x, point.pos.y, POINTSIZE, POINTSIZE])

    continued = True

    while continued:
        mouse_xy = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # On est obligé de faire en deux lignes car les événements parcourus peuvent retourner false.
            # On gère la fermeture via ESCAPE ou via la croix de la fenêtre
            if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == QUIT):
                continued = False
                return cost, best_path

            if (event.type == KEYDOWN and event.key == K_RETURN):
                starting_time = time()
                cost, best_path = solve(cities_list, window, max_time_relauch, gui)

            # Gestion des événements souris
            if event.type == MOUSEBUTTONDOWN and event.button == LEFTCLICK:
                x_mouse, y_mouse = event.pos[0], event.pos[1]
                # Attention : envoie une liste de tuples! La synthaxe est fine.
                cities_list.append(City(pos=(x_mouse, y_mouse)))
                pygame.draw.rect(window, WHITE, (x_mouse, y_mouse, POINTSIZE, POINTSIZE))

        pygame.display.update()


################################################################################
#  Classes
################################################################################

class City(object):
    """Représente une ville possible, avec un identifiant (à voir si il reste),
       un nom inutile, et une position. Les infos inutiles pourraient devenir
       utiles à l'avenir.
    """
    # On ne garde qu'une liste d'indexes pour les gênes afin de ne pas dupliquer l'information
    last_id = 0

    #Pour pos, passer un tuple (x,y)
    def __init__(self, pos, name = None):
        self.id = City.last_id
        self.name = name
        self.pos = Vector2(pos)
        City.last_id = City.last_id + 1

    def __repr__(self):
        return "[id:" + str(self.id) + " name : "+ self.name + " X:" + str(self.pos[0]) + " Y:" + str(self.pos[1]) + "]"

class Chromosome(object):
    """ représentation d'un individu sous la forme d'un chemin (suite de villes)
    et d'un coût"""

    def __init__(self, genes=None):
        self.genes = genes
        self.cost = 0
        if not self.genes == None:
            self.cost = self.calculate_cost()

    def mutate(self):
        """Mutation du chromosome simple en inversant deux indexes au hasard.
           On ne garde la mutation que si elle est meilleure. Il se trouve
           que l'on pourrait imaginer qu'inverser deux villes connexes pourrait
           améliorer le résultat mais ca ne semble pas être le cas."""
        new_genes_list = list(self.genes)

        # for _ in range(0,1):
        #     index1 = random.randrange(0, len(self.genes))
        #     index2 =  random.randrange(0, len(self.genes))
        #
        #     new_genes_list[index2], new_genes_list[index1] = new_genes_list[index1], new_genes_list[index2]

        for _ in range(0,2):
            start_index = random.randrange(0, len(self.genes))
            end_index = random.randrange(0, len(self.genes))

            if end_index < start_index:
                start_index, end_index = end_index, start_index

            part_to_reverse = new_genes_list[start_index:end_index]
            part_to_reverse.reverse()

            new_genes_list[start_index:end_index] = part_to_reverse

        return Chromosome(new_genes_list)

    def calculate_cost(self):
        nb_genes = len(self.genes)
        distance = 0

        c = cycle(self.genes)
        next(c)

        for index1, index2 in zip(self.genes, c):
            villeA = cities[index1]
            villeB = cities[index2]

            dx = abs(villeA.pos.x - villeB.pos.x)
            dy = abs(villeA.pos.y - villeB.pos.y)

            # distance += hypot(dx,dy)

            distance += villeA.pos.distance_to(villeB.pos)
            # distance += sqrt(dx**2 + dy**2)
        return distance

    def __repr__(self):
        return '[%s]' % ', '.join(map(str, self.genes)) + "] : Cost : " + str(self.cost)


################################################################################
#  Fin Classes
################################################################################


if __name__ == '__main__':
    main(sys.argv[1:])
