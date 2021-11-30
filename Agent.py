# world_knowledge
# 已知的地图加预测标记
# 8: 未知； 0：空房间； -1：气味； -2：微风； 1：怪物； 2：陷阱； 5:黄金

# world_visited
# 记录走过的位置
# 0:没去过， 1：去过

# path_out_of_cave
# 记录去终点的路径
# 1:上 2：下 3：左 4：右

#
class Agent:
    def __init__(self, world):
        self.world = world
        self.world_knowledge = [[8] * 10 for _ in range(10)]
        self.world_visited = [[0] * 10 for _ in range(10)]
        self.path_out_of_cave = [0] * 200
        self.path_return_cave = [0] * 200
        # 入口
        self.world.cave_entrance_row = self.world.agent_row
        self.world.cave_entrance_col = self.world.agent_col
        # 属性初始化
        self.exited = False
        self.has_dead = False
        self.found_gold = False
        # 步数，弓箭，分数，铁锹初始化
        self.steps = 0
        self.arrows = 3
        self.score = 0
        self.spade = 1
        # 标记初始化
        self.add_indicators_to_knowledge()
        self.is_exit()
        self.mark_visited()
        self.predict_wumpus()
        self.predict_pits()
        print("当前房间：", self.world.agent_row * 10 + self.world.agent_col + 1)

    # 按着来时路径回退一步
    def go_back_one_tile(self):

        if self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 2:
            self.move('u')
        elif self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 1:
            self.move('d')
        elif self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 3:
            self.move('r')
        else:
            self.move('l')

    # 找到金子后回到终点
    def go_back_to_end(self):
        if self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 2:
            self.move('u')
        elif self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 1:
            self.move('d')
        elif self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 3:
            self.move('r')
        else:
            self.move('l')

    # wumpus 开始移动，顺时针 bfs
    def explore(self):
        already_moved = False

        while not self.has_dead and not self.exited:
            if self.found_gold and self.world.agent_row * 10 + self.world.agent_col + 1 != 90 and \
                    self.world.agent_row * 10 + self.world.agent_col + 1 != 99:
                if self.world_visited[9][8] == 1 or self.world_visited[8][9] == 1:
                    self.go_back_to_end()
                    already_moved = True
            if self.world.agent_col + 1 < 10:
                if self.world_visited[self.world.agent_row][self.world.agent_col + 1] == 0 and not already_moved:
                    already_moved = self.move('r')

            if self.world.agent_row + 1 < 10:
                if self.world_visited[self.world.agent_row + 1][self.world.agent_col] == 0 and not already_moved:
                    already_moved = self.move('d')

            if self.world.agent_col - 1 >= 0:
                if self.world_visited[self.world.agent_row][self.world.agent_col - 1] == 0 and not already_moved:
                    already_moved = self.move('l')

            if self.world.agent_row - 1 >= 0:
                if self.world_visited[self.world.agent_row - 1][self.world.agent_col] == 0 and not already_moved:
                    already_moved = self.move('u')

            # 当前位置没有可去的房间
            if not already_moved:
                # 退出游戏
                if self.world.agent_row == self.world.cave_entrance_row and \
                        self.world.agent_col == self.world.cave_entrance_col:
                    print("地图错误")
                    break
                else:  # 后退一步
                    self.go_back_one_tile()

            print("当前房间：", self.world.agent_row * 10 + self.world.agent_col + 1, "\n")
            already_moved = False
        if self.has_dead:
            print("你死了 ！游戏结束")
        elif self.exited:
            print("你赢了！最终得分:", self.score)

    """
    尝试向 direction 移动一步，如果移动成功就更新 agent 的知识
    u: upper，向上走
    d: down，向下走
    l: left，向左走
    r: right，向右走
    """

    def move(self, direction):

        successful_move = False
        if self.has_dead:
            return False
        if direction == 'u':
            if self.is_safe_move(self.world.agent_row - 1, self.world.agent_col):
                successful_move = self.move_up()
        if direction == 'r':
            if self.is_safe_move(self.world.agent_row, self.world.agent_col + 1):
                successful_move = self.move_right()
        if direction == 'd':
            if self.is_safe_move(self.world.agent_row + 1, self.world.agent_col):
                successful_move = self.move_down()
        if direction == 'l':
            if self.is_safe_move(self.world.agent_row, self.world.agent_col - 1):
                successful_move = self.move_left()

        # 移动成功，更新 agent 的知识
        if successful_move:

            self.confirm_whether_is_dead()
            self.is_exit()
            self.mark_visited()
            self.add_indicators_to_knowledge()
            self.predict_wumpus()
            self.predict_pits()
            self.clean_predictions()

            self.steps += 1

            if self.world_knowledge[self.world.agent_row][self.world.agent_col] == 5 and self.spade > 0:
                self.found_gold = True
                self.score += 1000
                self.spade -= 1
                print("铁锹数量：", self.spade, "分数:", self.cal_score())
            else:
                print("铁锹数量：", self.spade, "分数:", self.cal_score())

            # 没发现 gold 就记录下当前房间，退出洞穴的时候要原路返回

        return successful_move

    # 更新关于 agent 所在房间的标记。如果杀死该房间怪物，更新world
    def add_indicators_to_knowledge(self):
        if self.world.world[self.world.agent_row][self.world.agent_col] == 1 and self.arrows >= 0:
            self.world.world[self.world.agent_row][self.world.agent_col] = 0
            self.update_world(self.world.agent_row, self.world.agent_col)
        else:
            self.world_knowledge[self.world.agent_row][self.world.agent_col] = \
                self.world.world[self.world.agent_row][self.world.agent_col]

    # 如果当前位置发现 breeze，更新 pits 的可能位置
    def predict_pits(self):
        if self.world.world[self.world.agent_row][self.world.agent_col] == -2 and \
                self.world.agent_row - 1 >= 0:
            if self.world_visited[self.world.agent_row - 1][self.world.agent_col] == 0:
                self.world_knowledge[self.world.agent_row - 1][self.world.agent_col] = 2

        if self.world.world[self.world.agent_row][self.world.agent_col] == -2 and \
                self.world.agent_col + 1 < self.world.num_cols:
            if self.world_visited[self.world.agent_row][self.world.agent_col + 1] == 0 and \
                    self.world_knowledge[self.world.agent_row][self.world.agent_col + 1] != -2:
                self.world_knowledge[self.world.agent_row][self.world.agent_col + 1] = 2

        if self.world.world[self.world.agent_row][self.world.agent_col] == -2 and \
                self.world.agent_row + 1 < self.world.num_rows:
            if self.world_visited[self.world.agent_row + 1][self.world.agent_col] == 0 and \
                    self.world_knowledge[self.world.agent_row + 1][self.world.agent_col] != -2:
                self.world_knowledge[self.world.agent_row + 1][self.world.agent_col] = 2

        if self.world.world[self.world.agent_row][self.world.agent_col] == -2 and \
                self.world.agent_col - 1 >= 0:
            if self.world_visited[self.world.agent_row][self.world.agent_col - 1] == 0 and \
                    self.world_knowledge[self.world.agent_row][self.world.agent_col - 1] != -2:
                self.world_knowledge[self.world.agent_row][self.world.agent_col - 1] = 2

    # 如果当前位置发现 stench，更新潜在 wumpus 的位置
    def predict_wumpus(self):
        if self.world.world[self.world.agent_row][self.world.agent_col] == -1 and \
                self.world.agent_row - 1 >= 0:
            if self.world_knowledge[self.world.agent_row - 1][self.world.agent_col] == 8 and \
                    self.world_knowledge[self.world.agent_row - 1][self.world.agent_col] != -1:
                self.world_knowledge[self.world.agent_row - 1][self.world.agent_col] = 1

        if self.world.world[self.world.agent_row][self.world.agent_col] == -1 and \
                self.world.agent_col + 1 < self.world.num_cols:
            if self.world_knowledge[self.world.agent_row][self.world.agent_col + 1] == 8 and \
                    self.world_knowledge[self.world.agent_row][self.world.agent_col + 1] != -1:
                self.world_knowledge[self.world.agent_row][self.world.agent_col + 1] = 1

        if self.world.world[self.world.agent_row][self.world.agent_col] == -1 and \
                self.world.agent_row + 1 < self.world.num_rows:
            if self.world_knowledge[self.world.agent_row + 1][self.world.agent_col] == 8 and \
                    self.world_knowledge[self.world.agent_row + 1][self.world.agent_col] != -1:
                self.world_knowledge[self.world.agent_row + 1][self.world.agent_col] = 1

        if self.world.world[self.world.agent_row][self.world.agent_col] == -1 and \
                self.world.agent_col - 1 >= 0:
            if self.world_knowledge[self.world.agent_row][self.world.agent_col - 1] == 8 and \
                    self.world_knowledge[self.world.agent_row][self.world.agent_col - 1] != -1:
                self.world_knowledge[self.world.agent_row][self.world.agent_col - 1] = 1

    # 基于记忆清除不合理的假设，同时统计记忆中所有 stench 数量
    def clean_predictions(self):

        for i in range(self.world.num_rows):
            for j in range(self.world.num_cols):
                # 记忆中一个潜在 wumpus 身边有不存在 stench 的房间，那这就不可能是一个真的 wumpus
                if self.world_knowledge[i][j] == 1:
                    if i - 1 >= 0 and self.world_visited[i - 1][j] == 1 and self.world_knowledge[i - 1][j] != -1:
                        self.world_knowledge[i][j] = 0

                    if j + 1 < self.world.num_cols and self.world_visited[i][j + 1] == 1 and \
                            self.world_knowledge[i][j + 1] != -1:
                        self.world_knowledge[i][j] = 0

                    if i + 1 < self.world.num_rows and self.world_visited[i + 1][j] == 1 and \
                            self.world_knowledge[i + 1][j] != -1:
                        self.world_knowledge[i][j] = 0

                    if j - 1 >= 0 and self.world_visited[i][j - 1] == 1 and self.world_knowledge[i][j - 1] != -1:
                        self.world_knowledge[i][j] = 0

                # 记忆中一个潜在 pit 身边有不存在 breeze 的房间，那这就不可能是一个真的 pit
                if self.world_knowledge[i][j] == 2:
                    if i - 1 >= 0 and self.world_visited[i - 1][j] == 1 and self.world_knowledge[i - 1][j] != -2:
                        self.world_knowledge[i][j] = 0

                    if j + 1 < self.world.num_cols and self.world_visited[i][j + 1] == 1 \
                            and self.world_knowledge[i][j + 1] != -2:
                        self.world_knowledge[i][j] = 0

                    if i + 1 < self.world.num_rows and self.world_visited[i + 1][j] == 1 and \
                            self.world_knowledge[i + 1][j] != -2:
                        self.world_knowledge[i][j] = 0

                    if j - 1 >= 0 and self.world_visited[i][j - 1] == 1 and self.world_knowledge[i][j - 1] != -2:
                        self.world_knowledge[i][j] = 0

    # 更新杀死怪物的地图
    def update_world(self, row, col):

        if row - 1 >= 0:
            self.world.world[row - 1][col] = 0
            self.world_knowledge[row - 1][col] = 0

        if row + 1 < self.world.num_cols:
            self.world.world[row + 1][col] = 0
            self.world_knowledge[row + 1][col] = 0

        if col + 1 < self.world.num_rows:
            self.world.world[row][col + 1] = 0
            self.world_knowledge[row][col + 1] = 0

        if col - 1 >= 0:
            self.world.world[row][col - 1] = 0
            self.world_knowledge[row][col - 1] = 0

    # 移动
    def move_up(self):
        if self.world.agent_row - 1 >= 0:
            self.world.agent_row -= 1
            if not self.found_gold and self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 0:
                if self.world_visited[9][8] == 1 or self.world_visited[8][9] == 1:
                    self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 1

            if self.world_visited[self.world.agent_row][self.world.agent_col] == 0:
                self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 1
            return True
        else:
            return False

    def move_right(self):
        if self.world.agent_col + 1 < 10:
            self.world.agent_col += 1
            if not self.found_gold and self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 0:
                if self.world_visited[9][8] == 1 or self.world_visited[8][9] == 1:
                    self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 4
            if self.world_visited[self.world.agent_row][self.world.agent_col] == 0:
                self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 4
            return True
        else:
            return False

    def move_down(self):
        if self.world.agent_row + 1 < 10:
            self.world.agent_row += 1
            if not self.found_gold and self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 0:
                if self.world_visited[9][8] == 1 or self.world_visited[8][9] == 1:
                    self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 2
            if self.world_visited[self.world.agent_row][self.world.agent_col] == 0:
                self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 2
            return True
        else:
            return False

    def move_left(self):
        if self.world.agent_col - 1 >= 0:
            self.world.agent_col -= 1
            if not self.found_gold and self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] == 0:
                if self.world_visited[9][8] == 1 or self.world_visited[8][9] == 1:
                    self.path_return_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 3
            if self.world_visited[self.world.agent_row][self.world.agent_col] == 0:
                self.path_out_of_cave[self.world.agent_row * 10 + self.world.agent_col + 1] = 3
            return True
        else:
            return False

    # 标记 agent 当前房间为已走过
    def mark_visited(self):
        self.world_visited[self.world.agent_row][self.world.agent_col] = 1

    # 判断是否离开
    def is_exit(self):
        if self.world.agent_row * 10 + self.world.agent_col + 1 == 100:
            self.exited = True

    # 判断是否死亡
    def confirm_whether_is_dead(self):
        if self.world.world[self.world.agent_row][self.world.agent_col] == 2:
            print("掉进陷阱里")
            self.score = -1000
            self.has_dead = True

    # 判断 [row, col] 房间是否安全。只有在房间合法且一定安全的时候返回 True
    def is_safe_move(self, row, col):
        if row * 10 + col + 1 == 100:
            print("不提前射箭    剩余箭数量：", self.arrows)
            return self.found_gold

        if row < 0 or col < 0 or row >= self.world.num_rows or col >= self.world.num_cols:
            return False

        if self.world_knowledge[row][col] == 2:
            return False

        if self.world_knowledge[row][col] == 1:
            if self.arrows > 0:
                self.arrows -= 1
                print("提前射箭!!!  剩余箭数量：", self.arrows)
                self.world_knowledge[row][col] = 0
                return True
            else:
                return False

        print("不提前射箭    剩余箭数量：", self.arrows)
        return True

    # 计算分数
    def cal_score(self):
        self.score -= 1

        return self.score
