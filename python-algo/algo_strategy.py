import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.pastHP = 9999
        self.minPing = 9
        self.minEMP = 3
        self.lastSentPing = False
        self.lastSentEMP = False
        self.sidesAttacked = {}
        self.sidesAttacked["right"] = 0.
        self.sidesAttacked["mid"] = 0.
        self.sidesAttacked["left"] = 0.
        self.destructor_locations = [[3,13],[24,13],[10,13],[17,13]]

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
        if game_state.turn_number > 0:
            #self.find_side_attacked(game_state, True)
            for idx in range(len(self.destructor_locations)):
                if game_state.can_spawn(DESTRUCTOR, [self.destructor_locations[idx][0], self.destructor_locations[idx][1]-1]) and not game_state.contains_stationary_unit(self.destructor_locations[idx]):
                    self.destructor_locations.append([self.destructor_locations[idx][0], self.destructor_locations[idx][1]-1])
                elif game_state.can_spawn(DESTRUCTOR, [self.destructor_locations[idx][0]+1, self.destructor_locations[idx][1]]) and not game_state.contains_stationary_unit(self.destructor_locations[idx]):
                    self.destructor_locations.append([self.destructor_locations[idx][0]+1, self.destructor_locations[idx][1]])
                elif game_state.can_spawn(DESTRUCTOR, [self.destructor_locations[idx][0]-1, self.destructor_locations[idx][1]]) and not game_state.contains_stationary_unit(self.destructor_locations[idx]):
                    self.destructor_locations.append([self.destructor_locations[idx][0]-1, self.destructor_locations[idx][1]])
        #gamelib.debug_write('sides: {}'.format(self.sidesAttacked))
        self.DenizStrat(game_state)
        #self.find_side_attacked(game_state, False)
        #gamelib.debug_write('sides_after: {}'.format(self.sidesAttacked))
        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def DenizStrat(self, game_state):
        self.defense_v2(game_state)
        self.attack_v2(game_state)

    def better_spawn_location(self, game_state, location_coordinates):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_coordinates:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_coordinates[damages.index(min(damages))]
    def old_defense(self, game_state):
        main_destructor = [[2,11], [3,13], [6,13], [9,13], [12,13], [15,13], [18,13], [21,13], [24,13], [25,11], [11,11], [16,11]]
        game_state.attempt_spawn(DESTRUCTOR, main_destructor)

    def find_side_attacked(self, game_state, start):
        left_c = [[1,13], [5,12], [9,12]]
        mid_c = [[12,12], [13,12], [14,12], [15,12]]
        right_c = [[26,13], [22,12], [18,12]]
        if start:
            for coor in left_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["left"] += 1
            for coor in midleft_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["midleft"] += 1
            for coor in midright_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["midright"] += 1
            for coor in right_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["right"] += 1
        else:
            for coor in left_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["left"] = self.sidesAttacked["left"] - 1
            for coor in mid_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["mid"] = self.sidesAttacked["mid"] -1
            for coor in right_c:
                if not game_state.contains_stationary_unit(coor):
                    self.sidesAttacked["right"] = self.sidesAttacked["right"] - 1
        pass

    def defense_v2(self, game_state):
        #destructor_locations2 = [[1,13],[2,13],[4,12],[5,12],[7,12],[8,12],[10,12],[11,12],[13,12],[14,12],[16,12],[17,12],[19,12],[20,12],[22,12],[23,12],[25,13],[26,13],[0,13],[27,13],[26,12],[1,12]]
        #destructor_locations = [[1,13],[26,13],[5,12],[22,12],[9,12],[18,12]]
        #filter_locations = [[12,13],[15,13],[13,13],[14,13],[0,13],[27,13],[8,13],[19,13],[7,13],[20,13],[6,13],[21,13],[5,13],[22,13],[1,13],[26,13],[0,13],[27,13]]
        game_state.attempt_spawn(DESTRUCTOR, self.destructor_locations)
        #game_state.attempt_spawn(FILTER, filter_locations)
