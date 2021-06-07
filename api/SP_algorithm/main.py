from copy import deepcopy, copy
import logging
from api.SP_algorithm.course import OOPCourse
from api.SP_algorithm.course_group import Course_group
from api.SP_algorithm.student import OOPStudent
from collections import OrderedDict
from api.models import Result, Course, Student
import sys


# logging.basicConfig(level=logging.DEBUG)


def check_overlap(student_object, course_object):
    """

    """
    overlap_courses = course_object.get_overlap_list()
    if len(overlap_courses) > 0:  # If there isn't overlap course we can simply say there isn't an overlap course
        output = True
        enroll_status = student_object.get_enrolment_status()
        logging.info("Checking if there is overlap course to course_object such that student_object try to enroll")
        for overlap in range(len(overlap_courses)):
            course_name = overlap_courses[overlap]
            check = enroll_status[course_name.get_name()]
            if check == 1:  # If The student is enroll to overlap course
                student_object.delete_current_preference()
                if output:
                    output = False
                    break

            return output

    else:
        return True


def ready_to_new_round(student_list, student_names, ranks, round):
    logging.info("Order the student highest bids to current situations such that in enroll students only have to check"
                 "if we can enroll the student to his most preferred to the current round number %d", round)
    _data = {}
    for i in range(len(ranks)):
        ranks[i] = student_list[i].get_changeable_cardinal()
        course_names = list(ranks[i].keys())
        vector_rank = list(ranks[i].values())
        index = vector_rank.index(max(vector_rank))
        _data[student_names[i]] = {course_names[index]: vector_rank[index]}

    return _data


def second_phase(student_object, elective_course_list, need_to_change, gap=0):
    logging.info("Student id %s is activate second phase", student_object.get_id())
    need_to_enroll = True
    tried = False
    while need_to_enroll:

        if need_to_change or tried:  # If we check overlap and there is we changed his bid to 0 and we not need to change to twice
            student_object.add_gap(gap)
            need_to_change = False

        tried = True  # After the first try we will change the preference from the next round for updating for the next
        # round of second phase
        next_pref = student_object.get_next_preference()
        next_key = list(next_pref.keys())

        for j in range(len(elective_course_list)):
            if elective_course_list[j].get_name() == next_key[0]:
                if check_overlap(student_object, elective_course_list[j]) and elective_course_list[
                    j].get_capacity() > 0:
                    if student_object.get_need_to_enroll() > 0:
                        logging.info("We found a course named %s that student with the ID %s can enrolled",
                                     elective_course_list[j].get_name(), student_object.get_id(), )
                        elective_course_list[j].student_enrollment(student_object.get_id(), student_object)
                        student_object.got_enrolled(elective_course_list[j].get_name())
                        s = Student.objects.get(student_id=student_object.get_id())
                        c = Course.objects.get(course_id=elective_course_list[j].get_id())
                        Result.objects.create(course=c, student=s, selected=True)
                        need_to_enroll = False  # The student have been enrolled so we can stop the loop and continue the algorithm

        if student_object.get_current_highest_bid() == 0:  # If there is no other preference break the loop and back to
            # enroll student function
            break


def there_is_a_tie(students_object):
    """
    >>> [OOPStudent(1, 5, 1, {'probability 2' : 1, })]


    """
    logging.info("We trying to enrolling more students to a course such that the number of student exceed"
                 "the remaining capacity")

    # We create a list of 0 with the length of the number of students that in this round want to enroll
    # and than we change the number zero where there is a tie between the bids when if there is several bids
    # the highest tie we change the index location to 1 (in the zeroes list) find another tie but smaller we change
    # 0 into 2 and so on this list helps us to sort afterward the students according to their bids if there is a tie
    start_end = [0 for i in range(len(students_object))]
    counter = 1
    for index in range(len(students_object) - 1):
        if students_object[index].get_current_highest_bid() == students_object[index + 1].get_current_highest_bid():
            start_end[index] = counter
            start_end[index + 1] = counter

        elif students_object[index].get_current_highest_bid() != students_object[index + 1].get_current_highest_bid() \
                and start_end[index] != 0:
            counter += 1

    return start_end


def sort_tie_breaker(student_object_try, check, course_name):
    logging.info(
        "There is a tie between some students so we sort the tie breaker between all the tie in the current list")
    max_value = max(check)
    for i in range(1, max_value + 1):
        min_index = check.index(i)
        max_index = len(check) - check[::-1].index(i) - 1  # sort other way around and find the index of the element i
        # for getting the last appearance of the i tie when 1 is the highest tie and max_value is the smallest tie
        tie_student = student_object_try[
                      min_index:max_index + 1]  # Take a sub list to activate on this sub list the sort function
        fixed_tie_student = sorted(tie_student, key=lambda x: (
        x.get_number_of_enrollments(), x.current_highest_ordinal(course_name)))
        student_object_try[
        min_index:max_index] = fixed_tie_student  # Insert back the sorted sub list into the list that
        # indicate about the ties in the same places


