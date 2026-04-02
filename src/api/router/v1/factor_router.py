"""
Factor Router - 因子路由
"""

from fastapi import APIRouter, Depends
from ..schema import FactorTestRequest
from ..controller import FactorController

router = APIRouter(prefix="/factors", tags=["factors"])


def get_factor_controller():
    return FactorController()


@router.get("/types")
async def get_factor_types(
    controller: FactorController = Depends(get_factor_controller)
):
    """获取因子类型列表"""
    return await controller.get_factor_types()


@router.get("/{factor_id}/code")
async def get_factor_code(
    factor_id: str,
    controller: FactorController = Depends(get_factor_controller)
):
    """获取因子 Python 代码"""
    return await controller.get_factor_code(factor_id)


@router.post("/test")
async def test_factor(
    request: FactorTestRequest,
    controller: FactorController = Depends(get_factor_controller)
):
    """测试因子有效性"""
    return await controller.test_factor(request)
