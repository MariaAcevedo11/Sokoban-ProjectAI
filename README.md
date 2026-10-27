# Sokoban-ProjectAI

Sokoban solver and benchmark implementation for published XSB levels.

## Implemented algorithms

1. **BFS**: uninformed baseline that expands states by depth.
2. **A\*** with **Manhattan assignment heuristic**: assigns boxes to goals to minimize total Manhattan distance.
3. **A\*** with **dead-square pruning**: precomputes dead squares using reverse box reachability from goals and prunes states that place boxes there.

All algorithms use the same state representation: `(player_position, box_positions)` with legal Sokoban movement and push rules.

## Dead-square detection

Dead squares are computed by reverse search from all goals. A reverse transition from box position `b` to `b-d` is allowed only when:

- `b-d` is floor (possible previous box position), and
- `b-2d` is floor (the required player stand position for the corresponding forward push).

Floor positions not reachable by this reverse process are marked dead squares.

## Node expansion budget

Every solver accepts a `max_expanded_nodes` budget (default `1_000_000`).
A level is counted solved only if a valid solution is found within this limit.

## Usage

### Solve one level

```bash
python -m sokoban.cli bfs /absolute/path/to/level.xsb
python -m sokoban.cli astar /absolute/path/to/level.xsb
python -m sokoban.cli astar-deadlock /absolute/path/to/level.xsb
```

### Benchmark a level collection

Provide a file containing multiple XSB levels separated by blank lines:

```bash
python -m sokoban.cli benchmark /absolute/path/to/levels.xsb
```

The benchmark prints for each algorithm:
- levels solved and percentage,
- nodes expanded per level,
- move-count per solution.

## Tests

Run focused tests with:

```bash
python -m unittest -v
```
