from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon

class Cart(object):
    #Initialize the cart
    def __init__(self,request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #Save an empty cart
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Store current applied coupon
        self.coupon_id = self.session.get('coupon_id')
    
    #Update the item quantity (inside of cart)
    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    #Ensure the session is saved by marking "modified"
    def save(self):
        self.session.modified = True
    
    #Remove the item from cart
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    #Iterate over the items in cart and get the products from database
    def __iter__(self):
        product_ids = self.cart.keys()
        #Get the products objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price']*item['quantity']
            yield item

    #Count all items in cart
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(Decimal(item['price'])*item['quantity'] for item in self.cart.values())

    #Clear the cart session
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    # After applying coupons
    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount/Decimal(100)*self.get_total_price())
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price()-self.get_discount()