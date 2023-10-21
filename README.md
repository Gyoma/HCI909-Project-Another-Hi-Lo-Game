# HCI909 Project - Another Hi-Lo Game

This game is based on Hi-Lo game, where only ranks of cards matter. If you have the higher rank, then you win.

- It's a game, where each player has a deck of 52 cards, and the goal is to beat the opponent by playing cards with higher rank.

- The game lasts 15 rounds and is played with 2 players. At each round both players select 3 unique cards, specifying an order. Then, the rank of each card is compared to the opponent’s corresponding card. At the end of the round these cards discards.

- The player with the higher rank gets a point. If the ranks are equal, no player gets a point. The player with more points at the end of a round wins.

- The winner is a player who won more rounds.

## Authors

Artem Golovin and Bezkhodarnov Nikolay

## How to run the game

Launch the game by running the following command in the project root directory:

``` python main.py ```

## Advanced interaction techniques

- To play the game, you need to prepare real card deck, because the game is played with real cards. The game is controlled by a camera, which is used to detect the cards and their order.
- The game is played with 2 players by a network connection. The players can be in different locations.
- The game can be controlled by user voice commands. The commands are used to start the game, end the game, and to play cards.

## How to configure the game

After launching the game, go to settings and choose the camera and the microphone you want to use. Then, you can start the game.
