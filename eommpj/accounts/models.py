from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type="user"):
        if not email:
            raise ValueError("이메일을 입력해주세요")
        if not username:
            raise ValueError("아이디를 입력해주세요")
        
        user = self.model(
            username = username,
            email = self.normalize_email(email),
            user_type = user_type,
        )

        user.set_password(password)

        user.save(using=self.db)

        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            user_type="admin"
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)
        return user
        