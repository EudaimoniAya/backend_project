import json


def format_json(data, indent=4, ensure_ascii=False):
    """
    格式化输出JSON字符串

    参数:
        data: 要格式化的数据（字典、列表等）
        indent: 缩进空格数，默认为4
        ensure_ascii: 是否确保ASCII编码，False时支持中文

    返回:
        格式化后的JSON字符串
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, sort_keys=False)
    except Exception as e:
        return f"JSON格式化错误: {str(e)}"


# 使用示例
if __name__ == "__main__":
    sample_data = (
        "{'token_usage': {'completion_tokens': 38, 'prompt_tokens': 7, 'total_tokens': 45, 'completion_tokens_details': "
        "None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}, 'prompt_cache_hit_tokens': 0, "
        "'prompt_cache_miss_tokens': 7}, 'model_provider': 'deepseek', 'model_name': 'deepseek-chat', "
        "'system_fingerprint': 'fp_eaab8d114b_prod0820_fp8_kvcache', 'id': '1f27d485-7f3c-456f-ba95-8b1ddcbca6a3', "
        "'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019bac98-3988-70c0-8fcb-d1ad8e961ce8-0', tool_calls=["
        "], invalid_tool_calls=[], usage_metadata={'input_tokens': 7, 'output_tokens': 38, 'total_tokens': 45, "
        "'input_token_details': {'cache_read': 0}, 'output_token_details': {}}"
    )

    # 默认缩进（4个空格）
    print("=== 默认缩进（4个空格）===")
    print(format_json(sample_data))

    # 自定义缩进（2个空格）
    print("\n=== 自定义缩进（2个空格）===")
    print(format_json(sample_data, indent=2))

    # 无缩进
    print("\n=== 无缩进（紧凑格式）===")
    print(format_json(sample_data, indent=0))
