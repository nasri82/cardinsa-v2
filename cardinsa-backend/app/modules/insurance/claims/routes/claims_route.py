from fastapi import APIRouter
router=APIRouter(prefix='/claims', tags=['claims'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'claims'}
