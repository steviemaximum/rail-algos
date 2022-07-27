from util import *
@dataclass
class PossibleSolution:
    edge_dict: dict
    total_weight: float
    score: float
    heuristic_score: float
    graph: int

    # static vars
    complete_graph = None
    empty_graph = None
    weight_limit = None

    def __init__(self, edge_dict=None, total_weight=None, score=None, heuristic_score=None, graph=None):
        self.edge_dict = edge_dict
        self.total_weight = total_weight
        self.score = score
        self.heuristic_score = heuristic_score
        self.graph = graph
    
    def __lt__(self, other):
        self.total_weight < other.total_weight

    def __le__(self, other):
        self.total_weight <= other.total_weight

    def fill_from_graph(self):
        self.total_weight = self.graph.size(weight='dist')
        self.score = self._get_score()
        self.heuristic_score = self._get_heuristic_score()

    def graph_from_edges(self):
        self.graph = self.empty_graph.copy()
        for edge in self.edge_dict:
            if self.edge_dict[edge]:
                self.graph.add_edge(*edge, dist=self.complete_graph.edges[edge]['dist'])

    # A small deviation from the solution
    def tweak(self):
        print("tweaking")
        num_to_add = round(10*random()) if self.total_weight < self.weight_limit else 0
        num_to_remove = 0

        add_count = 0
        add_weight = 0
        remove_count = 0
        remove_weight = 0
        new_sol = PossibleSolution()
        new_sol.empty_graph = self.empty_graph
        new_sol.complete_graph = self.complete_graph
        new_sol.weight_limit = self.weight_limit
        new_sol.edge_dict = {edge:self.edge_dict[edge] for edge in self.edge_dict}

        def naive_add():
            nonlocal add_count
            nonlocal add_weight
            while add_count < num_to_add:
                selection = choice([edge for edge in self.edge_dict])
                if not new_sol.edge_dict[selection]:
                    new_sol.edge_dict[selection] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[selection]['dist']

        def add_2opt():
            while True:
                nonlocal add_count
                nonlocal add_weight
                edge1 = choice([edge for edge in self.edge_dict])
                edge2 = edge1
                while edge2 == edge1:
                    edge2 = choice([edge for edge in self.edge_dict])
                if random() < 0.5:
                    new1 = (edge1[0], edge2[0])
                    new2 = (edge1[1], edge2[1])
                else:
                    new1 = (edge1[0], edge2[1])
                    new2 = (edge1[1], edge2[0])
                if new1 not in self.edge_dict:
                    new1 = new1[1], new1[0]
                if new1 not in self.complete_graph.edges:
                    continue
                if new2 not in self.edge_dict:
                    new2 = new2[1], new2[0]
                if new2 not in self.complete_graph.edges:
                    continue
                print([edge1, edge2])
                print([new1, new2])
                if not self.edge_dict[new1]:
                    self.edge_dict[new1] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[new1]['dist']
                if not self.edge_dict[new2]:
                    self.edge_dict[new2] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[new2]['dist']
                self.edge_dict[edge1] = False
                self.edge_dict[edge2] = False
                break
        
        def add_shortest_path(connected_only=True):
            nonlocal add_count
            nonlocal add_weight
            node1 = choice([node for node in self.graph.nodes if (not connected_only or self.graph.edges(node))])
            node2 = node1
            while node2 == node1:
                node2 = choice([node for node in self.graph.nodes])
            try:
                # shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight='dist')
                shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight=lambda end1, end2, dict: 1 / score_calc(self.complete_graph.nodes[end1]['population'], self.complete_graph.nodes[end2]['population'], dict['dist']))
                # shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight=lambda end1, end2, dict: 1 / score_calc(self.complete_graph.nodes[end1]['population'], self.complete_graph.nodes[end2]['population'], 1))
            except nx.NetworkXNoPath:
                return
            for node_idx in range(len(shortest_path) - 1):
                new_edge = tuple(shortest_path[node_idx:node_idx+2])
                if new_edge not in self.edge_dict:
                    new_edge = new_edge[1], new_edge[0]
                if not self.edge_dict[new_edge]:
                    new_sol.edge_dict[new_edge] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[new_edge]['dist']

        def replace_shortest_path():
            nonlocal add_count
            nonlocal add_weight
            nonlocal remove_count
            nonlocal remove_weight
            node1 = choice([node for node in self.graph.nodes])
            node2 = node1
            while node2 == node1:
                node2 = choice([node for node in self.graph.nodes])
            try:
                # new_shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight='dist')
                old_shortest_path = nx.shortest_path(self.graph, node1, node2, weight=lambda end1, end2, dict: 1 / score_calc(self.complete_graph.nodes[end1]['population'], self.complete_graph.nodes[end2]['population'], dict['dist']))
                new_shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight=lambda end1, end2, dict: 1 / score_calc(self.complete_graph.nodes[end1]['population'], self.complete_graph.nodes[end2]['population'], dict['dist']))
            except nx.NetworkXNoPath:
                print("no path found")
                return
            for node_idx in range(len(old_shortest_path) - 1):
                new_edge = tuple(old_shortest_path[node_idx:node_idx+2])
                if new_edge not in self.edge_dict:
                    new_edge = new_edge[1], new_edge[0]
                if self.edge_dict[new_edge]:
                    new_sol.edge_dict[new_edge] = False
                    remove_count += 1
                    remove_weight += self.complete_graph.edges[new_edge]['dist']
            for node_idx in range(len(new_shortest_path) - 1):
                new_edge = tuple(new_shortest_path[node_idx:node_idx+2])
                if new_edge not in self.edge_dict:
                    new_edge = new_edge[1], new_edge[0]
                if not self.edge_dict[new_edge]:
                    new_sol.edge_dict[new_edge] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[new_edge]['dist']


        def add_connected_edge():
    pass

        def add_intermediate_edge():
    pass

        add_shortest_path(connected_only=True)
        while self.total_weight + add_weight - remove_weight > self.weight_limit:
            selection = choice([edge for edge in self.graph.edges])
            if new_sol.edge_dict[selection]:
                new_sol.edge_dict[selection] = False
                remove_count += 1
                remove_weight += self.complete_graph.edges[selection]['dist']
        # print(f"tweak: {add_count=} of {(len(self.complete_graph.edges)-len(self.graph.edges))=}, {remove_count=} of {len(self.graph.edges)}")
        new_sol.graph_from_edges()
        new_sol.fill_from_graph()
        print(f"TWEAK: {new_sol.total_weight=}, {new_sol.score=}, {new_sol.heuristic_score=}")
        return new_sol

    # A large deviation from the solution, meant to break out of a local optimum
    def perturb(self):
        print("perturbing")
        # num_to_add = 10 * (1 - self.total_weight / self.weight_limit)
        num_to_add = random() * ceil(self.weight_limit / 100)
        # num_to_remove = random() * 1000

        add_count = 0
        add_weight = 0
        remove_count = 0
        remove_weight = 0
        new_sol = PossibleSolution()
        new_sol.edge_dict = {edge:self.edge_dict[edge] for edge in self.edge_dict}
        def naive_add():
            nonlocal add_count
            nonlocal add_weight
            while add_count < num_to_add:
                selection = choice([edge for edge in self.edge_dict])
                if not new_sol.edge_dict[selection]:
                    new_sol.edge_dict[selection] = True
                    add_count += 1
                    add_weight += self.complete_graph.edges[selection]['dist']
        def add_shortest_paths():
            nonlocal add_count
            nonlocal add_weight
            source = choice([node for node in self.graph.nodes])
            try:
                # shortest_path = nx.shortest_path(self.complete_graph, node1, node2, weight='dist')
                shortest_paths = nx.shortest_path(self.complete_graph, source=source, weight=lambda end1, end2, dict: 1 / score_calc(self.complete_graph.nodes[end1]['population'], self.complete_graph.nodes[end2]['population'], dict['dist']))
            except nx.NetworkXNoPath:
                print("no path found")
                return
            for target in shortest_paths:
                print(target)
                for node_idx in range(len(shortest_paths[target]) - 1):
                    new_edge = tuple(shortest_paths[target][node_idx:node_idx+2])
                    if new_edge not in new_sol.edge_dict:
                        new_edge = new_edge[1], new_edge[0]
                    if not new_sol.edge_dict[new_edge]:
                        new_sol.edge_dict[new_edge] = True
                        add_count += 1
                        add_weight += self.complete_graph.edges[new_edge]['dist']
                print("complete")

        naive_add()
        while self.total_weight + add_weight - remove_weight > self.weight_limit:
            selection = choice([edge for edge in self.graph.edges if new_sol.edge_dict[edge]])
            if new_sol.edge_dict[selection]:
                new_sol.edge_dict[selection] = False
                remove_count += 1
                remove_weight += self.complete_graph.edges[selection]['dist']
        print(self.total_weight + add_weight - remove_weight)
        print(f"perturb: {add_count=} of {(len(self.complete_graph.edges)-len(self.graph.edges))=}, {remove_count=} of {len(self.graph.edges)}")
        new_sol.graph_from_edges()
        new_sol.fill_from_graph()
        return new_sol

    # Decide whether to move the home base to the new local optimum
    def new_home_base(self, new_home):
        return self if self.heuristic_score > new_home.heuristic_score else new_home

    def _get_score(self):
        try:
            # print("try")
            # return approx_evaluate_solution(self.graph, self.sorted_nodes[:20], 0)
            return approx_evaluate_solution(self.graph, PossibleSolution.sorted_nodes[:500], 0)
            # return approx_evaluate_solution(self.graph, [], len(self.graph))
        except AttributeError:
            # print("except")
            PossibleSolution.sorted_nodes = sorted(self.complete_graph.nodes, key=lambda x: self.complete_graph.nodes[x]['population'])
            # return approx_evaluate_solution(self.graph, self.sorted_nodes[:20], 0)
            return approx_evaluate_solution(self.graph, PossibleSolution.sorted_nodes[:500], 0)
            # return approx_evaluate_solution(self.graph, [], len(self.graph))

    def _get_heuristic_score(self):
        return self.score - 1e15 * max(0, (self.total_weight - self.weight_limit))

