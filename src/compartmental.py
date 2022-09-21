import networkx as nx

class ModerationEffect():
    def __init__(self, nodes, fn, name, time_delay=0):
        self.fn = fn
        self.nodes = nodes
        self.name = name
        self.delay = time_delay

    def __call__(self, dependants, history):
        assert len(history) == self.delay
        return self.fn(dependants, history)

    def __neg__(self):
        return ModerationEffect(self.nodes, lambda dependants, history: -self.fn(dependants, history), f"-{self.name}", self.delay)

    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.nodes)})"
    
    def __repr__(self) -> str:
        return str(self)

def build_diffeq(g):
    dynamics = dict()

    for node in g.nodes:
        dynamics[node] = []

    for src, dst, properties in g.edges(data=True):
        moderation: ModerationEffect = properties['moderation']
        dynamics[dst].append(moderation)
        dynamics[src].append(-moderation)    

    derivatives = []
    for node in g.nodes:
        def derivative(state, history, node=node):
            total = 0
            for moderation in dynamics[node]:
                delay = moderation.delay               
                if delay == 0:
                    total += moderation(state, [])
                else:
                    hist = history[-delay:]
                    total += moderation(state, hist)
            return total

        derivatives.append((derivative, node))

    def ode(state, history):
        result = dict()
        for derivative, node in derivatives:
            result[node] = derivative(state, history)
        return result

    return ode
