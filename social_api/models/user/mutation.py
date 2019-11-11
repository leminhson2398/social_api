from graphene import ObjectType, Mutation as ObjectMutation, Field, String, Boolean, DateTime, List
from .import USER_COLLECTION
from .model import UserType
from validate_email import validate_email
from phonenumbers import parse, is_valid_number
from firebase_admin.exceptions import NotFoundError
from ...security.security import encrypt_password, check_password
import jwt
from social_api import config
from jwt import PyJWTError
import logging
from datetime import datetime, timedelta
import time
from .utils import send_activation_code, send_reset_code_email, send_reset_code_phone, validate_password


class Signup(ObjectMutation):
    ok = Boolean(required=True)
    user = Field(lambda: UserType)
    errorList = List(String, required=False)

    class Arguments:
        username = String(required=True)
        email_or_phone = String(required=True)
        gender = String(required=True)
        date_of_birth = DateTime(required=True)
        password1 = String(required=True)
        password2 = String(required=True)

    async def mutate(self, info, **kwargs):
        ok, errorList, user = False, [], None
        EMAIL: str = "email"
        PHONE_NUMBER: str = "phone_number"
        # 'emailOrPhone' will hold either "email" || "phone_number", in order to filter in database:
        emailOrPhone: str = ""

        fields = [
            "username",
            "email_or_phone",
            "password1",
            "password2",
            "date_of_birth",
            "gender",
        ]
        # check all parameters were passed in:
        if all([bool(kwargs.get(item, None).strip()) for item in fields if type(kwargs.get(item, None)) is str]):
            password1, password2 = [
                kwargs.pop(item) for item in ["password1", "password2"]
            ]
            # check email or phone in the field 'email_or_phone':
            email_or_phone: str = kwargs["email_or_phone"]
            if validate_email(email_or_phone):
                emailOrPhone = EMAIL
            else:
                try:
                    phoneNumber = parse(email_or_phone)
                except Exception:
                    errorList.append(
                        f"{email_or_phone} is not a valid phone number.")
                else:
                    if is_valid_number(phoneNumber):
                        emailOrPhone = PHONE_NUMBER
                    else:
                        errorList.append(
                            f"{email_or_phone} is not a valid phone number.")
            if emailOrPhone != "":
                # check user with phone_number or email does exist or not:
                try:
                    # check email existence
                    userWithEmailOrPhone = USER_COLLECTION.where(
                        u"{}".format(emailOrPhone),
                        u"==",
                        u"{}".format(email_or_phone)
                    ).limit(1).stream()
                    userList = [user for user in userWithEmailOrPhone]
                    if len(userList):
                        errorList.append(f"{emailOrPhone} is already taken.")
                    else:
                        # check username exist, only perform this operation if user is valid and does not exist
                        try:
                            userWithUsername = USER_COLLECTION.where(
                                u"username",
                                u"==",
                                u"{}".format(kwargs["username"])
                            ).limit(1).stream()
                            userList = [user for user in userWithUsername]
                            if len(userList):
                                errorList.append(
                                    f"username {kwargs['username']!r} is already taken."
                                )
                        except NotFoundError:
                            pass
                except NotFoundError:
                    pass

            # check password match
            if password1 != password2:
                errorList.append("Passwords do not match.")
            else:
                # validate password first to see whether user password satisfies requirements or not:
                passwordValidationErrorList = validate_password(password1)
                if not len(passwordValidationErrorList):
                    # create hashed password for this user:
                    password: str = encrypt_password(password1)
                else:
                    errorList.extend(passwordValidationErrorList)

            # check errorList list length:
            if not len(errorList):
                kwargs.update({
                    "password": password,
                    "active": False,
                    emailOrPhone: email_or_phone
                })
                # add new user to database:
                USER_COLLECTION.add(kwargs)
                ok = True
                user = kwargs
        else:
            errorList.append("Please enter correctly the required fields.")
        # get background task executor, only when created user successfully
        if ok:
            background = info.context["background"]
            background.add_task(send_activation_code)

        return Signup(ok=ok, errorList=errorList, user=user)


