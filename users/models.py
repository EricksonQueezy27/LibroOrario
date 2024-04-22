from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
import uuid


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True, unique=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    bi =  models.CharField(max_length=15, blank=True, null=True)
    telefone = models.IntegerField(blank=True, null=True)
    data_nascimento = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to  ="images/users/", blank=True, null=True)
    is_professor = models.BooleanField(default=False)
    is_encarregado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username
    
    # def save(self, *args, **kwargs):
    #       if not self.pk:    #Se é um novo usuário sendo criado
    #          self.password = make_password(self.password)   #Encripta a senha
    #          super().save(*args, **kwargs)


    groups = models.ManyToManyField(
    'auth.Group',
    related_name='auth_users',
    blank=True,
    verbose_name=('groups'),
    help_text=(
        'The groups this user belongs to. A user will get all permissions '
        'granted to each of their groups.'
    )
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions_users',
        blank=True,
        verbose_name=('user permissions'),
        help_text=('Specific permissions for this user.'),
        )
