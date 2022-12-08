import numpy as np


def deadlock_detection(allocation, request, availability):
    finish = []
    p = list(range(len(request)))
    while len(finish) < len(request):
        finish_len = len(finish)
        for i in range(len(request)):
            if i in p:
                if all(np.array(request[i]) <= np.array(availability)):
                    finish.append(True)
                    availability = np.array(allocation[i]) + np.array(availability)
                    p.remove(i)
                elif len(finish) == finish_len:
                    finish.append(False)
    return finish, p


allo = [[0, 1, 0], [2, 0, 0], [3, 0, 3], [2, 1, 1], [0, 0, 2]]
r = [[0, 0, 0], [2, 0, 2], [0, 0, 0], [1, 0, 0], [0, 0, 2]]

print(deadlock_detection(allo, r, [0, 0, 0]))
