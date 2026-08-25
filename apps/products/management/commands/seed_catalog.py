from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Brand, Category, Product

CATALOG = {
    "Laptops": [
        (
            "Apple",
            "MacBook Air M3 13",
            1099,
            24,
            {"cpu": "Apple M3", "ram_gb": 8, "storage_gb": 256, "screen_inches": 13.6},
        ),
        (
            "Apple",
            "MacBook Pro M3 14",
            1599,
            18,
            {"cpu": "Apple M3 Pro", "ram_gb": 18, "storage_gb": 512, "screen_inches": 14.2},
        ),
        (
            "Dell",
            "XPS 13 Plus",
            1299,
            15,
            {"cpu": "Intel Core Ultra 7", "ram_gb": 16, "storage_gb": 512, "screen_inches": 13.4},
        ),
        (
            "Dell",
            "Inspiron 16 Plus",
            899,
            30,
            {"cpu": "Intel Core i7", "ram_gb": 16, "storage_gb": 1000, "screen_inches": 16},
        ),
        (
            "Lenovo",
            "ThinkPad X1 Carbon Gen 12",
            1429,
            12,
            {"cpu": "Intel Core Ultra 7", "ram_gb": 32, "storage_gb": 1000, "screen_inches": 14},
        ),
        (
            "Lenovo",
            "Yoga 7i 14",
            799,
            22,
            {"cpu": "Intel Core Ultra 5", "ram_gb": 16, "storage_gb": 512, "screen_inches": 14},
        ),
        (
            "HP",
            "Spectre x360 14",
            1399,
            10,
            {"cpu": "Intel Core Ultra 7", "ram_gb": 16, "storage_gb": 1000, "screen_inches": 14},
        ),
        (
            "HP",
            "Pavilion Plus 14",
            749,
            25,
            {"cpu": "Intel Core i5", "ram_gb": 16, "storage_gb": 512, "screen_inches": 14},
        ),
        (
            "ASUS",
            "ROG Zephyrus G14",
            1799,
            9,
            {"cpu": "AMD Ryzen 9", "ram_gb": 32, "storage_gb": 1000, "screen_inches": 14},
        ),
        (
            "ASUS",
            "Zenbook 14 OLED",
            999,
            20,
            {"cpu": "Intel Core Ultra 7", "ram_gb": 16, "storage_gb": 1000, "screen_inches": 14},
        ),
        (
            "Acer",
            "Swift Go 14",
            699,
            28,
            {"cpu": "Intel Core Ultra 5", "ram_gb": 16, "storage_gb": 512, "screen_inches": 14},
        ),
        (
            "Microsoft",
            "Surface Laptop 6",
            1199,
            14,
            {"cpu": "Snapdragon X Elite", "ram_gb": 16, "storage_gb": 512, "screen_inches": 13.8},
        ),
        (
            "Razer",
            "Blade 15",
            1999,
            7,
            {"cpu": "Intel Core i7", "ram_gb": 32, "storage_gb": 1000, "screen_inches": 15.6},
        ),
    ],
    "Smartphones": [
        (
            "Apple",
            "iPhone 15",
            799,
            40,
            {"chip": "A16 Bionic", "ram_gb": 6, "storage_gb": 128, "display_inches": 6.1},
        ),
        (
            "Apple",
            "iPhone 15 Pro",
            999,
            35,
            {"chip": "A17 Pro", "ram_gb": 8, "storage_gb": 256, "display_inches": 6.1},
        ),
        (
            "Samsung",
            "Galaxy S24",
            799,
            38,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 8, "storage_gb": 256, "display_inches": 6.2},
        ),
        (
            "Samsung",
            "Galaxy S24 Ultra",
            1299,
            26,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 512, "display_inches": 6.8},
        ),
        (
            "Google",
            "Pixel 8",
            699,
            31,
            {"chip": "Google Tensor G3", "ram_gb": 8, "storage_gb": 128, "display_inches": 6.2},
        ),
        (
            "Google",
            "Pixel 8 Pro",
            999,
            20,
            {"chip": "Google Tensor G3", "ram_gb": 12, "storage_gb": 256, "display_inches": 6.7},
        ),
        (
            "OnePlus",
            "OnePlus 12",
            799,
            24,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "display_inches": 6.82},
        ),
        (
            "Xiaomi",
            "Xiaomi 14",
            699,
            27,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 512, "display_inches": 6.36},
        ),
        (
            "Motorola",
            "Edge 50 Pro",
            699,
            22,
            {"chip": "Snapdragon 7 Gen 3", "ram_gb": 12, "storage_gb": 512, "display_inches": 6.7},
        ),
        (
            "Sony",
            "Xperia 1 VI",
            1299,
            11,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 12, "storage_gb": 256, "display_inches": 6.5},
        ),
        (
            "Nothing",
            "Phone (2)",
            599,
            18,
            {"chip": "Snapdragon 8+ Gen 1", "ram_gb": 12, "storage_gb": 256, "display_inches": 6.7},
        ),
        (
            "ASUS",
            "ROG Phone 8",
            1099,
            16,
            {"chip": "Snapdragon 8 Gen 3", "ram_gb": 16, "storage_gb": 512, "display_inches": 6.78},
        ),
    ],
    "Headphones": [
        (
            "Sony",
            "WH-1000XM5",
            399,
            34,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 30, "codec": "LDAC"},
        ),
        (
            "Bose",
            "QuietComfort Ultra",
            429,
            25,
            {
                "type": "over-ear",
                "noise_cancelling": True,
                "battery_hours": 24,
                "codec": "aptX Adaptive",
            },
        ),
        (
            "Apple",
            "AirPods Pro 2",
            249,
            50,
            {"type": "in-ear", "noise_cancelling": True, "battery_hours": 6, "codec": "AAC"},
        ),
        (
            "Apple",
            "AirPods Max",
            549,
            15,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 20, "codec": "AAC"},
        ),
        (
            "Sennheiser",
            "Momentum 4 Wireless",
            349,
            21,
            {
                "type": "over-ear",
                "noise_cancelling": True,
                "battery_hours": 60,
                "codec": "aptX Adaptive",
            },
        ),
        (
            "Bose",
            "QuietComfort Headphones",
            349,
            18,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 24, "codec": "AAC"},
        ),
        (
            "JBL",
            "Live 770NC",
            199,
            29,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 65, "codec": "AAC"},
        ),
        (
            "JBL",
            "Tune 770NC",
            129,
            33,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 70, "codec": "AAC"},
        ),
        (
            "Beats",
            "Studio Pro",
            349,
            20,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 40, "codec": "AAC"},
        ),
        (
            "Audio-Technica",
            "ATH-M50xBT2",
            199,
            17,
            {"type": "over-ear", "noise_cancelling": False, "battery_hours": 50, "codec": "LDAC"},
        ),
        (
            "Anker",
            "Soundcore Space Q45",
            149,
            37,
            {"type": "over-ear", "noise_cancelling": True, "battery_hours": 50, "codec": "LDAC"},
        ),
        (
            "Samsung",
            "Galaxy Buds3 Pro",
            249,
            23,
            {"type": "in-ear", "noise_cancelling": True, "battery_hours": 7, "codec": "SSC"},
        ),
        (
            "Shokz",
            "OpenRun Pro 2",
            179,
            14,
            {
                "type": "open-ear",
                "noise_cancelling": False,
                "battery_hours": 12,
                "codec": "Bluetooth 5.3",
            },
        ),
    ],
    "Monitors": [
        (
            "Dell",
            "UltraSharp U2723QE",
            599,
            16,
            {"resolution": "4K", "panel": "IPS Black", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "LG",
            "27GP850-B",
            449,
            24,
            {"resolution": "QHD", "panel": "Nano IPS", "refresh_hz": 165, "size_inches": 27},
        ),
        (
            "Samsung",
            "Odyssey G7 32",
            699,
            13,
            {"resolution": "QHD", "panel": "VA", "refresh_hz": 240, "size_inches": 32},
        ),
        (
            "Samsung",
            "ViewFinity S9",
            1599,
            8,
            {"resolution": "5K", "panel": "IPS", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "ASUS",
            "ProArt PA279CV",
            499,
            19,
            {"resolution": "4K", "panel": "IPS", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "ASUS",
            "ROG Swift PG27AQDM",
            999,
            10,
            {"resolution": "QHD", "panel": "OLED", "refresh_hz": 240, "size_inches": 27},
        ),
        (
            "BenQ",
            "PD2705U",
            549,
            14,
            {"resolution": "4K", "panel": "IPS", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "Acer",
            "Nitro XV272U",
            329,
            26,
            {"resolution": "QHD", "panel": "IPS", "refresh_hz": 170, "size_inches": 27},
        ),
        (
            "ViewSonic",
            "VP2756-4K",
            399,
            18,
            {"resolution": "4K", "panel": "IPS", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "Gigabyte",
            "M32U",
            699,
            12,
            {"resolution": "4K", "panel": "SS IPS", "refresh_hz": 144, "size_inches": 32},
        ),
        (
            "HP",
            "Z27k G3",
            649,
            9,
            {"resolution": "4K", "panel": "IPS", "refresh_hz": 60, "size_inches": 27},
        ),
        (
            "MSI",
            "MAG 274QRF QD E2",
            399,
            21,
            {"resolution": "QHD", "panel": "Rapid IPS", "refresh_hz": 180, "size_inches": 27},
        ),
    ],
}

BRAND_DESCRIPTIONS = {
    "Apple": "طراح و تولیدکننده محصولات سخت‌افزاری و نرم‌افزاری پریمیوم.",
    "Dell": "برند جهانی رایانه، نمایشگر و تجهیزات سازمانی.",
    "Lenovo": "تولیدکننده لپ‌تاپ، تبلت و تجهیزات محاسباتی.",
    "HP": "برند باسابقه رایانه‌های شخصی و تجهیزات اداری.",
    "ASUS": "تولیدکننده لپ‌تاپ، مانیتور و تجهیزات گیمینگ.",
    "Acer": "برند محصولات محاسباتی و نمایشگرهای مقرون‌به‌صرفه.",
    "Microsoft": "ارائه‌دهنده محصولات Surface و نرم‌افزارهای بهره‌وری.",
    "Razer": "برند تخصصی تجهیزات گیمینگ و لپ‌تاپ‌های قدرتمند.",
    "Samsung": "تولیدکننده جهانی موبایل، نمایشگر و لوازم الکترونیکی.",
    "Google": "ارائه‌دهنده گوشی‌های Pixel و خدمات هوشمند.",
    "OnePlus": "برند گوشی‌های هوشمند با تمرکز بر عملکرد و سرعت.",
    "Xiaomi": "تولیدکننده محصولات هوشمند با ارزش خرید بالا.",
    "Motorola": "برند باسابقه تلفن همراه و تجهیزات ارتباطی.",
    "Sony": "تولیدکننده محصولات صوتی، تصویری و موبایل.",
    "Nothing": "برند طراحی‌محور در حوزه گوشی و لوازم هوشمند.",
    "Bose": "متخصص تجهیزات صوتی و فناوری حذف نویز.",
    "Sennheiser": "برند حرفه‌ای تجهیزات صوتی و هدفون.",
    "JBL": "برند محبوب تجهیزات صوتی مصرفی.",
    "Beats": "برند هدفون با تمرکز بر موسیقی و طراحی.",
    "Audio-Technica": "تولیدکننده تجهیزات صوتی حرفه‌ای.",
    "Anker": "برند لوازم جانبی و تجهیزات صوتی هوشمند.",
    "Shokz": "متخصص هدفون‌های باز و هدایت استخوانی.",
    "LG": "تولیدکننده نمایشگر و محصولات الکترونیکی.",
    "BenQ": "برند مانیتورهای حرفه‌ای و خلاقیت دیجیتال.",
    "ViewSonic": "تولیدکننده نمایشگرهای حرفه‌ای و آموزشی.",
    "Gigabyte": "تولیدکننده سخت‌افزار و مانیتورهای گیمینگ.",
    "MSI": "برند سخت‌افزار و نمایشگرهای گیمینگ.",
}


class Command(BaseCommand):
    help = "Seed a realistic SmartShop AI digital-products catalog."

    def handle(self, *args, **options):
        categories = {}
        brands = {}
        for category_name in CATALOG:
            category, _ = Category.objects.update_or_create(
                slug=slugify(category_name),
                defaults={"name": category_name, "parent": None},
            )
            categories[category_name] = category

        brand_names = {brand for products in CATALOG.values() for brand, *_ in products}
        for brand_name in brand_names:
            brand, _ = Brand.objects.update_or_create(
                slug=slugify(brand_name),
                defaults={
                    "name": brand_name,
                    "description": BRAND_DESCRIPTIONS.get(
                        brand_name, "برند معتبر محصولات دیجیتال."
                    ),
                },
            )
            brands[brand_name] = brand

        created = 0
        for category_name, products in CATALOG.items():
            for brand_name, name, price, stock, specifications in products:
                slug = slugify(f"{brand_name}-{name}")
                defaults = {
                    "name": name,
                    "description": f"{name} | {category_name} | مشخصات فنی واقعی‌نما.",
                    "price": Decimal(str(price)),
                    "stock": stock,
                    "category": categories[category_name],
                    "brand": brands[brand_name],
                    "specifications": specifications,
                    "average_rating": Decimal("4.3") if stock % 2 else Decimal("4.6"),
                }
                legacy_product = (
                    Product.objects.filter(
                        name=name,
                        category=categories[category_name],
                        brand=brands[brand_name],
                    )
                    .exclude(slug=slug)
                    .first()
                )
                if legacy_product:
                    legacy_product.slug = slug
                    for field, value in defaults.items():
                        setattr(legacy_product, field, value)
                    legacy_product.save()
                    was_created = False
                else:
                    _, was_created = Product.objects.update_or_create(
                        slug=slug,
                        defaults=defaults,
                    )
                created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog ready: {len(categories)} categories, {len(brands)} brands, "
                f"{Product.objects.count()} products ({created} newly created)."
            )
        )
