# Lem_in
It is a Unit Factory Educational project. At Unit Factory it should be written on C, but I recode it on Python, because my previous version on C can't handle hard maps with a lot of path intersections.
## Subject
You are given a map in the format, describing in the next part. This map describes a graph, that represents an *ant farm*. The goal is to move all *ants* through the *ant farm* with the least number of steps. They have to avoid traffic jams as well as walking all over their fellow ants. 2 ants can be in the same room only if it's a *start* or an *end* room.
## Map
Map has the following format:
- number_of_ants
- the_rooms
- the_links

Each line means one instruction.
At the beginning it must be a number of ants, represented by integer > 0.

Then there must be rooms, represented by following line:
```
room_name x y
```

Where x and y are coordinates, which could be used by visualization of algorithm. Each room must have a unique name

There could be presented comments, which start with **#** symbol and commands, which start with **##**.
Examples of commands:
```
##start => Mark the room from the next line as *Start* Room
##end => Mark the room from the next line as *End* Room
```
Then links part. It has the following format:
```
room1_name-room2_name
```

It links room1 with room2 and room2 with room1, to make the graph undirected.
Each link has to contain an existing room name and don't have duplicates.

There also must be a way to reach *end* from *start*.
If any of those constraints isn't respected, parser raises a SyntaxError, where the line, where the error occured, and an error message are written. It also stops the execution of the program.
## Algorithm
To avoid traffic jams and presence of 2 or more ants in the same room, I need to find the best combination of node-disjoint paths. To accomplish that, I use a [Suurballe Algorithm](http://www.macfreek.nl/memory/Disjoint_Path_Finding#Suurballe).

It contains the following steps:
1. Find the shortest path. I use simple Breadth-First Search, because all edges in my graph has cost 1.
2. Make the graph directed and replace the edges from the found path with inverse edges.
3. Split all intermediate nodes into **input** and **output** node.
4. Repeat steps 1, 2 and 3 to find k number of paths.
5. Remove all edges from graph and put edges from our paths.
6. Remove all edges, which has an inverse edge.

At the end, it allows me to find k node-disjoint paths.
But I don't know what is k, so i simply increase k from **1** to **max_routes**, which can be calculated such as:
```
max_routes = min(ants_num, len(start.edges), len(end.edges))
```

And I increase k until the BFS cannot find more paths or untill the new combination of paths makes the result worse, than it was on previous iteration.

## Running the program
```
python3 main.py map [--verbose]
map is the path to the map. You can find some of the maps inside maps/ directory
--verbose flag prints all intermediate steps inside the program
```
