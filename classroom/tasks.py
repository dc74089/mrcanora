from .models import SiteConfig, TeambuildingQuestion


def enable_exit_ticket():
    sc = SiteConfig.objects.get(key="exit_ticket")
    sc.value = True
    sc.save()


def disable_exit_ticket():
    sc = SiteConfig.objects.get(key="exit_ticket")
    sc.value = False
    sc.save()


def enable_random_question():
    tq = TeambuildingQuestion.objects.filter(active=False).order_by("?")

    if tq:
        q = tq.first()

        q.active = True

        q.save()


def debug_log():
    print("This happened")
