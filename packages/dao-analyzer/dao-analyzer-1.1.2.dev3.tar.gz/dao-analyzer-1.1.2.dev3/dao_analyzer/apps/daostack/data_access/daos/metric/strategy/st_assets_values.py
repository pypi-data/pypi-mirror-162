import dao_analyzer.apps.common.data_access.daos.metric.strategy as stcommon

class StAssetsValues(stcommon.StAssetsValues):
    def __init__(self):
        super().__init__('dao')
