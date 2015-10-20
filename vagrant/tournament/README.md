## Requirements
1. latest Python 2.*
2. vagrant vm correctly installed

## Quick Start:
1. Clone the repository
2. Launch the Vagrant VM, ssh into the VM
3. Run the `tournament_test.py` in the VM

## Basic Functionality

##### `registerPlayer(name)`: 
* Adds one player to the tournament db.

##### `countPlayers()`: 
* Returns the number of registered players. 

##### `deletePlayers()`: 
* Delete all the player records from the db.

##### `reportMatch(winner, loser)`: 
* Stores the result of a single match between two players in the db.

##### `deleteMatches()`: 
* Clear out all the match records from the db.

##### `playerStandings()`: 
* Returns a list of (id, name, wins, matches) for each player, sorted by the number of wins of each player in descending order.

##### `swissPairings()`: 
* Given the currently registered players and the matches result they have played, returns a list of pairings according to the Swiss system. Each pairing is a tuple (id1, name1, id2, name2).

## Enhancements
1. Implements OMW(Opponent Match Wins) to help sort the players When two players have the same number of wins, rank them according to OMW, the total number of wins by players they have played against. 
2. Prevent rematches between players when doing swiss pairing.

## Comments

The test case for enhancements 1 and 2 are not listed since it’s a little bit tricky to write test case for them. Usually, when I test them, I follow the steps below:

1. create 6 players, register them using the `registerPlayer()` function
2. use `swissPairings()` to get the pair and use `reportMatch(winner, loser)` to assign match results randomly
3. use `playerStandings()` to get the rank of all players, check if it’s correct based on previous steps
4. repeat step 2,3 check if the results are the same as you compute them manually
5. use `swissPairings()` to get the pair, now check if the new pairing avoids rematch

Usually when you assign different match results several times, you could notice that both enhancements 1 and 2 are in effect and give the correct pairing and player standing