def enroll_students(_data, student_list, elective_course_list, group_course):
    amount_of_bidrs = {}
    student_element = {}
    # Create dictionaries such that key is name of the course and the value is
    # a list of student that wish to enroll
    for co in elective_course_list:
        amount_of_bidrs[co.get_name()] = []
        student_element[co.get_name()] = []

    course_bid = list(_data.values())
    # Adding the students to the value list of preferred course (course = key) the dictionaries as mention above
    for i in range(len(student_list)):
        if student_list[i].get_current_highest_bid() > 0:
            course = list(course_bid[i].keys())
            amount_of_bidrs[course[0]].append(student_list[i].get_id())
            student_element[course[0]].append(student_list[i])

    j = -1
    need_to_pass = 0
    for key, value in amount_of_bidrs.items():
        j += 1
        logging.info("Starting to check if we can to enroll student to the course %s", key)
        logging.info("While the students ID is: " + str(value)[1:-1])
        if not need_to_pass == 0:
            logging.info(
                "We need to pass on current course because we tried to enroll to this course in other option previously")
            need_to_pass -= 1
            continue

        else:
            if len(value) > 0:
                try_to_enroll = amount_of_bidrs[key]
                student_object_try = student_element[key]

                group = None  # Find the possibles for some course such that if there is more than one option we continue
                # to the option of 2 or more option that start line 259 else one option start in line 159
                for group_index in group_course:
                    if group_index.get_id() == elective_course_list[j].get_id_group():
                        group = group_index

                possibles = group.get_possibles()

                if key == elective_course_list[j].get_name():
                    if len(possibles) == 1:
                        if elective_course_list[j].can_be_enroll(len(try_to_enroll)):
                            if len(try_to_enroll) > 0:  # when we can enroll everyone
                                for need_to in range(len(try_to_enroll)):
                                    logging.info("Try to enroll student %s", try_to_enroll[need_to])
                                    if check_overlap(student_object_try[need_to],
                                                     elective_course_list[j]):  # Enroll student if he dose
                                        if student_object_try[need_to].get_need_to_enroll() > 0:
                                            # not have overlap course to elective_course_list[j]
                                            elective_course_list[j].student_enrollment(try_to_enroll[need_to],
                                                                                       student_object_try[need_to])
                                            student_object_try[need_to].got_enrolled(elective_course_list[j].get_name())
                                            s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                            c = Course.objects.get(course_id=elective_course_list[j].get_id())
                                            Result.objects.create(course=c, student=s, selected=True)

                                    else:  # If the student enrolled already to overlap course over course_list[j]
                                        # gap = elective_course_list[j].get_lowest_bid() - \
                                        #      student_object_try[need_to].get_current_highest_bid()

                                        # student_object_try[need_to].add_gap(gap)

                                        second_phase(student_object_try[need_to], elective_course_list, False)



                        elif elective_course_list[j].get_capacity() == 0:  # If the capacity is zero
                            logging.info(
                                "No student can be enrolled because there is no remaining capacity to the course named %s",
                                elective_course_list[j].get_name())
                            for need_to in range(len(student_object_try)):
                                if student_object_try[need_to].get_need_to_enroll() > 0:
                                    # gap = elective_course_list[j].get_lowest_bid() - \
                                    #      student_object_try[need_to].get_current_highest_bid()

                                    # student_object_try[need_to].add_gap(gap)

                                    second_phase(student_object_try[need_to], elective_course_list, True)



                        elif not elective_course_list[j].can_be_enroll(len(try_to_enroll)):
                            # If the capacity is not let to enroll all student who put bid over that course
                            student_object_try = sorted(student_object_try, key=lambda x: x.get_current_highest_bid(),
                                                        reverse=True)
                            logging.info(
                                "We try to enroll more students when number of student is %d than remaining capacity %d",
                                len(student_object_try), elective_course_list[j].get_capacity())
                            check = there_is_a_tie(student_object_try)
                            if check.count(0) == len(check):  # In case there isn't a tie between student bids
                                for need_to in range(len(student_object_try)):
                                    if elective_course_list[j].get_capacity() > 0 and check_overlap(
                                            student_object_try[need_to], elective_course_list[j]):
                                        if student_object_try[need_to].get_need_to_enroll() > 0:
                                            elective_course_list[j].student_enrollment(
                                                student_object_try[need_to].get_id(), student_object_try[need_to])
                                            student_object_try[need_to].got_enrolled(elective_course_list[j].get_name())
                                            s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                            c = Course.objects.get(course_id=elective_course_list[j].get_id())
                                            Result.objects.create(course=c, student=s, selected=True)



                                    else:
                                        # If there is a student such that want to enroll to course but is overlap or have zero
                                        # capacity

                                        # gap = elective_course_list[j].get_lowest_bid() - \
                                        #      student_object_try[need_to].get_current_highest_bid()

                                        # student_object_try[need_to].add_gap(gap)

                                        if elective_course_list[j].get_capacity() == 0:
                                            second_phase(student_object_try[need_to], elective_course_list, True)

                                        else:
                                            second_phase(student_object_try[need_to], elective_course_list, False)




                            else:  # In case there is a tie between student bids we break the tie by there ordinal order
                                sort_tie_breaker(student_object_try, check, elective_course_list[j].get_name())
                                for need_to in range(len(student_object_try)):
                                    if elective_course_list[j].get_capacity() > 0 and check_overlap(
                                            student_object_try[need_to], elective_course_list[j]):
                                        if student_object_try[need_to].get_need_to_enroll() > 0:
                                            # If there is a place to enroll student need_to
                                            elective_course_list[j].student_enrollment(
                                                student_object_try[need_to].get_id(),
                                                student_object_try[need_to])
                                            student_object_try[need_to].got_enrolled(elective_course_list[j].get_name())
                                            s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                            c = Course.objects.get(course_id=elective_course_list[j].get_id())
                                            Result.objects.create(course=c, student=s, selected=True)

                                    else:
                                        # If there is a student such that want to enroll to course but is overlap or have zero
                                        # capacity

                                        # gap = elective_course_list[j].get_lowest_bid() - \
                                        #    student_object_try[need_to].get_current_highest_bid()

                                        # student_object_try[need_to].add_gap(gap)

                                        if elective_course_list[j].get_capacity() == 0:
                                            second_phase(student_object_try[need_to], elective_course_list, True)

                                        else:
                                            second_phase(student_object_try[need_to], elective_course_list, False)


                    else:
                        need_to_pass = len(possibles) - 1
                        sorted_possibles = sorted(possibles, key=lambda x: x.get_capacity(), reverse=True)

                        got_to_enroll = [False for i in range(len(student_object_try))]
                        logging.info("We can enroll to more option to the same course")
                        total_capacity = 0
                        for index in sorted_possibles:
                            total_capacity += index.get_capacity()

                        if total_capacity >= len(try_to_enroll):
                            for need_to in range(len(try_to_enroll)):
                                logging.info("Try to enroll student %s", try_to_enroll[need_to])
                                for possible_index in sorted_possibles:
                                    if possible_index.get_capacity() > 0 and \
                                            check_overlap(student_object_try[need_to], possible_index) and \
                                            student_object_try[need_to].get_need_to_enroll() > 0:
                                        possible_index.student_enrollment(try_to_enroll[need_to],
                                                                          student_object_try[need_to])
                                        student_object_try[need_to].got_enrolled(possible_index.get_name())
                                        s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                        c = Course.objects.get(course_id=possible_index.get_id())
                                        Result.objects.create(course=c, student=s, selected=True)
                                        got_to_enroll[need_to] = True
                                        break

                                if not got_to_enroll[need_to]:
                                    if elective_course_list[j].get_capacity() == 0:
                                        second_phase(student_object_try[need_to], elective_course_list, True)

                                    else:
                                        second_phase(student_object_try[need_to], elective_course_list, False)

                        elif total_capacity == 0:
                            for need_to in range(len(student_object_try)):
                                logging.info(
                                    "No student can be enrolled because there is no remaining capacity to the course named %s",
                                    elective_course_list[j].get_name())
                                if student_object_try[need_to].get_need_to_enroll() > 0:
                                    # gap = elective_course_list[j].get_lowest_bid() - \
                                    #    student_object_try[need_to].get_current_highest_bid()

                                    # student_object_try[need_to].add_gap(gap)

                                    second_phase(student_object_try[need_to], elective_course_list, True)


                        elif total_capacity < len(try_to_enroll):
                            student_object_try = sorted(student_object_try, key=lambda x: x.get_current_highest_bid(),
                                                        reverse=True)
                            check = there_is_a_tie(student_object_try)
                            logging.info(
                                "We try to enroll more students when number of student is %d than remaining capacity %d",
                                len(student_object_try), elective_course_list[j].get_capacity())
                            if check.count(0) == len(check):
                                for need_to in range(len(try_to_enroll)):
                                    for possible_index in sorted_possibles:
                                        if possible_index.get_capacity() > 0 and \
                                                check_overlap(student_object_try[need_to], possible_index) and \
                                                student_object_try[need_to].get_need_to_enroll() > 0:
                                            possible_index.student_enrollment(try_to_enroll[need_to],
                                                                              student_object_try[need_to])
                                            student_object_try[need_to].got_enrolled(possible_index.get_name())
                                            s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                            c = Course.objects.get(course_id=possible_index.get_id())
                                            Result.objects.create(course=c, student=s, selected=True)
                                            got_to_enroll[need_to] = True
                                            break

                                    if not got_to_enroll[need_to]:

                                        if elective_course_list[j].get_capacity() == 0:
                                            second_phase(student_object_try[need_to], elective_course_list, True)

                                        else:
                                            second_phase(student_object_try[need_to], elective_course_list, False)

                            else:
                                sort_tie_breaker(student_object_try, check, sorted_possibles[0].get_name()[::-2])
                                for need_to in range(len(student_object_try)):
                                    for possible_index in sorted_possibles:
                                        if possible_index.get_capacity() > 0 and \
                                                check_overlap(student_object_try[need_to], possible_index) and \
                                                student_object_try[need_to].get_need_to_enroll() > 0:
                                            possible_index.student_enrollment(student_object_try[need_to].get_id(),
                                                                              student_object_try[need_to])
                                            student_object_try[need_to].got_enrolled(possible_index.get_name())
                                            s = Student.objects.get(student_id=student_object_try[need_to].get_id())
                                            c = Course.objects.get(course_id=possible_index.get_id())
                                            Result.objects.create(course=c, student=s, selected=True)
                                            got_to_enroll[need_to] = True
                                            break

                                    if not got_to_enroll[need_to]:
                                        if elective_course_list[j].get_capacity() == 0:
                                            second_phase(student_object_try[need_to], elective_course_list, True)

                                        else:
                                            second_phase(student_object_try[need_to], elective_course_list, False)


