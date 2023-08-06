from django.db import models 
from choices import StateChoices


# WORKFLOW ITEMS MODEL

class workflowitems(models.Model):
    
    created_date = models.DateTimeField(auto_now_add=True)
    initial_state = models.CharField(max_length=50, default=StateChoices.STATUS_DRAFT)
    interim_state = models.CharField(max_length=50, default=StateChoices.STATUS_DRAFT)
    final_state = models.CharField(max_length=50, default=StateChoices.STATUS_DRAFT)
    # next_available_transitions = ArrayField(models.CharField(max_length=500,blank=True, null=True,default=None),blank=True, null=True,default = None)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='customername')
    # current_from_party = models.ForeignKey("accounts.Parties", on_delete=models.DO_NOTHING, related_name='from_party')
    # current_to_party = models.ForeignKey("accounts.Parties", on_delete=models.DO_NOTHING, related_name='to_party')
    action = models.CharField(max_length=25, default='SAVE')
    subaction = models.CharField(max_length=55 , blank=True, null=True)
    previous_action = models.CharField(max_length=55 , blank=True, null=True)
    type = models.CharField(max_length=55)
    comments = models.CharField(max_length=500,blank=True, null=True)
    is_read = models.BooleanField(default=True,blank=True, null=True)

    class Meta:
        verbose_name_plural = "Workflowitem"


# WORKEVENTS
class workevents(models.Model):

    workitems = models.ForeignKey(workflowitems, on_delete=models.CASCADE, related_name='workflowevent')
    from_state = models.CharField(max_length=50, default='DRAFT')
    action = models.CharField(max_length=25, default='SAVE')
    subaction = models.CharField(max_length=55 , blank=True, null=True)
    to_state = models.CharField(max_length=50, default='DRAFT')
    interim_state = models.CharField(max_length=50, default='DRAFT')
    # from_party = models.ForeignKey('accounts.Parties', on_delete=models.CASCADE, related_name='from_we_party')
    # to_party = models.ForeignKey('accounts.Parties', on_delete=models.CASCADE, related_name='to_wf_party')
    event_user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='event_user')
    record_datas = models.JSONField(blank=True, null=True)
    end = models.CharField(max_length=55,blank=True, null=True)
    is_read = models.BooleanField(default=True,blank=True, null=True)
    final = models.CharField(max_length=55,blank=True, null=True)
    c_final = models.CharField(max_length=55,blank=True, null=True)
    comments = models.CharField(max_length=500,blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=55)
    
    class Meta:
        verbose_name_plural = "WorkEvent"
        ordering = ['id']
    
    # def save(self, *args, **kwargs):
    #     try:
    #         qs = Programs.objects.get(id =self.workitems.program.id)
    #         # qs2 = Programs.objects.get(id = self.workitems.invoice.pairing.program_id.id)
    #         # qs1 = Invoices.objects.get(id = self.workitems.invoices)
    #         # qs2 = Invoiceuploads.objects.get(id = self.workitems.uploads)
            
    #         program_data_template = {
    #                 "party" : qs.party.name,
    #                 "party_type" : qs.party.party_type,
    #                 "program_type" : qs.program_type,
    #                 "finance_request_type" : qs.finance_request_type,
    #                 "limit_currency": qs.limit_currency,
    #                 "total_limit_amount":str(qs.total_limit_amount),
    #                 "finance_currency" : qs.finance_currency,
    #                 "settlement_currency" : qs.settlement_currency,
    #                 "expiry_date" : str(qs.expiry_date),
    #                 "max_finance_percentage":str(qs.max_finance_percentage),
    #                 "max_invoice_age_for_funding" : qs.max_invoice_age_for_funding,
    #                 "max_age_for_repayment" : qs.max_age_for_repayment,
    #                 "minimum_period" : qs.minimum_period,
    #                 "maximum_period" : str(qs.maximum_period),
    #                 "maximum_amount" : str(qs.maximum_amount),
    #                 "minimum_amount" : str(qs.minimum_amount),
    #                 "financed_amount":str(qs.financed_amount),
    #                 "balance_amount" : str(qs.balance_amount),
    #                 "grace_period" : qs.grace_period,
    #                 "interest_type" : qs.interest_type.description,
    #                 "interest_rate_type" : qs.interest_rate_type.description,
    #                 "interest_rate": str(qs.interest_rate),
    #                 "margin" : str(qs.margin),
    #                 "comments" : qs.comments,
    #                 "status" : qs.status,
    #                 "is_locked" : qs.is_locked,
    #                 # "created_date" : str(qs.created_date)
    #         }
    #         # invoice_data_template = {
    #         #     "party" : qs1.party.name,
    #         #     "party_type" : qs1.party.party_type,
    #         #     "program_type" : qs1.program_type,
    #         #     "pairing":qs1.pairing,
    #         #     "invoice_no":qs1.invoice_no,
    #         #     "issue_date":qs1.issue_date,
    #         #     "due_date":qs1.due_date,
    #         #     "invoice_currency":qs1.invoice_currency,
    #         #     "amount":qs1.amount,
    #         #     "funding_req_type":qs1.funding_req_type,
    #         #     "finance_currency_type" :qs1.finance_currency_type,
    #         #     "settlement_currency_type" :qs1.settlement_currency_type,
    #         #     "interest_rate" : qs1.interest_rate,
    #         #     "financed_amount" : qs1.financed_amount,
    #         #     "bank_loan_id" : qs1.bank_loan_id,
    #         #     "created_date" : qs1.created_date
    #         # }
    #         self.record_datas = program_data_template
    #         return super(workevents, self).save( *args, **kwargs) 
    #     except:
    #         self.record_datas = None
    #         return super(workevents, self).save( *args, **kwargs)