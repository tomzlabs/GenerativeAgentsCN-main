"""generative_agents.modules.remote_agent"""

import requests
import json
from modules.agent import Agent
from modules import memory, utils

class RemoteAgent(Agent):
    """
    An agent that delegates decision making to an external API.
    """
    def __init__(self, config, maze, conversation, logger):
        super().__init__(config, maze, conversation, logger)
        self.api_url = config.get("api_url", "http://localhost:5000/agent/action")
        self.logger.info(f"RemoteAgent {self.name} initialized. Target API: {self.api_url}")

    def think(self, status, agents):
        """
        Override the default think method to query external API instead of LLM.
        """
        # 1. Update perception (simulated senses)
        self.percept()
        
        # 2. Gather context for the external bot
        context = self._gather_context(agents)
        
        # 3. Query external API
        try:
            self.logger.info(f"{self.name} sending state to {self.api_url}...")
            # Set a short timeout to prevent hanging the simulation
            response = requests.post(self.api_url, json=context, timeout=5) 
            
            if response.status_code == 200:
                data = response.json()
                self._apply_external_action(data)
            else:
                self.logger.error(f"RemoteAgent API Error: {response.status_code} - {response.text}")
                # Fallback: Stay idle or continue previous action? 
                # For now, we just pass to maintain game stability
                pass
                
        except Exception as e:
            self.logger.error(f"RemoteAgent Connection Failed: {e}")
        
        # 4. Generate plan structure required by the game engine
        # The game engine expects a specific dictionary structure to render the agent.
        
        # Calculate visual updates (emojis)
        emojis = {}
        if self.action:
            emojis[self.name] = {"emoji": self.get_event().emoji, "coord": self.coord}
            
        self.plan = {
            "name": self.name,
            "path": self.path, # Path updated by _apply_external_action -> move
            "emojis": emojis,
        }
        return self.plan

    def _gather_context(self, agents):
        """
        Package relevant game state into a clean JSON payload.
        """
        # Get nearby events that we have perceived
        perceived_events = []
        for concept in self.concepts:
            perceived_events.append(concept.event.abstract())

        # Get nearby agents
        nearby_agents_info = []
        for name, agent_obj in agents.items():
            if name == self.name: continue
            # Check distance (simple Manhattan or similar check could go here)
            # For now, we assume if they are in 'agents' list passed to think(), they are relevant context
            nearby_agents_info.append({
                "name": name,
                "position": agent_obj.coord,
                "action": agent_obj.get_event().abstract()
            })

        return {
            "agent_name": self.name,
            "tick": utils.get_timer().daily_duration(),
            "time": utils.get_timer().get_date(),
            "position": self.coord,
            "status": self.status,
            "perceived_events": perceived_events,
            "nearby_agents": nearby_agents_info,
            "current_action": self.action.abstract() if self.action else None
        }

    def _apply_external_action(self, data):
        """
        Translate external API response to internal game actions.
        Expected data format:
        {
            "action_type": "move" | "wait" | "chat",
            "target_coord": [x, y],
            "description": "Walking to the bar",
            "emoji": "🚶"
        }
        """
        action_type = data.get("action_type", "wait")
        
        if action_type == "move":
            target = data.get("target_coord")
            if target:
                # Find path using internal maze solver logic
                self.path = self.maze.find_path(self.coord, target)
                # Take one step if path exists
                if self.path:
                    next_step = self.path[0]
                    # Update internal position
                    self.move(next_step, self.path)
            
            description = data.get("description", "moving")
            emoji = data.get("emoji", "🚶")
            
            # Create a simple action event for history
            event = memory.Event(self.name, "is", description, address=[f"{self.coord}"], emoji=emoji)
            self.action = memory.Action(event, event, duration=10, start=utils.get_timer().get_date())

        elif action_type == "chat":
            # Chat logic is complex in this engine (requires 'associate' memory and LLM calls).
            # For a basic remote agent, we might just assume 'speaking' state without 
            # full conversation simulation unless the external bot handles that text too.
            pass
