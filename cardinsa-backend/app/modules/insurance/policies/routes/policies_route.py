from fastapi import APIRouter
router=APIRouter(prefix='/policies', tags=['policies'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'policies'}
