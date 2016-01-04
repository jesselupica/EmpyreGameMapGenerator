
class Biome:
	ocean,lake,	desert,	mountain, marsh, coast = range(0, 6)

class GraphNode:

#	fields:
#		center
#		edge_list
#		elevation
#		biome
#		adjacent_nodes

	def __init__(self, point, edge_list):
		self.center = point
		self.edge_list = edge_list
		self.adjacent_nodes = []
		self.elevation = None
		self.is_land = None 
		self.biome = None

	def connect_adjacent_nodes(self, adjacent_nodes):
		self.adjacent_nodes.extend(adjacent_nodes)
		self.adjacent_nodes.remove(self)

