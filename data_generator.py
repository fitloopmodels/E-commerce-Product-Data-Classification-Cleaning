"""
data_generator.py
-----------------
Generates 1000+ realistic, intentionally messy e-commerce product records
to simulate real-world raw data ingestion scenarios.

Mess introduced:
  - Missing values (brand, category, size, price)
  - Duplicate records (exact + near-duplicates)
  - Inconsistent casing and spacing
  - Incorrect / swapped category labels
  - Mixed size formats (S/M/L vs 38/40, ml vs mL)
  - Placeholder / junk values (e.g. "N/A", "TBD", "???")
"""

import random
import uuid
import csv
import os
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# Seed data pools
# ------------------------------------------------------------------

BRANDS = {
    "Electronics": [
        "Samsung", "Apple", "sony", "OnePlus", "REALME", "Xiaomi",
        "Boat", "JBL", "Bose", "Canon", "Nikon", "LG", "Dell", "HP",
        "Lenovo", "ASUS", "acer", "Motorola", None, "N/A", "Unknown"
    ],
    "Clothing": [
        "Nike", "Adidas", "H&M", "Zara", "PUMA", "allen solly",
        "Van Heusen", "Levis", "Wrangler", "UCB", "Roadster", None, "TBD"
    ],
    "Footwear": [
        "Nike", "Adidas", "Puma", "Reebok", "Bata", "Skechers",
        "woodland", "Red Tape", "LIBERTY", None, "N/A"
    ],
    "Home & Kitchen": [
        "Prestige", "Hawkins", "Bajaj", "Philips", "Bosch", "INALSA",
        "Pigeon", "Cello", "Tupperware", "IKEA", None, "???"
    ],
    "Beauty & Personal Care": [
        "Lakme", "Maybelline", "LOreal", "Himalaya", "Biotique",
        "Neutrogena", "Nivea", "Dove", "WOW", "Mamaearth", None, "N/A"
    ],
    "Sports & Fitness": [
        "Decathlon", "Cosco", "SG", "MRF", "Nike", "Adidas",
        "Boldfit", "STRAUSS", None, "Unknown"
    ],
    "Books & Stationery": [
        "Penguin", "HarperCollins", "Oxford", "Scholastic",
        "Classmate", "Reynolds", None
    ],
    "Toys & Games": [
        "Hasbro", "Mattel", "LEGO", "Fisher-Price", "Funskool",
        "Skoodle", None, "N/A"
    ]
}