def generate_solution(empty_graph, complete_graph, cities, weight_limit):
    # edge_prob = 400/len(complete_graph.edges)

    num_edges = len(complete_graph.edges)
    new_sol = PossibleSolution()
    PossibleSolution.empty_graph = empty_graph
    PossibleSolution.complete_graph = complete_graph
    PossibleSolution.weight_limit = weight_limit
    # new_sol.graph = greedy_buildup(cities, weight_limit)
    # new_sol.graph = max_weight_spanning_tree_buildup(cities, weight_limit)
    new_sol.graph = min_dist_spanning_tree_buildup(cities, weight_limit)
    new_sol.edge_dict = {edge:(edge in new_sol.graph.edges) for edge in complete_graph.edges}
    new_sol.fill_from_graph()

    return new_sol
    

# Local search with a perturbation when a local optimum is found. Perturbation is made to be different
# from a previous local minima.
def iterated_local_search(cities, k, global_timeout=600, local_timeout=30):
    empty = empty_solution(cities)
    complete = complete_solution(cities)
    curr_sol = generate_solution(empty, complete, cities, k)
    curr_home = curr_sol
    curr_best = curr_sol
    global_start_time = time.time()
    while time.time() - global_start_time < global_timeout:
        local_start_time = time.time()
        while time.time() - local_start_time < local_timeout:
            print(f"BEST: {curr_best.total_weight=}, {curr_best.score=}, {curr_best.heuristic_score=}")
            print(f"HOME: {curr_home.total_weight=}, {curr_home.score=}, {curr_home.heuristic_score=}")
            print(f"CURRENT: {curr_sol.total_weight=}, {curr_sol.score=}, {curr_sol.heuristic_score=}")
            new_sol = curr_sol.tweak()
            if new_sol.heuristic_score > curr_sol.heuristic_score:
                curr_sol = new_sol
        if curr_sol.heuristic_score > curr_best.heuristic_score:
            curr_best = curr_sol
        curr_home = curr_home.new_home_base(curr_sol)
        curr_sol = curr_home.perturb()
    return curr_best.graph
        
        
