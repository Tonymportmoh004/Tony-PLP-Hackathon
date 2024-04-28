from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from PIL import Image, ImageOps
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _

class CustomUserManager(models.Manager):
    def create_user(self, username, email=None, password=None):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
        help_text=_('Specific permissions for this user.'),
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.profile_pic.path)

        # Resize the image to a maximum of 300x300 pixels
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)

        # Create a new image with mode 'L' (grayscale) and size as the original image
        mask = Image.new('L', img.size, 0)

        # Create a white circle on the mask at the center with radius as half of the smaller dimension (width/height)
        mask_img = ImageOps.fit(mask, mask.size, centering=(0.5, 0.5))
        mask_img.paste(255, Image.new('L', (min(mask.size),) * 2).transform(mask.size, Image.EXTENT, (0, 0, min(mask.size), min(mask.size)), Image.BICUBIC))

        # Convert the original image to 'RGBA' (to support transparency)
        img = img.convert('RGBA')

        # Paste the original image onto the mask using the mask as the alpha channel
        result = Image.new('RGBA', img.size)
        result.paste(img, mask_img)

        # Save the result image replacing the original image
        result.save(self.profile_pic.path)

    
class blogPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    photo = models.ImageField(upload_to='blog_photos', blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.create_slug()
        super().save(*args, **kwargs)

    def create_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while blogPost.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.photo.path)

        # Resize the image to a maximum of 800x800 pixels
        if img.height > 800 or img.width > 800:
            output_size = (800, 800)
            img.thumbnail(output_size)

        # Create a new image with mode 'L' (grayscale) and size as the original image
        mask = Image.new('L', img.size, 0)

        # create a rectangle on the mask at the center with radius as half of the smaller dimension (width/height)
        mask_img = ImageOps.fit(mask, mask.size, centering=(0.5, 0.5))
        mask_img.paste(255, Image.new('L', (min(mask.size),) * 2).transform(mask.size, Image.EXTENT, (0, 0, min(mask.size), min(mask.size)), Image.BICUBIC))
        
        # Convert the original image to 'RGBA' (to support transparency)
        img = img.convert('RGBA')

        # Paste the original image onto the mask using the mask as the alpha channel
        result = Image.new('RGBA', img.size)
        result.paste(img, mask_img)

        
        # Save the result image replacing the original image
        result.save(self.photo.path)


class Comment(models.Model):
    blog_post = models.ForeignKey(blogPost, on_delete=models.CASCADE, related_name='blogpost_comments')
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comments')
    post = models.ForeignKey(blogPost, on_delete=models.CASCADE, related_name='post_comments')
    
    def __str__(self):
        return self.content


