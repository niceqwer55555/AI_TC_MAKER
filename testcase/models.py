from django.db import models

class LLMProvider(models.Model):
    """大模型提供商"""
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class TestCase(models.Model):
    """测试用例模型"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '生效'),
        ('deprecated', '废弃')
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    steps = models.TextField()
    expected_result = models.TextField()
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    llm_provider = models.ForeignKey(LLMProvider, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

class PromptTemplate(models.Model):
    """提示词模板"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    template = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 