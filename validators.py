import re

def validate_email_task(email):
    # 1. Стандартный Regex
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return False
    # 2. фильтровать email с подстрокой "admin" после символа @
    parts = email.split('@')
    if len(parts) > 1 and "admin" in parts[1].lower():
        return False
    return True

def validate_password_task(p):
    # 8+ симв, заглавная, цифра, спецсимвол
    return (len(p) >= 8 and any(c.isupper() for c in p) 
            and any(c.isdigit() for c in p) 
            and any(c in "!@#$%^&*()" for c in p))

