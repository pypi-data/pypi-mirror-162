from IPython import get_ipython

from hindsight.utils.voila import QueryParams

def set_query_params(global_ref):
    ipython = get_ipython()
    ipython.events.register('post_execute', QueryParams(global_ref).set_variables)
