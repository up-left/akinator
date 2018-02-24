from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
import json
import uuid

from .models import Game, Question, Guess, Answer, AnswerGuess, GameGuess, GameQuestionOffer
from .serializers import GuessSerializer, QuestionSerializer


MAX_QUESTIONS = 5
GUESS_THRESHOLD = 1.8  # превышение вероятности, после которого стоит спросить пользователя о догадке


@csrf_exempt
@require_http_methods(["POST"])
def play(request):
    request_data = json.loads(request.body.decode('utf-8'))
    response_data = {}

    is_start = 'uid' not in request_data
    is_guess = 'guess_id' in request_data
    is_question = 'question_id' in request_data
    is_user_guess = 'guess' in request_data
    is_user_question = 'question' in request_data

    if is_start:
        game = Game.objects.create(uid=uuid.uuid4())
        response_data['uid'] = game.uid
    else:
        game = get_object_or_404(Game, uid=request_data['uid'])

    # Сохранение ответа на вопрос
    if is_question or is_guess:
        if is_question:
            answer = Answer.objects.filter(game=game, question=int(request_data['question_id'])).first()
        else:
            answer = AnswerGuess.objects.filter(game=game, guess=int(request_data['guess_id'])).first()

        if not answer:
            return JsonResponse({'message': 'question not asked'}, status=422)
        if 'choice' not in request_data:
            return JsonResponse({'message': '"choice" field not found'}, status=422)
        if answer.choice is not None:
            return JsonResponse({'message': 'question already answered'}, status=422)

        choice = request_data['choice']
        if choice == 'y':
            if is_question:
                answer.choice = True
                answer.save()
            else:
                answer.delete()
                game.right_guess_id = answer.guess_id
                game.save()
                Answer.objects.filter(game=game).update(guess=answer.guess_id)
                return JsonResponse({'finish': True})
        elif choice == 'n':
            answer.choice = False
            answer.save()
        elif choice == 's':
            pass
        else:
            return JsonResponse({'message': 'choice can be only "y", "n" or "s"'}, status=422)

    # Генерация нового вопроса или догадки
    if is_start or is_question or is_guess:
        question_offer = GameQuestionOffer.objects.filter(game=game).order_by('th').first()
        questions_exceed = game.answer_set.count() + game.answerguess_set.count() >= MAX_QUESTIONS or not question_offer

        best_guesses = GameGuess.objects.filter(game=game, answerguess_id__isnull=True).order_by('-p')[:2]
        best_guess = best_guesses[0].guess if best_guesses else None
        has_guess = best_guesses and (len(best_guesses) == 1 or
                                      best_guesses[0].p >= best_guesses[1].p * GUESS_THRESHOLD)

        if (is_guess and questions_exceed) or not best_guess:
            # просим прислать догадку, если вопросы кончились, а лучшая на данный момент догадка не подошла
            response_data.update({'send_guess': True})
        elif questions_exceed or has_guess:
            AnswerGuess.objects.create(game=game, guess=best_guess)
            response_data.update({'guess_id': best_guess.id, 'guess': best_guess.name})
        else:
            question = question_offer.question
            Answer.objects.create(game=game, question=question)
            response_data.update({'question_id': question.id, 'question': question.name})

    # Сохранение догадки, присланной пользователем
    elif is_user_guess:
        if game.right_guess is not None:
            return JsonResponse({'message': 'this game already has right answer'}, status=422)

        guess, _ = Guess.objects.get_or_create(name=request_data['guess'])
        Answer.objects.filter(game=game).update(guess=guess)
        game.right_guess = guess
        game.save()

        best_guess_no_filter = GameGuess.objects.filter(game=game).exclude(guess=guess).order_by('-p').first()
        if not best_guess_no_filter:
            return JsonResponse({'finish': True})

        response_data.update({'send_question': True,
                              'second_guess_id': best_guess_no_filter.guess.id,
                              'second_guess': best_guess_no_filter.guess.name})

    # Сохранение вопроса, присланного пользователем
    elif is_user_question:
        question, _ = Question.objects.get_or_create(name=request_data['question'])
        second_guess = get_object_or_404(Guess, id=int(request_data['second_guess_id']))
        Answer.objects.create(game=game, question=question, guess=game.right_guess, choice=True)
        Answer.objects.create(game=game, question=question, guess=second_guess, choice=False)
        return JsonResponse({'finish': True})

    return JsonResponse(response_data)


class SearchMixin:

    def get_queryset(self):
        search = self.request.query_params.get('search', None)
        queryset = super().get_queryset()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class GuessList(SearchMixin, generics.ListAPIView):
    serializer_class = GuessSerializer
    queryset = Guess.objects.all()


class QuestionList(SearchMixin, generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
