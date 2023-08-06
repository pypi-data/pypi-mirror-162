from transition import FinFlotransition
from django.shortcuts import HttpResponse



# EXAMPLE CODE
qs = FinFlotransition()

def index(self):
    # transition2(stage = 3)
    qs.transition(type = "INVOICE" , action = "DELETE" , stage = 2)
    return HttpResponse(str("data"))
