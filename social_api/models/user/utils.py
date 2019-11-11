import time
import typing
import re


async def send_activation_code() -> None:
    """
        used for sending activation code or email after user successfully signing up
    """
    import time
    time.sleep(10)
    print("hihihi")


async def send_reset_code_email(email: str, other: typing.Any) -> None:
    """send code for resetting password to an email"""
    import time
    time.sleep(4)
    print(f"sending code to {email!r} with content {other!r}")


async def send_reset_code_phone(number: str, other: typing.Any) -> None:
    """send reset password code to phone number"""
    import time
    time.sleep(4)
    print(f"sending code to {number!r} with content {other!r}")


def validate_password(password: str) -> typing.List[str]:
    """
        password must be at least 8 characters long, one uppercase, one lowercase,
        one digit, one special character.
        validate your password, whether it satisfies the system standard password or not
        if the returned is an empty list, the password satisfies, otherwise, not.
    """
    if isinstance(password, str) and password != "":
        password = password.strip()
        # password fullcase:
        PASSWORD_FULLCASE = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        # one uppercase:
        ONE_UPPERCASE = r"[A-Z]+"
        # one lowercase:
        ONE_LOWERCASE = r"[a-z]+"
        # one digit:
        ONE_DIGIT = r"[0-9]+"
        # one special character:
        ONE_SPECIAL_CHARACTER = r"[!$%&'()*+,-.:;<=>?@[\]^_`{|}~]"
        # eight characters:
        EIGHT_CHARACTERS = r"(.){8,}"

        matchDict = {
            "Password must has at least 1 lowercase character": ONE_LOWERCASE,
            "Password must has at least 1 uppercase character": ONE_UPPERCASE,
            "Password must has at least 1 digit": ONE_DIGIT,
            "Password must has at least 1 special character": ONE_SPECIAL_CHARACTER,
            "Password must has at least 8 characters": EIGHT_CHARACTERS
        }

        if not re.compile(PASSWORD_FULLCASE).match(password) is None:
            return list()
        # otherwise:
        return [
            message for message in matchDict.keys() if re.compile(
                matchDict[message]
            ).search(password) is None
        ]
    else:
        return ["Please enter a valid password."]
