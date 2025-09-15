from fastapi import APIRouter
router=APIRouter(prefix='/subscriptions', tags=['subscriptions'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'subscriptions'}
