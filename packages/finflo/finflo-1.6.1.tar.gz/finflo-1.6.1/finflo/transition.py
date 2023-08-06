from django.http import HttpResponse
from .models import TransitionManager , Action, workevents, workflowitems , Flowmodel
from .serializer import TransitionManagerserializer , Actionseriaizer, Workitemserializer, workeventslistserializer, workflowitemslistserializer
from .middleware import get_current_user
from rest_framework.generics import ListAPIView , ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .exception import ModelNotFound, SignLengthError, TransitionNotAllowed
from .states import sign_list, sub_action




####################################################
#############       CORE     #######################
####################################################




def gets_wf_item(gets_model):
    ws = workflowitems.objects.get(transitionmanager=gets_model.id)
    return ws


class FinFlotransition:
    
    def delete(self):
        return None

    def transition(self, type, action, stage, id=None):
        try:
            gets_model = TransitionManager.objects.get(type=type.upper() , t_id = id)
            gets_flows = Flowmodel.objects.get(description  = type.lower())
            gets_action = Action.objects.get(description=action,model = gets_flows.id)
        except:
            raise ModelNotFound("no model found ")

        # sign length check
        if id is not None:
            gets_model_id = TransitionManager.objects.get(t_id=id)
        else:
            print("no transition model found on this id")

        # check sign and stage 
        if stage == gets_model.sub_sign:
            if gets_action.sign_required >= stage:
                def Transition_Handler():
                    gets_sign = gets_action.sign_required

                    # no sign_Required
                    if stage and gets_sign == 0:
                        print("1")
                        gets_model.sub_sign = stage
                        gets_model.save()
                        ws = workflowitems.objects.update_or_create( transitionmanager=gets_model or gets_model_id, defaults= {"initial_state" : gets_action.from_state.description, "interim_state" : gets_action.to_state.description or sign_list[0], 
                            "final_state" : gets_action.to_state.description, "action" : action, "subaction" : sub_action[0], "model_type" : type.upper(), "event_user" : get_current_user() , "current_from_party" : gets_action.from_party , "current_to_party" : gets_action.to_party})
                        gets_wf = gets_wf_item(gets_model)
                        workevents.objects.create(workflowitems=gets_wf, event_user=get_current_user(),  initial_state=gets_action.from_state.description,
                                                  interim_state=gets_action.to_state.description, final_state=gets_action.to_state.description, action=action, subaction=sub_action[0], type=type.upper(), final_value="YES" , from_party = gets_action.from_party , to_party = gets_action.to_party)

                    # initial_stage_transition
                    if stage == 0:
                        print("2")
                        gets_model.sub_sign = stage + 1
                        gets_model.save()
                        ws =  workflowitems.objects.update_or_create(transitionmanager=gets_model or gets_model_id, defaults = {"initial_state" : gets_action.from_state.description, "interim_state" : sign_list[1], 
                            "final_state" : gets_action.to_state.description, "action" : action, "subaction" : sub_action[0], "model_type" : type.upper(), "event_user" : get_current_user() , "current_from_party" : gets_action.from_party , "current_to_party" : gets_action.from_party})
                        gets_wf = gets_wf_item(gets_model)
                        workevents.objects.create(workflowitems=gets_wf or ws, event_user=get_current_user(),  initial_state=gets_action.from_state.description,
                                                  interim_state=sign_list[1], final_state=gets_action.to_state.description, action=action, subaction=sub_action[0], type=type.upper() , from_party = gets_action.from_party , to_party = gets_action.from_party)
                    
                    # final transition
                    elif stage == gets_sign:
                        print("3")
                        gets_model.sub_sign = 0
                        gets_model.save()
                        gets_wf = gets_wf_item(gets_model)
                        workflowitems.objects.filter(id=int(gets_wf.id)).update(
                            initial_state=gets_action.from_state.description, interim_state=gets_action.to_state.description, transitionmanager=gets_model.id or gets_model_id,
                            final_state=gets_action.to_state.description, action=action, subaction=sub_action[int(stage)], model_type=type.upper(), event_user=get_current_user() , current_from_party = gets_action.from_party , current_to_party = gets_action.to_party)
                        
                        workevents.objects.create(workflowitems=gets_wf, event_user=get_current_user(),  initial_state=gets_action.from_state.description,
                                                  interim_state=gets_action.to_state.description, final_state=gets_action.to_state.description, action=action, subaction=sub_action[int(stage)], type=type.upper(), final_value="YES" , from_party = gets_action.from_party , to_party = gets_action.to_party)
                    
                    # inbetween all transitions
                    else:
                        print("4")
                        gets_wf = gets_wf_item(gets_model)
                        gets_model.sub_sign = stage + 1
                        gets_model.save()
                        workflowitems.objects.filter(id=int(gets_wf.id)).update(
                            initial_state=gets_action.from_state.description, interim_state=sign_list[
                                1 + stage], transitionmanager=gets_model or gets_model_id,
                            final_state=gets_action.to_state.description, action=action, subaction=sub_action[int(stage)], model_type=type.upper(), event_user=get_current_user(), current_from_party = gets_action.from_party , current_to_party = gets_action.from_party)
                        workevents.objects.create(workflowitems=gets_wf, event_user=get_current_user(),  initial_state=gets_action.from_state.description,
                                                  interim_state=sign_list[1 + stage], final_state=gets_action.to_state.description, action=action, subaction=sub_action[int(stage)], type=type.upper() , from_party = gets_action.from_party , to_party = gets_action.from_party)

                return Transition_Handler()
            else:
                raise SignLengthError(
                    "either the stage nor the sign_required length mismatching and the stage should not be zero ")
        else:
            raise TransitionNotAllowed(
                "TransitionNotAllowed please try again")






####################################################
#############       API      #######################
####################################################



class DetailsListApiView(ListAPIView):
    queryset = TransitionManager.objects.all()
    serializer_class = TransitionManagerserializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self, request):
    #     type = self.request.query_params.get('type')
    #     if type is None:
    #         queryset = TransitionManager.objects.all()
    #     queryset = TransitionManager.objects.filter(type=type)
    #     return queryset

    def list(self, request):
        queryset = TransitionManager.objects.all()
        serializer = TransitionManagerserializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)



# worflow api 

class WorkFlowitemsListApi(ListAPIView):
    queryset = workflowitems.objects.all()
    serializer_class = Workitemserializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = workflowitems.objects.all()
        serializer = Workitemserializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)




# workevents api 


class WorkEventsListApi(ListAPIView):
    queryset = workevents.objects.all()
    serializer_class = workeventslistserializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = workevents.objects.all()
        serializer = workeventslistserializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)






# action create and list api 


class ActionListApi(ListCreateAPIView):
    queryset = Action.objects.all()
    serializer_class = Actionseriaizer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Action.objects.all()
        serializer = Actionseriaizer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = Actionseriaizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "failure", "data": serializer.errors},status=status.HTTP_204_NO_CONTENT)





