from django import template
from ..models import X, O


register = template.Library()


@register.filter
def board_representation(cell_value):
    if cell_value == X:
        return 'X'
    elif cell_value == O:
        return 'O'
    else:
        return ' '

