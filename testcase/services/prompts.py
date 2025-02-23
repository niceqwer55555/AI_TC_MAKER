from abc import ABC, abstractmethod
from typing import Dict

class BasePrompt(ABC):
    @abstractmethod
    def get_system_prompt(self) -> Dict[str, str]:
        pass

class TestCasePrompt(BasePrompt):
    def get_system_prompt(self) -> Dict[str, str]:
        return {
            "role": "system",
            "content": """你是一个测试用例生成助手。请根据用户的描述生成测试用例，并以JSON格式返回。
返回的JSON必须包含以下字段：
- name: 测试用例名称
- steps: 测试步骤（数组格式，每个步骤都必须包含序号，如"1. 打开登录页面"）
- expected_results: 预期结果（数组格式，与步骤一一对应，每个结果都必须包含序号，如"1. 登录页面成功加载"）

示例格式：
{
    "name": "测试用例名称",
    "steps": [
        "1. 第一个步骤",
        "2. 第二个步骤",
        "3. 第三个步骤"
    ],
    "expected_results": [
        "1. 第一个预期结果",
        "2. 第二个预期结果",
        "3. 第三个预期结果"
    ]
}

注意：
1. 测试用例名称不进行编号，但是每个步骤和预期结果必须包含序号
2. 步骤和预期结果的序号必须一一对应
3. 序号必须从1开始连续递增
"""
        }

# 可以添加其他类型的 prompt
class BugReportPrompt(BasePrompt):
    def get_system_prompt(self) -> Dict[str, str]:
        return {
            "role": "system",
            "content": "你是一个缺陷报告生成助手..."  # 具体内容
        } 