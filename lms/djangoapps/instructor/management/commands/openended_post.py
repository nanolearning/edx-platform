"""
Command to manually re-post open ended submissions to the grader.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from optparse import make_option

from courseware.courses import get_course
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.open_ended_grading_classes.openendedchild import OpenEndedChild
from ._utils import get_module_for_student


class Command(BaseCommand):
    """
    Command to manually re-post open ended submissions to the grader.
    """

    help = ("Usage: openended_post <course_id> <problem_location> <student_ids.txt> --dry-run --task-index=<task_index>\n"
            "The text file should contain a User.id in each line.")

    option_list = BaseCommand.option_list + (
        make_option('-n', '--dry-run',
                    action='store_true', dest='dry_run', default=False,
                    help="Do everything except send the submission to the grader. "),
        make_option('--task-index',
                    type='int', default=0,
                    help="Index of task state."),
    )

    def handle(self, *args, **options):

        dry_run = options['dry_run']
        task_index = options['task_index']

        if len(args) == 3:
            course_id = args[0]
            location = args[1]
            students_ids = [line.strip() for line in open(args[2])]
        else:
            print self.help
            return

        try:
            course = get_course(course_id)
        except ValueError as err:
            print err
            return

        descriptor = modulestore().get_instance(course.id, location, depth=0)
        if descriptor is None:
            print "Location not found in course"
            return

        if dry_run:
            print "Doing a dry run."

        students = User.objects.filter(id__in=students_ids).order_by('username')
        print "Number of students: {0}".format(students.count())

        for student in students:
            print "{0}:{1}".format(student.id, student.username)
            try:
                module = get_module_for_student(student, course, location)
                if module is None:
                    print "  WARNING: No state found."
                    continue

                latest_task = module.child_module.get_task_at_index(task_index)
                if latest_task is None:
                    print "  WARNING: No task state found."
                    continue

                latest_task_state = latest_task.child_state

                if latest_task_state == OpenEndedChild.INITIAL:
                    print "  WARNING: No submission."
                elif latest_task_state == OpenEndedChild.POST_ASSESSMENT or latest_task_state == OpenEndedChild.DONE:
                    print "  WARNING: Submission already graded."
                elif latest_task_state == OpenEndedChild.ASSESSING:
                    latest_answer = latest_task.latest_answer()
                    if dry_run:
                        print "  Skipped sending submission to grader: {0!r}".format(latest_answer[:100].encode('utf-8'))
                    else:
                        latest_task.send_to_grader(latest_answer, latest_task.system)
                        print "  Sent submission to grader: {0!r}".format(latest_answer[:100].encode('utf-8'))
                else:
                    print "WARNING: Invalid task_state: {0}".format(latest_task_state)
            except Exception as err:  # pylint: disable=broad-except
                print err