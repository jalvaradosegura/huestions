from django.shortcuts import redirect, render
from django.views.generic import DetailView
from django.views.generic.base import TemplateView

from .models import DemoList


class AnswerDemoView1(DetailView):
    template_name = 'demo/answer_1.html'
    model = DemoList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.object.questions.all()[0]
        alternative_1 = question.alternatives.all()[0]
        alternative_2 = question.alternatives.all()[1]

        context['question'] = question
        context['alternative_1'] = alternative_1
        context['alternative_2'] = alternative_2
        return context

    def post(self, request, *args, **kwargs):
        demo_list = DemoList.objects.get(id=self.kwargs.get('pk'))

        if 'alternative_1' in request.POST or 'vote_1' in request.POST:
            alternative = demo_list.questions.all()[0].alternatives.all()[0]
            alternative.votes += 1
            alternative.save()
            return redirect('answer_demo_2', demo_list.id)

        if 'alternative_2' in request.POST or 'vote_2' in request.POST:
            alternative = demo_list.questions.all()[0].alternatives.all()[1]
            alternative.votes += 1
            alternative.save()
            return redirect('answer_demo_2', demo_list.id)

        question = demo_list.questions.first()
        context = {
            'questions': question,
            'alternative_1': question.alternatives.all()[0],
            'alternative_2': question.alternatives.all()[1],
        }
        return render(request, self.template_name, context)


class AnswerDemoView2(DetailView):
    template_name = 'demo/answer_2.html'
    model = DemoList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.object.questions.all()[1]
        alternative_1 = question.alternatives.all()[0]
        alternative_2 = question.alternatives.all()[1]

        context['question'] = question
        context['alternative_1'] = alternative_1
        context['alternative_2'] = alternative_2
        return context

    def post(self, request, *args, **kwargs):
        demo_list = DemoList.objects.get(id=self.kwargs.get('pk'))

        if 'alternative_1' in request.POST or 'vote_1' in request.POST:
            alternative = demo_list.questions.all()[1].alternatives.all()[0]
            alternative.votes += 1
            alternative.save()
            return redirect('answer_demo_3', demo_list.id)

        if 'alternative_2' in request.POST or 'vote_2' in request.POST:
            alternative = demo_list.questions.all()[1].alternatives.all()[1]
            alternative.votes += 1
            alternative.save()
            return redirect('answer_demo_3', demo_list.id)

        question = demo_list.questions.all()[1]
        context = {
            'questions': question,
            'alternative_1': question.alternatives.all()[0],
            'alternative_2': question.alternatives.all()[1],
        }
        return render(request, self.template_name, context)


class AnswerDemoView3(DetailView):
    template_name = 'demo/answer_3.html'
    model = DemoList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.object.questions.all()[2]
        alternative_1 = question.alternatives.all()[0]
        alternative_2 = question.alternatives.all()[1]

        context['question'] = question
        context['alternative_1'] = alternative_1
        context['alternative_2'] = alternative_2
        return context

    def post(self, request, *args, **kwargs):
        demo_list = DemoList.objects.get(id=self.kwargs.get('pk'))

        if 'alternative_1' in request.POST or 'vote_1' in request.POST:
            alternative = demo_list.questions.all()[2].alternatives.all()[0]
            alternative.votes += 1
            alternative.save()
            return redirect('demo_results', demo_list.id)

        if 'alternative_2' in request.POST or 'vote_2' in request.POST:
            alternative = demo_list.questions.all()[2].alternatives.all()[1]
            alternative.votes += 1
            alternative.save()
            return redirect('demo_results', demo_list.id)

        question = demo_list.questions.all()[2]
        context = {
            'questions': question,
            'alternative_1': question.alternatives.all()[0],
            'alternative_2': question.alternatives.all()[1],
        }
        return render(request, self.template_name, context)


class DemoResults(TemplateView):
    template_name = 'demo/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        demo_list = DemoList.objects.get(id=self.kwargs.get('pk'))

        question_1 = demo_list.questions.all()[0]
        question_2 = demo_list.questions.all()[1]
        question_3 = demo_list.questions.all()[2]

        alternative_1 = question_1.alternatives.all()[0]
        alternative_2 = question_1.alternatives.all()[1]
        alternative_3 = question_2.alternatives.all()[0]
        alternative_4 = question_2.alternatives.all()[1]
        alternative_5 = question_3.alternatives.all()[0]
        alternative_6 = question_3.alternatives.all()[1]

        image_1 = alternative_1.image
        image_2 = alternative_2.image
        image_3 = alternative_3.image
        image_4 = alternative_4.image
        image_5 = alternative_5.image
        image_6 = alternative_6.image

        q1_divide_by = (
            (alternative_1.votes + alternative_2.votes)
            if (alternative_1.votes + alternative_2.votes) != 0
            else 1
        )
        q2_divide_by = (
            (alternative_3.votes + alternative_4.votes)
            if alternative_3.votes + alternative_4.votes != 0
            else 1
        )
        q3_divide_by = (
            (alternative_5.votes + alternative_6.votes)
            if alternative_5.votes + alternative_6.votes != 0
            else 1
        )

        votes_percentage_1 = float(
            "{:.2f}".format(alternative_1.votes * 100 / q1_divide_by)
        )
        votes_percentage_2 = float(
            "{:.2f}".format(alternative_2.votes * 100 / q1_divide_by)
        )
        votes_percentage_3 = float(
            "{:.2f}".format(alternative_3.votes * 100 / q2_divide_by)
        )
        votes_percentage_4 = float(
            "{:.2f}".format(alternative_4.votes * 100 / q2_divide_by)
        )
        votes_percentage_5 = float(
            "{:.2f}".format(alternative_5.votes * 100 / q3_divide_by)
        )
        votes_percentage_6 = float(
            "{:.2f}".format(alternative_6.votes * 100 / q3_divide_by)
        )

        context['question_1'] = question_1
        context['question_2'] = question_2
        context['question_3'] = question_3
        context['alternative_1'] = alternative_1
        context['alternative_2'] = alternative_2
        context['alternative_3'] = alternative_3
        context['alternative_4'] = alternative_4
        context['alternative_5'] = alternative_5
        context['alternative_6'] = alternative_6
        context['image_1'] = image_1
        context['image_2'] = image_2
        context['image_3'] = image_3
        context['image_4'] = image_4
        context['image_5'] = image_5
        context['image_6'] = image_6
        context['votes_percentage_1'] = votes_percentage_1
        context['votes_percentage_2'] = votes_percentage_2
        context['votes_percentage_3'] = votes_percentage_3
        context['votes_percentage_4'] = votes_percentage_4
        context['votes_percentage_5'] = votes_percentage_5
        context['votes_percentage_6'] = votes_percentage_6

        return context
