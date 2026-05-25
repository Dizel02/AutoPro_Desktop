import re

def validate_email_task(email):
    # Стандартная валидация (согласно лучшим практикам из вашего скрина)
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def validate_password_task(p):
    # 8+ симв, заглавная, цифра, спецсимвол
    return (len(p) >= 8 and any(c.isupper() for c in p) 
            and any(c.isdigit() for c in p) 
            and any(c in "!@#$%^&*()" for c in p))
