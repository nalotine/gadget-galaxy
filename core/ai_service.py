
from google import genai
from django.conf import settings
from .models import Product, Order

def get_available_products():

    products = Product.objects.filter(
        is_available=True,
        stock__gt=0
    )

    product_info = []

    for product in products:
        product_info.append(
            f"""
            Product: {product.name}
            Brand: {product.brand}
            Category: {product.category}
            Price: ₹{product.price}
            Stock: {product.stock}
            Description: {product.description}
            """
        )

    return "\n".join(product_info)

def get_user_orders(user):

    if not user or not user.is_authenticated:
        return "Customer is not logged in. No order information is available."

    orders = Order.objects.filter(
        user=user
    ).prefetch_related('items__product').order_by('-created_at')[:10]

    if not orders.exists():
        return "This customer has no orders."

    order_info = []

    for order in orders:

        products = []

        for item in order.items.all():
            products.append(
                f"{item.product.name} - Quantity: {item.quantity}"
            )

        order_info.append(f"""
        Order ID: {order.id}
        Order Date: {order.created_at}
        Products: {', '.join(products)}
        Total Amount: ₹{order.total_amount}
        Order Status: {order.get_status_display()}
        Payment Method: {order.get_payment_method_display()}
        Payment Status: {order.get_payment_status_display()}
        """)

    return "\n".join(order_info)



   
def ask_gemini(prompt, user=None):

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    products = get_available_products()
    orders = get_user_orders(user)

    system_instruction = f"""
    You are the official AI Shopping Assistant of Gadget Galaxy.

    AVAILABLE PRODUCTS:
    {products}

    CUSTOMER'S ORDER INFORMATION:
    {orders}

    RULES:
    - Recommend products only from the available product list.
    - Use the actual prices from the database.
    - Answer order questions only using the provided order information.
    - Never invent order IDs, payment statuses or delivery statuses.
    - Never reveal another customer's information.
    - If order information is unavailable, explain that politely.
    - Be friendly and helpful.
    - Never use ** for bold text.
    - Never use Markdown formatting.
    - Do not use asterisks, hashtags or backticks for styling.
    - Use plain text with simple numbered lists when needed.
    - Keep responses clean and easy to read.
    - you can use emojis to make the conversation more engaging.
    - you can use funny and witty responses to make the conversation more enjoyable.
    - you can use casual and friendly language to make the conversation more relatable.
    - you can roster the conversation with a touch of humor to make it more entertaining.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=system_instruction + "\n\nCustomer: " + prompt
    )

    return response.text
