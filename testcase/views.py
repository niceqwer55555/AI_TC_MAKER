from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TestCase, LLMProvider, PromptTemplate
from .forms import TestCaseForm
import json
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatDeepInfra
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from .config.settings import LLM_PROVIDERS, DEFAULT_MODELS
from .services.llm_service import LLMService
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

def index(request):
    """测试用例列表页面"""
    # 从配置中获取 LLM 提供商列表
    llm_providers = [
        {"id": provider_id, "name": config["name"]} 
        for provider_id, config in LLM_PROVIDERS.items()
    ]
    
    context = {
        'llm_providers': llm_providers,
        'testcases': [],  # 你的测试用例列表
        'prompt_templates': []  # 你的提示词模板列表
    }
    return render(request, 'testcase/index.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def generate_testcase(request):
    try:
        data = json.loads(request.body)
        provider = data.get('provider')
        prompt = data.get('prompt')
        
        from .config.settings import DEFAULT_MODELS
        model = DEFAULT_MODELS.get(provider)
        if not model:
            raise ValueError(f"未知的提供商: {provider}")
        
        logger.info(f"Using model {model} for provider {provider}")
        
        llm_service = LLMService()
        messages = [{"role": "user", "content": prompt}]
        response = llm_service.chat(messages, model)
        
        try:
            testcase_data = json.loads(response)
            # 如果返回的是列表，直接使用
            if isinstance(testcase_data, list):
                return JsonResponse({
                    'success': True,
                    'testcases': testcase_data  # 不需要额外的嵌套
                })
            # 如果是单个测试用例，包装成列表
            else:
                return JsonResponse({
                    'success': True,
                    'testcases': [testcase_data]
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': "Invalid JSON response from LLM"
            })
            
    except Exception as e:
        logger.error(f"Error in generate_testcase: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def edit_testcase(request, testcase_id):
    """编辑测试用例"""
    testcase = TestCase.objects.get(id=testcase_id)
    if request.method == 'POST':
        form = TestCaseForm(request.POST, instance=testcase)
        if form.is_valid():
            form.save()
            return redirect('testcase_list')
    else:
        form = TestCaseForm(instance=testcase)
    return render(request, 'testcase/edit.html', {'form': form})

def delete_testcase(request, testcase_id):
    """删除测试用例"""
    if request.method == 'POST':
        testcase = TestCase.objects.get(id=testcase_id)
        testcase.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': '仅支持POST请求'}, status=405)

# 工具函数
def call_chatgpt_api(prompt, api_key):
    """调用ChatGPT API"""
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个测试专家，请根据用户的需求生成测试用例。响应格式必须是JSON，包含name、description、steps、expected_result字段。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def call_deepseek_api(prompt, api_key):
    """调用Deepseek API"""
    # 实现Deepseek API调用逻辑
    pass

def get_template(request, template_id):
    """获取提示词模板"""
    template = PromptTemplate.objects.get(id=template_id)
    return JsonResponse({
        'template': template.template
    }) 