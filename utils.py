from datetime import datetime
import random, string

# Semi random id helps when its needed to verify issue, we will get exact time when issue occured
def get_random_id():
    time_stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    randomword = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    randomId = time_stamp + randomword
    return randomId

# todo - Check how many decimal digits is allowed - I assume its 2 as its not specified
def get_random_double():
    random_double = round(random.uniform(0.0, 100.0), 2)
    return random_double