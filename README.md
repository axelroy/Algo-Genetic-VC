# Algo-Genetic-VC

Implementation of genetic algorithm for the problem of the commercial traveler in Python.

Auteurs                      : Arnaud Droxler & Axel Roy
Date dernière modification   : 15 Janvier 2017
But                          : Implémentation d'un algorithme génétique pour résoudre
                               le problème du voyageur de commerce

Informations à propos des choix pour l'algorithme génétique

# Orientation globale de l'algorithme

L'algorithme génétique utilise les trois phases habituelles d'un algorithme génétique,
soit la sélection, le croisement puis les mutations.

De manière générale, il y a deux aspects que l'on peut rechercher de l'algorithme :
* La vitesse de convergence
* La robustesse et la constance des résultats (ne pas bloquer sur un minimum local)

Nous avons volontairement donné la priorité à la résistance de l'algorithme en
implémentant des méthodes qui génèrent beaucoup de bruit sur les gênes des chromosomes
de la population.

#                                     Population

Aucune méthode gourmande n'a été utilisée pour essayer de générer une solution bonne
dès le départ. On aurait par exemple pu essayer de partir d'un point et de chercher
toujours la ville la plus proche.

Nous avons préféré opter pour une génération de la population totalement aléatoire.

# Selection

Nous avons choisi de privilégier une selection élitiste, très simple et très rapide
implémentée par une simple list comprehension.

# Croisements

Nous avons utilisé un croisement en deux points, avec réarrangement via la
méthode du croisement ox. Cette méthode est relativement gourmande, mais génère des
résultats très pertinents.

Un soin tout particulier a été accordé à l'algorithme, en partant des explications
de la documentation fournie avec ce travail pratique, en décorticant les étapes et
en trouvant une méthode d'implémentation rapide via des rotations. Elle est
précisément décrite dans la méthode ox_cross.

# Mutations

Pour les mutations, on selectionne au hasard des chromosome qui vont générer
une mutation. Le chromosome selectionné n'est jamais remplacé, on génère un nouveau
chromosome, sans se soucier de son efficacité. C'est la prochaine phase de selection
qui va le garder ou non.

# Tests

Le programme a été fait pour que les paramètres pour l'algorithme soient facilement
modifiables. Des tests ont été effectués pour paramétrer au mieux ces facteurs, en
lancant n fois l'expérience et en récupérant les résultats moyens.

Il en sort qu'il n'est pas utile d'utiliser de grandes populations pour aboutir à
de bons résultats, cela a plutôt tendance à faire baisser les performances.

Etant donné l'implémentation des mutations (qui retournent un nouveau chromosome),
il est utile de mettre un taux de mutation plus élevé que les 30% que l'on retrouve
dans la documentation scientifique du domaine.

Les paramètres ne sont pas encore totalement optimisés par manque de temps.

L'utilisation en tant que module a été testée avec le PVC-tester-3.5, et il n'a
pas fourni d'erreur. On pourrait tenter de réduire la constante TIMELIMIT qui fixe
le temps qu'il faut laisser pour l'aggrégation des résultat et le retour des
méthodes, mais on risque de fournir des timeout pour le testeur.

# Conclusions

Globalement, on peut constater que les choix effectués dans les méthodes de selection,
croisements et mutations permettent d'explorer largement le domaine des solutions,
mais que les performances en terme de convergence sont affectés. Ceci est volontaire,
et les résultats pour un nombre de villes conséquents avec un temps court fourni des
résultats tout de même très satisfaisants.

On peut voir en mode graphique qu'en laissant suffisamment de temps, on arrive rarement
à une solution qui présente des croisements de routes, l'algorithme réussi à démeler
fortement les noeuds.

Nous avons implémenté une augmentation du nombre de mutations en fin de temps à disposition
pour faire en sorte qu'il ne reste pas bloqué dans un minimum local, et il est visuellement
possible d'observer qu'il arrive que cela permet de sortir d'un minimum local.

En effet, il n'est pas rare que l'algorithme parte d'un chemin sans croisements
et trouve un nouveau chemin très différent, qui comporte des croisements de chemins,
le fait muter et le dénoue.

Les avantages de cette implémentation sont les suivants :

* Etant donné que l'on repose entièrement sur l'aléatoire, on ne dirige pas
  les résultats dans un minimum local.
* L'algorithme a la capacité de sortir des minimums locaux.
* Il est robuste et optimisé pour les phases critiques qui demandent beaucoup
  de calculs

Les inconvénients sont les suivants :

* Il pourrait converger plus rapidement vers une solution acceptable.
* Il n'implémente pas de notion de convergence de manière très poussée pour stopper la recherche.

  Il est possible de le faire facilement en comparant à chaque boucle l'ancien
  meilleur résultat avec le nouveau, et de faire en sorte que si c'est le cas
  x fois, on stop la recherche.

  L'idéal serait de comparer la distance moyenne entre les échantillons de
  la population, et de faire en sorte que si il sont tous très semblables on
  peut dire qu'il n'est pas utile de faire plus.

  La deuxième est beaucoup plus intéressant mais allourdi énormément la boucle
  principale de l'algorithme.

# Améliorations et perspectives

L'algorithme peut être amélioré pour ce qui est de la vitesse de convergence,
ceci en générant une population plus dirigée, puis en changeant la selection
élitiste par une autre méthode (la méthode par tournoi semble une bonne option).

On pourrait imaginer lancer plusieurs expériences en parralèlle et récupérer
le meilleur résultat parmis celles-ci.

En terme de programmation, l'utilisation d'une heapq semble être une bonne
option, mais il faut vérifier qu'elle apporte vraiment plus qu'elle ne coûte,
car les tris sont effectués à un seul moment actuellement, tandis qu'une heapq
trie à chaque ajout/suppression.

Un profilage montre que l'estimation du coût, le tri des listes et le croisement
sont les sections critiques de l'algorithme.

Il serait intéressant de proposer des mutations qui résultent en plus de désordre,
par exemple en mêlant l'inversion d'une portion aléatoire, et y ajouter n échanges
aléatoires de villes.
