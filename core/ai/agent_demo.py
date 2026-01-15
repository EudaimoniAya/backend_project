from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from operations.settings import settings
from operations.cost_tracking import CostTrackingCallback
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


# 1. 定义工具输入模型
class WeatherQueryInput(BaseModel):
    location: str = Field(description="需要查询天气的城市名称")


# 2. 创建天气查询工具（固定返回晴朗）
class SimpleWeatherTool(BaseTool):
    name: str = "simple_weather_tool"
    description: str = "查询指定城市的天气情况"
    args_schema: Type[BaseModel] = WeatherQueryInput

    def _run(self, location: str) -> str:
        """执行工具，固定返回晴朗天气"""
        print(f"[工具执行] 查询城市: {location}")
        return f"{location}的天气是晴朗，温度25°C，湿度50%，东南风3级"

    async def _arun(self, location: str) -> str:
        """异步执行工具"""
        return self._run(location)


# 1. 获取回调处理器
cost_tracker = CostTrackingCallback()

chat_llm_ds = ChatDeepSeek(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key,
    api_base=settings.deepseek_api_base,
    temperature=1
)

agent = create_agent(
    model=chat_llm_ds,
    system_prompt="你是一个智能助手，回答问题前尽量调用工具",
    tools=[SimpleWeatherTool()],
)

res = agent.invoke({
    "role": "human",
    "message": "你好，今天南昌天气怎么样？"},
    config={"callbacks": [cost_tracker]}
)
print(res)
