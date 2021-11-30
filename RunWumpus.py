import Agent
import CreateWorld


if __name__ == "__main__":
    # 运行
    world = CreateWorld.World()
    world.generate_world()
    world.populate_indicators()
    agent = Agent.Agent(world)
    agent.explore()
