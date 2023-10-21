# HCI909 Project - Another Hi-Lo Game

This game is based on Hi-Lo game, where only ranks of cards matter. If you have the higher rank, then you win.

- It's a game, where each player has a deck of 52 cards, and the goal is to beat the opponent by playing cards with higher rank.

- The game lasts 15 rounds and is played with 2 players. At each round both players select 3 unique cards, specifying an order. Then, the rank of each card is compared to the opponent’s corresponding card. At the end of the round these cards discards.

- The player with the higher rank gets a point. If the ranks are equal, no player gets a point. The player with more points at the end of a round wins.

- The winner is a player who won more rounds.

## Authors

Artem Golovin and Nikolay Bezkhodarnov

## Game rules
This game is based on the Hi-Lo game rules, where only ranks of cards matter. If you have the higher rank, then you win.

- The game requires 2 players and french playing cards (V for Jack, D for Queen, R for King, 1 for Ace)
- Each player has a deck of 52 cards (without Jokers), and the goal is to beat the opponent by playing cards with higher rank.
- The game lasts 15 rounds. At each round both players select 3 unique cards, specifying an order. Then, the rank of each card is compared to the opponent’s corresponding card.
- The player with the higher rank gets a point. If the ranks are equal, no player gets a point. The player with more points at the end of a round wins it.
- The winner of the game is a player who won more rounds.
- You can use a unique card just once during the whole game match, so after the current round, cards become unavailable for selection in subsequent rounds

## Advanced interaction techniques

- To play the game, you need to prepare a real (physical) french card deck, because the game is played with real cards. The card loading is controlled by a camera, which is used to detect, identify the cards and their order, so you need to choose a plain monochrome surface you are going to place your cards on.  Make sure you adjusted your camera well so that all cards fit into the picture and there are no problems with surrounding light, etc.
- The game is played with 2 players by a network connection. The players can be in different locations.
- The game can be controlled by user voice commands. The commands are used to control the game flow, but all the manipulations in menus preceding the game are controlled by mouse.


## How to run the game

First, install all requirements. You might need to install python v3.11. Launch the game by running the following command in the project root directory:

``` python main.py ```

For more details check our report.