PRODUCT_TEMPLATES = [
    # Electronics
    ("Samsung Galaxy S24 Ultra 12GB RAM 256GB", "Electronics", "Mobile Phones", "256GB", "Black"),
    ("apple iphone 15 pro max 512 gb natural titanium", "Electronics", "Mobile Phones", "512GB", "Natural Titanium"),
    ("OnePlus 12 5G Flowy Emerald 8GB 128GB", "Electronics", "Mobile Phones", "128GB", "Emerald"),
    ("Sony WH-1000XM5 Wireless Noise Cancelling Headphone", "Electronics", "Headphones", None, "Black"),
    ("boAt Rockerz 450 Bluetooth Headphone", "Electronics", "Headphones", None, "Blue"),
    ("Dell Inspiron 15 Laptop Intel i5 16GB 512GB SSD", "Electronics", "Laptops", '15"', "Platinum Silver"),
    ("ASUS VivoBook 14 AMD Ryzen 5 8GB 512GB", "Electronics", "Laptops", "14 inch", "Transparent Silver"),
    ("Apple MacBook Air M2 8GB 256GB Midnight", "Electronics", "Laptops", '13"', "Midnight"),
    ("Samsung 55 Inch 4K Smart QLED TV", "Electronics", "Televisions", '55"', "Black"),
    ("Canon EOS 200D II DSLR Camera 24.1 MP", "Electronics", "Cameras", None, "Black"),
    ("Anker 20000mAh Power Bank USB-C", "Electronics", "Accessories", None, "Black"),
    ("ZEBRONICS Zeb-Thunder Wireless Headphone", "Electronics", "Headphones", None, "Black"),
    ("Lenovo IdeaPad Slim 3 Intel i3 8GB 256GB", "Electronics", "Laptops", '15.6"', "Arctic Grey"),
    ("JBL Tune 760NC Wireless Headphone", "Electronics", "Headphones", None, "Blue"),
    ("Realme Narzo 60 Pro 5G 128GB 8GB", "Electronics", "Mobile Phones", "128GB", "Cosmic Black"),
    # Clothing
    ("Nike Dri-FIT Men's Running T-Shirt", "Clothing", "Men's Clothing", "L", "Blue"),
    ("Adidas Women's Track Jacket", "Clothing", "Women's Clothing", "M", "Black"),
    ("H&M Slim Fit Chinos Men", "Clothing", "Men's Clothing", "32x30", "Beige"),
    ("Levi's 501 Original Fit Jeans", "Clothing", "Men's Clothing", "34", "Dark Wash"),
    ("Zara Women Floral Wrap Dress", "Clothing", "Women's Clothing", "S", "Multicolor"),
    ("Allen Solly Formal Shirt Men White", "Clothing", "Men's Clothing", "XL", "White"),
    ("Puma Girls Sports Legging", "Clothing", "Kids' Clothing", "10-11 yrs", "Black"),
    ("Roadster Men Hooded Sweatshirt", "Clothing", "Winter Wear", "XXL", "Grey"),
    ("Van Heusen Men's Polo T-Shirt", "Clothing", "Men's Clothing", "40", "Navy"),
    ("WROGN Men Slim Fit Jogger", "Clothing", "Activewear", "M", "Olive"),
    # Footwear
    ("Nike Air Max 270 Running Shoes Men", "Footwear", "Sports Shoes", "UK 9", "White"),
    ("Adidas Ultraboost 22 Men's Shoes", "Footwear", "Sports Shoes", "10 UK", "Black"),
    ("Bata Men Formal Leather Oxford", "Footwear", "Formal Shoes", "UK-8", "Brown"),
    ("Puma Men Slip-On Loafers", "Footwear", "Casual Shoes", "9", "Black"),
    ("Woodland Men Trekking Boot", "Footwear", "Boots", "UK 10", "Camel"),
    ("Red Tape Women Heeled Sandal", "Footwear", "Sandals & Slippers", "38 EU", "Tan"),
    ("Skechers Women Arch Fit Sneaker", "Footwear", "Sports Shoes", "5 UK", "White"),
    # Home & Kitchen
    ("Prestige Deluxe Alpha Pressure Cooker 5L", "Home & Kitchen", "Cookware", "5L", "Silver"),
    ("Philips HL7756 750W Mixer Grinder 3 Jars", "Home & Kitchen", "Kitchen Appliances", None, "White"),
    ("Bajaj Majesty 1000TSS Toaster", "Home & Kitchen", "Kitchen Appliances", None, "Silver"),
    ("INALSA Air Fryer Crisp Air 1400W 4L", "Home & Kitchen", "Kitchen Appliances", "4L", "Black"),
    ("Solimo Microfibre Bedsheet Double 300TC", "Home & Kitchen", "Bedding", "Double", "Teal"),
    ("Cello Plastic Storage Container Set 6 Pcs", "Home & Kitchen", "Storage", None, "Transparent"),
    ("Pigeon Induction Cooktop 1800W", "Home & Kitchen", "Kitchen Appliances", None, "Black"),
    ("Tupperware Modular Mates Set 5 Pcs", "Home & Kitchen", "Storage", None, "White"),
    # Beauty & Personal Care
    ("Lakme Absolute Skin Natural Mousse Foundation SPF8", "Beauty & Personal Care", "Makeup", "25ml", "Natural Light"),
    ("Maybelline Fit Me Matte Foundation", "Beauty & Personal Care", "Makeup", "30ml", "120 Classic Ivory"),
    ("WOW Skin Science Apple Cider Vinegar Shampoo", "Beauty & Personal Care", "Haircare", "300ml", None),
    ("Mamaearth Vitamin C Sunscreen SPF 50", "Beauty & Personal Care", "Skincare", "80g", None),
    ("Neutrogena Hydro Boost Water Gel Moisturizer", "Beauty & Personal Care", "Skincare", "50ml", None),
    ("Dove Body Lotion Deeply Nourishing 400ml", "Beauty & Personal Care", "Bath & Body", "400ml", None),
    ("Himalaya Purifying Neem Face Wash 150ml", "Beauty & Personal Care", "Skincare", "150ml", None),
    ("L'Oreal Paris Elnett Satin Hairspray 400ml", "Beauty & Personal Care", "Haircare", "400ml", None),
    # Sports & Fitness
    ("Decathlon Domyos 5kg Rubber Dumbbell Pair", "Sports & Fitness", "Gym Equipment", "5kg", "Black"),
    ("Boldfit Resistance Bands Set 5 Pcs", "Sports & Fitness", "Gym Equipment", None, "Multicolor"),
    ("SG Cricket Bat Kashmir Willow", "Sports & Fitness", "Outdoor Sports", 'Short Handle', "Natural"),
    ("Cosco Football Size 5 Tornado", "Sports & Fitness", "Outdoor Sports", "Size 5", "Multicolor"),
    ("STRAUSS Yoga Mat 6mm Anti-Slip", "Sports & Fitness", "Yoga & Wellness", "6mm", "Blue"),
    ("Nivia Sports Water Bottle 750ml", "Sports & Fitness", "Sports Accessories", "750ml", "Black"),
    # Books
    ("Atomic Habits James Clear Paperback", "Books & Stationery", "Books", None, None),
    ("The Alchemist Paulo Coelho English", "Books & Stationery", "Books", None, None),
    ("Python Crash Course 3rd Edition Eric Matthes", "Books & Stationery", "Books", None, None),
    ("Classmate Notebook A4 Single Line 160 Pages", "Books & Stationery", "Stationery", None, "Green"),
    ("Reynolds Ball Point Pen Blue 10 Pcs", "Books & Stationery", "Stationery", None, "Blue"),
    # Toys
    ("LEGO Classic Creative Bricks 484 Pieces", "Toys & Games", "Educational Toys", None, "Multicolor"),
    ("Hasbro Jenga Classic Game", "Toys & Games", "Board Games", None, "Natural"),
    ("Funskool Handycraft Paper Quilling Kit", "Toys & Games", "Educational Toys", None, "Multicolor"),
    ("Mattel Hot Wheels 5-Car Pack", "Toys & Games", "Action Figures", None, "Multicolor"),
]

