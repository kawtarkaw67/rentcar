from django import template

register = template.Library()


@register.simple_tag
def nb_notifications_non_lues(user):
    """Retourne le nombre de notifications non lues d'un utilisateur."""
    if user.is_authenticated:
        return user.notifications.filter(lu=False).count()
    return 0
