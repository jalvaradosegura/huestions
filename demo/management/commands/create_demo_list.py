from django.core.management.base import BaseCommand, CommandError

from core.constants import (
    COMMAND_CREATE_DEMO_ERROR_MESSAGE,
    COMMAND_CREATE_DEMO_HELP_TEXT,
    COMMAND_CREATE_DEMO_SUCCESS_MESSAGE,
    IMAGE_1_NAME,
    IMAGE_2_NAME,
    IMAGE_3_NAME,
    IMAGE_4_NAME,
    IMAGE_5_NAME,
    IMAGE_6_NAME,
)

from ...factories import (
    DemoAlternativeFactory,
    DemoListFactory,
    DemoQuestionFactory,
)


class Command(BaseCommand):
    help = COMMAND_CREATE_DEMO_HELP_TEXT

    def handle(self, *args, **options):
        try:
            demo_list = DemoListFactory(title='Demo List')

            demo_q1 = DemoQuestionFactory(
                title='Which one do you prefer?', child_of=demo_list
            )
            demo_a1 = DemoAlternativeFactory(
                title='Coca Cola', question=demo_q1
            )
            demo_a1.image = 'alternative_pics/demo/' + IMAGE_1_NAME
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(title='Pepsi', question=demo_q1)
            demo_a2.image = 'alternative_pics/demo/' + IMAGE_2_NAME
            demo_a2.save()

            demo_q2 = DemoQuestionFactory(
                title=(
                    'You have to eat one of these for the rest of your life, '
                    'which one?'
                ),
                child_of=demo_list,
            )
            demo_a1 = DemoAlternativeFactory(title='Burger', question=demo_q2)
            demo_a1.image = 'alternative_pics/demo/' + IMAGE_3_NAME
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(title='Pizza', question=demo_q2)
            demo_a2.image = 'alternative_pics/demo/' + IMAGE_4_NAME
            demo_a2.save()

            demo_q3 = DemoQuestionFactory(
                title='How do you prefer to eat a burger?', child_of=demo_list
            )
            demo_a1 = DemoAlternativeFactory(
                title='With cutlery', question=demo_q3
            )
            demo_a1.image = 'alternative_pics/demo/' + IMAGE_5_NAME
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(
                title='With your bare hands', question=demo_q3
            )
            demo_a2.image = 'alternative_pics/demo/' + IMAGE_6_NAME
            demo_a2.save()

        except FileNotFoundError:
            raise CommandError(COMMAND_CREATE_DEMO_ERROR_MESSAGE)

        self.stdout.write(self.style.SUCCESS(
            COMMAND_CREATE_DEMO_SUCCESS_MESSAGE)
        )
