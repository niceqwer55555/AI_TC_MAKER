# LLM提供商配置
LLM_PROVIDERS = {
    "openai": {
        "name": "openai",
        "api_key": "your-openai-api-key",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-3.5-turbo", "gpt-4"]
    },
    "deepseek": {
        "name": "deepseek", 
        "api_key": "",  # 替换为你的 DeepSeek API 密钥
        "base_url": "https://api.deepseek.com/v1",  # 修正的 DeepSeek API 地址
        "models": ["deepseek-chat"]
    }
}

# 提供商默认模型映射
DEFAULT_MODELS = {
    "openai": "gpt-3.5-turbo",
    "deepseek": "deepseek-chat"
} 