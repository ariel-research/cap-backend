from copy import deepcopy
import logging

class OOPCourse:

    def __init__(self, id_num, id_g, course_name, capacity_bounds, start_time, end_time, semester, day, lec, office_num, elect = [], overlap_courses=[]):
        self.id = id_num
        self.id_group = id_g
        self.name = course_name
        self.maximal_capacity = capacity_bounds + 5
        self.capacity = capacity_bounds
        self.students = []
        self.overlap = set(overlap_courses)
        self.lowest_bid = 0
        self.start = start_time
        self.end = end_time
        self.sem = semester
        self.d = day
        self.lecturer = lec
        self.office = office_num
        self.elective = elect

    def student_enrollment(self, student_name, student_element):
        if self.capacity > 0 and student_name not in self.students and student_element.get_need_to_enroll() > 0:
            logging.info("For course %s we enroll student with the ID %s", self.name, student_name)
            self.capacity -= 1
            self.maximal_capacity -= 1
            self.students.append(student_name)
            if student_element.get_current_highest_bid() < self.lowest_bid or self.lowest_bid == 0:
                self.lowest_bid = student_element.get_current_highest_bid()

        else:
            raise Exception("We can't enroll you to the course named", self.name)

    def can_be_enroll(self, number_of_students):
        return self.capacity >= number_of_students

    def set_overlap(self, overlap_list):
        self.overlap = deepcopy(overlap_list)

    def get_id(self):
        return self.id

    def get_id_group(self):
        return self.id_group

    def get_office(self):
        return self.office

    def get_elective(self):
        return self.elective

    def get_lowest_bid(self):
        return self.lowest_bid

    def get_overlap_list(self):
        return self.overlap

    def get_name(self):
        return self.name

    def get_capacity(self):
        return self.capacity

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_semester(self):
        return self.sem

    def get_day(self):
        return self.d

    def to_string(self):
        print("Course name: ", self.name, ", Capacity: ", self.capacity, "\n" 
              "Number of student that enroll to this course is: ", len(self.students), "\n"
              "Student list: ", self.students, "\n")

        print("Overlap courses are: ")
        for i in self.overlap:
            print(i.get_name() )
