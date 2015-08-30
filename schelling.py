import random
from collections import Counter

directions = [[1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1]]
empty = 'empty'

def flatten_list(ls):
    l = []
    for el in ls:
        if isinstance(el, list):
            [l.append(e) for e in flatten_list(el)]
        else:
            l.append(el)
    return l

def build_uid(col, row):
    return 'col'+str(col)+'row'+str(row)


class Actor:
    def __init__(self, label=empty, preference=0., dif_phob=0.5, d_weight=0):
        self.label = label
        self.preference = preference
        self.dif_phob = 1 - dif_phob
        self.d_weight = d_weight
        self.col = None
        self.row = None
        self.neighbors = Counter()
        self.empty_tiles = []

    def set_position(self, col, row):
        self.col = col
        self.row = row

    def get_uid(self):
        return build_uid(self.col, self.row)

    def is_empty(self):
        return True if self.label == empty else False

    def add_neigbour(self, neighbour):
        self.neighbors.update([neighbour])

    def add_empty_tile(self, tile):
        self.empty_tiles.append(tile)

    def clear_neighbors(self):
        self.neighbors = Counter()
        self.empty_tiles = []

    def get_different_neighbors(self):
        total = 0
        for n in self.neighbors:
            if n != self.label and n != empty:
                total += self.neighbors[n]
        return total

    def wants_to_move(self):
        no_of_neighbours = sum(self.neighbors.values()) + len(self.empty_tiles)
        percentage_similar = self.get_similar()/float(no_of_neighbours)
        percentage_different = self.get_different_neighbors()/float(no_of_neighbours)
        print percentage_different
        if (percentage_similar <= self.preference or
            percentage_different >= self.dif_phob):
            print 'yes'
            return True
        else:
            return False

    @staticmethod
    def can_occupy_tile(tile):
        if tile:
            if tile.is_empty():
                can_occupy = True
            else:
                can_occupy = False
        else:
            can_occupy = True
        return can_occupy

    def can_move_to(self, taken_spots):
        chosen_tile = None
        if len(self.empty_tiles) == 0:
            return chosen_tile
        random.shuffle(self.empty_tiles)
        for tile in self.empty_tiles:
            spot = taken_spots.get(tile.get_uid(), None)
            can_occupy = self.can_occupy_tile(spot)
            if (tile.get_similar(self.label)-1 > self.get_similar() and can_occupy):
                if (chosen_tile and chosen_tile.get_similar(self.label)-1 <
                    tile.get_similar(self.label)-1):
                    chosen_tile = tile
                else:
                    chosen_tile = tile
        return chosen_tile

    def get_similar(self, l=None):
        return self.neighbors.get(l if l else self.label, 0)


class World(object):
    def __init__(self, cols, rows, actors):
        self.cols = cols
        self.rows = rows
        self.actors_bucket = flatten_list([[actor] * actor.d_weight for actor in actors])
        self.actors = actors
        self.tilemap = {}
        for row in range(rows):
            for col in range(cols):
                uid = build_uid(col, row)
                actor_type = random.choice(self.actors_bucket)
                actor = Actor(actor_type.label, actor_type.preference)
                actor.set_position(col, row)
                self.tilemap[uid] = actor
        self.update_tiles()

    def run_iteration(self):
        self.random_process_movement()
        self.update_tiles()

    def update_tiles(self):
        for actor in self.tilemap.values():
            self.count_neighbours(actor)

    def random_process_movement(self):
        temp_map = {}
        while len(self.tilemap) > 0:
            actor = self.tilemap.pop(random.choice(self.tilemap.keys()))
            if actor.is_empty():
                uid = actor.get_uid()
                spot = temp_map.get(uid, None)
                can_occupy = actor.can_occupy_tile(spot)
                if can_occupy:
                    temp_map[uid] = self.get_empty_tile(actor)
                continue
            if actor.wants_to_move():
                to_tile = actor.can_move_to(temp_map)
                if to_tile:
                    new_actor, new_uid = self.get_new_tile(actor, to_tile)
                    old_uid = build_uid(actor.col, actor.row)
                    temp_map[old_uid] = self.get_empty_tile(actor)
                else:
                    new_actor, new_uid = self.get_new_tile(actor, actor)
                temp_map[new_uid] = new_actor
            else:
                new_actor, new_uid = self.get_new_tile(actor, actor)
                temp_map[new_uid] = new_actor
        self.tilemap = temp_map

    def get_empty_tile(self, actor):
        empty_tile = Actor()
        empty_tile.set_position(actor.col, actor.row)
        return empty_tile

    def get_new_tile(self, old_actor, to_tile):
        new_actor = Actor(old_actor.label, old_actor.preference, old_actor.dif_phob)
        new_actor.set_position(to_tile.col, to_tile.row)
        new_uid = new_actor.get_uid()
        return new_actor, new_uid

    def count_neighbours(self, actor):
        actor.clear_neighbors()
        for direction in directions:
            uid = build_uid(actor.col+direction[0], actor.row+direction[1])
            n = self.tilemap.get(uid, None)
            if n and n.label != empty:
                actor.add_neigbour(n.label)
            if n and n.label == empty:
                actor.add_empty_tile(n)
