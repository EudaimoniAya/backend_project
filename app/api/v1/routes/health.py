"""健康检查与存活探针。"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="健康检查")
async def health() -> dict[str, str]:
    """供负载均衡或编排探针使用。"""
    return {"status": "ok"}