def algorithm(fixed, student_list, elective_course_list, group_course, rounds=5):
    student_names = list(fixed.keys())
    ranks = list(fixed.values())
    for i in range(1, rounds + 1):
        logging.info("Starting round number %d", i)
        round_data = ready_to_new_round(student_list, student_names, ranks, i)
        enroll_students(round_data, student_list, elective_course_list, group_course)


def order_course_data(raw_course_list):
    """
    >>> order_course_data([OrderedDict([('id', 10), ('name', 'הסתברות למדעי המחשב 2'), ('is_elective', False), ('office', 1),
    >>> ('courses', [OrderedDict([('course_id', '1'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30),
    >>> ('day', 'א'), ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')]),
    >>> OrderedDict([('course_id', '2'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30), ('day', 'ב'),
    >>> ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')])])]),
    >>> , OrderedDict([('id', 11), ('name', 'חישוביות'), ('is_elective', False), ('office', 1),
    >>> ('courses', [OrderedDict([('course_id', '3'), ('Semester', 'א'), ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'),
    >>> ('capacity', 30), ('day', 'ב'), ('time_start', '15:00:00'), ('time_end', '18:00:00'),
    >>> ('course_group', 'חישוביות11')]), OrderedDict([('course_id', '4'), ('Semester', 'א'),
    >>> ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'), ('capacity', 30), ('day', 'ג'), ('time_start', '11:00:00'),
    >>> ('time_end', '14:00:00'), ('course_group', 'חישוביות11')])])])])
    [<class Course_group>, <class Course_group>], [], [<class OOPCourse>, <class OOPCourse>]

    >>> order_course_data([OrderedDict([('id', 10), ('name', 'הסתברות למדעי המחשב 2'), ('is_elective', False), ('office', 1),
    >>> ('courses', [OrderedDict([('course_id', '1'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30),
    >>> ('day', 'א'), ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')]),
    >>> OrderedDict([('course_id', '2'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30), ('day', 'ב'),
    >>> ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')])])]),
    >>> OrderedDict([('id', 11), ('name', 'חישוביות'), ('is_elective', False), ('office', 1),
    >>> ('courses', [OrderedDict([('course_id', '3'), ('Semester', 'א'), ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'),
    >>> ('capacity', 30), ('day', 'ב'), ('time_start', '15:00:00'), ('time_end', '18:00:00'),
    >>> ('course_group', 'חישוביות11')]), OrderedDict([('course_id', '4'), ('Semester', 'א'),
    >>> ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'), ('capacity', 30), ('day', 'ג'), ('time_start', '11:00:00'),
    >>> ('time_end', '14:00:00'), ('course_group', 'חישוביות11')])])]),
    >>> OrderedDict([('id', 28), ('name', 'מבוא לקריפטוגרפיה'), ('is_elective', True), ('office', 1),
    >>> ('courses', [OrderedDict([('course_id', '71'),  ('Semester', 'א'), ('lecturer', '\tד"ר פסקין צ\'רניאבסקי ענת'),
    >>> ('capacity', 10), ('day', 'א'), ('time_start', '12:00:00'), ('time_end', '15:00:00'),
    >>> ('course_group', 'מבוא לקריפטוגרפיה28')])])])])
        [<class Course_group>, <class Course_group>, <class Course_group>], [<class OPPCourse>], [<class OOPCourse>, <class OOPCourse>]

    """

    logging.info(
        "Create the course list that will contain the course data that the program get from the server about courses and group courses")

    group_course_list = []
    course_list_elective_output = []
    course_list_mandatory_output = []
    possible_list = []
    max_office = 0

    logging.info("Starting the procedure of convert order dictionary we got from the server to group course")
    create_course = 0
    create_group = 0

    for dic in raw_course_list:
        id_group = int(dic['id'])
        name = dic['name']
        office = int(dic['office'])
        if max_office < office:
            max_office = office

        elect = dic['is_elective']

        counter = 1
        for dic2 in dic['courses']:
            id = int(dic2['course_id'])
            semester = dic2['Semester']
            lecturer = dic2['lecturer']
            capacity = int(dic2['capacity'])
            day = dic2['day']
            start = dic2['time_start']
            end = dic2['time_end']
            tmp = OOPCourse(id, id_group, name + ' ' + str(counter), capacity, start, end, semester, day, lecturer,
                            office, elect)
            logging.info("Finish the procedure of create a new course number %d", create_course)
            create_course += 1
            counter += 1
            possible_list.append(tmp)

        if elect:
            for co in possible_list:
                course_list_elective_output.append(co)

        else:
            for co in possible_list:
                course_list_mandatory_output.append(co)

        new_group = Course_group(id_group, name, office, copy(possible_list))
        logging.info("Finish the procedure of create a new group course number %d and named %s", create_group, name)
        create_group += 1
        group_course_list.append(new_group)
        possible_list.clear()

    return group_course_list, course_list_elective_output, course_list_mandatory_output, max_office


