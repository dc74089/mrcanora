from .models import SiteConfig


def enable_exit_ticket():
    sc = SiteConfig.objects.get(key="exit_ticket")
    sc.value = True
    sc.save()


def disable_exit_ticket():
    sc = SiteConfig.objects.get(key="exit_ticket")
    sc.value = False
    sc.save()


def debug_log():
    print("This happened")
