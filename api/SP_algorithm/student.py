from copy import deepcopy
import logging


def check_budget(order):
    sum_bidding = 0
    order_values = list(order.values())
    for i in range(len(order_values)):
        sum_bidding += order_values[i]

    if sum_bidding > 1000:
        raise Exception("Sorry, the sum of bidding is can't be summarized above 1000")

    else:
        return True


def create_ordinal_order(order):
    count = 1
    ordinal = list(order.values())
    course_names = list(order.keys())
    for i in range(len(ordinal)):
        ind = ordinal.index(max(ordinal))
        ordinal[ind] = count
        count += 1

    output = deepcopy(order)
    for i in range(len(output)):
        output[course_names[i]] = ordinal[i]

    return output


class OOPStudent:

    def __init__(self, id, need_number , student_office, enrolled_or_not_enrolled, cardinal):
        self.id = id
        self.need_to_enroll = need_number
        self.enrolled_num = 0
        self.cardinal_order = deepcopy(cardinal)
        self.changeable_cardinal_order = deepcopy(cardinal)
        self.enrolled_or_not = enrolled_or_not_enrolled
        self.ordinal_order = create_ordinal_order(self.cardinal_order)
        self.cardinal_utility = 0
        self.ordinal_utility = 0
        self.enrolled_first_phase = False
        self.office = student_office


    def get_id(self):
        return self.id

    def get_office(self):
        return self.office

    def get_ordinal(self):
        return self.ordinal_order

    def get_cardinal(self):
        return self.cardinal_order

    def get_changeable_cardinal(self):
        return self.changeable_cardinal_order

    def get_cardinal_utility(self):
        return self.cardinal_utility

    def get_need_to_enroll(self):
        return self.need_to_enroll

    def get_enrolment_status(self):
        return self.enrolled_or_not

    def enrolled_to_other_option(self, course_name):
        logging.info("Student enrolled to other option of the same course so every bid on each option will be changed into 0")
        sliced_name = course_name[:-2]
        names = list(self.changeable_cardinal_order.keys())
        index_first = names.index(sliced_name + ' 1') # Searching for <course-name> 1 such that after him there will be
        #<course-name> 2 <course-name> 3 and so on
        not_found = True
        while not_found:
             if index_first < len(names) and names[index_first][:-2] == sliced_name:
                self.changeable_cardinal_order[names[index_first]] = 0
                index_first += 1

             else:
                 not_found = False # In case if the course named has changed so we stop here


    def delete_current_preference(self):
        logging.info("The student with the ID %s has been enrolled to overlap course", self.id)
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        course_name = cardinal_keys[max_value_index]
        self.changeable_cardinal_order[course_name] = 0
        cardinal_value[max_value_index] = 0


    def get_next_preference(self):
        logging.info("Asking for the current highest bid of student %s",  self.id)
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        return {cardinal_keys[max_value_index]: cardinal_value[max_value_index]}

    def get_number_of_enrollments(self):
        return self.enrolled_num

    def add_gap(self, gap):
        logging.info("If the student with ID %s didn't enroll we try to enroll him to his next preferred while taking"
                     "portion/whole of his rejected bid to the next preferred", self.id)
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        course_name = cardinal_keys[max_value_index]
        self.changeable_cardinal_order[course_name] = 0
        cardinal_value[max_value_index] = 0
        if cardinal_value.count(0) != len(cardinal_value): # In case there isn't another preference (all his bids are 0)
            max_value_index = cardinal_value.index(max(cardinal_value))
            course_name = cardinal_keys[max_value_index]
            self.changeable_cardinal_order[course_name] = cardinal_value[max_value_index] + gap

    def get_current_highest_bid(self):
        cardinal_value = list(self.changeable_cardinal_order.values())
        index = cardinal_value.index(max(cardinal_value))
        return cardinal_value[index]

    def current_highest_ordinal(self, course_name):
        return self.ordinal_order[course_name]

    def got_enrolled(self, course_name):
        if self.need_to_enroll > 0 and self.enrolled_or_not[course_name] == 0:
            logging.info("We enroll student with ID %s to coursed named %s", self.id, course_name)
            self.need_to_enroll -= 1
            self.cardinal_utility += self.changeable_cardinal_order[course_name]
            self.changeable_cardinal_order[course_name] = 0
            self.enrolled_or_not[course_name] = 1
            self.enrolled_num += 1
            self.ordinal_utility += len(self.ordinal_order) - self.ordinal_order[course_name]+1
            self.enrolled_to_other_option(course_name)

        elif self.enrolled_or_not[course_name] == 1:
            print("Student: ", self.id, ", is already enrolled to the course: ", course_name)

        else:
            print("Student: ", self.id, " got to the limit of courses enrollment")

    def to_string(self):
        print("Student id:", self.id, ", The cardinal order is: ", self.cardinal_order, "\n"  "The ordinal is: ",
              self.ordinal_order, "\n", "The courses that: ", self.id, " enrolled are: ")

        for key, value in self.enrolled_or_not.items():
            if value == 1:
                print(key)

        print("The cardinal utility is: ", self.cardinal_utility, ", The ordinal utility is: ", self.ordinal_utility)
