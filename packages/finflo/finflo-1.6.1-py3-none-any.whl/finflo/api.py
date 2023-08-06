from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .transition import FinFlotransition

class TransitionApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        transitions = FinFlotransition()
        type = request.data.get("type")
        action = request.data.get("action")
        stage = request.data.get("stage")
        t_id = request.data.get("t_id")
        cs = int(stage) 
        if type and action  is not None:
            transitions.transition(type = type, action = action , stage = cs , id = t_id)
            return Response({"status" : "Transition success"},status = status.HTTP_200_OK)
        return Response({"status" : "Transition failure"},status = status.HTTP_204_NO_CONTENT)