def overlap_course(course_list):
    # Check which course is overlap each and other, for overlap the courses must be
    # in the same semester and day before checking if they overlap.
    # Afterward we check if course is starting while other course has been starting and finish later or
    # the course is ending while other course has been start and not finish yet or the starting and ending
    # time is the same. this is the three option that if one of that happened we add the other course
    # to the list of overlap courses the course we checking currently

    """
    >>> courses = [OOPCourse(1, 10, 'a', 30, '09:00:00', '11:00:00', 'a', 'monday',  'l', 1),
    >>> OOPCourse(2, 7, 'b', 25, '11:00:00', '14:00:00', 'b', 'Thursday',  'e', 1),
    >>> OOPCourse(3, 5, 'c', 25, '10:00:00', '13:00:00', 'c', 'Thursday',  'r', 2]
    >>> overlap_course(courses)
    >>> tmp = courses[0].get_overlap_list()
    >>> print(tmp)
    []
    >>> tmp = courses[1].get_overlap_list()
    []
    >>> tmp = courses[2].get_overlap_list()
    []
        ...
    >>> courses = [OOPCourse(1, 10, 'aa', 30, '09:00:00', '11:00:00', 'a', 'monday',  'l', 1),
    >>> OOPCourse(2, 7, 'ab', 25, '11:00:00', '14:00:00', 'b', 'Thursday',  'e', 1),
    >>> OOPCourse(3, 5, 'ac', 25, '10:00:00', '13:00:00', 'c', 'Thursday',  'r', 1]
    >>> overlap_course(courses)
    >>> tmp = courses[0].get_overlap_list()
    >>> print(tmp)
    []
    >>> tmp = courses[1].get_overlap_list()
    >>> print(tmp)
    [<class OOPCourse>]
    >>> tmp = courses[2].get_overlap_list()
    >>> print(tmp)
    [<class OOPCourse>]
        ...
    >>> courses = [OOPCourse(1, 10, 'aa', 30, '09:00:00', '11:00:00', 'a', 'monday',  'l', 1),
    >>> OOPCourse(2, 7, 'ab', 25, '11:00:00', '14:00:00', 'b', 'monday',  'e', 1),
    >>> OOPCourse(3, 5, 'ac', 25, '10:00:00', '13:00:00', 'c', 'monday',  'r', 1]
    >>> overlap_course(courses)
    >>> tmp = courses[0].get_overlap_list()
    >>> print(tmp)
    []
    >>> tmp = courses[1].get_overlap_list()
    >>> print(tmp)
    [<class OOPCourse>]
    >>> tmp = courses[2].get_overlap_list()
    >>> print(tmp)
    [<class OOPCourse>, <class OOPCourse>]
       ...
    >>> courses = [OOPCourse(1, 10, 'aa', 30, '09:00:00', '11:00:00', 'a', 'monday',  'l', 1),
    >>> OOPCourse(2, 7, 'ab', 25, '11:00:00', '14:00:00', 'b', 'monday',  'e', 1),
    >>> OOPCourse(3, 5, 'ac', 25, '14:00:00', '16:00:00', 'c', 'monday',  'r', 1]
    >>> overlap_course(courses)
    >>> tmp = courses[0].get_overlap_list()
    >>> print(tmp)
    []
    >>> tmp = courses[1].get_overlap_list()
    >>> print(tmp)
    []
    >>> tmp = courses[2].get_overlap_list()
    >>> print(tmp)
    []
    """

    for i in range(len(course_list)):
        overlap_list_for_i = []
        for j in range(len(course_list)):
            if not i == j:
                if course_list[j].get_office() == course_list[i].get_office():
                    if course_list[j].get_day() == course_list[i].get_day():
                        if course_list[j].get_semester() == course_list[i].get_semester():
                            if course_list[j].get_start() <= course_list[i].get_start() < course_list[j].get_end():
                                overlap_list_for_i.append(course_list[j])

                            elif course_list[j].get_start() < course_list[i].get_end() <= course_list[j].get_end():
                                overlap_list_for_i.append(course_list[j])

                            elif course_list[j].get_start() == course_list[i].get_start() and \
                                    course_list[i].get_end() == course_list[j].get_end():
                                overlap_list_for_i.append(course_list[j])

        course_list[i].set_overlap(overlap_list_for_i)
        overlap_list_for_i.clear()


