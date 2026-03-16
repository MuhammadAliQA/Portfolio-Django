from django.db import migrations, models


def seed_more_exams(apps, schema_editor):
    Exam = apps.get_model("assessments", "Exam")
    Question = apps.get_model("assessments", "Question")
    Choice = apps.get_model("assessments", "Choice")

    listening_exam, created = Exam.objects.get_or_create(
        title="IELTS Listening Focus",
        defaults={
            "track": "ielts",
            "section": "Listening",
            "description": "Listening signal words va detail catching bo'yicha starter mock.",
            "level": "Band 5.5+",
            "duration_minutes": 18,
            "is_published": True,
        },
    )
    if created:
        q1 = Question.objects.create(
            exam=listening_exam,
            order=1,
            points=1,
            context_text="You will hear a conversation about a library membership. The student needs access to evening study rooms.",
            prompt="What does the student need most?",
        )
        Choice.objects.bulk_create([
            Choice(question=q1, text="A new student card", is_correct=False, order=1),
            Choice(question=q1, text="Evening study room access", is_correct=True, order=2),
            Choice(question=q1, text="A cheaper cafeteria plan", is_correct=False, order=3),
            Choice(question=q1, text="Weekend parking", is_correct=False, order=4),
        ])
        q2 = Question.objects.create(
            exam=listening_exam,
            order=2,
            points=1,
            context_text="The speaker says registrations close on Friday, but support is available by email after that.",
            prompt="When does registration close?",
        )
        Choice.objects.bulk_create([
            Choice(question=q2, text="Wednesday", is_correct=False, order=1),
            Choice(question=q2, text="Thursday", is_correct=False, order=2),
            Choice(question=q2, text="Friday", is_correct=True, order=3),
            Choice(question=q2, text="Sunday", is_correct=False, order=4),
        ])

    verbal_exam, created = Exam.objects.get_or_create(
        title="SAT Verbal Logic",
        defaults={
            "track": "sat",
            "section": "Verbal",
            "description": "Short passage va evidence-based verbal practice.",
            "level": "1200-1400",
            "duration_minutes": 18,
            "is_published": True,
        },
    )
    if created:
        q1 = Question.objects.create(
            exam=verbal_exam,
            order=1,
            points=1,
            context_text="Passage: 'While speed matters in modern products, clarity remains the foundation of trust between users and systems.'",
            prompt="The passage suggests that trust is built primarily through:",
        )
        Choice.objects.bulk_create([
            Choice(question=q1, text="Aggressive marketing", is_correct=False, order=1),
            Choice(question=q1, text="Clarity", is_correct=True, order=2),
            Choice(question=q1, text="Lower prices only", is_correct=False, order=3),
            Choice(question=q1, text="Visual complexity", is_correct=False, order=4),
        ])
        q2 = Question.objects.create(
            exam=verbal_exam,
            order=2,
            points=1,
            context_text="Passage: 'The author contrasts fast output with thoughtful design to emphasize balance rather than extremes.'",
            prompt="Which word best describes the author's tone?",
        )
        Choice.objects.bulk_create([
            Choice(question=q2, text="Balanced", is_correct=True, order=1),
            Choice(question=q2, text="Hostile", is_correct=False, order=2),
            Choice(question=q2, text="Confused", is_correct=False, order=3),
            Choice(question=q2, text="Sarcastic", is_correct=False, order=4),
        ])


def enrich_existing_questions(apps, schema_editor):
    Question = apps.get_model("assessments", "Question")
    for question in Question.objects.filter(context_text=""):
        if question.exam.track == "ielts":
            question.context_text = "Read the short prompt carefully, identify the main idea, then choose the most accurate option."
        else:
            question.context_text = "Use the information in the prompt and apply the correct SAT reasoning strategy before selecting your answer."
        question.save(update_fields=["context_text"])


class Migration(migrations.Migration):
    dependencies = [
        ("assessments", "0002_seed_sample_exams"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="context_text",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(enrich_existing_questions, migrations.RunPython.noop),
        migrations.RunPython(seed_more_exams, migrations.RunPython.noop),
    ]
