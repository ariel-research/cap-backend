from copy import deepcopy, copy
import logging
from api.SP_algorithm.course import OOPCourse
from api.SP_algorithm.course_group import Course_group
from api.SP_algorithm.student import OOPStudent
from api.models import Result, Course, Student


#logging.basicConfig(level=logging.DEBUG)


def check_overlap(student_object, course_object): # Check if there is an overlap course to the course we tried to enroll
    overlap_courses = course_object.get_overlap_list()
    if len(overlap_courses) > 0:  # If there isn't overlap course we can simply say there isn't an overlap course
        output = True   # We'll presume there is no enrolled course such that is overlapped with course_object
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


def second_phase(student_object, elective_course_list, need_to_change, gap=0):  # need_to_change
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
                if check_overlap(student_object, elective_course_list[j]):
                    if elective_course_list[j].get_capacity() > 0:
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
        tie_student = student_object_try[min_index:max_index]
        # Take a sub list to activate on this sub list the sort function
        fixed_tie_student = sorted(tie_student, key=lambda x: (
            x.get_number_of_enrollments(), x.current_highest_ordinal(course_name)), reverse=False)
        student_object_try[min_index:max_index] = fixed_tie_student
        # Insert back the sorted sub list into the list that
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
        tmp_student_list = list(student_element[key])
        logging.info("Starting to check if we can to enroll student to the course %s", key)
        for index in tmp_student_list:
            next_preference = index.get_next_preference()
            pre_key = list(next_preference.keys())
            pre_value = list(next_preference.values())
            logging.info("While the students ID is: %s, for course named %s, and there bid %d is", str(index.get_id()),
                         pre_key[0], pre_value[0])

        if len(value) > 0:
            try_to_enroll = amount_of_bidrs[key]
            student_object_try = student_element[key]


            if key == elective_course_list[j].get_name():
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
                    logging.info("No student can be enrolled because there is no remaining capacity to the"
                                  " course named %s", elective_course_list[j].get_name())
                    for need_to in range(len(student_object_try)):
                        if student_object_try[need_to].get_need_to_enroll() > 0:
                            # gap = elective_course_list[j].get_lowest_bid() - \
                            #      student_object_try[need_to].get_current_highest_bid()

                            # student_object_try[need_to].add_gap(gap)

                            second_phase(student_object_try[need_to], elective_course_list, True)

                elif not elective_course_list[j].can_be_enroll(len(try_to_enroll)):
                    # If the capacity is not let to enroll all student who put bid over that course
                    logging.info("Sort the students is decreasing order according to their highest bid")
                    student_object_try = sorted(student_object_try, key=lambda x: x.get_current_highest_bid(),
                                                reverse=False)
                    for index in student_object_try:
                        next_preference = index.get_next_preference()
                        pre_key = list(next_preference.keys())
                        pre_value = list(next_preference.values())
                        logging.info("While the students ID is: %s, for course named %s, and there bid %d is",
                                     str(index.get_id()), pre_key[0], pre_value[0])

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


def algorithm(fixed, student_list, elective_course_list, group_course, rounds=5):
    student_names = list(fixed.keys())
    ranks = list(fixed.values())
    for i in range(1, rounds + 1):
        logging.info("Starting round number %d", i)
        round_data = ready_to_new_round(student_list, student_names, ranks, i)  # Create a dictionary of
        # {<student id>: {<course name>: <highest bid>}, ...} return for all students in the input list
        enroll_students(round_data, student_list, elective_course_list, group_course)


# Changes the orderDic of courses that we getting from the server and convert to an object OOPCourse
def order_course_data(raw_course_list):
    logging.info(
        "Create the course list that will contain the course data that "
        "the program get from the server about courses and group courses")

    group_course_list = []
    course_list_elective_output = []
    course_list_mandatory_output = []
    possible_list = []

    logging.info("Starting the procedure of convert order dictionary we got from the server to group course")
    create_course = 0
    create_group = 0

    for dic in raw_course_list:
        id_group = int(dic['id'])
        name = dic['name']
        id_office = int(dic['office'])
        elect = dic['is_elective']

        counter = 1
        for dic2 in dic['courses']: # dic2 is representing the courses of group_course (= dic1)
            id = int(dic2['course_id'])
            semester = dic2['Semester']
            lecturer = dic2['lecturer']
            capacity = int(dic2['capacity'])
            day = dic2['day']
            start = dic2['time_start']
            end = dic2['time_end']
            tmp = OOPCourse(id, id_group, name + ' ' + str(counter), capacity, start, end, semester, day, lecturer,
                            id_office, elect)
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

        new_group = Course_group(id_group, name, id_office, copy(possible_list))
        logging.info("Finish the procedure of create a new group course number %d and named %s", create_group, name)
        create_group += 1
        group_course_list.append(new_group)
        possible_list.clear()

    return group_course_list, course_list_elective_output, course_list_mandatory_output


