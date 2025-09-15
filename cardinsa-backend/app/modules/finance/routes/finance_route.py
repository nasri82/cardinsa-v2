from fastapi import APIRouter
router=APIRouter(prefix='/finance', tags=['finance'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'finance'}
