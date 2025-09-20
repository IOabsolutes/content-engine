import random
import string
from django.utils.text import slugify


def generate_random_string(size=10):
    chars = string.ascii_lowercase + string.digits
    random_chars = [random.choice(chars) for _ in range(0, size)]
    return "".join(random_chars)


def unique_slug_generator(
    instance, new_slug=None, size=5, slug_field="slug", title_field="titile"
):
    """
    Made it a celery task
    """
    """
    Generate a unique slug for the given instance.

    Args:
        instance: Model instance
        new_slug: Pre-computed slug (optional)
        size: Length of random string to append if needed
        slug_field: Field name that stores the slug
        title_field: Field name that contains the title to slugify

    Returns:
        str: Unique slug
    """
    # Get the title value from the instance
    title_value = getattr(instance, title_field, None)

    if new_slug is not None:
        slug = new_slug
    elif title_value:
        slug = slugify(title_value)
    else:
        # Fallback if no title is available
        slug = generate_random_string(size=size)

    # Build lookup dictionary for checking uniqueness
    lookup = {f"{slug_field}__iexact": slug}
    ModelClass = instance.__class__

    # Check if slug already exists (exclude current instance if updating)
    queryset = ModelClass.objects.filter(**lookup)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    if queryset.exists():
        # Generate new slug with random suffix
        random_str = generate_random_string(size=size)
        new_slug = f"{slug}-{random_str}"
        return unique_slug_generator(
            instance,
            new_slug=new_slug,
            size=size,
            slug_field=slug_field,
            title_field=title_field,
        )

    return slug
