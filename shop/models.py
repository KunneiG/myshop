from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    # Типы головок, покрытий и т.д. можно вынести в TextChoices, но для простоты используем CharField
    HEAD_CHOICES = [
        ('countersunk', 'Потай'),
        ('round', 'Полукруглая'),
        ('hex', 'Шестигранная'),
    ]
    MATERIAL_CHOICES = [
        ('steel', 'Сталь'),
        ('stainless', 'Нержавейка'),
        ('brass', 'Латунь'),
    ]
    PACKAGING_CHOICES = [
        ('pcs', 'шт.'),
        ('kg', 'кг'),
        ('box', 'коробка'),
    ]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    size = models.CharField(max_length=50, help_text='Например: 4.0×50 мм')
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, default='steel')
    coating = models.CharField(max_length=50, blank=True, help_text='цинк, оксид, без покрытия')
    head_type = models.CharField(max_length=20, choices=HEAD_CHOICES, default='countersunk')
    packaging = models.CharField(max_length=20, choices=PACKAGING_CHOICES, default='pcs')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.size}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    def __str__(self):
        return f"{self.name} ({self.size})"

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('completed', 'Выполнен'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    # Для авторизованных пользователей (доп. функция)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Заказ #{self.pk}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity
