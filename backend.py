import logging
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import math
import json
import os
from pathlib import Path


def routes_db_connector(path, routes_db=None):
    try:
        sqliteConnection = sqlite3.connect(os.path.join(path, routes_db))
        cursor = sqliteConnection.cursor()
        query = 'select * from ROUTES'
        cursor.execute(query)
        result = cursor.fetchall()
        return result
        cursor.close()
    except sqlite3.Error as error:
        logging.error('Watch out!', error)
    finally:

        if sqliteConnection:
            sqliteConnection.close()

#⚠️💊🎢🗽🗼🏗🐘🏭♟️ '`https://twitter.com/C_RMWH_F/status/1719474495319105965?t=-93ATHp9jKk2uJAbm_UGhQ&s=19`'
class War: 
    path = ""
    empire = dict()
    millennium_falcon = dict()
    bounty_hunters = dict()
    strategic_paths = dict()
    max_path_probability = dict()
    universe_model = nx.Graph()
    count_down = 0
    MAX_STOP_DAYS = 2

    def __init__(self, millennium_falcon_path, empire_path):
        self.path = Path(millennium_falcon_path).parent
        with open(empire_path) as empire_json_file:
            self.empire = json.load(empire_json_file)
            empire_json_file.close()

        with open(millennium_falcon_path) as millennium_falcon_json_file:
            self.millennium_falcon = json.load(millennium_falcon_json_file)
            millennium_falcon_json_file.close()

        self.count_down = self.empire['countdown']
        self.bounty_hunters_parser(self.empire)

    def bounty_hunters_parser(self, _empire):
        for hunter in _empire["bounty_hunters"]:
            self.bounty_hunters.setdefault(hunter["planet"], []).append(hunter["day"])

    def universe_routes_model(self):
        source_model = routes_db_connector(self.path, routes_db=self.millennium_falcon["routes_db"])
        for edge in source_model:
            hunters = {}
            self.universe_model.add_edge(edge[0], edge[1], weight=edge[2])
            if self.bounty_hunters.get(edge[0], False):
                hunters.setdefault((edge[0], edge[1]), {"days": self.bounty_hunters.get(edge[0])})
            elif self.bounty_hunters.get(edge[1], False):
                hunters.setdefault((edge[0], edge[1]), {"days": self.bounty_hunters.get(edge[1])})
            nx.set_edge_attributes(self.universe_model, hunters)

    def strategy(self):
        # O(V + E)
        for _path in nx.all_simple_paths(self.universe_model, source=self.millennium_falcon['departure'],
                                         target=self.millennium_falcon['arrival']):
            # simple weight some with max calculated refuel stop days
            path_weight = math.floor(nx.path_weight(self.universe_model, _path, 'weight') * (
                    1 + 1 / self.millennium_falcon.get('autonomy', 6)))

            # possible strategies that requires risks evaluations
            if 0 < path_weight <= self.count_down:
                _allowed_rest_days = self.count_down - path_weight
                pathGraph = nx.path_graph(_path).edges()
                path_edges = [(ea, self.universe_model.edges[ea[0], ea[1]]['weight']) for ea in pathGraph]
                probability = self.strategic_decision_probability(path_edges, _allowed_rest_days)
                self.strategic_paths.setdefault(probability, [pathGraph]).append(pathGraph)
                # Todo display all other available options probability < max_probability
                # print(_path, "path_weight", path_weight, "probability", probability)

    def get_max_path_probability(self):
        if self.strategic_paths:
            _max = max([key[0] for key in self.strategic_paths.items()])
            self.max_path_probability = dict(self.strategic_paths).get(_max)
            return _max

    def strategic_decision_probability(self, _path_edges, _allowed_rest_days):

        # O(E)
        hunters_holder = []
        days_tracker = 0
        weight_some = 0
        millennium_falcon_autonomy = self.millennium_falcon.get("autonomy", 6)

        for edge in _path_edges:
            edge_start = edge[0][0]
            edge_end = edge[0][1]
            edge_weight = edge[1]
            # time is fundamentally out of control, time always move forward
            days_tracker = days_tracker + edge_weight
            hunter_stay_days = []
            # forced refuel stop
            if edge_weight >= millennium_falcon_autonomy:
                autonomy = millennium_falcon_autonomy
                days_tracker = math.floor(days_tracker * (1 + 1 / millennium_falcon_autonomy))
            else:
                # autonomy formula
                autonomy = days_tracker % millennium_falcon_autonomy
            # undirected graph model requires to check start and end
            if self.universe_model[edge_start][edge_end].get("days", False):
                hunter_stay_days = self.universe_model[edge_start][edge_end].get("days")
                hunters_holder.append((edge_start, edge_end))
            if self.universe_model[edge_start][edge_end].get("days", False) and \
                    ((autonomy == millennium_falcon_autonomy and days_tracker - 1 in hunter_stay_days)
                     or (days_tracker in hunter_stay_days)):
                forced_stop_days = 1
                # hunters detector
                if len(hunters_holder) == 2:
                    hunters_holder.clear()
                else:
                    # init first weight_some formula
                    start = 0
                    # forced stop to refuel in a planet with hunters
                    if autonomy == millennium_falcon_autonomy:
                        if len(hunter_stay_days) > 1:
                            forced_stop_days = self.MAX_STOP_DAYS
                            weight_some = 0.1
                            start = 1
                    # weight_some formula
                    weight_some = weight_some + sum(math.pow(9, i) / math.pow(10, i + 1) for i in
                                                    range(start, forced_stop_days))
                    adjustment_day = 0
                    if _allowed_rest_days > self.MAX_STOP_DAYS:
                        _allowed_rest_days = _allowed_rest_days - forced_stop_days
                        adjustment_day = forced_stop_days

                    elif _allowed_rest_days > 0:
                        _allowed_rest_days = 0
                        if forced_stop_days < self.MAX_STOP_DAYS:
                            if days_tracker - 1 in hunter_stay_days:
                                adjustment_day = 1
                        else:
                            if len(hunter_stay_days) == 1:
                                adjustment_day = 1

                    if adjustment_day > 0:
                        # utility adjustment function formula based on rest days
                        weight_some = weight_some - sum(math.pow(9, i) / math.pow(10, i + 1) for i in
                                                        range(0, adjustment_day))

        return 1 - weight_some

    def display_strategic_paths(self):

        nx.set_node_attributes(self.universe_model, self.bounty_hunters, name="days")
        # positions for all nodes
        pos = nx.spring_layout(self.universe_model, seed=7)
        # nodes
        nx.draw_networkx_nodes(self.universe_model, pos, node_size=700)
        # edges
        if self.max_path_probability:
            for edges in self.max_path_probability:
                nx.draw_networkx_edges(self.universe_model, pos, edgelist=edges, width=6)

        # node labels
        nx.draw_networkx_labels(self.universe_model, pos, font_size=20, font_family="sans-serif")
        # edge weight labels
        edge_labels = nx.get_edge_attributes(self.universe_model, "weight")
        nx.draw_networkx_edge_labels(self.universe_model, pos, edge_labels)
        ax = plt.gca()
        ax.margins(0.08)
        plt.axis("off")
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    path = 'giskard/developer-test-main/examples/example{0}'.format(2)
    empire = os.path.join(path, 'empire.json')
    millennium_falcon = os.path.join(path, 'millennium-falcon.json')
    war = War(millennium_falcon, empire)
    war.universe_routes_model()
    # this strategy enforce the millennium_falcon to stay maximum 2 days in a planet with hunters
    war.strategy()
    war.get_max_path_probability()
    war.display_strategic_paths()

