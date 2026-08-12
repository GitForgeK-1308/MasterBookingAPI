from io import BytesIO
from PIL import Image, UnidentifiedImageError
import uuid

from fastapi import UploadFile

from src.auth.password import hash_password, verify_password
from src.users.exceptions import (
    AvatarTooLargeError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidAvatarTypeError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from src.users.models import User
from src.users.repository import UserRepository
from src.users.schemas import UserProfileUpdate, UserRegister


MAX_AVATAR_SIZE = 5 * 1024 * 1024


ALLOWED_AVATAR_FORMATS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


class UserService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    async def get_user_by_id(
        self,
        user_id: uuid.UUID,
    ) -> User:
        user = await self.repository.get_by_id(
            user_id
        )

        if user is None:
            raise UserNotFoundError

        return user

    async def register_user(
        self,
        data: UserRegister,
    ) -> User:
        normalized_email = str(data.email).lower()

        existing_user = await self.repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise EmailAlreadyExistsError

        hashed_password = hash_password(
            data.password
        )

        new_user = User(
            email=normalized_email,
            hashed_password=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
        )

        return await self.repository.create(
            new_user
        )


    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.lower()

        user = await self.repository.get_by_email(
            normalized_email
        )


        if user is None:
            raise InvalidCredentialsError


        password_is_valid = verify_password(
            plain_password=password,
            hashed_password=user.hashed_password,
        )
        

        if not password_is_valid:
            raise InvalidCredentialsError

        
        if not user.is_active:
            raise InactiveUserError


        return user


    async def update_profile(
    self,
    user: User,
    data: UserProfileUpdate,
) -> User:
        data_dict = data.model_dump(
            exclude_unset=True,
        )

        for key, value in data_dict.items():
            setattr(
                user,
                key,
                value,
            )

        return await self.repository.update(
            user
        )


   
    async def upload_avatar(
        self,
        user: User,
        file: UploadFile,
    ) -> User:
        content = await file.read(
            MAX_AVATAR_SIZE + 1
        )

        if len(content) > MAX_AVATAR_SIZE:
            raise AvatarTooLargeError

        try:
            image = Image.open(
                BytesIO(content)
            )

            image_format = image.format

            image.verify()

        except (
            UnidentifiedImageError,
            OSError,
            Image.DecompressionBombError,
        ):
            raise InvalidAvatarTypeError

        if image_format not in ALLOWED_AVATAR_FORMATS:
            raise InvalidAvatarTypeError

        extension = ALLOWED_AVATAR_FORMATS[
            image_format
        ]

        old_avatar = user.avatar_storage_key

        new_storage_key = await self.storage.save(
            content=content,
            extension=extension,
        )

        try:
            user.avatar_storage_key = new_storage_key

            updated_user = await self.repository.update(
                user
            )

        except Exception:
            await self.storage.delete(
                new_storage_key
            )
            raise

        if old_avatar is not None:
            await self.storage.delete(
                old_avatar
            )

        return updated_user