class Signin(ObjectMutation):
    ok = Boolean(required=True)
    errorList = List(String, required=False)
    token = String(required=False)

    class Arguments:
        email = String(required=True)
        password = String(required=True)

    async def mutate(self, info, **kwargs):
        ok, errorList, token = False, [], None
        email, password = [
            kwargs.get(key, "").strip() for key in ["email", "password"]
        ]
        if isinstance(email, str) and email != "" and isinstance(password, str) and password != "":
            try:
                userWithEmail = USER_COLLECTION.where(
                    u"email",
                    u"==",
                    u"{}".format(email)
                ).limit(1).stream()
                userWithEmail = [user for user in userWithEmail]
                if len(userWithEmail):
                    # user with the email does exist
                    # check password:
                    userMatch = userWithEmail[0].to_dict()
                    try:
                        if check_password(password, userMatch["password"]):
                            try:
                                token = jwt.encode(
                                    {
                                        "username": userMatch["username"],
                                        "id": userWithEmail[0].id,
                                        "password": userMatch["password"],
                                        "expire": (datetime.utcnow() + timedelta(minutes=10)).timestamp()
                                    },
                                    config.get("SECRET", default=""),
                                    algorithm="HS256"
                                ).decode(encoding="utf-8")
                            except PyJWTError as e:
                                logging.info(f"Error encoding token {e}")
                                pass
                            else:
                                # if try was success
                                ok = True
                        else:
                            errorList.append("Password is in correct.")
                    except Exception as e:
                        logging.info(f"Error checking password {e}")
                else:
                    errorList.append(f"Your credentials are invalid.")
            except Exception as e:
                logging.error(f"Error fetching: {e}")
        else:
            errorList.append("Please enter valid email and password.")

        return Signin(
            ok=ok,
            errorList=errorList,
            token=token,
        )


class ResetPassword(ObjectMutation):
    ok = Boolean(required=True)
    errors = List(String, required=False)

    class Arguments:
        email_or_phone = String(required=True)

    async def mutate(self, info, **kwargs):
        EMAIL: str = "email"
        PHONE_NUMBER: str = "phone_number"

        ok, errors = False, []
        email_or_phone = kwargs.get("email_or_phone", None)
        emailOrPhone: str = ""

        if email_or_phone:
            # check email or phone number
            if validate_email(email_or_phone):
                emailOrPhone = EMAIL
            else:
                try:
                    phoneNumber = parse(email_or_phone)
                except Exception:
                    errors.append(f"{email_or_phone} is not \
                        a valid phone number.")
                else:
                    if is_valid_number(phoneNumber):
                        emailOrPhone = PHONE_NUMBER
                    else:
                        errors.append(f"{email_or_phone} is not \
                        a valid phone number.")

            # check user in database or not:
            try:
                # fet user in database:
                userWithEmailOrPhone = USER_COLLECTION.where(
                    u"{}".format(emailOrPhone),
                    u"==",
                    u"{}".format(email_or_phone)
                ).limit(1).stream()
                try:
                    next(userWithEmailOrPhone)
                except StopIteration:
                    errors.append(f"We did not find \
                        the {emailOrPhone} {email_or_phone} in our system.")
                else:
                    # the user exist:
                    ok = True
            except NotFoundError:
                errors.append(f"We did not find the \
                    {emailOrPhone} {email_or_phone} in our system.")
        else:
            errors.append("Please enter email or phone number")

        if ok:
            background = info.context["background"]
            background.add_task(
                send_reset_code_email, "leminhson2398@outlook.com", "hihi"
            ) if emailOrPhone is EMAIL else background.add_task(
                send_reset_code_phone, "+84354575050", "hihi"
            )

        return ResetPassword(
            ok=ok,
            errors=errors
        )


class Mutation(ObjectType):
    signup = Signup.Field()
    signin = Signin.Field()
    reset = ResetPassword.Field()
