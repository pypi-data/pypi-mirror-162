#!/usr/bin/env python3

from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from ..pubsub import publish, exit_flag


# a simple card observer that prints inserted/removed cards
class FederCardObserver(CardObserver):
    
    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))
            self.publish_exit()

    def publish_exit(self):
        publish("exit")
        exit_flag.set()

if __name__ == '__main__':
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver()
    cardmonitor.addObserver(cardobserver)

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

