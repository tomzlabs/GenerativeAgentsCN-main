"""generative_agents.game"""

import os
import copy

from modules.utils import GenerativeAgentsMap, GenerativeAgentsKey
from modules import utils
from .maze import Maze
from .agent import Agent
from .remote_agent import RemoteAgent  # Import the new class


class Game:
    """The Game"""

    def __init__(self, name, static_root, config, conversation, logger=None):
        self.name = name
        self.static_root = static_root
        self.record_iterval = config.get("record_iterval", 30)
        self.logger = logger or utils.IOLogger()
        self.maze = Maze(self.load_static(config["maze"]["path"]), self.logger)
        self.conversation = conversation
        self.agents = {}
        if "agent_base" in config:
            agent_base = config["agent_base"]
        else:
            agent_base = {}
        storage_root = os.path.join(f"results/checkpoints/{name}", "storage")
        if not os.path.isdir(storage_root):
            os.makedirs(storage_root)
        for name, agent in config["agents"].items():
            agent_config = utils.update_dict(
                copy.deepcopy(agent_base), self.load_static(agent["config_path"])
            )
            agent_config = utils.update_dict(agent_config, agent)

            agent_config["storage_root"] = os.path.join(storage_root, name)
            
            # Check for remote flag
            if agent.get("is_remote", False):
                self.agents[name] = RemoteAgent(agent_config, self.maze, self.conversation, self.logger)
            else:
                self.agents[name] = Agent(agent_config, self.maze, self.conversation, self.logger)

    def get_agent(self, name):
        return self.agents[name]

    def agent_think(self, name, status):
        agent = self.get_agent(name)
        plan = agent.think(status, self.agents)
        info = {
            "currently": agent.scratch.currently,
            "associate": agent.associate.abstract(),
            "concepts": {c.node_id: c.abstract() for c in agent.concepts},
            "chats": [
                {"name": "self" if n == agent.name else n, "chat": c}
                for n, c in agent.chats
            ],
            "action": agent.action.abstract(),
            "schedule": agent.schedule.abstract(),
            "address": agent.get_tile().get_address(as_list=False),
        }
        if (
            utils.get_timer().daily_duration() - agent.last_record
        ) > self.record_iterval:
            info["record"] = True
            agent.last_record = utils.get_timer().daily_duration()
        else:
            info["record"] = False
        if agent.llm_available():
            info["llm"] = agent._llm.get_summary()
        title = "{}.summary @ {}".format(
            name, utils.get_timer().get_date("%Y%m%d-%H:%M:%S")
        )
        self.logger.info("\n{}\n{}\n".format(utils.split_line(title), agent))
        return {"plan": plan, "info": info}

    def load_static(self, path):
        return utils.load_dict(os.path.join(self.static_root, path))

    def reset_game(self):
        for a_name, agent in self.agents.items():
            agent.reset()
            title = "{}.reset".format(a_name)
            self.logger.info("\n{}\n{}\n".format(utils.split_line(title), agent))

    def swap_to_remote(self, agent_name, api_url):
        """
        Hot-swap an agent to a RemoteAgent dynamically.
        """
        if agent_name not in self.agents:
            return False, "Agent not found"
        
        current_agent = self.agents[agent_name]
        
        # If already remote, just update the URL
        if isinstance(current_agent, RemoteAgent):
            current_agent.api_url = api_url
            return True, f"Updated {agent_name} API URL to {api_url}"

        # Create config for remote agent based on current agent properties
        # We need to preserve essential config while adding remote params
        new_config = {
            "name": current_agent.name,
            "percept": current_agent.percept_config,
            "think": current_agent.think_config,
            "chat_iter": current_agent.chat_iter,
            "spatial": current_agent.spatial.to_dict() if hasattr(current_agent.spatial, "to_dict") else {}, # Re-initializing might be tricky without full config
            # Simpler approach: Create RemoteAgent and manually copy state
            "api_url": api_url
        }
        
        # NOTE: Ideally we'd reload from the original config file, but we might not have the path handy easily 
        # unless we stored it. The Agent init is complex.
        # Let's try to wrap the existing agent or re-instantiate carefully.
        # A safer pattern for hot-swapping:
        # 1. Instantiate RemoteAgent with same args as original used?
        # The original Game.__init__ loaded from files. Re-loading is safest.
        
        # Taking a shortcut for this demo: Modify the existing object class via mixin or brute replacement? 
        # Brute replacement is safer but requires config.
        # Let's use the stored config in Game (it might be in self.agents... wait, Agent doesn't store full raw config).
        # Actually, let's look at Game.__init__. It iterates config["agents"].
        
        # BETTER APPROACH: Just change the class of the instance (Python magic) or Monkey Patch the `think` method.
        # Changing class is cleaner for `reset` etc.
        
        current_agent.__class__ = RemoteAgent
        current_agent.api_url = api_url
        current_agent.logger.info(f"Hot-swapped {agent_name} to RemoteAgent targeting {api_url}")
        
        return True, "Success"


def create_game(name, static_root, config, conversation, logger=None):
    """Create the game"""

    utils.set_timer(**config.get("time", {}))
    GenerativeAgentsMap.set(GenerativeAgentsKey.GAME, Game(name, static_root, config, conversation, logger=logger))
    return GenerativeAgentsMap.get(GenerativeAgentsKey.GAME)


def get_game():
    """Get the gloabl game"""

    return GenerativeAgentsMap.get(GenerativeAgentsKey.GAME)
