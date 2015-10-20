#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("delete from matches")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("delete from players")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("select count(id) from players")
    num = cur.fetchone()
    conn.close()
    return num[0]

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("insert into players (name, score) values (%s, %s)", (name,0,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT players.id, name, score, score+count(loser_id) FROM players left join matches on players.id = matches.loser_id group by players.id order by score desc")
    game_result = cur.fetchall()
    conn.close()
    # build a dictionary that stores the id and its win score
    score_dic = {tup[0]: tup[2] for tup in game_result}
    # go through the result list, check if a sub-list has the same score for all players in that sub-list. If so, calculate their OMW and sort the sub-list based on OMW
    match_dic = getMatchDic()
    start_index = 0
    end_index = 1
    while(start_index < len(game_result)):
        while(end_index < len(game_result) and game_result[start_index][2] == game_result[end_index][2]):
            end_index += 1
        if((end_index - start_index) > 1):
            sort_omw(start_index, end_index, game_result, match_dic, score_dic)
        start_index = end_index
        end_index = end_index + 1
    return game_result

def sort_omw(lo_index, hi_index, arr, match_dic, score_dic):
    """sort the arr(id, name, wins, matches) from index lo(included) to index hi(not included) according to wins, descendingly
    Returns:
        a partially sorted arr(from lo to hi)
    """
    temp_arr = arr[lo_index: hi_index]
    for i in range(len(temp_arr)):
        cur = temp_arr[i]
        cur_id = cur[0]
        cur_opponents = match_dic[cur_id]
        cur_omw = 0
        for oppo in cur_opponents:
            cur_omw += score_dic[oppo]
        temp_arr[i] = cur + (cur_omw,)
    temp_arr = sorted(temp_arr,key=lambda tup: tup[4],reverse=True)
    arr[lo_index: hi_index] = [tup[0:4] for tup in temp_arr]

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO matches (winner_id, loser_id) VALUES (%s , %s)", (winner, loser,))
    cur.execute("UPDATE players SET score = score + 1 where id = (%s)", (winner,))
    conn.commit()
    conn.close()

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # fetch all match result
    match_dic = getMatchDic()
    rank = playerStandings()
    # use a DFS to get the possible pair combinations, then select one
    total = len(rank)
    pairPath = []
    pairList = []
    pair_dfs(rank, match_dic, pairPath, pairList)
    return pairList[0]

def pair_dfs(rank, match_dic, pairPath, pairList):
    """Returns a list of possible pairing results based on rank and match_dic

    Args:
        1, rank: the player list sorted by win score and omw, descendingly
        2, match_dic: a dictionary that stores the player id and its opponents's id list
        3, pairPath: a list stores current pairing result
        4, pairList: a list stores all pairPath
    """
    if(len(rank) < 2):
        pairList.append(pairPath[:])
        return
    firstPlayer = rank.pop(0)
    for i in range(len(rank)):
        secondPlayer = rank[i]
        newRank = rank[:]
        newRank.remove(secondPlayer)
        if(((firstPlayer[2] - secondPlayer[2]) <= 1) and canPair(firstPlayer[0], secondPlayer[0], match_dic)):
            pair = (firstPlayer[0], firstPlayer[1], secondPlayer[0], secondPlayer[1])
            pairPath.append(pair)
            pair_dfs(newRank, match_dic, pairPath, pairList)
            pairPath.pop(len(pairPath) - 1)

def getMatchDic():
    """Returns a dictionary that stores player id and that player's list of opponents

    Returns: a dictionary
        key: player id
        value: a list of player #id's opponents
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT winner_id, loser_id FROM matches;")
    match_results = cur.fetchall()
    cur.execute("SELECT id FROM players;")
    players_list = cur.fetchall()
    # build a dictionary to track the opponents of each player
    match_dic = {id[0]: [] for id in players_list}
    for row in match_results:
        match_dic[row[0]].append(row[1])
        match_dic[row[1]].append(row[0])
    return match_dic

def swap(index1, index2, arr):
    """Swap two tuples in an array

    Args:
        index1: the first player's index in playerStandings array
        index2: the second player's index in playerStandings array
    """
    temp = arr[index1]
    arr[index1] = arr[index2]
    arr[index2] = temp

def canPair(id1, id2, match_dic):
    """Determine if player id1 has been paired with player id2 before

    Args:
        id1: the first player to be paired
        id2: the second player to be paired

    Returns:
        true: if id1 and id2 haven't played with each other
        false: if id1 and id2 have played with each other
    """
    opponents_list = match_dic[id1]
    for opponent in opponents_list:
        if(opponent == id2):
            return False
    return True