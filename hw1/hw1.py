def print_map(m, pos):
    out = []
    for i in range(0, len(m)):
        out_list = ["." if el else "#" for el in m[i]]
        if i == pos[0]:
            out_list[pos[1]] = "@"
        out.append("".join(out_list))
    print("\n".join(out))


def shape(m):
    return len(m), len(m[0])

def neighbours(m, pos):
    neighs = []
    if pos[0] > 0:
        if m[pos[0] - 1][pos[1]]:
            neighs.append((pos[0] - 1, pos[1]))
    if pos[0] < shape(m)[0] - 1:
        if m[pos[0] + 1][pos[1]]:
            neighs.append((pos[0] + 1, pos[1]))
    if pos[1] > 0:
        if m[pos[0]][pos[1] - 1]:
            neighs.append((pos[0], pos[1] - 1))
    if pos[1] < shape(m)[1] - 1:
        if m[pos[0]][pos[1] + 1]:
            neighs.append((pos[0], pos[1] + 1))
    return neighs

def inner_find_route(m, pos, visited):
    route = []
    visited.append(pos)
    for neigh in neighbours(m, pos):
        if neigh[0] == 0 or neigh[0] == shape(m)[0] - 1 or neigh[1] == 0 or neigh[1] == shape(m)[1] - 1:
            route.append(pos)
            route.append(neigh)
            return route
    have_unvisited_neighs = False
    for neigh in neighbours(m, pos):
        if neigh not in visited:
            have_unvisited_neighs = True
            inr_fnd_rt = inner_find_route(m, neigh, visited)
            if inr_fnd_rt != -1:
                route.append(pos)
                route += inr_fnd_rt
                return route
    if not have_unvisited_neighs or route == []:
        return -1


def find_route(m, pos):
    visited = []
    return inner_find_route(m, pos, visited)

def escape(m, initial):
    for pos in find_route(m,initial):
        print("\n")
        print_map(m, pos)


m = [[False, False, False, False],
     [False, True, False, False],
     [False, True, False, True],
     [True, True, False, True],
     [False, False, False, False]]
pos = (1, 1)
print_map(m,pos)
escape(m, pos)