def order_student_data(raw_student_list, raw_rank_list, elective_course_list, mandatory_course_list, num_offices):
    """
    >>> order_student_data([OrderedDict([('student_id', 205666407), ('user', 1), ('amount_elective', 5), ('office', 1), ('courses',
    >>> [OrderedDict([('course_id', '1'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30), ('day', 'א'),
    >>> ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')]),
    >>> OrderedDict([('course_id', '3'), ('Semester', 'א'), ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'), ('capacity', 30),
    >>> ('day', 'ב'), ('time_start', '15:00:00'), ('time_end', '18:00:00'), ('course_group', 'חישוביות11')]),
    >>> OrderedDict([('course_id', '16'), ('Semester', 'ב'), ('lecturer', 'ד"ר דביר עמית זאב'), ('capacity', 20),
    >>> ('day', 'ד'), ('time_start', '11:00:00'), ('time_end', '13:00:00'), ('course_group', 'סמינר כללי במדעי המחשב14')]),
    >>> OrderedDict([('course_id', '20'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30), ('day', 'ה'),
    >>> ('time_start', '10:00:00'), ('time_end', '12:00:00'), ('course_group', 'מערכות מבוזרות15')])])]),
    >>> OrderedDict([('student_id', 203777401), ('user', 41), ('amount_elective', 5), ('office', 1), ('courses',
    >>> [OrderedDict([('course_id', '1'), ('Semester', 'א'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 30), ('day', 'א'),
    >>> ('time_start', '09:00:00'), ('time_end', '11:00:00'), ('course_group', 'הסתברות למדעי המחשב 210')]),
    >>> OrderedDict([('course_id', '3'), ('Semester', 'א'), ('lecturer', 'ד"ר פסקין צ\'רניאבסקי ענת'), ('capacity', 30),
    >>> ('day', 'ב'), ('time_start', '15:00:00'), ('time_end', '18:00:00'), ('course_group', 'חישוביות11')]),
    >>> OrderedDict([('course_id', '9'), ('Semester', 'ב'), ('lecturer', 'ד"ר וויסברג פנחס'), ('capacity', 30),
    >>> ('day', 'ד'), ('time_start', '13:00:00'), ('time_end', '16:00:00'), ('course_group', 'תכנות מתקדם13')]),
    >>> OrderedDict([('course_id', '14'), ('Semester', 'ב'), ('lecturer', "פרופ' חפץ דן"), ('capacity', 20), ('day', 'ב'),
    >>> ('time_start', '14:00:00'), ('time_end', '16:00:00'), ('course_group', 'סמינר כללי במדעי המחשב14')])])])],
    >>> [OrderedDict([('id', 44), ('rank', 2), ('student', "205666407's profile"), ('course_group', 23)]), OrderedDict([('id', 45), ('rank', 82), ('student', "205666407's profile"), ('course_group', 24)]), OrderedDict([('id', 46), ('rank', 0), ('student', "205666407's profile"), ('course_group', 25)]), OrderedDict([('id', 47), ('rank', 4), ('student', "205666407's profile"), ('course_group', 26)]), OrderedDict([('id', 48), ('rank', 45), ('student', "205666407's profile"), ('course_group', 27)]), OrderedDict([('id', 49), ('rank', 45), ('student', "205666407's profile"), ('course_group', 28)]), OrderedDict([('id', 50), ('rank', 45), ('student', "205666407's profile"), ('course_group', 29)]), OrderedDict([('id', 51), ('rank', 97), ('student', "205666407's profile"), ('course_group', 30)]), OrderedDict([('id', 52), ('rank', 45), ('student', "205666407's profile"), ('course_group', 31)]), OrderedDict([('id', 53), ('rank', 45), ('student', "205666407's profile"), ('course_group', 32)]), OrderedDict([('id', 54), ('rank', 131), ('student', "205666407's profile"), ('course_group', 33)]), OrderedDict([('id', 55), ('rank', 45), ('student', "205666407's profile"), ('course_group', 34)]), OrderedDict([('id', 56), ('rank', 45), ('student', "205666407's profile"), ('course_group', 35)]), OrderedDict([('id', 57), ('rank', 45), ('student', "205666407's profile"), ('course_group', 36)]), OrderedDict([('id', 58), ('rank', 45), ('student', "205666407's profile"), ('course_group', 37)]), OrderedDict([('id', 59), ('rank', 45), ('student', "205666407's profile"), ('course_group', 38)]), OrderedDict([('id', 60), ('rank', 45), ('student', "205666407's profile"), ('course_group', 39)]), OrderedDict([('id', 61), ('rank', 45), ('student', "205666407's profile"), ('course_group', 40)]), OrderedDict([('id', 62), ('rank', 45), ('student', "205666407's profile"), ('course_group', 41)]), OrderedDict([('id', 63), ('rank', 45), ('student', "205666407's profile"), ('course_group', 42)]), OrderedDict([('id', 64), ('rank', 45), ('student', "205666407's profile"), ('course_group', 43)]),
    >>> OrderedDict([('id', 1007), ('rank', 47), ('student', "203777401's profile"), ('course_group', 23)]), OrderedDict([('id', 1008), ('rank', 47), ('student', "203777401's profile"), ('course_group', 24)]), OrderedDict([('id', 1009), ('rank', 47), ('student', "203777401's profile"), ('course_group', 25)]), OrderedDict([('id', 1010), ('rank', 47), ('student', "203777401's profile"), ('course_group', 26)]), OrderedDict([('id', 1011), ('rank', 47), ('student', "203777401's profile"), ('course_group', 27)]), OrderedDict([('id', 1012), ('rank', 47), ('student', "203777401's profile"), ('course_group', 28)]), OrderedDict([('id', 1013), ('rank', 47), ('student', "203777401's profile"), ('course_group', 29)]), OrderedDict([('id', 1014), ('rank', 47), ('student', "203777401's profile"), ('course_group', 30)]), OrderedDict([('id', 1015), ('rank', 47), ('student', "203777401's profile"), ('course_group', 31)]), OrderedDict([('id', 1016), ('rank', 47), ('student', "203777401's profile"), ('course_group', 32)]), OrderedDict([('id', 1017), ('rank', 47), ('student', "203777401's profile"), ('course_group', 33)]), OrderedDict([('id', 1018), ('rank', 47), ('student', "203777401's profile"), ('course_group', 34)]), OrderedDict([('id', 1019), ('rank', 47), ('student', "203777401's profile"), ('course_group', 35)]), OrderedDict([('id', 1020), ('rank', 47), ('student', "203777401's profile"), ('course_group', 36)]), OrderedDict([('id', 1021), ('rank', 47), ('student', "203777401's profile"), ('course_group', 37)]), OrderedDict([('id', 1022), ('rank', 47), ('student', "203777401's profile"), ('course_group', 38)]), OrderedDict([('id', 1023), ('rank', 47), ('student', "203777401's profile"), ('course_group', 39)]), OrderedDict([('id', 1024), ('rank', 47), ('student', "203777401's profile"), ('course_group', 40)]), OrderedDict([('id', 1025), ('rank', 47), ('student', "203777401's profile"), ('course_group', 41)]), OrderedDict([('id', 1026), ('rank', 47), ('student', "203777401's profile"), ('course_group', 42)]), OrderedDict([('id', 1027), ('rank', 47), ('student', "203777401's profile"), ('course_group', 43)])],
    >>> elective_course_list, mandatory_course_list, num_offices)
    [<class OOPStudent>, <class OOPstudent>]
    """

    counter = 0
    logging.info(
        "create the student list that will contain the data such that the program get from the server about students")
    indexed_enrollment = [{} for i in range(num_offices)]
    cardinal_order = [{} for i in range(num_offices)]
    student_list = [[] for i in range(num_offices)]
    course_list = [[] for i in range(num_offices)]

    for i in range(num_offices):
        course_list[i] = elective_course_list[i] + mandatory_course_list[i]

    for office_number in course_list:
        for i in office_number:
            indexed_enrollment[i.get_office() - 1][i.get_name()] = 0

            if i.get_elective():
                cardinal_order[i.get_office() - 1][i.get_name()] = 0

    logging.info("starting the procedure of convert order dictionary we got from the server to students")

    for dic in raw_student_list:
        tmp1 = deepcopy(indexed_enrollment)
        tmp2 = deepcopy(cardinal_order)
        id = int(dic['student_id'])
        need_to_enroll = int(dic['amount_elective'])
        office = int(dic['office'])

        for i in range(len(course_list[office - 1])):
            for dic2 in dic['courses']:
                if course_list[office - 1][i].get_id() == int(dic2['course_id']):
                    tmp1[office - 1][course_list[office - 1][i].get_name()] = 1

        for rank_dic in raw_rank_list:
            student_id = int(rank_dic['student'][0:9])
            group_id = int(rank_dic['course_group'])
            rank = int(rank_dic['rank'])
            if student_id == id:
                for office_number in elective_course_list:
                    for course in office_number:
                        if course.get_id_group() == group_id:
                            tmp2[office - 1][course.get_name()] = rank

        logging.info(
            "Create a new student number %d and insert him to the student_list in the row of his office number %d",
            counter, office)
        s = OOPStudent(id, need_to_enroll, office, deepcopy(tmp1[office - 1]), deepcopy(tmp2[office - 1]))
        student_list[office - 1].append(s)
        counter += 1

    return student_list


