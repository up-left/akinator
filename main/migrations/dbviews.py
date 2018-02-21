from django.db import migrations


class Migration(migrations.Migration):

    # ./manage.py migrate --fake main 0001_initial && ./manage.py migrate main dbviews

    dependencies = [
        ('main', '0001_initial'),  # иcправить на последнюю для пересоздания
    ]

    sqls = (
        """drop aggregate if exists mul(real) cascade""",

        """create aggregate mul(real) (sfunc = float4mul, stype = real)""",

        """drop view if exists guess_question cascade""",

        # вероятность ответить 'y' на вопрос для данной догадки
        """
        create or replace view guess_question as
        select main_guess.id guess_id, main_question.id question_id,
        sum(case main_answer.choice when 't' then 1 else 0 end) + 1 y,
        sum(case when main_answer.choice is not null then 1 else 0 end) + 2 total
        from main_guess
        cross join main_question
        full join main_answer on main_answer.guess_id = main_guess.id and main_answer.question_id = main_question.id
        group by main_guess.id, main_question.id
        """,

        # вероятность догадки в данной игре
        """
        create or replace view game_guess as
        select row_number() over () id, main_game.uid game_id, main_guess.id guess_id, main_answerguess.id answerguess_id,
            coalesce(mul((case main_answer.choice when 't' then y else total - y end)::numeric / total::numeric), 1) p
        from main_game
        cross join main_guess
        full join main_answer on main_game.uid = main_answer.game_id
        full join guess_question on guess_question.question_id = main_answer.question_id and guess_question.guess_id = main_guess.id
        left join main_answerguess on main_answerguess.game_id = main_game.uid and main_answerguess.guess_id = main_guess.id
        group by main_game.uid, main_guess.id, main_answerguess.id
        """,

        # вероятность догадки в данной игре (сумма вероятностей догадок для игры = 1)
        """
        create or replace view game_guess_fixed as
        with p_total as (select game_id, sum(p) p from game_guess where answerguess_id is null group by game_id)
        select game_guess.game_id, guess_id, game_guess.p / p_total.p p
        from game_guess
        left join p_total on game_guess.game_id = p_total.game_id
        where answerguess_id is null
        order by p desc
        """,

        # вероятность ответить 'y' на вопрос в данной игре
        """
        create or replace view game_question as
        select game_id, question_id, sum(p * y / total) p
        from guess_question
        join game_guess_fixed on game_guess_fixed.guess_id = guess_question.guess_id
        group by game_id, question_id
        """,

        # вероятность догадки в данной игре при ответе 'y' или 'n' для всех вопросов
        """
        create or replace view game_guess_question as
        select game_guess_fixed.game_id, game_guess_fixed.guess_id, guess_question.question_id,
            p * y::numeric / total py, p * (1 - y::numeric / total) pn
        from game_guess_fixed
        join guess_question on game_guess_fixed.guess_id = guess_question.guess_id
        left join main_answer on main_answer.game_id = game_guess_fixed.game_id and main_answer.question_id = guess_question.question_id
        where main_answer.id is null
        """,

        # энтропия догадок в данной игре для всех вопросов
        """
        create or replace view game_question_h as
        select game_guess_question.game_id, game_guess_question.question_id,
        sum(-py * log(2, py::numeric)) hy, sum(-pn * log(2, pn::numeric)) hn
        from game_guess_question
        group by game_guess_question.game_id, game_guess_question.question_id
        """,

        # энтропия догадок в данной игре для всех вопросов (просуммированная для 'y' и 'n')
        """
        create or replace view game_question_offer as
        select row_number() over () id, game_question.game_id, game_question.question_id, hy * p + hn * (1 - p) th
        from game_question_h
        join game_question on game_question.game_id = game_question_h.game_id
            and game_question.question_id = game_question_h.question_id
        order by th
        """
    )

    operations = [migrations.RunSQL(sql) for sql in sqls]
