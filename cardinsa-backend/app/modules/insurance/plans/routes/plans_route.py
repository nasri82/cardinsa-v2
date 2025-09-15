from fastapi import APIRouter
router=APIRouter(prefix='/plans', tags=['plans'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'plans'}
