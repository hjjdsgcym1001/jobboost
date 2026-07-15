"""
JobBoost 支付宝支付模块
使用当面付（扫码支付）API
"""
import os
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/payment", tags=["payment"])

# Alipay config
APP_ID = "2021006172697065"
NOTIFY_URL = ""  # 设置后支付宝支付成功会回调此URL

# Plans and prices (单位：分)
PLANS = {
    "pro_monthly": {"name": "Pro 月度会员", "price": 1900},
    "proplus_monthly": {"name": "Pro+ 月度会员", "price": 2900},
    "pro_lifetime": {"name": "Pro 终身会员", "price": 9900},
    "proplus_lifetime": {"name": "Pro+ 终身会员", "price": 19900},
}

# In-memory payment records
payments: dict = {}

def get_alipay():
    """初始化支付宝客户端"""
    from alipay import AliPay
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    priv_path = os.path.join(base_dir, "backend", "payment_keys", "app_private_key.pem")
    pub_path = os.path.join(base_dir, "backend", "payment_keys", "alipay_public_key.pem")
    
    with open(priv_path, encoding="utf-8") as f:
        app_priv = f.read()
    with open(pub_path, encoding="utf-8") as f:
        alipay_pub = f.read()
    
    return AliPay(
        appid=APP_ID,
        app_notify_url=NOTIFY_URL,
        app_private_key_string=app_priv,
        alipay_public_key_string=alipay_pub,
        sign_type="RSA2",
    )

class CheckoutRequest(BaseModel):
    plan_id: str  # pro_monthly / proplus_monthly / pro_lifetime / proplus_lifetime

@router.post("/create")
async def create_payment(req: CheckoutRequest):
    """创建支付订单，返回支付宝付款二维码"""
    plan = PLANS.get(req.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="无效的套餐")
    
    alipay = get_alipay()
    order_id = f"JB{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    
    # 调用当面付 API 生成二维码
    result = alipay.api_alipay_trade_precreate(
        subject=plan["name"],
        out_trade_no=order_id,
        total_amount=plan["price"] / 100,  # 元
    )
    
    if result.get("code") == "10000":
        qr_code = result.get("qr_code", "")
        payments[order_id] = {
            "plan_id": req.plan_id,
            "status": "pending",
            "amount": plan["price"],
            "created_at": datetime.utcnow().isoformat(),
        }
        return {"order_id": order_id, "qr_code": qr_code, "amount": plan["price"]}
    else:
        logger.error(f"Alipay error: {result}")
        raise HTTPException(status_code=500, detail=f"支付创建失败: {result.get('msg', '')}")

@router.get("/query/{order_id}")
async def query_payment(order_id: str):
    """查询订单支付状态"""
    alipay = get_alipay()
    result = alipay.api_alipay_trade_query(out_trade_no=order_id)
    
    trade_status = result.get("trade_status", "")
    is_success = trade_status == "TRADE_SUCCESS"
    
    if order_id in payments:
        if is_success:
            payments[order_id]["status"] = "paid"
        payments[order_id]["trade_status"] = trade_status
    
    return {
        "order_id": order_id,
        "trade_status": trade_status,
        "is_paid": is_success,
    }