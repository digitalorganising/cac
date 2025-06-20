from transforms.events_machine import machine_params
from transitions.extensions.diagrams import GraphMachine

machine = GraphMachine(graph_engine="mermaid", **machine_params)
print(machine.get_graph().draw(None))
