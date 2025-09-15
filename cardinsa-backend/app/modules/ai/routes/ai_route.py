from fastapi import APIRouter
router=APIRouter(prefix='/ai', tags=['ai'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'ai'}
