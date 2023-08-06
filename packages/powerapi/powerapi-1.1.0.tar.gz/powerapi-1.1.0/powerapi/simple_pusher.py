# Copyright (c) 2022, INRIA
# Copyright (c) 2022, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from thespian.actors import ActorAddress, ActorExitRequest

from powerapi.actor import Actor
from powerapi.message import EndMessage, SimplePusherStartMessage, StartMessage, \
    GetReceivedReportsSimplePusherMessage, ReceivedReportsSimplePusherMessage
from powerapi.report import PowerReport, Report, HWPCReport


class SimplePusherActor(Actor):
    """
    PusherActor class

    The Pusher allow to save Report sent by Formula.
    """

    def __init__(self):
        Actor.__init__(self, SimplePusherStartMessage)
        self.reports = []
        self.number_of_reports_to_store = 0

    def _initialization(self, start_message: SimplePusherStartMessage):
        self.number_of_reports_to_store = start_message.number_of_reports_to_store

    def receiveMsg_PowerReport(self, message: PowerReport, _: ActorAddress):
        """
        When receiving a PowerReport save it to the list of reports
        """
        self.log_debug('received message ' + str(message))
        self.save_report(message)
        self.log_debug(str(message) + 'saved to list')

        self.stop_actors_if_required()

    def receiveMsg_HWPCReport(self, message: HWPCReport, _: ActorAddress):
        """
        When receiving a PowerReport save it to the list of reports
        """
        self.log_debug('received message ' + str(message))
        self.save_report(message)
        self.log_debug(str(message) + 'saved to list')

        self.stop_actors_if_required()

    def save_report(self, report: Report):
        """
        Saves the received report in a list
        :param report: Report to be saved
        """
        self.reports.append(report)

    def receiveMsg_StartMessage(self, message: StartMessage, sender: ActorAddress):
        """
        Initialize the actor by using the received start message
        :param message: The start message
        :param sender: Address of the sender of the message
        """
        self.log_debug('received message ' + str(message))
        Actor.receiveMsg_StartMessage(self, message=message, sender=sender)

    def receiveMsg_EndMessage(self, message: EndMessage, _: ActorAddress):
        """
        When receiving an EndMessage notify the ActorSystem and Kill itself
        """
        self.log_debug('received message ' + str(message))
        self.send(self.parent, EndMessage(self.name))
        self.send(self.myAddress, ActorExitRequest())

    def receiveMsg_GetReceivedReportsSimplePusherMessage(self, message: GetReceivedReportsSimplePusherMessage,
                                                         sender: ActorAddress):
        """
        When receiving  GetReceivedReportsSimplePusherMessage returns the stored reports
        """
        self.log_debug('received message ' + str(message))
        self.send(sender, ReceivedReportsSimplePusherMessage(self.name, self.reports))

    def stop_actors_if_required(self):
        """
        Stops the actor system if number_of_reports_to_store is reached
        """
        if len(self.reports) >= self.number_of_reports_to_store:
            self.log_debug("reports saved :" + str(len(self.reports)))
            self.send(self.parent, EndMessage(self.name))
            self.log_debug("exit request sent")
