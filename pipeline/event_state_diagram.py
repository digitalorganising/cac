from transforms.events import EventsBuilder
from transitions.extensions.diagrams import GraphMachine

machine = GraphMachine(graph_engine="mermaid", **EventsBuilder.get_machine_params())
print(machine.get_graph().draw(None))
