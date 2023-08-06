import types
from django.http import HttpRequest
from functools import partial

__all__ = ['form_validator',
           'RequestMethodError',
           'FormValidationError']


class RequestMethodError(Exception):
    """请求方法错误"""


class FormValidationError(Exception):
    """表单验证失败"""


def form_validator(form=None, *, must_method: str = None):
    """
    将django的forms.Form包装成一个表单验证装饰器，下面是演示：

    # 1.LoginForm变成了一个表单验证装饰器
    @form_validator
    class LoginForm(forms.Form):
        username = forms.CharField(required=True)
        password = forms.CharField(required=True)

    # 2.LoginForm装饰到接口函中
    @LoginForm
    def login_view(request):
        pass

    # 3.指定请求方法
    @form_validator(must_method)
    class LoginForm(forms.Form):
        pas

    # 4.定义Form时从其它Form中摘取字段
    @form_validator
    class A(forms.Form): # 定义一个AForm
        username = forms.CharField(required=True)

        def clean_username(self):
            return self.cleaned_data['username']

    @form_validator  # Form B从Form A中摘取username和clean_username
    class B(forms.Form):
        username = A.username
        clean_username = A.clean_username

    # 5.注意：被装饰过的From不能被继承（被包装成了一个表单验证器了）
    """
    if must_method:
        must_method = must_method.upper()
    if form:
        return FormValidator(form, must_method=must_method)
    else:
        return partial(FormValidator, must_method=must_method)


class FormValidator:
    def __init__(self, form=None, *, must_method: str = None):
        self.Form = form
        self.must_method = must_method

    def __call__(self, _callable):
        # 判断被装饰的是普通函数还是APIView
        is_func = True if isinstance(_callable, types.FunctionType) else False
        func = _callable if is_func else _callable.api

        def wrapped(*args, **kwargs):
            request = next(i for i in args if isinstance(i, HttpRequest))
            # 检查请求方法
            if self.must_method and request.method != self.must_method:
                raise RequestMethodError(f'必须为{self.must_method}请求！')
            form = self.Form(getattr(request, request.method))
            if not form.is_valid():  # 表单验证不通过直接抛出异常
                raise FormValidationError(dict(form.errors))
            request.cleaned_data = form.cleaned_data  # 添加cleaned_data
            return func(*args, **kwargs)

        if not is_func:  # 如果不是函数则认为是APIView
            _callable.api = wrapped
        return wrapped if is_func else _callable

    def __getattr__(self, item):
        if item.startswith('clean_'):
            return getattr(self.Form, item)
        try:
            return self.Form.base_fields[item]
        except KeyError:
            raise AttributeError(f"'{self.Form.__name__}' has no attribute '{item}'")

# def form_validator(form_class: Form, must_method: str = None):
#     """
#     检查form参数
#     请求方法验证失败抛出 RequestMethodError 异常
#     表单验证不通过时抛出 FormValidationError 异常
#     :param form_class:Django form class
#     :param must_method: POST or GET
#
#     @form_validator(LoginForm, must_method="POST")
#     def login(request):
#         pass
#     """
#
#     def wrap(func):
#         def core(*args, **kwargs):
#             request = next(i for i in args if isinstance(i, HttpRequest))
#             if must_method and request.method != must_method:
#                 raise RequestMethodError(f'必须为{must_method}请求！')
#             form = form_class(getattr(request, request.method))
#             if not form.is_valid():
#                 raise FormValidationError(form.errors)
#             return func(*args, **kwargs)
#
#         return core
#
#     return wrap


# class FormValidator:
#     """
#     # 先定义一个APPForm，可以将应用中需要验证的字段都放到APPForm中
#     class APPForm(forms.Form):
#         username = forms.CharField(required=True)
#         password = forms.CharField(required=True)
#         email = forms.CharField(required=True)
#         phone = forms.CharField(required=True)
#
#     # 定义一个表单验证器
#     class LoginFormValidator(FormValidator):
#         must_method = 'POST'
#         target_form = APPForm # APPForm作为目标Form
#         fields = ('username', 'password') # 根据fields从目标Form中生成相应字段的Form
#
#     # API 接口中使用
#     @LoginFormValidator
#     def login(request):
#         return JsonResponse({'result': 'ok'})
#
#     """
#     # 指定的请求方法，为None则不限制请求方法
#     must_method = 'POST'
#     # pick_form使用的字段，也就是需要验证的字段
#     fields: Tuple[str] = None
#     # 目标Form, pick_form会从目标目标Form根据fields生成一个Form Class
#     target_form: Form = None
#
#     def __init__(self, func):
#         self.func = func
#
#     def __call__(self, *args, **kwargs):
#         request = next(i for i in args if isinstance(i, HttpRequest))
#         # 检查请求方法
#         if self.must_method and request.method != self.must_method:
#             raise RequestMethodError(f'必须为{self.must_method}请求！')
#         # 检查表单验证
#         form = self.form_class(getattr(request, request.method))
#         if not form.is_valid():
#             raise FormValidationError(dict(form.errors))
#
#         return self.func(*args, **kwargs)
#
#     def __get__(self, instance, cls):
#         if instance is None:
#             return self
#         else:
#             return types.MethodType(self, instance)
#
#     def __init_subclass__(cls, **kwargs):
#         meta = cls.__dict__.get('Meta', None)
#         is_abstract = getattr(meta, 'abstract', False)
#         if is_abstract:  # 作为抽象基类不检查类定义
#             return
#
#         if not cls.target_form:
#             raise RuntimeError(f'{cls.__name__} 必须指定一个 target_form')
#
#         if not cls.fields:
#             raise RuntimeError(f'{cls.__name__} 必须定义一个fields元组')
#         # pick一个From类
#         cls.form_class = pick_form(*cls.fields, target_form=cls.target_form)
