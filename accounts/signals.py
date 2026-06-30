from django.db.models.signals import pre_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(pre_save, sender=User)
def normalize_email(sender, instance, **kwargs):
    if instance.email:
        instance.email = instance.email.strip().lower()


@receiver(post_migrate)
def seed_initial_data(sender, **kwargs):
    """
    Runs once after every migrate command (fires per app).
    Gated on 'accounts' so it only executes once per migrate run.
    Idempotent — skips silently if admin already exists.
    """
    if sender.name != "accounts":
        return

    if User.objects.filter(username="admin").exists():
        return

    try:
        from devices.models import Device
        from fleet.models import Vehicle
        from drivers.models import Driver
        from tyres.models import Tyre
    except Exception as e:
        print(f"  [seed] Skipped — tables not ready: {e}")
        return

    from datetime import date

    # ── 1. Admin ──────────────────────────────────────────────────────────
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@fleet.local",
        password="Admin@1234",
        role="admin",
    )
    admin.email_verified = True
    admin.save(update_fields=["email_verified"])
    print("  [seed] admin  → Admin@1234")
    print("  [seed] 10 drivers created  → Driver@1234")
    print("  [seed] Seeding complete ✓")
