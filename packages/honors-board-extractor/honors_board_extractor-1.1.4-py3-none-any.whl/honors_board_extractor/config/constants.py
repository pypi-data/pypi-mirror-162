GRADE_SUBJECT_MAP = {str(grade_number): f"Grade {grade_number}" for grade_number in range(0, 13)}
AM_GRADE_SUBJECT_MAP = {
    **GRADE_SUBJECT_MAP,
    '9': 'Algebra I',
    '10': 'Geometry',
    '11': 'Algebra II',
    '12': 'Pre-Calculus',
    '14': 14
}
AE_GRADE_SUBJECT_MAP = {
    **GRADE_SUBJECT_MAP,
    '9': 'Honors World Literature',
    '10': 'Honors British Literature',
    '11': 'Honors American Literature',
    '14': 14
}

GENERAL_SUBJECT_GRADE_MAP = {GRADE_SUBJECT_MAP[grade_id]: int(grade_id) for grade_id in GRADE_SUBJECT_MAP}
GENERAL_SUBJECT_GRADE_MAP.update({14: 14})
AM_SUBJECT_GRADE_MAP = {AM_GRADE_SUBJECT_MAP[grade_id]: int(grade_id) for grade_id in AM_GRADE_SUBJECT_MAP}
AE_SUBJECT_GRADE_MAP = {AE_GRADE_SUBJECT_MAP[grade_id]: int(grade_id) for grade_id in AE_GRADE_SUBJECT_MAP}
