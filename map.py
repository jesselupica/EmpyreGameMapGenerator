import sys, pygame, random, math, time, Queue
from sympy.geometry import Line, Point, Segment, Ray, convex_hull, Polygon
from voronoi import voronoi
from graph_node import GraphNode

from pygame.locals import * 

pygame.init()

width = 700
height = 700
num_points = 20
buf = 10

number_of_peaks = 2

max_elevation = 3 

RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
ORANGE = (255,140,0)

screen = pygame.display.set_mode((width + 5, height + 5))

# Boundaries[0, 1, 2, 3] = top, right, bottom, left
# ordered clockwise starting at the top
def adjust_out_of_bounds_points(vert1, vert2, boundaries):
	line_seg = None
	if vert1[0] < 0 or vert1[1] < 0 or vert2[0] < 0 or vert2[1] < 0 or vert1[0] > width or vert1[1] > height or vert2[0] > width or vert2[1] > height:
		line_seg = Segment(Point(vert1), Point(vert2))

		if vert1[0] < 0: 
			intrscts = line_seg.intersection(boundaries[3])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert1 = intrsct.x, intrsct.y

		if vert1[1] < 0: 
			intrscts = line_seg.intersection(boundaries[0])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert1 = intrsct.x, intrsct.y
		if vert2[0] < 0: 
			intrscts = line_seg.intersection(boundaries[3])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert2 = intrsct.x, intrsct.y
		if vert2[1] < 0: 
			intrscts = line_seg.intersection(boundaries[0])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert2 = intrsct.x, intrsct.y
		if vert1[0] > width: 
			intrscts = line_seg.intersection(boundaries[1])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert1 = intrsct.x, intrsct.y
		if vert1[1] > height: 
			intrscts = line_seg.intersection(boundaries[2])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert1 = intrsct.x, intrsct.y
		if vert2[0] > width: 
			intrscts = line_seg.intersection(boundaries[1])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert2 = intrsct.x, intrsct.y
		if vert2[1] > height:
			intrscts = line_seg.intersection(boundaries[2])
			if len(intrscts) == 0:
				return None, None
			intrsct = intrscts[0]
			vert2 = intrsct.x, intrsct.y
	return vert1, vert2

def draw_segment(seg, color):
	vert1 = (seg.p1.x, seg.p1.y)
	vert2 = (seg.p2.x, seg.p2.y)
	pygame.draw.line(screen, color, vert1, vert2, 2)
	pygame.display.flip()

def draw_point(p, color):
	pygame.draw.circle(screen, color, (p.x,p.y), 4, 2)
	pygame.display.flip()


def generate_polygons(points_dict, segments, points, point_to_segment_dict):
	
	polygons = []
	segments_to_polygons = {}
	i = 1

	for p in points:
		point = Point(p)
		#draw_point(point, WHITE)
		polygon_vertices = []
		closest_segment = None
		for seg in segments:
			if closest_segment == None or abs(seg.distance(point)) < abs(closest_segment.distance(point)):
				closest_segment = seg
		
		polygon_vertices.extend(closest_segment.points)
		current_vertex = closest_segment.points[0] 
		previous_vertex = closest_segment.points[1]
		
		polygon_complete = False 
		segs = [closest_segment]
		
		while not polygon_complete:
			#time.sleep(2)
			#draw_point(current_vertex, WHITE)
			#draw_point(previous_vertex, ORANGE)

			vertex_list = points_dict[current_vertex]
			temp_seg_list = []
			#for v in vertex_list:
			#	segs = point_to_segment_dict[v]
			#	temp_seg_list.extend(segs)
			closest_vertex = None 
			best_seg = None
			#draw_segment(closest_segment, ORANGE)
			
			for vertex in vertex_list:
				if vertex != previous_vertex:
					
					temp_seg = Segment(current_vertex, vertex)
					temp_seg_mid = temp_seg.midpoint
					point_to_temp_mid = Segment(temp_seg_mid, point)
					#draw_segment(point_to_temp_mid, WHITE)
					
					relevant_segs = []
					relevant_segs.extend(segs)
					relevant_segs.extend(temp_seg_list)

					
					closest = True
					for seg in segments:
						closer_points = point_to_temp_mid.intersection(seg)
						if len(closer_points) > 0:
							if not temp_seg.distance(closer_points[0]) < 0.001:
								closest = False
								
								#draw_point(closer_points[0], BLUE)
								#draw_segment(temp_seg, BLUE)
						
					if closest:
						closest_vertex = vertex
						best_seg = temp_seg
						break

			print closest_vertex
			if closest_vertex in polygon_vertices:
				polygon_complete = True

			segs.append(best_seg)
			polygon_vertices.append(closest_vertex)
			previous_vertex = current_vertex
			current_vertex = closest_vertex

		print(str(i))
		i += 1
		#for seg in segs:
			#draw_segment(seg, WHITE)

		polygon = GraphNode(point, polygon_vertices)

		#c = polygon.centroid
		#p = (c.x, c.y)
		#pygame.draw.circle(screen, ORANGE, p, 2, 1)

		pygame.display.flip()

		polygons.append(polygon)

		for seg in segs:
			if not seg in segments_to_polygons:
				segments_to_polygons[seg] = []
			segments_to_polygons[seg].append(polygon)

	return polygons, segments_to_polygons

