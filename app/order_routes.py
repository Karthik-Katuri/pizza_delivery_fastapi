from fastapi import APIRouter, Depends, status, Form
from fastapi.exceptions import HTTPException
from app.models import User, Order
from app.database import Session
from app.dependencies import get_current_user, get_db
from fastapi.encoders import jsonable_encoder
from app.schemas import OrderModel, ApproveModel

order_router = APIRouter(prefix="/order", tags=["orders"])


@order_router.get("/")
async def hello_user(current_user: User = Depends(get_current_user)):
    return {"message": f"hello {current_user.username}"}


@order_router.post("/place", status_code=status.HTTP_201_CREATED)
async def place_an_order(
    pizza_size: str = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_order = Order(pizza_size=pizza_size, quantity=quantity, user_id=current_user.id)

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "id": new_order.id,
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "status": new_order.order_status,
    }


@order_router.get("/orders")
async def list_all_order(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user.username).first()
    if user.is_staff:
        orders = db.query(Order).all()
        return jsonable_encoder(orders)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a super user"
    )


@order_router.get("/orders/{id}")
async def get_order_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(User.username == current_user.username).first()
    if user.is_staff:
        order = db.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a super user"
    )


@order_router.get("/user/orders")
async def get_user_orders(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user.username).first()

    return jsonable_encoder(current_user.orders)


@order_router.get("/user/orders/{id}")
async def get_specific_order(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == id).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="this order is not found"
        )

    if order.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not the user"
        )
    return jsonable_encoder(order)


@order_router.put("/update/order/{id}")
async def update_specific_order(
    id: int,
    order: OrderModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_to_update = db.query(Order).filter(Order.id == id).first()
    if not order_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order does not exist"
        )

    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    db.commit()
    db.refresh(order_to_update)

    return jsonable_encoder(order_to_update)


@order_router.put("/status/update/{id}")
async def update_status_order(
    id: int,
    order: ApproveModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    user = db.query(User).filter(User.username == current_user.username).first()

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update status",
        )

    order_status_to_update = db.query(Order).filter(Order.id == id).first()

    if not order_status_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Order does not exist"
        )

    order_status_to_update.order_status = order.order_status

    db.commit()
    db.refresh(order_status_to_update)

    return order_status_to_update


@order_router.delete("/delete/{id}")
async def delete_order(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    order_to_delete = db.query(Order).filter(Order.id == id).first()

    if not order_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order does not exist"
        )

    if order_to_delete.user_id == current_user.id or current_user.is_staff:

        db.delete(order_to_delete)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you cannot delete this order",
        )

    return {"message": f"Order {id} deleted successfully"}
