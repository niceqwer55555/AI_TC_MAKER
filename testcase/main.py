from services.llm_service import LLMService
from models import LLMProvider

def main():
    # 确保数据库中有必要的提供商配置
    try:
        # 创建服务实例
        llm_service = LLMService()

        # 准备对话消息
        messages = [
            {"role": "user", "content": "你好，请介绍一下自己"}
        ]

        # 使用不同的模型
        gpt_response = llm_service.chat(messages, "gpt-3.5-turbo")
        print("GPT Response:", gpt_response)

        deepseek_response = llm_service.chat(messages, "deepseek-chat")
        print("DeepSeek Response:", deepseek_response)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 