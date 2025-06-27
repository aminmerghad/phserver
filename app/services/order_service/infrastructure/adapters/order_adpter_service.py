from app.services.order_service.infrastructure.adapters.outgoing.inventory_adapter import InventoryServiceAdapter
from app.services.order_service.infrastructure.adapters.outgoing.product_adapter import ProductServiceAdapter
from app.shared.acl.unified_acl import UnifiedACL
from app.shared.contracts.inventory.stock_check import StockCheckRequestContract


class OrderAdapterService:
    def __init__(self, acl: UnifiedACL):
        self._acl = acl
        self._stock_check_adapter = InventoryServiceAdapter(self._acl)
        self._product_adapter = ProductServiceAdapter(self._acl)

    def stock_check(self, request: StockCheckRequestContract):
        return self._stock_check_adapter.stock_check(request)
    
    def get_product_by_id(self, product_id):
        return self._product_adapter.get_product_by_id(product_id)
    
    def get_products_by_ids(self, product_ids):
        return self._product_adapter.get_products_by_ids(product_ids)