from fastapi import APIRouter
router=APIRouter(prefix='/documents', tags=['documents'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'documents'}
