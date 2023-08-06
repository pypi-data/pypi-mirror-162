__version__ = '0.0.1'

# Code to convert Month to int
def MonthToNum(Month):
    return{
        'Jan': 1,
        'Feb':2,
        'Mar':3,
        'Apr' :4,
        'May' :5,
        'Jun':6,
        'Jul':7,
        'Aug': 8,
        'Sep':9,
        'Oct':10,
        'Nov':11,
        'Dec':12,
    } [Month]

# Code to convert int to Abbreviated Month
def NumToAbbrMonth(Month):
    return{
        1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec',
    } [Month]


# Code to convert int to Full Month
def NumToMonth (Month):
    return{
        1:'January',
        2:'February',
        3:'March',
        4:'April',
        5:'May',
        6:'June',
        7:'July',
        8:'August',
        9:'September',
        10:'October',
        11:'November',
        12:'December',
    } [Month]


