from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000,
)


def encrypt_password(password: str) -> str:
    return pwd_context.encrypt(password)


def check_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

if __name__ == "__main__":
    value = check_password("anhyeuem98", b"$pbkdf2-sha256$30000$IMT4///f.99b650zRgghRA$tom1x5WR29xzrodFyYUIMyRqwid9jjgZmw3TkWaz.SE")
    print(value)
