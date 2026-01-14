import heapq
import copy 
import database as db

class Leaderboard:
    """
    Docstring: This class represents a leaderboard that tracks and manages scores
    for players in a game or competition.
    """

    def __init__(self, name, k = None):
        """
        The constructor method initializes the Leaderboard instance with a name and top entries.
        """
        self.name = name 
        self.lb = []  # Heap to store leaderboard entries
        # Need to store scores as negative to make it a max heap
        
        #Set the podium player count/top leaderboard entries (e.g., top 3,5,10 players in a leaderboard)
        if k is None: 
            self.k = 3 
        else: self.k = k


    def add_player(self, player_name, score = None):
        if score is None:
            self.lb.append((0, player_name))
        else:
            heapq.heappush(self.lb, (-score, player_name))
        
    def remove_player(self, player_name):
        index = 0
        for name, score in self.lb:
            if name == player_name:
                break
            index += 1
            
        self.lb[index] = self.lb[-1]
        self.lb.pop()
        heapq.heapify(self.lb)
    
    def increase_points(self, player_name, points):
        index = 0
        new_score = points
        for name, old_score in self.lb:
            if name == player_name:
                 new_score += abs(old_score)
                 break
            index +=1 
            
        self.lb[index] = (-1 * new_score, player_name)
        
        heapq.heapify(self.lb)
        
    def decrease_points(self, player_name, points_removing):
        index = 0
        new_score = 0
        for name, old_score in self.lb:
            if name == player_name:
                 new_score += abs(old_score) - points_removing
                 if new_score < 0:
                     new_score = 0
                 break
            index +=1 
            
        self.lb[index] = (-1 * new_score, player_name)
        
        heapq.heapify(self.lb)
        
    def reset_player(self, player_name):
        index = 0
    
        for name, old_score in self.lb:
            if name == player_name:
                 break
            index +=1 
            
        self.lb[index] = (0, player_name)
        
        heapq.heapify(self.lb)
        
    def reset_all_players(self):
        index = 0
        for player_name, score in range(len(self.lb)):
            self.lb[index] = (0, player_name)
            index += 0
    
    def change_k(self, k):
        if k < 3 or k != 3 or k != 5 or k!= 7:
            return
        else:
            self.k = k
            
    def get_list_of_players_ordered(self):
        return copy.deepcopy(self.lb)
    
    def get_name(self):
        return self.name
    
    def load_heap(self, scores):
        for discord_tag, points in scores:
            self.add_player(discord_tag, points)
