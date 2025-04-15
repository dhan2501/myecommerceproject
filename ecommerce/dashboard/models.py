# models.py
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

# Product Category Model
class ProductCategory(models.Model):
    name = models.CharField(max_length=255)  # Category name
    image = models.ImageField(upload_to='category_images/')  # Category image
    description = models.TextField(blank=True, null=True)  # Category description
    meta_title = models.CharField(max_length=255, blank=True, null=True)  # Meta title for SEO
    meta_description = models.TextField(blank=True, null=True)  # Meta description for SEO
    is_active = models.BooleanField(default=True)  # Active/Inactive status
    created_at = models.DateTimeField(auto_now_add=True)  # Time when category was created
    updated_at = models.DateTimeField(auto_now=True)  # Time when category was last updated

    def __str__(self):
        return self.name
    
    def image_tag(self):
        if self.image:
            return f'<img src="{self.image.url}" style="width: 70px; height: auto;" />'
        return "No Image"
    image_tag.allow_tags = True
    image_tag.short_description = 'Image'

# product tags model
class ProductTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while ProductTag.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

# Products model
class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)  # Auto URL slug field
    image = models.ImageField(upload_to='product_images/')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tags = models.ManyToManyField(ProductTag, blank=True, related_name='products')
    discount_percentage = models.PositiveIntegerField(null=True, blank=True)
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()

    def __str__(self):
        return self.title

    def image_tag(self):
        if self.image:
            return f'<img src="{self.image.url}" style="width: 70px; height: auto;" />'
        return "No Image"
    image_tag.allow_tags = True
    image_tag.short_description = 'Product Image'

    def save(self, *args, **kwargs):
        # Auto-calculate discount_percentage if regular and sale prices are set
        if self.regular_price and self.sale_price:
            self.discount_percentage = round(100 - (self.sale_price / self.regular_price * 100))
        else:
            self.discount_percentage = None
        super().save(*args, **kwargs)

     # Auto-generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    

class Order(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"