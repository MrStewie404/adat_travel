import random
from datetime import date

from main.models.clients.coupons.coupon import Coupon
from main.models.clients.coupons.coupon_label import CouponLabel


def default_code_for_client(client, label=None):
    if not label:
        label = CouponLabel.default_promo_code_label(client.agency)
    surname_str = client.surname[0] if client.surname else ''
    name_str = client.name[0]
    middle_name_str = client.middle_name[0] if client.middle_name else ''
    code = f"{surname_str}{name_str}{middle_name_str}{date.today().year}"
    code_prefix = ''
    if Coupon.objects.filter(label=label, number=code).exists():
        code_prefix = random_promo_code(letters_count=2, digits_count=0)
    return f"{code_prefix}{code}"


def random_promo_code(letters_count=5, digits_count=3):
    # Включаем не все буквы. Например, букву "O" можно спутать с нулём, букву "З" - с тройкой,
    # а с шипящими вроде Х, Ц и Щ получаются не очень читаемые промокоды.
    letter_choices = "АБВГДЕИКЛМНПРСТУ"
    digit_choices = "12456789"  # Ноль и 3 не включаем, т.к. их можно спутать с буквами "О" и "З".
    rand = random.SystemRandom()
    letters_str = ''.join(rand.choice(letter_choices) for _ in range(letters_count))
    digits_str = ''.join(rand.choice(digit_choices) for _ in range(digits_count))
    code = letters_str + digits_str
    return code
