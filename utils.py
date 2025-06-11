from datetime import datetime
import random, string

def get_random_id():
    time_stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    randomword = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
    randomId = time_stamp + randomword
    return randomId

def get_random_double():
    random_double = round(random.uniform(0.0, 100.0), 2)
    return random_double