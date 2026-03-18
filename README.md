# Émulateur CHIP-8

Un petit émulateur CHIP-8 écrit en Python.

![demo](images/opcodes.gif)

## Présentation

Ce projet permet de charger et d’exécuter une ROM CHIP-8.
Il inclut les principales fonctionnalités nécessaires :

- lecture et exécution des opcodes
- gestion des registres et de la mémoire
- affichage de l’écran
- gestion des timers
- lecture des entrées clavier

## Installation

Créer un environnement virtuel puis installer les dépendances :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Structure du projet

- `chip8.py` : logique principale de l’émulateur
- `frontend.py` : affichage dans le terminal
- `inputs.py` : gestion des touches
- `main.py` : lancement du programme

## But du projet

Ce projet a été réalisé dans un but d’apprentissage, afin de mieux comprendre :

- l’architecture CHIP-8
- le fonctionnement d’un émulateur
- la gestion des instructions, de la mémoire et de l’affichage

## Limites

Cet émulateur reste un projet simple et peut encore être amélioré.
