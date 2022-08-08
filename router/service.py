from __future__ import print_function

from math import sin, cos, sqrt, atan2, radians

import json
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

from router.persistence import *


def handle(event):
    return main(event)


def main(event):
    print("v4.0.0")
    data = event

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['points']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        R = 6373.0

        start_lat = radians(data['points'][from_node]['lat'])
        start_lng = radians(data['points'][from_node]['lng'])

        end_lat = radians(data['points'][to_node]['lat'])
        end_lng = radians(data['points'][to_node]['lng'])

        dlon = end_lng - start_lng
        dlat = end_lat - start_lat

        a = sin(dlat / 2) ** 2 + cos(start_lat) * cos(end_lat) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # Distance in meters
        dist = R * c * 1000
        return dist

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    # Esta regra garante o balanceamento de distancia
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        data['max_distance'],  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(data['distance_span'])

    # Add Capacity constraint.
    def max_load_callback(from_index):
        return 1

    max_load_index = routing.RegisterUnaryTransitCallback(max_load_callback)
    # Add Distance constraint.
    max_load_dimension = 'MaxLoad'
    routing.AddDimension(
        max_load_index,
        0,  # no slack
        data['max_load'],  # vehicle maximum load
        True,  # start cumul to zero
        max_load_dimension)
    dimension = routing.GetDimensionOrDie(max_load_dimension)
    dimension.SetGlobalSpanCostCoefficient(data['load_span'])

    # Allow to drop nodes.
    if data['penalty'] > 0:
        penalty = data['penalty']
        for node in range(1, len(data['points'])):
            # https://github.com/google/or-tools/issues/883#issuecomment-429214756 Just use a Disjunction. i.e.
            # Solver try to visit the node (and pay the traveling cost etc...) or pay the penalty cost and don't
            # visit the node, knowing that the solver will try to minimize the objective (sum of all cost).
            # routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
            # ---
            # According to the docs: https://developers.google.com/optimization/routing/penalties
            # Penalty sizes
            # In the example above, we chose penalties that are larger than the sum of all distances between locations
            # (excluding the depot).
            # As a result, after dropping one location to make the problem feasible, the solver doesn't drop
            # any additional locations, because the penalty for doing so would exceed any further reduction in travel
            # distance. Assuming you want to make as many deliveries as possible, this gives a satisfactory solution
            # to the problem.
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION

    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = data['time_limit']
    search_parameters.log_search = data['debug_mode']

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        result = to_json_solution(data, manager, routing, solution)
        persist(result, data['id'], data)

        return result
    else:
        result = {
            'error': 1
        }
        return result


def to_json_solution(data, manager, routing, solution):
    routes = []
    max_route_distance = -1
    result = {
        'routes': routes
    }
    for vehicle_reference in range(data['num_vehicles']):
        index = routing.Start(vehicle_reference)
        route_distance = 0
        counter = 0
        route = {}
        route['points'] = []
        while not routing.IsEnd(index):
            counter = counter + 1
            route['points'].append(data['points'][manager.IndexToNode(index)])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_reference)
        route['points'].append(data['points'][manager.IndexToNode(index)])
        route['distance'] = [route_distance]
        routes.append(route)
        print("Route[" + str(index) + "]- DISTANCE:" + str(route_distance))
        # plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        max_route_distance = max(route_distance, max_route_distance)
    # print_solution(data, manager, routing, solution)
    return result


def print_solution(data, manager, routing, solution):
    """Prints assignment on console."""
    max_route_distance = 0
    dropped_nodes = 'DROPS:\n['
    for node in range(routing.Size()):
        if routing.IsStart(node) or routing.IsEnd(node):
            continue
        if solution.Value(routing.NextVar(node)) == node:
            dropped_nodes += ' {}, '.format(manager.IndexToNode(node))
    dropped_nodes += "]"
    print(dropped_nodes)

    plan_output = '[\n'
    for vehicle_reference in range(data['num_vehicles']):
        index = routing.Start(vehicle_reference)
        route_distance = 0
        counter = 0
        plan_output += '[ '
        while not routing.IsEnd(index):
            counter = counter + 1
            plan_output += "{},".format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_reference)
        plan_output += '{} ],\n // {}, {}\n'.format(manager.IndexToNode(index), route_distance, counter)
        max_route_distance = max(route_distance, max_route_distance)
    plan_output += ']'
    print(max_route_distance)
    return plan_output