# Local search with a steadily decreasing chance to move to an inferior solution
def simulated_annealing(cities, k, timeout=600, temp_mult=30):
    def temp(elapsed_time):
        return temp_mult * (1 - (elapsed_time / timeout))
    def switch_prob(temp, better_qual, worse_qual):
        try:
            print(exp((worse_qual - better_qual) / temp))
            return exp((worse_qual - better_qual) / temp)
        except OverflowError:
            return 0

    empty = empty_solution(cities)
    complete = complete_solution(cities)
    curr_sol = generate_solution(empty, complete, cities, k)
    curr_best = curr_sol
    start_time = time.time()
    while time.time() - start_time < timeout:
        print(f"BEST: {curr_best.total_weight=}, {curr_best.score=}, {curr_best.heuristic_score=}")
        print(f"CURRENT: {curr_sol.total_weight=}, {curr_sol.score=}, {curr_sol.heuristic_score=}")
        new_sol = curr_sol.tweak()
        if new_sol.heuristic_score > curr_sol.heuristic_score or random() < switch_prob(temp(time.time() - start_time), curr_sol.heuristic_score, new_sol.heuristic_score):
            curr_sol = new_sol
        if curr_sol.heuristic_score > curr_best.heuristic_score:
            curr_best = curr_sol
    return curr_best.graph

    pass

# Local search inspired by evolution
def genetic_algorithm(cities, timeout, k):
    pass