# LLM提供商配置
LLM_PROVIDERS = {
    "openai": {
        "name": "openai",
        "api_key": "sk-09xb54w68BfJ3b2rCb5108F46f98414990578fBf3f5e7aBa",
        "base_url": "http://10.17.18.162:3001/v1",
        "models": ["coder"]
    },
    "deepseek": {
        "name": "deepseek", 
        "api_key": "sk-09xb54w68BfJ3b2rCb5108F46f98414990578fBf3f5e7aBa",  # 替换为你的 DeepSeek API 密钥
        "base_url": "http://10.17.18.162:3001/v1",  # 修正的 DeepSeek API 地址
        "models": ["coder"]
    },
    "qwen": {
        "name": "qwen",
        "api_key": "",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-plus"]
    }
}

# 提供商默认模型映射
DEFAULT_MODELS = {
    "deepseek": "coder",
    "openai": "coder",
    "qwen": "qwen-plus"
} 