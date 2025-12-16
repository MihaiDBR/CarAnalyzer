"""
Whitelist of Major Car Manufacturers
Only well-known car brands that are popular in Romania and Europe
"""

# Major car manufacturers - organized by region
MAJOR_MANUFACTURERS = {
    # German brands
    "audi", "bmw", "mercedes-benz", "mercedes", "volkswagen", "vw", "porsche",
    "opel", "smart",

    # French brands
    "peugeot", "renault", "citroen", "dacia", "ds",

    # Italian brands
    "fiat", "alfa romeo", "lancia", "maserati", "ferrari", "lamborghini",

    # Japanese brands
    "toyota", "honda", "nissan", "mazda", "suzuki", "mitsubishi", "subaru",
    "lexus", "infiniti", "acura",

    # Korean brands
    "hyundai", "kia", "genesis",

    # American brands
    "ford", "chevrolet", "dodge", "jeep", "chrysler", "cadillac", "lincoln",
    "tesla", "buick", "gmc",

    # British brands
    "land rover", "range rover", "jaguar", "mini", "bentley", "rolls-royce",
    "aston martin", "lotus", "mclaren",

    # Swedish brands
    "volvo", "saab",

    # Czech brands
    "skoda",

    # Spanish brands
    "seat",

    # Chinese brands (popular in Europe)
    "byd", "mg", "lynk & co",

    # Other European
    "cupra"
}

# Alternative names mapping (for API inconsistencies)
BRAND_ALIASES = {
    "vw": "volkswagen",
    "mercedes": "mercedes-benz",
    "alfa": "alfa romeo",
    "range rover": "land rover"
}

# Blacklist - companies that contain car brand names but are NOT car manufacturers
# (trailers, parts, etc.)
BLACKLIST_KEYWORDS = {
    "trailer", "trailers", "steel", "industries", "fuso", "motorcycles",
    "truck", "trucks", "manufacturing", "solutions", "transport", "big",
    " rv", "supreme", "monsoon", "motor company of", "santana"
}

def is_major_manufacturer(make_name: str) -> bool:
    """
    Check if a make is a major manufacturer
    Uses STRICT matching to avoid false positives

    Args:
        make_name: Make name to check

    Returns:
        True if major manufacturer, False otherwise
    """
    if not make_name:
        return False

    make_lower = make_name.lower().strip()

    # First check blacklist - reject immediately if contains blacklisted keywords
    for keyword in BLACKLIST_KEYWORDS:
        if keyword in make_lower:
            return False

    # Check direct exact match
    if make_lower in MAJOR_MANUFACTURERS:
        return True

    # Check if it's an alias
    if make_lower in BRAND_ALIASES:
        return True

    # STRICT: Only match if the make name STARTS with a major brand
    # This handles "BMW Motorrad" → BMW, but rejects "Affordable Alfa" or "Fords Trailer"
    for brand in MAJOR_MANUFACTURERS:
        # Exact match or starts with brand followed by space
        if make_lower == brand or make_lower.startswith(brand + " "):
            return True

    return False

def normalize_make_name(make_name: str) -> str:
    """
    Normalize make name using aliases

    Args:
        make_name: Original make name

    Returns:
        Normalized make name
    """
    if not make_name:
        return make_name

    make_lower = make_name.lower().strip()

    # Check if it's an alias
    if make_lower in BRAND_ALIASES:
        return BRAND_ALIASES[make_lower].title()

    return make_name

def get_major_manufacturers_list() -> list:
    """
    Get sorted list of major manufacturers for display

    Returns:
        Sorted list of manufacturer names
    """
    return sorted([m.title() for m in MAJOR_MANUFACTURERS])
