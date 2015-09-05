import random
import operator
import copy
from collections import Counter

class Env(object):
    directions = [[1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1]]
    empty = 'empty'

    @classmethod
    def flatten_list(cls, ls):
        l = []
        for el in ls:
            if isinstance(el, list):
                [l.append(e) for e in Env.flatten_list(el)]
            else:
                l.append(el)
        return l

    @classmethod
    def build_uid(cls, col, row):
        return 'col'+str(col)+'row'+str(row)

    @classmethod
    def get_uid_by_direction(cls, tile, direction):
        return cls.build_uid(tile.col + direction[0], tile.row + direction[1])

    @classmethod
    def can_occupy_tile(cls, tile):
        if tile:
            if tile.is_empty():
                can_occupy = True
            else:
                can_occupy = False
        else:
            can_occupy = True
        return can_occupy


class Tile:
    def __init__(self, label=Env.empty, preference=0., dif_phob=0.5, d_weight=0):
        self.label = label
        self.preference = preference
        self.dif_phob = 1 - dif_phob
        self.d_weight = d_weight
        self.col = None
        self.row = None
        self.neighbors = Counter()

    def set_position(self, col, row):
        self.col = col
        self.row = row

    def get_uid(self):
        return Env.build_uid(self.col, self.row)

    def is_empty(self):
        return True if self.label == Env.empty else False

    def add_neighbour(self, neighbour):
        self.neighbors.update([neighbour.label])

    def clear_neighbors(self):
        self.neighbors = Counter()

    def wants_to_move(self):
        if self.is_empty():
            return None
        no_of_neighbours = sum(self.neighbors.values())
        percentage_similar = self.get_similar_to()/float(no_of_neighbours)
        percentage_different = self.get_different_to()/float(no_of_neighbours)
        if (percentage_similar <= self.preference or
            percentage_different >= self.dif_phob):
            return True
        else:
            return False

    def can_move_to(self, taken_spots):
        chosen_tile = None
        neighbors = {}
        for direction in Env.directions:
            t_uid = Env.get_uid_by_direction(self, direction)
            tile = taken_spots.get(t_uid, None)
            if tile and tile.is_empty():
                neighbors[tile] = ((tile.get_similar_to(self.label) - 1) +
                                   (len(Env.directions) -
                                    tile.get_different_to(self.label)))
        try:
            max_tile = max(neighbors.iteritems(), key=operator.itemgetter(1))[0]
            if neighbors[max_tile] > (self.get_similar_to() +
                                      (len(Env.directions) -
                                       self.get_different_to())):
                chosen_tile = max_tile
        except ValueError:
            pass
        return chosen_tile

    def get_different_to(self, label=None):
        total = 0
        label = self.label if not label else label
        for n in self.neighbors:
            if n != label and n != Env.empty:
                total += self.neighbors[n]
        return total

    def get_similar_to(self, l=None):
        return self.neighbors.get(l if l else self.label, 0)


class World(object):
    def __init__(self, cols, rows, tiles):
        self.cols = cols
        self.rows = rows
        self.tiles_bucket = Env.flatten_list([[tile] * tile.d_weight for tile in tiles])
        self.tiles = tiles
        self.tilemap = {}
        for row in range(rows):
            for col in range(cols):
                uid = Env.build_uid(col, row)
                tile_type = random.choice(self.tiles_bucket)
                tile = Tile(tile_type.label, tile_type.preference)
                tile.set_position(col, row)
                self.tilemap[uid] = tile
        self.update_tiles()

    def run_iteration(self):
        self.random_process_movement()
        self.update_tiles()

    def update_tiles(self):
        for tile in self.tilemap.values():
            self.update_negibors(tile)

    def random_process_movement(self):
        temp_map = copy.deepcopy(self.tilemap)
        while len(self.tilemap) > 0:
            tile = self.tilemap.pop(random.choice(self.tilemap.keys()))
            if tile.is_empty():
                continue
            if tile.wants_to_move():
                to_tile = tile.can_move_to(temp_map)
                if to_tile:
                    new_tile, new_uid = self.get_new_tile(tile, to_tile)
                    old_uid = tile.get_uid()
                    temp_map[old_uid] = self.get_empty_tile(tile)
                else:
                    new_tile, new_uid = self.get_new_tile(tile, tile)
                temp_map[new_uid] = new_tile
            else:
                new_tile, new_uid = self.get_new_tile(tile, tile)
                temp_map[new_uid] = new_tile
        self.tilemap = temp_map

    def get_empty_tile(self, tile):
        empty_tile = Tile()
        empty_tile.set_position(tile.col, tile.row)
        return empty_tile

    def get_new_tile(self, old_tile, to_tile):
        new_tile = Tile(old_tile.label, old_tile.preference, old_tile.dif_phob)
        new_tile.set_position(to_tile.col, to_tile.row)
        new_uid = new_tile.get_uid()
        return new_tile, new_uid

    def update_negibors(self, tile):
        tile.clear_neighbors()
        for direction in Env.directions:
            uid = Env.get_uid_by_direction(tile, direction)
            n = self.tilemap.get(uid, None)
            if n:
                tile.add_neighbour(n)

    def show_world(self):
        for row in range(self.rows):
            for col in range(self.cols):
                uid = Env.build_uid(col, row)
                t = self.tilemap[uid]
                print(t.label),
            print()



"""
# usage
# create a base tile for each type, also add the empty tile
# d_weight represents the proportion of a specific tile type during map init

a1 = Tile(label='red', preference=0.5, dif_phob=0., d_weight=2)
a2 = Tile(label='blue', preference=0.5, dif_phob=0., d_weight=2)
e = Tile(label=Env.empty, d_weight=1)
base_tiles = [a2, a1, e]

w = World(7, 7, base_tiles)
w.show_world()
w.run_iteration()
print '+' * 60
w.show_world()
w.run_iteration()
print '+' * 60
w.show_world()
"""
