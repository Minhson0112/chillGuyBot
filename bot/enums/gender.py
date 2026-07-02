from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    LGBTQ_PLUS = "lgbtq_plus"
