from langchain_core.outputs import LLMResult
from operations.settings import settings

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.runnables.base import Runnable


class CostTrackingCallback(BaseCallbackHandler):
    """使用集中配置的成本追踪回调"""
    def __init__(self):
        super().__init__()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.call_records = []

    def _detect_model_name(self, ai_message) -> str:    # noqa
        """从AIMessage中检测模型名称（根据你的提供商调整）"""
        # 示例：从 response_metadata 提取
        metadata = getattr(ai_message, 'response_metadata', {})
        # 不同提供商字段可能不同，需要适配
        name = metadata.get('model_name') or metadata.get('model') or 'unknown'
        # 可以做一个映射，将提供商名称标准化为你配置表中的键
        return name.lower()

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"[回调] 工具调用开始: {serialized.get('name', 'unknown')}")

    def on_tool_end(self, output, **kwargs):
        print(f"[回调] 工具调用结束，返回: {str(output)[:50]}...")

    def on_llm_end(self, response: LLMResult, **kwargs):
        print(f"[LLM处理完成]")
        print(response)
        print("------")
        print(type(response))

        try:
            if response.generations:
                first_gen = response.generations[0][0]

                if hasattr(first_gen, 'message'):
                    ai_message = first_gen.message

                    if hasattr(ai_message, 'usage_metadata'):
                        tokens = ai_message.usage_metadata
                        input_tokens = tokens.get('input_tokens', 0)
                        output_tokens = tokens.get('output_tokens', 0)

                        # 从配置系统获取价格并计算成本
                        model_name = self._detect_model_name(ai_message)    # 需要实现一个模型名检测方法
                        pricing = settings.get_pricing(model_name)  # 使用全局配置

                        # 计算本次调用成本
                        call_cost = (
                            (input_tokens / 1000) * pricing.input_price_per_1k +
                            (output_tokens / 1000) * pricing.output_price_per_1k
                        )

                        # 累加Token和单价到实例变量
                        self.total_input_tokens += input_tokens
                        self.total_output_tokens += output_tokens
                        self.total_cost_usd += call_cost
                        print(f"💰 单次成本: ${call_cost:.6f} | 累计成本: ${self.total_cost_usd:.6f}")

                        # 记录本次调用明细（可选）
                        self.call_records.append({
                            'run_id': kwargs.get('run_id'),
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'total_tokens': input_tokens + output_tokens,
                            'content_preview': ai_message.content[:50]
                        })

                        print(f"✅ 单次Token数据 -> 输入: {input_tokens}, 输出: {output_tokens}")
                        print(f"📊 累计Token数据 -> 输入: {self.total_input_tokens}, 输出: {self.total_output_tokens}")

        except Exception as e:
            print(f"解析响应时出错: {e}")

    def get_summary(self):
        """获取累计摘要"""
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': total_tokens,
            'call_count': len(self.call_records)
        }
