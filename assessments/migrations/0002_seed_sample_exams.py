from django.db import migrations


def seed_exams(apps, schema_editor):
    Exam = apps.get_model("assessments", "Exam")
    Question = apps.get_model("assessments", "Question")
    Choice = apps.get_model("assessments", "Choice")

    if Exam.objects.exists():
        return

    ielts = Exam.objects.create(
        title="IELTS Reading Sprint",
        track="ielts",
        section="Reading",
        description="Band oshirish uchun tezkor reading mock test.",
        level="Band 6.0+",
        duration_minutes=25,
        is_published=True,
    )
    sat = Exam.objects.create(
        title="SAT Math Pulse",
        track="sat",
        section="Math",
        description="Core algebra va problem solving bo'yicha qisqa SAT mock.",
        level="1100-1350",
        duration_minutes=20,
        is_published=True,
    )

    ielts_q1 = Question.objects.create(exam=ielts, prompt="A synonym of 'rapid' is:", order=1, points=1)
    Choice.objects.bulk_create([
        Choice(question=ielts_q1, text="slow", is_correct=False, order=1),
        Choice(question=ielts_q1, text="quick", is_correct=True, order=2),
        Choice(question=ielts_q1, text="unclear", is_correct=False, order=3),
        Choice(question=ielts_q1, text="formal", is_correct=False, order=4),
    ])
    ielts_q2 = Question.objects.create(exam=ielts, prompt="The writer's main purpose is usually identified by:", order=2, points=1)
    Choice.objects.bulk_create([
        Choice(question=ielts_q2, text="Only the first sentence", is_correct=False, order=1),
        Choice(question=ielts_q2, text="The overall argument and supporting details", is_correct=True, order=2),
        Choice(question=ielts_q2, text="The last word of each paragraph", is_correct=False, order=3),
        Choice(question=ielts_q2, text="The title font size", is_correct=False, order=4),
    ])
    ielts_q3 = Question.objects.create(exam=ielts, prompt="Skimming is best used for:", order=3, points=1)
    Choice.objects.bulk_create([
        Choice(question=ielts_q3, text="Finding exact numbers only", is_correct=False, order=1),
        Choice(question=ielts_q3, text="Getting the general idea quickly", is_correct=True, order=2),
        Choice(question=ielts_q3, text="Memorising every sentence", is_correct=False, order=3),
        Choice(question=ielts_q3, text="Checking spelling rules", is_correct=False, order=4),
    ])

    sat_q1 = Question.objects.create(exam=sat, prompt="If 3x + 9 = 24, what is x?", order=1, points=1)
    Choice.objects.bulk_create([
        Choice(question=sat_q1, text="3", is_correct=False, order=1),
        Choice(question=sat_q1, text="4", is_correct=False, order=2),
        Choice(question=sat_q1, text="5", is_correct=True, order=3),
        Choice(question=sat_q1, text="6", is_correct=False, order=4),
    ])
    sat_q2 = Question.objects.create(exam=sat, prompt="Which value satisfies x^2 = 49?", order=2, points=1)
    Choice.objects.bulk_create([
        Choice(question=sat_q2, text="7 and -7", is_correct=True, order=1),
        Choice(question=sat_q2, text="Only 7", is_correct=False, order=2),
        Choice(question=sat_q2, text="Only -7", is_correct=False, order=3),
        Choice(question=sat_q2, text="0", is_correct=False, order=4),
    ])
    sat_q3 = Question.objects.create(exam=sat, prompt="What is 20% of 150?", order=3, points=1)
    Choice.objects.bulk_create([
        Choice(question=sat_q3, text="15", is_correct=False, order=1),
        Choice(question=sat_q3, text="20", is_correct=False, order=2),
        Choice(question=sat_q3, text="25", is_correct=False, order=3),
        Choice(question=sat_q3, text="30", is_correct=True, order=4),
    ])


def unseed_exams(apps, schema_editor):
    Exam = apps.get_model("assessments", "Exam")
    Exam.objects.filter(title__in=["IELTS Reading Sprint", "SAT Math Pulse"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_exams, unseed_exams),
    ]
