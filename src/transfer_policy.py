"""Make sure every transfer policy's decision is "None" when both queues are empty"""

def vanilla_transfer_policy(remote_state, hw_info, queue_len):
    #return one of ["None", "Request", "Transfer"]
    return "None"
