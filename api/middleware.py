import json
import time
from uuid import uuid4

import redis
import settings

# Connect to Redis and assign to variable `db``
# Make use of settings.py module to get Redis settings like host, port, etc.
db = redis.Redis(
    db=settings.REDIS_DB_ID, host=settings.REDIS_IP, port=settings.REDIS_PORT
)


def model_predict(user_id):
    """
    Receives an user_id and queues the job into Redis.
    Will loop until getting the answer from our ML service.

    Parameters
    ----------
    user_id : str | int. User id

    Returns
    -------
    Dict with top jobs and accuraccy
    """

    # Assign an unique ID for this job and add it to the queue.
    # We need to assing this ID because we must be able to keep track
    # of this particular job across all the services

    job_id = str(uuid4())

    # Create a dict with the job data we will send through Redis having the
    # following shape:
    # {
    #    "id": str,
    #    "user_id": str,
    # }

    msg = {
        "id": job_id,
        "user_id": user_id,
    }
    job_data = json.dumps(msg)
    # Send the job to the model service using Redis

    db.lpush(settings.REDIS_QUEUE, job_data)

    # Loop until we received the response from our ML model
    while True:
        # Attempt to get model predictions using job_id
        output = db.get(job_id)

        # Check if the text was correctly processed by our ML model
        # Don't modify the code below, it should work as expected
        if output is not None:
            output = json.loads(output.decode("utf-8"))
            db.delete(job_id)
            break

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

    return output
