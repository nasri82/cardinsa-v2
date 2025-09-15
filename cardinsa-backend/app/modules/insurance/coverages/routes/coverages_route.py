from fastapi import APIRouter
router=APIRouter(prefix='/coverages', tags=['coverages'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'coverages'}
