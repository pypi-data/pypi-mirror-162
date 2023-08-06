class RfcError(Exception):
    pass


class LogonError(RfcError):
    pass


class CommunicationError(RfcError):
    pass


class BapiException(Exception):
    def __init__(self, bapiret2, messages):
        super(BapiException, self).__init__(bapiret2.message)
        self.type       = bapiret2.type
        self.id         = bapiret2.id
        self.number     = bapiret2.number
        self.message    = bapiret2.message
        self.log_no     = bapiret2.log_no
        self.log_msg_no = bapiret2.log_msg_no
        self.message_v1 = self.v1 = self.var1 = bapiret2.message_v1
        self.message_v2 = self.v2 = self.var2 = bapiret2.message_v2
        self.message_v3 = self.v3 = self.var3 = bapiret2.message_v3
        self.message_v4 = self.v4 = self.var4 = bapiret2.message_v4
        self.parameter  = bapiret2.parameter
        self.row        = bapiret2.row
        self.field      = bapiret2.field
        self.system     = bapiret2.system
        self.messages   = messages