def sort_by_office_courses(course_list, num_offices):
    sort_office_list_course = [[] for i in range(num_offices)]

    for i in course_list:
        sort_office_list_course[i.get_office() - 1].append(i)

    return sort_office_list_course


def main(raw_student_list, raw_course_list, raw_rank_list):

    print(raw_student_list)
    print(raw_course_list)
    print(raw_rank_list)

    course_group_list, course_elect_list, course_mandatory_list, num_offices = order_course_data(raw_course_list)
    logging.info("Sorting the elective courses into office according to the number of offices")
    set_of_offices_elective_courses = sort_by_office_courses(course_elect_list, num_offices)
    logging.info("Sorting the mandatory courses into office according to the number of offices")
    set_of_offices_mandatory_courses = sort_by_office_courses(course_mandatory_list, num_offices)

    logging.info("Now merging the elective and mandatory courses for checking possible overlap while maintaining the"
                 "separation of courses according to the office number")


    course_list = [[] for i in range(num_offices)]
    for index in range(num_offices):
        course_list[index] = set_of_offices_elective_courses[index] + set_of_offices_mandatory_courses[index]
        overlap_course(course_list[index])

    logging.info("while convert the student data from order dictionary to Student we sort student according to their office ")
    set_of_offices_students = order_student_data(raw_student_list, raw_rank_list, set_of_offices_elective_courses,
                                                 set_of_offices_mandatory_courses, num_offices)

    logging.info("Sorting the group courses into office according to the number of offices")
    set_of_office_group = sort_by_office_courses(course_group_list, num_offices)

    logging.info("Order the data for the algorithm in a list of dictionaries as each dictionary is represent"
                 " a single office while the data is portrayed by {student id: dictionary of cardinal ranking"
                 " of the same student}")
    fixed = [{} for i in range(num_offices)]
    dic = {}
    iteration = 0
    for office_index in set_of_offices_students:
        for student in office_index:
            dic[student.get_id()] = student.get_cardinal()

        tmp = deepcopy(dic)
        fixed[iteration] = tmp
        iteration += 1
        dic.clear()


    for index in range(num_offices):
        logging.info("Activate the algorithm for office number %d", index+1)
        algorithm(fixed[index], set_of_offices_students[index], set_of_offices_elective_courses[index], set_of_office_group[index])


    for office in set_of_offices_students:
        for i in office:
            i.to_string()
            print()

    for office in set_of_offices_elective_courses:
        for i in office:
            i.to_string()
            print()

    sum = 0
    for office_num in set_of_offices_students:
        for index in office_num:
            sum += index.get_number_of_enrollments()

    print(sum)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

