from IPython.parallel import Client
import time

def run_task():
    import time
    time.sleep(7)

def main():

    client = Client()
    lbview = client.load_balanced_view()
    lbview.track = True
    lbview.retries = 10
    
    print("create 10 tasks:")
    msg_ids = []
    i = 0
    while i < 10:
        ar = lbview.apply(run_task)
        print("Task " + ar.msg_ids[0])
        ar.wait_for_send()
        msg_ids.append(ar.msg_ids[0])
        i += 1

    time.sleep(10) 

    print("\nsearch for tasks in DB:")
    tasks = client.db_query({"msg_id" : {"$in" : msg_ids}})

    # stop all tasks which are not yet done
    print("\nstop all tasks which are not yet done:")
    tasks_to_stop = []
    for task in tasks:
        print("Task " + task["msg_id"] + ": ")
        if ("result_header" in task) and (task["result_header"] != None) and (task["result_header"]["status"] == "ok"):
            print("  finished at " + str(task["completed"]))
        else:
            print("  not finished yet. will abort.")
            tasks_to_stop.append(task["msg_id"])
    client.abort(tasks_to_stop)

    time.sleep(10)

    print("\nsearch for tasks in DB:")
    tasks = client.db_query({"msg_id" : {"$in" : msg_ids}})

    print("\nresubmit all tasks which are not yet done:")
    tasks_to_resubmit = []
    for task in tasks:
        print("Task " + task["msg_id"] + ": ")
        if ("result_header" in task) and (task["result_header"] != None) and (task["result_header"]["status"] == "ok"):
            print("  finished at " + str(task["completed"])) 
        else:
            print("  not finished yet. will resubmit.")
            tasks_to_resubmit.append(task["msg_id"])
    client.resubmit(tasks_to_resubmit)


if __name__== "__main__":
    main()
