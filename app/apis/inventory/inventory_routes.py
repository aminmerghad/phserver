from http import HTTPStatus
from flask import jsonify, make_response, request
from flask.views import MethodView
from marshmallow import Schema,fields
from pydantic import BaseModel
from app.apis import inventory_bp
from app.apis.base_routes import BaseRoute
from app.apis.inventory.dtos.stock_received_dto import ReceivedStockDto
from app.extensions import container

from app.services.inventory_service.application.commands.received_stock_command import ReceivedStockCommand

from app.shared.contracts.inventory.stock_check import StockCheckItemContract, StockCheckRequestContract



class StockCheckItemDto(BaseModel):
    product_id: str
    quantity: int
class StockCheckItemsDto(BaseModel):    
    items: list[StockCheckItemDto]

class StockChecResponseSchema(Schema):
    code = fields.Int(description="Stock Check code")
    message = fields.Str(description="Stock Check message")
    data = fields.Dict(description="Stock Check data")
class StockCheckItemRequestSchema(Schema):
    product_id=fields.UUID()
    quantity=fields.Int()

class StockCheckRequestSchema(Schema):
    items = fields.Nested(StockCheckItemRequestSchema, many=True)
    consumer_id=fields.UUID()






@inventory_bp.route('/stock/check')
class StockCheckRoute(BaseRoute):
    @inventory_bp.arguments(StockCheckRequestSchema)
    @inventory_bp.response(HTTPStatus.OK, StockChecResponseSchema)
    def post(self,stock_check_data):          
        result = container.inventory_service().stock_check(
            StockCheckRequestContract(
                items=[
                    StockCheckItemContract(
                        product_id=item["product_id"],
                        quantity=item["quantity"]
                    )
                    for item in stock_check_data.get("items")
                ],
                consumer_id=stock_check_data.get("consumer_id")

            )
        )
        return self._success_response(
            data=result.model_dump(),
            message="Sotck checked successfully",
            status_code=HTTPStatus.OK
        )


class StockReceiveRequestSchema(Schema):
    product_id= fields.UUID()
    quantity = fields.Int()
    

@inventory_bp.route('/receive')
class StockReceiveRoute(BaseRoute):
    @inventory_bp.arguments(StockReceiveRequestSchema)
    # @inventory_bp.response(HTTPStatus.OK, StockReceiveResponseSchema)
    def post(self,stock_receive_data):
        result = container.inventory_service().receive_stock(
            ReceivedStockCommand(
                **stock_receive_data
            )
        )
        return self._success_response(
            data=result,
            message="Sotck checked successfully",
            status_code=HTTPStatus.OK
        )
                 











   


