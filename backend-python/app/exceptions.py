class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, 404)


class ValidationException(BusinessException):
    """参数验证异常"""
    def __init__(self, message: str = "参数验证失败"):
        super().__init__(message, 400)


class DuplicateException(BusinessException):
    """重复数据异常"""
    def __init__(self, message: str = "数据已存在"):
        super().__init__(message, 409)
