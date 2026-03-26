# clavier-accoredon-midi
clavier accordeon midi pour controler un nanobass 

après avoir récupéré la partie main gauche d'un viel orgue accordeon, j'ai pu le recycler grace à un peu de bois, un Raspberry pi pico et un ads1115.

(je ne suis pas un programmeur)
code simple qui :

- scanne la grille des boutons, 6 lignes et 4 colonnes pour un totale de 24 touches
- envoie un message midi din a chaque pression d'un bouton (basses et accords)
- 5 potentiometres qui envoient en midi din pitchwheel, Modwheel, et des parametres propres au nanobass
- 3 boutons un pour les basses (basse / basse + octave / octave + autre ocatve), le même pour les accords et un dernier pour choisir le canal midi : 1, 1+2, 2
- le midi passe dans un buffer pour convertir le 3.3v en 5v

à faire mais pas cette fois ci : ajouter un gate in pour synchrioniser avec le synthé modulaire

    
librairies :

https://github.com/robert-hh/ads1x15

https://github.com/sensai7/Micropython-midi-library
