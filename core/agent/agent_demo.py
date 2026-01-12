from langchain_core.callbacks import BaseCallbackHandler
from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from operations.settings import settings


# 1. 定义一个最简单的回调处理器
class SimpleCallback(BaseCallbackHandler):
    """最简单的回调处理器，仅打印事件触发信息"""
    def on_llm_start(self, serialized, prompts, **kwargs):
        """当LLM开始处理时触发"""
        print(f"[回调被触发] LLM开始处理，收到 {len(prompts)} 个提示")
        run_id = kwargs.get("run_id", "unknown")
        print(f"          本次运行ID: {run_id}")


class VerboseCallback(BaseCallbackHandler):
    """打印更多事件的回调处理器"""

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[LLM 开始] Run ID: {kwargs.get('run_id')}")

    def on_llm_end(self, response, **kwargs):
        # response 是 LLMResult 类型
        # 1. 提取第一个生成结果（通常只有一个）
        if response.generations and len(response.generations) > 0:
            first_gen_list = response.generations[0]  # 这是一个列表
            if first_gen_list and len(first_gen_list) > 0:
                generation = first_gen_list[0]  # 第一个 ChatGeneration

                # 2. 从 generation 中提取 AIMessage
                if hasattr(generation, 'message'):
                    ai_message = generation.message
                    # 现在可以访问 content 了
                    content_preview = ai_message.content[:50] + "..." if len(
                        ai_message.content) > 50 else ai_message.content
                    print(f"[LLM 结束] 生成回复: {content_preview}")

                    # 3. 提取token使用信息（你关心的成本追踪数据）
                    if hasattr(ai_message, 'usage_metadata'):
                        tokens = ai_message.usage_metadata
                        print(
                            f"          Token使用: 输入{tokens.get('input_tokens')}, 输出{tokens.get('output_tokens')}, 总计{tokens.get('total_tokens')}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"[工具 开始] 调用工具: {serialized.get('name')}")

    def on_tool_end(self, output, **kwargs):
        print(f"[工具 结束] 工具返回结果")


from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class AccurateCallback(BaseCallbackHandler):
    """准确处理不同类型响应的回调处理器"""

    def on_llm_start(self, serialized, prompts, **kwargs):
        # 查看被调用的模型究竟是什么
        model_name = serialized.get('name', serialized.get('id', ['Unknown']))
        print(f"[LLM开始] 模型标识: {model_name}")
        print(f"[LLM开始] 是否是聊天模型: {serialized.get('is_chat', 'Unknown')}")

    def on_llm_end(self, response: LLMResult, **kwargs):
        print(f"[LLM处理完成]")

        try:
            if response.generations:
                first_gen = response.generations[0][0]

                # 首要目标：提取 Token 使用数据
                if hasattr(first_gen, 'message'):
                    ai_message = first_gen.message

                    # 1. 找到成本追踪的核心 —— usage_metadata
                    if hasattr(ai_message, 'usage_metadata'):
                        tokens = ai_message.usage_metadata
                        input_tokens = tokens.get('input_tokens')
                        output_tokens = tokens.get('output_tokens')

                        # 这是你所有成本计算的基石！
                        print(f"✅ [Token数据获取成功]")
                        print(f"   输入Token: {input_tokens}")
                        print(f"   输出Token: {output_tokens}")
                        print(f"   总计Token: {tokens.get('total_tokens')}")

                        # 你可以在这里立刻进行成本计算
                        # cost = calculate_cost(model_name, input_tokens, output_tokens)

                    # 2. 同时，响应内容也在这里
                    print(f"   回复预览: {ai_message.content[:50]}...")

        except Exception as e:
            print(f"解析响应时出错: {e}")

    def on_chat_model_end(self, response, **kwargs):
        """专用处理聊天模型结束事件（如果可用）"""
        # 这个方法的response可能已经是处理过的消息列表
        print(f"[聊天模型处理完成]")
        # 这里可以更直接地处理消息

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM错误] {error}")


chat_llm_ds = ChatDeepSeek(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key,
    api_base=settings.deepseek_api_base,
    temperature=1
)

agent = create_agent(
    model=chat_llm_ds,
    system_prompt="你是一个智能助手",
)

# 2. 实例化回调处理器
callback = SimpleCallback()

res = agent.invoke({
    "role": "human",
    "message": "你好，你叫什么？"},
    config={"callbacks": [AccurateCallback()]}
)
print(res)
