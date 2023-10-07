from app.src.readers import AlgoReader
from app.src.mst import Graph

class Group:

    def __init__(self, reader: AlgoReader) -> None:
        
        self.READER = reader
        self.THRESHOLD = 0.5
        self.DISTANCE = []
        self.POSITIONS = []
        self.GROUPS = []

    def gen(self):

        self.POSITIONS = self.READER.get_data()

        size = len(self.POSITIONS)
        self.DISTANCE = [[0 for _ in range(size)] for _ in range(size)]
        self.IS_MARKED = [False for _ in range(size)]

        for i in range(len(self.POSITIONS)):
            for j in range(i + 1, len(self.POSITIONS)):

                distance = self.POSITIONS[i] - self.POSITIONS[j]
                self.DISTANCE[i][j] = distance
                self.DISTANCE[j][i] = distance

        graph = Graph(size)
        graph.graph = self.DISTANCE

        results = graph.primMST()

        self.GROUPS = [[pos] for pos in self.POSITIONS]

        parent_group = None
        child_group = None

        for result in results:

            parent, child, weight = result

            if weight < self.THRESHOLD:
                
                for group in self.GROUPS:

                    if self.POSITIONS[parent] in group:
                        parent_group = group

                    if self.POSITIONS[child] in group:
                        child_group = group

                parent_group += child_group
                self.GROUPS.remove(child_group)
                        
        return self.GROUPS


if __name__ == "__main__":

    from src.readers import DEFAULT
    import matplotlib.pyplot as plt

    algo = Group(DEFAULT())
    result = []

    areas = algo.gen()

    for area in areas:

        x = []
        y = []

        for position in area:

            x.append(position.x)
            y.append(position.y)

        plt.plot(x, y, linewidth=4)
        plt.scatter(x, y)

        result.append({
            "positions": area,
            "center": [sum(x)/len(x), sum(y)/len(y)]
        })

    plt.show()
    print(result)

    # # plot
    # fig, ax = plt.subplots()

    # ax.scatter(x, y)
    # # ax.set(xlim=(x., 8), ylim=(0, 8))

    # plt.show()
