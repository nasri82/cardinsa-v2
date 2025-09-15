from fastapi import APIRouter
router=APIRouter(prefix='/provider-networks', tags=['provider_networks'])
@router.get('/_ping')
def _ping():
    return {'ok': True, 'module': 'provider_networks'}
