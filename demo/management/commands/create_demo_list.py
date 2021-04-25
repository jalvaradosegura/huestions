from django.core.management.base import BaseCommand, CommandError

from ...factories import (
    DemoAlternativeFactory,
    DemoListFactory,
    DemoQuestionFactory,
)


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        try:
            demo_list = DemoListFactory(title='Demo List')

            demo_q1 = DemoQuestionFactory(
                title='Which one do you prefer?', child_of=demo_list
            )
            demo_a1 = DemoAlternativeFactory(
                title='Coca Cola', question=demo_q1
            )
            demo_a1.image = 'alternative_pics/demo/demo_coca_cola.jpeg'
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(title='Pepsi', question=demo_q1)
            demo_a2.image = 'alternative_pics/demo/demo_pepsi.jpeg'
            demo_a2.save()

            demo_q2 = DemoQuestionFactory(
                title='You have to eat one of these for the rest of your life, which one?',
                child_of=demo_list,
            )
            demo_a1 = DemoAlternativeFactory(title='Burger', question=demo_q2)
            demo_a1.image = 'alternative_pics/demo/demo_burguer.jpeg'
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(title='Pizza', question=demo_q2)
            demo_a2.image = 'alternative_pics/demo/demo_pizza.jpeg'
            demo_a2.save()

            demo_q3 = DemoQuestionFactory(
                title='How do you prefer to eat a burger?', child_of=demo_list
            )
            demo_a1 = DemoAlternativeFactory(
                title='With cutlery', question=demo_q3
            )
            demo_a1.image = 'alternative_pics/demo/demo_cutlery.jpeg'
            demo_a1.save()
            demo_a2 = DemoAlternativeFactory(
                title='With your bare hands', question=demo_q3
            )
            demo_a2.image = 'alternative_pics/demo/demo_bare_hands.jpeg'
            demo_a2.save()

        except FileNotFoundError:
            raise CommandError('error')

        self.stdout.write(self.style.SUCCESS('success'))
