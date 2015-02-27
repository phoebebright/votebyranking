from django.db import models
from django.db.models import Max, Sum
from django.conf import settings

from taggit.managers import TaggableManager


# from lazysignup.signals import converted
# from django.dispatch import receiver
#
# @receiver(converted)
# def my_callback(sender, **kwargs):
#     print "New user account: %s!" % kwargs['user'].username

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class MyUserManager(BaseUserManager):
    def create_user(self, email,  password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),

        )


        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=150, default='')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        self.username = self.email
        super(MyUser, self).save(*args, **kwargs)

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Answer(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    help_text = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    question = models.ForeignKey('Question', related_name="answers")

    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ('question', 'order')

    def __unicode__(self):
        return u"%s: %s" % (self.question.label, self.title)



class GroupedAnswer(Answer):
    group = models.CharField(max_length=255)

    class Meta:
        ordering = ('group', 'order',)

class Question(models.Model):
    QUESTION_TYPES = [
        ('S', 'Single-choice question'),
        ('M', 'Multi-choice question'),
        ('F', 'Free-text question'),
        ('P', 'Prioritise question'),
    ]


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
        return self.label



class SubmissionSet(models.Model):
    """ A set of submissions stored and associated with a particular user to
        provide a mechanism through which a single user can provide repeated
        sets of answers to the same questionnaire.
    """
    slug = models.SlugField(blank=True)
    tag = models.SlugField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saq_submissions_sets')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)



    def save(self, *args, **kwargs):

        super(SubmissionSet, self).save(*args, **kwargs)


class Submission(models.Model):
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    answer_text = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saq_submissions')

    submission_set = models.ForeignKey(
        SubmissionSet, related_name='submissions', null=True)

    class Meta:
        ordering = ('submission_set', 'user', 'question', 'score')



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