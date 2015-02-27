from django.db import models
from django.db.models import Max, Sum


from taggit.managers import TaggableManager


# from lazysignup.signals import converted
# from django.dispatch import receiver
#
# @receiver(converted)
# def my_callback(sender, **kwargs):
#     print "New user account: %s!" % kwargs['user'].username


class Answer(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    help_text = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    question = models.ForeignKey('Question', related_name="answers")

    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ('question', 'order', 'slug')
        unique_together = (('question', 'slug'),)

    def __unicode__(self):
        return u"%s: %s" % (self.question.slug, self.title)


    def save(self, *args, **kwargs):

        super(Answer, self).save(*args, **kwargs)

class GroupedAnswer(Answer):
    group = models.CharField(max_length=255)

    class Meta:
        ordering = ('group', 'order', 'slug')

class Question(models.Model):
    QUESTION_TYPES = [
        ('S', 'Single-choice question'),
        ('M', 'Multi-choice question'),
        ('F', 'Free-text question'),
        ('P', 'Prioritise question'),
    ]

    slug = models.SlugField(
        help_text="A slug for identifying answers to this specific question "
        "(allows multiple only for multiple languages)")
    tags = TaggableManager(blank=True)
    label = models.CharField(max_length=512, blank=True)
    help_text = models.CharField(max_length=512, blank=True)
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES)
    optional = models.BooleanField(
        default=False,
        help_text="Only applies to free text questions",
    )

    depends_on_answer = models.ForeignKey(
        Answer, null=True, blank=True, related_name='trigger_questions')

    def save(self, *args, **kwargs):

        super(Question, self).save(*args, **kwargs)

    def copy_relations(self, oldinstance):
        for answer in oldinstance.answers.all():
            answer.pk = None
            answer.question = self
            answer.save()

        self.depends_on_answer = oldinstance.depends_on_answer

    # @staticmethod
    # def all_in_tree(page):
    #     root = page.get_root()
    #     # Remember that there might be questions on the root page as well!
    #     tree = root.get_descendants() | Page.objects.filter(id=root.id)
    #     placeholders = Placeholder.objects.filter(page__in=tree)
    #     return Question.objects.filter(placeholder__in=placeholders)
    #
    # @staticmethod
    # def all_in_page(page):
    #     placeholders = Placeholder.objects.filter(page=page)
    #     return Question.objects.filter(placeholder__in=placeholders)

    def score(self, answers):
        if self.question_type == 'F':
            return 0
        elif self.question_type == 'S':
            return self.answers.get(slug=answers).score
        elif self.question_type == 'M':
            answers_list = answers.split(',')
            return sum([self.answers.get(slug=a).score for a in answers_list])

    @property
    def max_score(self):
        if not hasattr(self, '_max_score'):
            if self.question_type == "S":
                self._max_score = self.answers.aggregate(
                    Max('score'))['score__max']
            elif self.question_type == "M":
                self._max_score = self.answers.aggregate(
                    Sum('score'))['score__sum']
            else:
                self._max_score = None  # don't score free-text answers
        return self._max_score

    def percent_score_for_user(self, user):
        if self.max_score:
            try:
                score = Submission.objects.get(
                    question=self.slug,
                    user=user,
                ).score
            except Submission.DoesNotExist:
                return 0
            return 100.0 * score / self.max_score
        else:
            return None

    def __unicode__(self):
        return self.slug



class SubmissionSet(models.Model):
    """ A set of submissions stored and associated with a particular user to
        provide a mechanism through which a single user can provide repeated
        sets of answers to the same questionnaire.
    """
    slug = models.SlugField(blank=True)
    tag = models.SlugField(blank=True)
    user = models.ForeignKey('auth.User', related_name='saq_submissions_sets')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        super(SubmissionSet, self).save(*args, **kwargs)


class Submission(models.Model):
    question = models.SlugField()
    answer = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    user = models.ForeignKey('auth.User', related_name='saq_submissions')

    submission_set = models.ForeignKey(
        SubmissionSet, related_name='submissions', null=True)

    class Meta:
        ordering = ('submission_set', 'user', 'question', 'score')


    def answer_list(self):
        return self.answer.split(",")

    def __unicode__(self):
        return u"%s answer to %s (%s)" % (
            self.user, self.question, self.submission_set.slug
            if self.submission_set else "default")

    def save(self, *args, **kwargs):

        super(Submission, self).save(*args, **kwargs)

def aggregate_score_for_user_by_questions(user, questions):
    scores = []
    for question in questions:
        score = question.percent_score_for_user(user)
        if score is not None:
            scores.append(score)
    if len(scores):
        return sum(scores) / len(scores)
    else:
        return 0


def aggregate_score_for_user_by_tags(user, tags):
    questions = Question.objects.filter(tags__name__in=tags).distinct()
    scores = []
    for question in questions:
        score = question.percent_score_for_user(user)
        if score is not None:
            scores.append(score)
    if len(scores):
        return sum(scores) / len(scores)
    else:
        return 0