SIZE_VARIANTS = ["XS", "S", "M", "L", "XL", "XXL", "XXXL",
                 "6 UK", "7 UK", "8 UK", "9 UK", "10 UK",
                 "250ml", "500ml", "1L", "2L", "5L", "100g", "200g"]

JUNK_VALUES = ["N/A", "NA", "n/a", "TBD", "???", "Unknown", "-", "NULL", "none", ""]


def _random_sku():
    return f"SKU-{random.randint(10000, 99999)}"


def _random_price(category):
    ranges = {
        "Electronics": (500, 150000),
        "Clothing": (199, 8000),
        "Footwear": (299, 12000),
        "Home & Kitchen": (199, 25000),
        "Beauty & Personal Care": (99, 3000),
        "Sports & Fitness": (199, 20000),
        "Books & Stationery": (49, 1500),
        "Toys & Games": (199, 8000),
    }
    lo, hi = ranges.get(category, (100, 5000))
    price = round(random.uniform(lo, hi), 2)
    # Introduce ~8% missing prices
    return price if random.random() > 0.08 else None


def _maybe_corrupt(value, junk_prob=0.07):
    """Randomly replace a value with a junk placeholder."""
    if value is None:
        return None
    if random.random() < junk_prob:
        return random.choice(JUNK_VALUES)
    return value


def _random_casing(text):
    """Randomly alter casing of a string."""
    choice = random.random()
    if choice < 0.2:
        return text.upper()
    elif choice < 0.4:
        return text.lower()
    elif choice < 0.5:
        return "  " + text + "  "   # Extra whitespace
    return text


def generate_records(n=1200, seed=42):
    """
    Generate `n` raw product records with realistic messiness.

    Returns: list[dict]
    """
    random.seed(seed)
    records = []
    used_skus = set()

    for i in range(n):
        template = random.choice(PRODUCT_TEMPLATES)
        name, category, subcategory, size, color = template

        brand_pool = BRANDS.get(category, [None])
        brand = random.choice(brand_pool)

        # Casing corruption on name
        name = _random_casing(name) if random.random() < 0.25 else name

        # Category corruption: ~10% wrong/missing category
        if random.random() < 0.10:
            category = random.choice([
                None, "N/A", random.choice(list(BRANDS.keys()))
            ])

        # Size corruption
        if size and random.random() < 0.15:
            size = random.choice(SIZE_VARIANTS)
        size = _maybe_corrupt(size)

        # SKU generation
        sku = _random_sku()
        while sku in used_skus:
            sku = _random_sku()
        used_skus.add(sku)

        price = _random_price(category if category in BRANDS else "Electronics")

        stock = random.randint(0, 500) if random.random() > 0.05 else None

        record = {
            "product_id": str(uuid.uuid4()),
            "sku": sku,
            "product_name": name,
            "brand": _maybe_corrupt(brand),
            "category": _maybe_corrupt(category),
            "subcategory": _maybe_corrupt(subcategory, junk_prob=0.12),
            "size": size,
            "color": _maybe_corrupt(color),
            "price": price,
            "stock_quantity": stock,
            "created_at": (
                datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))
            ).strftime("%Y-%m-%d"),
            "rating": round(random.uniform(1.0, 5.0), 1) if random.random() > 0.10 else None,
        }
        records.append(record)

    # Inject ~5% exact duplicates
    num_dupes = int(n * 0.05)
    for _ in range(num_dupes):
        dupe = random.choice(records).copy()
        dupe["product_id"] = str(uuid.uuid4())
        records.append(dupe)

    # Inject ~3% near-duplicates (same SKU, different product_id)
    num_near = int(n * 0.03)
    for _ in range(num_near):
        base = random.choice(records).copy()
        base["product_id"] = str(uuid.uuid4())
        base["product_name"] = base["product_name"] + " " if base["product_name"] else base["product_name"]
        records.append(base)

    random.shuffle(records)
    return records


def save_to_csv(records, path):
    if not records:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fieldnames = list(records[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"[DataGenerator] Saved {len(records)} records → {path}")


if __name__ == "__main__":
    records = generate_records(n=1200)
    save_to_csv(records, "data/raw/products_raw.csv")
