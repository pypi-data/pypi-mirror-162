from ..utils import Utils


class Lot:
    def __init__(self, default_sku_id = '', default_sku = '', default_number = '', default_description = '', 
                default_quantity = '', default_expiration_date = ''):
        self.default_sku_id = default_sku_id
        self.default_sku = default_sku
        self.default_number = default_number
        self.default_description = default_description
        self.default_quantity = default_quantity
        self.default_expiration_date = Utils.convert_to_datetime(default_expiration_date)