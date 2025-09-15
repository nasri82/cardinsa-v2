from fastapi import APIRouter
router=APIRouter(prefix='/security', tags=['security'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'security'}