def overlap_course(course_list):
    # Check which course is overlap each and other, for overlap the courses must be
    # in the same semester and day before checking if they overlap.
    # Afterward we check if course is starting while other course has been starting and finish later or
    # the course is ending while other course has been start and not finish yet or the starting and ending
    # time is the same. this is the three option that if one of that happened we add the other course
    # to the list of overlap courses the course we checking currently

    for i in range(len(course_list)):
        overlap_list_for_i = []
        for j in range(len(course_list)):
            if not i == j:  # If it's not same course
                if course_list[j].get_day() == course_list[i].get_day():  # If it's in the same day
                    if course_list[j].get_semester() == course_list[i].get_semester():  # If it's in the same day
                        if course_list[j].get_start() <= course_list[i].get_start() < course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() < course_list[i].get_end() <= course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() == course_list[i].get_start() and \
                                course_list[i].get_end() == course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

        course_list[i].set_overlap(overlap_list_for_i)
        overlap_list_for_i.clear()


def order_student_data(raw_student_list, raw_rank_list, elective_course_list, course_list):
    counter = 0
    logging.info(
        "create the student list that will contain the data such that the program get from the server about students")
    indexed_enrollment = {}
    cardinal_order = {}
    student_list = []

    for i in course_list:
        indexed_enrollment[i.get_name()] = 0

        if i.get_elective():
            cardinal_order[i.get_name()] = 0

    logging.info("starting the procedure of convert order dictionary we got from the server to students")

    for dic in raw_student_list:
        deepcopy_indexed_enrollment = deepcopy(indexed_enrollment)
        deepcopy_cardinal_order = deepcopy(cardinal_order)
        id = int(dic['student_id'])
        need_to_enroll = int(dic['amount_elective'])
        office = int(dic['office'])

        # Updating the enrollment status for mandatory courses

        for i in range(len(course_list)):
            for dic2 in dic['courses']:
                if course_list[i].get_id() == int(dic2['course_id']):
                    deepcopy_indexed_enrollment[course_list[i].get_name()] = 1

        for rank_dic in raw_rank_list:  # Update the ranking of elective courses for all student in current office
            student_id = int(rank_dic['student'][0:9]) # Taking the student id for checking if is the same student
            course_id = int(rank_dic['course'])
            rank = int(rank_dic['rank'])
            #if rank == 0:
            #    rank += 1

            if student_id == id:
                for course in elective_course_list:
                    if course.get_id() == course_id:
                        deepcopy_cardinal_order[course.get_name()] = rank

        logging.info(
            "Create a new student number %d and insert him to the student_list in the row of his office number %d",
            counter, office)

        s = OOPStudent(id, need_to_enroll, office, deepcopy(deepcopy_indexed_enrollment), deepcopy(deepcopy_cardinal_order))
        student_list.append(s)
        counter += 1

    return student_list


'''
def sort_by_office_courses(course_list, num_offices):
    sort_office_list_course = [[] for i in range(num_offices)]
    for i in course_list:
        sort_office_list_course[i.get_office() - 1].append(i)
    return sort_office_list_course
'''


def main(raw_student_list, raw_course_list, raw_rank_list):
    print(raw_student_list)
    print(raw_course_list)
    print(raw_rank_list)

    course_group_list, course_elect_list, course_mandatory_list = order_course_data(raw_course_list)
    # logging.info("Sorting the elective courses into office according to the number of offices")
    # set_of_offices_elective_courses = sort_by_office_courses(course_elect_list, num_offices)
    # logging.info("Sorting the mandatory courses into office according to the number of offices")
    # set_of_offices_mandatory_courses = sort_by_office_courses(course_mandatory_list, num_offices)

    logging.info("Now merging the elective and mandatory courses for checking possible overlap while maintaining the"
                 "separation of courses according to the office number")

    course_list = course_elect_list + course_mandatory_list
    overlap_course(course_list)

    logging.info(
        "while convert the student data from order dictionary to Student we sort student according to their office ")
    student_list = order_student_data(raw_student_list, raw_rank_list, course_elect_list, course_list)

    logging.info("Order the data for the algorithm in a list of dictionaries as each dictionary is represent"
                 " a single office while the data is portrayed by {student id: dictionary of cardinal ranking"
                 " of the same student}")
    fixed = {}
    for student in student_list:
        fixed[student.get_id()] = student.get_cardinal()

    logging.info("Activate the algorithm")
    algorithm(fixed, student_list, course_elect_list, course_group_list)

    for i in student_list:
        i.to_string()
        print()

    for i in course_elect_list:
        i.to_string()
        print()

    sum = 0
    for i in student_list:
        sum += i.get_number_of_enrollments()

    print(sum)