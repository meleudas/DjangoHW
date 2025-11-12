from django.conf import settings
from main.models import Product
from discounts.models import PromoCode


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    
    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        
    
        current_qty = self.cart.get(product_id, {}).get('quantity', 0)
        new_qty = quantity if update_quantity else current_qty + quantity
        effective_price = product.get_discounted_price(quantity=new_qty)
        

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)  
            }
        
   
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        

        self.cart[product_id]['price'] = str(effective_price)
        self.save()

    def save(self):
        self.session.modified = True

    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save

    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        # Створюємо мапу ID → Product
        products_dict = {str(p.id): p for p in products}

        for product_id, item in self.cart.items():
            product = products_dict.get(product_id)
            if product:
                # Копіюємо дані з кошика
                cart_item = {
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'slug': product.slug,
                        'price': float(product.price),
                        'get_absolute_url': product.get_absolute_url(),
                        'category': {'name': product.category.name},
                        'image_url': product.image.url if product.image else None,
                    },
                    'quantity': item['quantity'],
                    'price': float(item['price']),  # з рядка назад у float
                }
                cart_item['total_price'] = cart_item['price'] * cart_item['quantity']
                yield cart_item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    
    def get_promo_info(self):
        """Повертає словник: {'promo': PromoCode, 'discount': Decimal, 'new_total': Decimal} або None"""
        promo_id = self.session.get('applied_promo')
        if not promo_id:
            return None
        try:
            promo = PromoCode.objects.get(id=promo_id)
            if not promo.is_valid_for_application():
                self.session.pop('applied_promo', None)
                return None
            total = self.get_total_price()
            if total < promo.min_order_amount:
                return None
            discount, new_total, note = promo.apply_discount(total)
            return {
                'promo': promo,
                'discount': discount,
                'new_total': new_total,
                'note': note
            }
        except PromoCode.DoesNotExist:
            self.session.pop('applied_promo', None)
            return None