from fastapi import APIRouter
router=APIRouter(prefix='/quotations', tags=['quotations'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'quotations'}
