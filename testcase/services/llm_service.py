from openai import OpenAI
import requests
from typing import List, Dict, Any
from ..config.settings import LLM_PROVIDERS
from .prompts import BasePrompt, TestCasePrompt, BugReportPrompt
import json
import re
import os

class LLMService:
    """统一的 LLM 服务类"""
    
    # prompt 类型映射
    PROMPT_TYPES = {
        "test_case": TestCasePrompt,
        "bug_report": BugReportPrompt,
        # 可以添加更多类型
    }
    
    def __init__(self):
        # 缓存已创建的客户端连接
        self._clients = {}
        
    def chat(self, messages: List[Dict[str, str]], model_name: str, prompt_type: str = "test_case") -> str:
        """
        统一的对话接口
        :param messages: 对话历史记录
        :param model_name: 模型名称，如 'gpt-3.5-turbo' 或 'deepseek-chat'
        :param prompt_type: 提示类型，如 'test_case' 或 'bug_report'
        :return: 模型回复的文本内容
        """
        try:
            # 获取对应的 prompt 类
            prompt_class = self.PROMPT_TYPES.get(prompt_type)
            if not prompt_class:
                raise ValueError(f"未知的 prompt 类型: {prompt_type}")
            
            # 创建 prompt 实例并获取系统 prompt
            prompt_instance = prompt_class()
            system_prompt = prompt_instance.get_system_prompt()
            
            # 将系统 prompt 添加到消息列表的开头
            full_messages = [system_prompt] + messages
            
            # 获取模型对应的提供商配置
            provider_config = self._get_provider_config(model_name)
            
            # 获取或创建客户端
            client = self._get_client(provider_config)
            
            # 调用对应的方法并获取响应
            if provider_config["name"] == "openai":
                response = self._chat_openai(client, full_messages, model_name)
            elif provider_config["name"] == "deepseek":
                response = self._chat_deepseek(client, full_messages, model_name)
            elif provider_config["name"] == "qwen":
                response = self._chat_qwen(client, full_messages, model_name)
            else:
                raise ValueError(f"不支持的提供商: {provider_config['name']}")
            
            print(f"Raw LLM response: {response}")
            
            # 提取 ```json 和 ``` 之间的内容
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # 如果没有 markdown 格式，尝试直接提取 JSON
                json_match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    # 最后尝试提取单个对象
                    json_match = re.search(r'\{\s*".*?\}\s*', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                    else:
                        raise ValueError("No valid JSON found in response")

            try:
                # 解析提取的 JSON
                testcase = json.loads(json_str)
                # 如果是单个测试用例，转换为列表
                if isinstance(testcase, dict) and "name" in testcase and "steps" in testcase:
                    testcases = [testcase]
                else:
                    # 如果已经是列表，直接使用
                    testcases = testcase if isinstance(testcase, list) else [testcase]
                
                print(f"Final testcases to return: {json.dumps(testcases, indent=2, ensure_ascii=False)}")
                return json.dumps(testcases)
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                raise ValueError("Invalid JSON format in response")
                
        except Exception as e:
            print(f"Chat error: {str(e)}")
            raise

    def _get_provider_config(self, model_name: str) -> Dict:
        """根据模型名称获取对应的提供商配置"""
        for provider_config in LLM_PROVIDERS.values():
            if model_name in provider_config["models"]:
                return provider_config
        raise ValueError(f"未知的模型: {model_name}")

    def _get_client(self, provider_config: Dict) -> Any:
        """获取或创建API客户端"""
        provider_name = provider_config["name"]
        if provider_name not in self._clients:
            # 尝试从环境变量获取 api_key，如果没有则使用配置文件中的值
            api_key = os.getenv(f"{provider_name.upper()}_API_KEY") or provider_config["api_key"]
            
            if provider_name == "openai":
                self._clients[provider_name] = OpenAI(
                    api_key=api_key,
                    base_url=provider_config["base_url"]
                )
            elif provider_name in ["deepseek", "qwen"]:
                self._clients[provider_name] = {
                    "api_key": api_key,
                    "base_url": provider_config["base_url"],
                    "headers": {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                }
        return self._clients[provider_name]

    def _chat_openai(self, client: OpenAI, messages: List[Dict[str, str]], model: str) -> str:
        """调用 OpenAI API"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            raise

    def _chat_deepseek(self, client: Dict, messages: List[Dict[str, str]], model: str) -> str:
        """调用 DeepSeek API"""
        try:
            # 移除多余的 v1 路径
            url = f"{client['base_url']}/chat/completions"  # 修改这里
            print(f"Calling DeepSeek API: {url}")  # 调试日志
            
            response = requests.post(
                url,
                headers=client["headers"],
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=30,
                verify=False  # 临时禁用 SSL 验证
            )
            
            print(f"DeepSeek API response: {response.text}")
            
            if response.status_code != 200:
                raise ValueError(f"API错误: {response.status_code} - {response.text}")
                
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise
        except (KeyError, IndexError) as e:
            print(f"Response parsing error: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    def _chat_qwen(self, client: Dict, messages: List[Dict[str, str]], model: str) -> str:
        """调用 Qwen API"""
        try:
            url = f"{client['base_url']}/chat/completions"
            print(f"Calling Qwen API: {url}")  # 打印请求URL
            
            request_data = {
                "model": model,
                "messages": messages
            }
            print(f"Request data: {json.dumps(request_data, indent=2, ensure_ascii=False)}")  # 打印请求数据
            
            response = requests.post(
                url,
                headers=client["headers"],
                json=request_data,
                timeout=30
            )
            
            print(f"Qwen API response status: {response.status_code}")  # 打印响应状态码
            print(f"Qwen API response: {response.text}")  # 打印完整响应
            
            if response.status_code != 200:
                raise ValueError(f"API错误: {response.status_code} - {response.text}")
                
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]
            print(f"Extracted content: {result}")  # 打印提取的内容
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise
        except (KeyError, IndexError) as e:
            print(f"Response parsing error: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise 