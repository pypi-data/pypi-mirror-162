# vim: set fileencoding=utf-8:


from coronado.baseobjects import BASE_ACTIVE_OFFER_DICT
from coronado.offer import Offer
from coronado.offer import OfferType
from coronado.reward import RewardType


# *** classes and objects ***

class ActiveOffer(Offer):
    """
    Active offer associated with a customer.  Not all offers are eligible for
    rewards until the customer activates them.  Some offers are ephemeral and
    may require re-activation after a number of days.
    """

    requiredAttributes = [
        'objID',
        'activatedAt',
        'cardAccountID',
        'headline',
        'offerID',
        'rewardType',
        'type',
    ]
    allAttributes = [
        'objID',
        'activatedAt',
        'activationExpiresOn',
        'cardAccountID',
        'currencyCode',
        'headline',
        'merchant',
        'offerID',
        'rewardRate',
        'rewardType',
        'rewardValue',
        'type',
    ]


    def __init__(self, obj = BASE_ACTIVE_OFFER_DICT):
        """
        Create a new active offer instance.  The triple API activates offers in
        response to activation requests at the account level.

        See:  `coronado.cardaccount.CardAccount.activate` for details.
        """
        Offer.__init__(self, obj)

        setattr(self, 'rewardType', RewardType(getattr(self, 'rewardType')) if getattr(self, 'rewardType', None) else None)
        setattr(self, 'type', OfferType(getattr(self, 'type')) if getattr(self, 'type', None) else None)

