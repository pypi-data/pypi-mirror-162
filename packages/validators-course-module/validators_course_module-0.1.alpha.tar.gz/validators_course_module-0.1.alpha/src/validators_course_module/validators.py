# module with validator decorators
from email import message
import re

class InvalidMailException(BaseException):
    def __init__(self, message):
        super().__init__(message)

email_pattern=r"^([a-z].*){1,8}.([a-z].*){1,8}@([a-z].*){1,8}.com$"

cp=re.compile(email_pattern)

def email_validator(func):
    """
    This is a docstring for email validator decorator.
    """
    def wrapper(s):
        if cp.search(func(s))!=None:
            return func(s)
        else:
            raise InvalidMailException("INVALID MAIL")
    return wrapper
    

if __name__=="__main__":

    @email_validator
    def get_mail(m):
        return m

    import sys
    try:
        email=sys.argv[1]
        print(get_mail(email))
    except Exception as e:
        print(e,"usage: validators <email address>")
			                    
                     