def generate_random_points(num_points, width, height, buf):
	
	points = []
	for i in range(num_points):
		x = random.randint(0 + buf, width - buf)
		y = random.randint(0 + buf, height - buf)

		points.append((x,y))
	return points

def generate_map(): 
 

	screen.fill((0, 0, 0))

	points = generate_random_points(num_points, width, height, buf)


	#for x, y in points:
	#	pygame.draw.circle(screen, WHITE, (x,y), 2, 1)

	voronoi_context = voronoi(points)

	voronoi_point_dict = {}
	point_to_segment_dict = {}
	segments = []
	vertices = []

	top_l =  Point(0,0)
	top_r = Point(width,0)
	bottom_l = Point(0, height)
	bottom_r = Point(width, height) 

	top = Line(top_l, top_r) 
	left = Line(top_l, bottom_l) 
	right = Line(top_r, bottom_r) 
	bottom = Line(bottom_l, bottom_r) 

	boundaries = [top, right, bottom, left]

	for edge in voronoi_context.edges:
		il, i1, i2 = edge # index of line, index of vertex 1, index of vertex 2

		line_color = RED 

		vert1 = None
		vert2 = None
		print_line = True

		if i1 is not -1 and i2 is not -1:
			vert1 = voronoi_context.vertices[i1]
			vert2 = voronoi_context.vertices[i2]

		else:
			line_point = None

			if i1 is -1:
				line_p = voronoi_context.vertices[i2]
			if i2 is -1: 
				line_p = voronoi_context.vertices[i1]

			line_point = Point(line_p[0], line_p[1])
			line = voronoi_context.lines[il] 

			p1 = None
			p2 = None
			if line[1] == 0:
				p1 = line_point
				p2 = Point(line[0]/line[2], 1)
			else: 
				p1 = Point(0, line[2]/line[1])
				p2 = line_point

			l = Line(p1, p2)

			top_intersect = l.intersection(top)
			bottom_intersect = l.intersection(bottom)
			right_intersect = l.intersection(right)
			left_intersect = l.intersection(left)

			distances = []

			top_dist = None
			bottom_dist = None
			right_dist = None
			left_dist = None

			if len(top_intersect) != 0: 
				top_dist = abs(line_point.distance(top_intersect[0]))
				distances.append(top_dist)
			if len(bottom_intersect) != 0 : 
				bottom_dist = abs(line_point.distance(bottom_intersect[0]))
				distances.append(bottom_dist)
			if len(right_intersect) != 0:
				right_dist = abs(line_point.distance(right_intersect[0]))
				distances.append(right_dist)
			if len(left_intersect) != 0: 
				left_dist = abs(line_point.distance(left_intersect[0]))
				distances.append(left_dist)

			vert1 = line_p 
			v2 = None

			if top_dist == min(distances):
				v2 = top_intersect[0]
			elif bottom_dist == min(distances):
				v2 = bottom_intersect[0]
			elif right_dist == min(distances):
				v2 = right_intersect[0]
			elif left_dist == min(distances):
				v2 = left_intersect[0]
			else: 
				v2 = Point(0, 0)
			
			vert2 = (v2.x, v2.y)

			if vert1[0] < 0 or vert1[1] < 0 or vert2[0] < 0 or vert2[1] < 0 or vert1[0] > width or vert1[1] > height or vert2[0] > width or vert2[1] > height:
				print_line = False

		if print_line:
			vert1, vert2 = adjust_out_of_bounds_points(vert1, vert2, boundaries)

		seg = None
		if vert1 == None or vert2 == None:
			print_line = False 
		if print_line: 
			vert1_p = Point(vert1)
			vert2_p = Point(vert2)
			seg = Segment(vert1_p, vert2_p)
			segments.append(seg)
		
			if not vert1_p in voronoi_point_dict:
				voronoi_point_dict[vert1_p] = []
			if not vert2_p in voronoi_point_dict:
				voronoi_point_dict[vert2_p] = []	

	 		voronoi_point_dict[vert1_p].append(vert2_p)
	 		voronoi_point_dict[vert2_p].append(vert1_p) 

	 		if not vert1_p in point_to_segment_dict:
	 			point_to_segment_dict[vert1_p] = []
	 		if not vert2_p in point_to_segment_dict:
	 			point_to_segment_dict[vert2_p] = []

	 		point_to_segment_dict[vert1_p].append(seg)
	 		point_to_segment_dict[vert2_p].append(seg)
	 	
			pygame.draw.line(screen, line_color, vert1, vert2, 1)

	pygame.display.flip()

	top_intersects = []
	bottom_intersects = [] 
	right_intersects = [] 
	left_intersects = [] 

	for seg in segments:
		if seg.p1.y <= 1:
			top_intersects.append(seg.p1)
		if seg.p2.y <= 1:
			top_intersects.append(seg.p2)
		if seg.p1.x >= width -1: 
			right_intersects.append(seg.p1)
		if seg.p2.x >= width-1: 
			right_intersects.append(seg.p2)
		if seg.p1.x <= 1:
			left_intersects.append(seg.p1)
		if seg.p2.x <= 1:
			left_intersects.append(seg.p2)
		if seg.p1.y >= height-1: 
			bottom_intersects.append(seg.p1)
		if seg.p2.y >= height-1: 
			bottom_intersects.append(seg.p2)

	top_intersects = sorted(top_intersects, key=lambda point: point.x)
	bottom_intersects = sorted(bottom_intersects, key=lambda point: point.x)
	left_intersects = sorted(left_intersects, key=lambda point: point.y)
	right_intersects = sorted(right_intersects, key=lambda point: point.y)

	for i in range(0, 4):
		intersect = None
		prev_vertex = None
		final_vertex = None

		if i == 0:
			prev_vertex = top_l
			intersect = top_intersects
			intersect.append(top_r)
		if i == 1:
			prev_vertex = bottom_l
			intersect = bottom_intersects
			intersect.append(bottom_r)
		if i == 2:
			prev_vertex = top_l
			intersect = left_intersects
			intersect.append(bottom_l)
		if i == 3:
			prev_vertex = top_r
			intersect = right_intersects
			intersect.append(bottom_r)

		if not prev_vertex in voronoi_point_dict:
			voronoi_point_dict[prev_vertex] = []
		if not final_vertex in voronoi_point_dict:
			voronoi_point_dict[final_vertex] = []

		if not prev_vertex in point_to_segment_dict:
	 		point_to_segment_dict[prev_vertex] = []
	 	if not final_vertex in point_to_segment_dict:
	 		point_to_segment_dict[final_vertex] = []

	 		

		for vertex in intersect:
			if not vertex in voronoi_point_dict:
				voronoi_point_dict[vertex] = []
			if not prev_vertex in voronoi_point_dict:
				voronoi_point_dict[prev_vertex] = []	
			s = Segment(prev_vertex, vertex)
		 	voronoi_point_dict[vertex].append(prev_vertex)
		 	voronoi_point_dict[prev_vertex].append(vertex)

		 	if not vertex in point_to_segment_dict:
	 			point_to_segment_dict[vertex] = []
	 		if not prev_vertex in point_to_segment_dict:
	 			point_to_segment_dict[prev_vertex] = []

	 		point_to_segment_dict[vertex].append(s)
	 		point_to_segment_dict[prev_vertex].append(s)

		 	prev_vertex = vertex
	 
	try: 
		polygons, segments_to_polygons = generate_polygons(voronoi_point_dict, segments, points, point_to_segment_dict)
	except Exception as e:
		print e 
		print "crashed"
		while 1:
			""" helllo"""
	for seg, gons in segments_to_polygons.iteritems():
		for gon in gons:
			gon.connect_adjacent_nodes(gons)

	for polygon in polygons:
		for node in polygon.adjacent_nodes:
			s = Segment(node.center, polygon.center)
			draw_segment(s, WHITE)

	highest_points_of_elevation = []
	frontiers = []

	for i in range(0, number_of_peaks):
		p = random.choice(polygons)
		p.elevation = max_elevation
		highest_points_of_elevation.append(p)

		frontiers.append(set(p.adjacent_nodes))

	marked_polygons = set([])	

	elevation = max_elevation
	while len(marked_polygons) < num_points:
		elevation -= 1 
		for i in range(0, number_of_peaks):
			new_frontier = set([])

			while len(frontiers[i]) > 0:
				node = frontiers[i].pop()
				node.elevation = elevation
				draw_point(node.center, ORANGE)

				for n in node.adjacent_nodes:
					if n not in marked_polygons:
						new_frontier.add(n)

				marked_polygons.add(node)
			frontiers[i] = new_frontier


	for polygon in polygons:
		if polygon.elevation <= 0:
			vertices = []
			for edge in polygon.edge_list:
				p = (edge.x, edge.y)
				vertices.append(p)
			pygame.draw.polygon(screen, BLUE, vertices, 0)
			pygame.display.flip()
	pygame.display.flip()



generate_map()

while 1 :
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
