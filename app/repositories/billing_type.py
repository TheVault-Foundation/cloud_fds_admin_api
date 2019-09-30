from app import models as m


class BillingTypeRepository(object):
    def get_by_billing_type(self, b_type):
        return m.BillingType.objects(billingType=b_type).first()

    def create(self, args):
        try:
            billing_type = m.BillingType(**args)
            billing_type.save()
            return billing_type
        except Exception:
            return None


billing_type_repo = BillingTypeRepository()
