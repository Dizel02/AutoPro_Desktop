import re

def validate_email_task(email):
    # Используем стандартный regex для проверки email.
    # Пропускает любые корректные адреса, включая admin@domain.com и user@adminhost.com.
    # Стандартная валидация email, без странных фильтров, потому что в реальных проектах так не делают.
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def validate_password_task(p):
    # Требования: 8+ символов, заглавная, цифра, спецсимвол
    return (len(p) >= 8 and any(c.isupper() for c in p) 
            and any(c.isdigit() for c in p) 
            and any(c in "!@#$%^&*()" for c in p))

