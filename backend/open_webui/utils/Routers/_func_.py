from pydantic import BaseModel
from typing import Optional

from open_webui.utils.Routers.tool_router import ToolRouter
from open_webui.utils.Routers.model_router import ModelRouter
from open_webui.utils.Routers.guardrail_router import GuardrailRouter

from open_webui.models.tools import Tools


featured_tools = [
    {"web_search": "search the web"},
    {"code_interpreter": "interpret or execute code"},
    {"image_generation": "generate images"},
]

class Filter:
    class Valves(BaseModel):  
        pass

    def __init__(self):
        self.valves = self.Valves()
        self.tools = featured_tools
        self.tool_router: ToolRouter = None

    def inlet(self, body: dict) -> dict:
        self.tools = Tools.get_tools()
        self.tool_router = ToolRouter(
        tools={tool.id: tool.specs[0]['description'] for tool in self.tools}
    )
        
        self.tools.append(Tools.get_tools())
        query = body["messages"][-1]["content"]
        selected_tools = self.tool_router.route_query(query)
        _tools_, prob = selected_tools[0] if selected_tools else (None, None)
        if _tools_ in featured_tools.keys():
            body["features"][_tools_] = True
        body["tool_ids"] = [_tools_]
        print("===" * 10)
        print(f"Selected tool: {_tools_}\nProbability: {prob}")
        print("===" * 10)
        return body

    def stream(self, event: dict) -> dict:
        return event

    def outlet(self, body: dict) -> None:
        # This is where you manipulate model outputs.
        return body