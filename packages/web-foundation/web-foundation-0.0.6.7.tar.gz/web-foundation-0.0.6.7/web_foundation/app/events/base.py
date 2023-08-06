from web_foundation.kernel import IMessage


class AeEvent(IMessage):
    pass


class CloseChargeAeEvent(AeEvent):
    message_type = "close_charge"
