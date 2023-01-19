"""Models of the user experience module."""
from django.db import models


class Menu(models.Model):
    """A menu to be displayed in the user interface."""

    menu_id = models.CharField(max_length=255, unique=True, primary_key=True)
    extension = models.ForeignKey(
        'extensions.Extension', on_delete=models.CASCADE, null=True)


# TODO Advanced validators for requirements with if-clauses
# TODO Item_id only has to be unique per extension
class MenuItem(models.Model):
    """An item to be displayed in a menu."""

    item_id = models.CharField(max_length=255, unique=True, primary_key=True)
    menu_id = models.ForeignKey(
        'menus.Menu', on_delete=models.CASCADE)
    label = models.CharField(max_length=255)
    extension = models.ForeignKey(
        'extensions.Extension', on_delete=models.CASCADE)
    action = models.CharField(
        max_length=50,
        null=True,
        choices=[
            ('component', 'component'),
            ('link', 'link'),
        ]
    )
    action_target = models.CharField(
        max_length=50,
        default='main',
        choices=[
            ('main', 'main'),
            ('blank', 'blank')
        ]
    )
    component_name = models.CharField(max_length=255, null=True)
    link_source = models.URLField(null=True)
    order = models.FloatField(default=1)
    parent_item = models.ForeignKey(
        'menus.MenuItem', on_delete=models.CASCADE, null=True)
    style = models.CharField(
        max_length=50,
        default='normal',
        choices=[
            ('normal', 'normal'),
        ]
    )
    required_role = models.CharField(max_length=255, null=True)
    icon_name = models.CharField(max_length=255, null=True)
    icon_path = models.URLField(null=True)

    def __str__(self):
        """Return string representation of the model."""
        return f'MenuItem ({self.item_id})'
