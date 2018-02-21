from django.db import models


class Question(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Guess(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Game(models.Model):
    uid = models.UUIDField(primary_key=True)
    play_time = models.DateTimeField(auto_now=True)
    # поле информационное, для подсчета используется Answer.guess
    right_guess = models.ForeignKey(Guess, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1}'.format(self.uid, self.right_guess)


class Answer(models.Model):
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    guess = models.ForeignKey(Guess, null=True, blank=True, on_delete=models.CASCADE)
    choice = models.NullBooleanField()

    def __str__(self):
        return '{0}: {1}: {2} - {3}'.format(
            self.game.uid if self.game else 'Ext', self.guess, self.question.name, self.choice)


class AnswerGuess(models.Model):
    game = models.ForeignKey(Game, null=True, blank=True, on_delete=models.CASCADE)
    guess = models.ForeignKey(Guess, on_delete=models.CASCADE)
    choice = models.NullBooleanField()

    def __str__(self):
        return '{0}: {1} - {2}'.format(self.game.uid if self.game else 'Ext', self.guess.name, self.choice)


# модели для view из базы данных

class GameGuess(models.Model):
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    guess = models.ForeignKey(Guess, on_delete=models.DO_NOTHING)
    answerguess = models.ForeignKey(AnswerGuess, on_delete=models.DO_NOTHING)
    p = models.FloatField()

    class Meta:
        managed = False
        db_table = 'game_guess'


class GameQuestionOffer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    th = models.FloatField()

    class Meta:
        managed = False
        db_table = 'game_question_offer'
