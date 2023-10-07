from typing import List

class Graph():
    def __init__(self, vertices):
        self.V = vertices
        self.graph = [[0 for _ in range(vertices)] for _ in range(vertices)]
 
    def genMST(self, parent) -> List[tuple[int, int, float]]:

        result = []

        for i in range(1, self.V):
            result.append((parent[i], i, self.graph[i][parent[i]]))

        return result

    def minKey(self, key, mstSet):
 
        min = 1e9
 
        for v in range(self.V):
            if key[v] < min and mstSet[v] == False:
                min = key[v]
                min_index = v
 
        return min_index
 

    def primMST(self) -> List[tuple[int, int]]:

        key = [1e9] * self.V
        parent = [None] * self.V  
        key[0] = 0
        mstSet = [False] * self.V
 
        parent[0] = -1
 
        for _ in range(self.V):

            u = self.minKey(key, mstSet)

            mstSet[u] = True

            for v in range(self.V):

                if self.graph[u][v] > 0 and mstSet[v] == False and key[v] > self.graph[u][v]:
                    key[v] = self.graph[u][v]
                    parent[v] = u
 
        return self.genMST(parent)