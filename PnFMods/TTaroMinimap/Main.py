API_VERSION = 'API_v1.0'
MOD_NAME = 'TTaroMinimap'

try:
    import events, ui, utils, dataHub, constants
except:
    pass

from EntityController import EntityController


CC = constants.UiComponents
ShipTypes = constants.ShipTypes
KM_TO_BW = 1000.0 / 30.0

class ShipConsumableChecker(object):
    """
    Checks the ship consumables in a match
    """

    COMPONENT_KEY = 'modTTaroMinimapConsumableRanges'

    TITLE_TO_INFO = {
        'RLSSearch'         : {'type': 'RADAR',             'attr': 'distShip'},
        'SonarSearch'       : {'type': 'HYDRO',             'attr': 'distShip'},
        'SubmarineLocator'  : {'type': 'SUBRADAR',          'attr': 'acousticWaveMaxDist_submarine_detection'},
        #'Hydrophone'        : {'type': 'hydrophone',        'attr': 'hydrophoneWaveRadius'},
    }

    def __init__(self):
        self.entityController = EntityController(ShipConsumableChecker.COMPONENT_KEY)
        events.onBattleShown(self.__onBattleStart)
        events.onBattleQuit(self.__onBattleEnd)

    def __onBattleStart(self, *args):
        self.entityController.createEntity()
        data = self._getAllConsumablesData()
        self.entityController.updateEntity(data)

        utils.logInfo('[TTaroMinimap] Ship consumables have been updated.')

    def __onBattleEnd(self, *args):
        self.entityController.removeEntity()

    def _getAllConsumablesData(self):
        consumablesData = {}
        for entity in dataHub.getEntityCollections('shipBattleInfo'):
            ship = entity[CC.shipBattleInfo]
            data = self._getConsumablesDataByShip(ship)
            if data is not None:
                consumablesData[ship.playerId] = data

        return consumablesData
    
    def _getConsumablesDataByShip(self, ship):
        data = {}
        allConsumables = ship.mainConsumables + [cons for consList in ship.altConsumables for cons in consList]
        for cons in allConsumables:
            consInfo = self.__getConsumableInfo(cons)
            if consInfo is None:
                continue
            consType = consInfo['type']
            data[consType] = self.__getConsumableRange(cons, consInfo)

        if len(data) > 0:
            return data
        return None

    def __getConsumableInfo(self, consumable):
        consName = consumable.title
        for ident, consInfo in ShipConsumableChecker.TITLE_TO_INFO.iteritems():
            if ident.upper() in consName:
                return consInfo
        return None

    def __getConsumableRange(self, consumable, consInfo):
        paramName = consInfo['attr']
        for attr in consumable.attributes.neutral:
            if attr.paramName == paramName:
                bw = attr.numericValue * KM_TO_BW
                return ui.getLengthOnMiniMap(bw)
            
consChecker = ShipConsumableChecker()