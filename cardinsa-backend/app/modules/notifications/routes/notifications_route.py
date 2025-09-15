from fastapi import APIRouter
router=APIRouter(prefix='/notifications', tags=['notifications'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'notifications'}