#        if self.sidesAttacked["left"] >= 0.9 and self.sidesAttacked["left"] >= self.sidesAttacked["mid"] and self.sidesAttacked["left"] >= self.sidesAttacked["right"]:
#            game_state.attempt_spawn(SCRAMBLER, [4,9])
#        if self.sidesAttacked["right"] >= 0.9 and self.sidesAttacked["right"] >= self.sidesAttacked["mid"] and self.sidesAttacked["right"] >= self.sidesAttacked["left"]:
#            game_state.attempt_spawn(SCRAMBLER, [23,9])
#        if self.sidesAttacked["mid"] >= 0.9 and self.sidesAttacked["left"] >= 0.5 and self.sidesAttacked["left"] >= self.sidesAttacked["right"]:
#            game_state.attempt_spawn(SCRAMBLER, [20,6])
#        if self.sidesAttacked["mid"] >= 0.9 and self.sidesAttacked["right"] >= 0.5 and self.sidesAttacked["right"] >= self.sidesAttacked["left"]:
#            game_state.attempt_spawn(SCRAMBLER, [7,6])

    def attack_v2(self, game_state):
        encryptor_locations = [[13,0],[15,1],[14,2],[13,2],[11,2],[11,3],[12,4],[13,4],[14,4],[15,4],[16,4],[18,4],[18,5],[17,6],[16,6],[15,6],[14,6],[13,6],[12,6],[11,6],[10,6],[9,6],[7,6],[7,7], [8,8],[9,8],[10,8],[11,8],[12,8],[13,8],[14,8],[15,8],[16,8],[17,8],[18,8],[19,8],[20,8],[22,8], [10,5], [15,2], [16,2], [10,3], [18,6], [19,6], [20,6], [22,9], [21,10], [20,10], [19,10], [18,10], [17,10],[16,10],[15,10],[14,10],[13,10],[12,10],[11,10],[10,10],[9,10],[8,10],[7,10],[6,10],[5,10],[3,10]]
        destructor_locations2 = [[1,13],[2,13],[4,12],[5,12],[7,12],[8,12],[10,12],[11,12],[13,12],[14,12],[16,12],[17,12],[19,12],[20,12],[22,12],[23,12],[25,13],[26,13],[0,13],[27,13],[26,12],[1,12]]
        #game_state.attempt_spawn(FILTER, final_filter)
        if not game_state.can_spawn(DESTRUCTOR, [17,13]):
            game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)
        #scrambler_pos = [24,10]
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations2)
        #game_state.attempt_spawn(ENCRYPTOR, encryptor_locations2)

        """This optimizes the number of pings and EMPs to send"""
        if self.lastSentPing and self.pastHP - game_state.enemy_health >= (self.minPing)/2 + 1:
            self.minPing = self.minPing-4
            if self.minPing < 9:
                self.minPing = 9
        elif game_state.enemy_health >= self.pastHP and self.lastSentPing:
            self.minPing = self.minPing+4
        if self.lastSentEMP and self.pastHP - game_state.enemy_health >= (self.minEMP)/2 + 1:
            self.minEMP = self.minPing-1
            if self.minEMP < 0:
                self.minEMP = 0
        elif game_state.enemy_health >= self.pastHP and self.lastSentEMP:
            self.minEMP = self.minEMP+1

        """This sends either EMPs or pings"""
        if(game_state.enemy_health >= self.pastHP and game_state.number_affordable(EMP) >= self.minEMP):
            game_state.attempt_spawn(EMP, self.better_spawn_location(game_state, [[14, 0], [12,1]]), 1000)
            self.lastSentPing = False
            self.lastSentEMP = True
        elif(game_state.enemy_health < self.pastHP and game_state.number_affordable(PING) >= self.minPing):
            #game_state.attempt_spawn(SCRAMBLER, [24,10], 1)
            #game_state.attempt_spawn(SCRAMBLER, self.better_spawn_location(game_state), 1)
            #game_state.attempt_spawn(PING, self.better_spawn_location(game_state, [[16, 2], [10,3]]), 3)
            self.lastSentEMP = False
            if game_state.number_affordable(PING) > 0:
                self.lastSentPing = True
            else:
                self.lastSentPing = False
            game_state.attempt_spawn(PING, self.better_spawn_location(game_state, [[14, 0], [12,1]]), 1000)
            self.pastHP = game_state.enemy_health
        else:
            #game_state.attempt_spawn(SCRAMBLER, self.better_spawn_location(game_state, [[14, 0], [12,1]]), 1)
            self.lastSentPing = False
            self.lastSentEMP = False
        #game_state.attempt_spawn(SCRAMBLER, self.better_spawn_location(game_state), 1)

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with Scramblers and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_scramblers(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our EMPs to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.emp_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Pings there.

                # Only spawn Ping's every other turn
                # Sending more at once is better since attacks can only hit a single ping at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    ping_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
                    game_state.attempt_spawn(PING, best_location, 1000)

                # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
                encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        destructor_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

        # Place filters in front of destructors to soak up damage for them
        filter_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(FILTER, filter_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own firewalls
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        # While we have remaining bits to spend lets send out scramblers randomly.
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information
            units can occupy the same space.
            """

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
