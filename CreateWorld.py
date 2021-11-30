# 根据文件生成 wumpus 世界地图
class World:
    def __init__(self):
        # 初始化坐标 (绝对坐标)
        self.gold = [[4, 4]]
        self.monsters = [[3, 9], [3, 3], [8, 3]]
        self.pits = [[2, 6], [5, 5], [9, 9]]

        self.world = [[0] * 10 for _ in range(10)]
        self.num_rows = 10
        self.num_cols = 10

        self.agent_row = 0
        self.agent_col = 0
        self.cave_entrance_row = 10
        self.cave_entrance_col = 10

    def generate_world(self):
        for i in self.monsters:
            self.world[i[0] - 1][i[1] - 1] = 1
        for i in self.pits:
            self.world[i[0] - 1][i[1] - 1] = 2
        for i in self.gold:
            self.world[i[0] - 1][i[1] - 1] = 5

    # 根据 monsters 和 pits 坐标在相邻房间生成各自的指示
    def populate_indicators(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                for i in range(10):
                    if self.world[row][col] == 1:
                        if row - 1 >= 0:
                            self.world[row - 1][col] = -1

                        if row + 1 < self.num_rows:
                            self.world[row + 1][col] = -1

                        if col + 1 < self.num_cols:
                            self.world[row][col + 1] = -1

                        if col - 1 >= 0:
                            self.world[row][col - 1] = -1

                    if self.world[row][col] == 2:
                        if row - 1 >= 0:
                            self.world[row - 1][col] = -2

                        if col + 1 < self.num_cols:
                            self.world[row][col + 1] = -2

                        if row + 1 < self.num_rows:
                            self.world[row + 1][col] = -2

                        if col - 1 >= 0:
                            self.world[row][col - 1] = -2
        # 生成地图
        print("地图:")
        for var in self.world:
            print(var)
