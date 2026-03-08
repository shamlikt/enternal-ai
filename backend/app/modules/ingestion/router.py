from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.ingestion import schemas, service

router = APIRouter()


@router.get("/integrations/", response_model=list[schemas.IntegrationResponse])
async def list_integrations(db: AsyncSession = Depends(get_db)):
    return await service.list_integrations(db)


@router.post(
    "/integrations/",
    response_model=schemas.IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_integration(
    data: schemas.IntegrationCreate,
    db: AsyncSession = Depends(get_db),
):
    # TODO: inject current_user once auth module is complete
    return await service.create_integration(db, data, user_id=1)


@router.get("/integrations/{integration_id}", response_model=schemas.IntegrationResponse)
async def get_integration(integration_id: int, db: AsyncSession = Depends(get_db)):
    integration = await service.get_integration(db, integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/integrations/{integration_id}", response_model=schemas.IntegrationResponse)
async def update_integration(
    integration_id: int,
    data: schemas.IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
):
    integration = await service.update_integration(db, integration_id, data)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(integration_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await service.delete_integration(db, integration_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Integration not found")


@router.post("/integrations/{integration_id}/test")
async def test_integration(integration_id: int, db: AsyncSession = Depends(get_db)):
    integration = await service.get_integration(db, integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if integration.type == "fhir":
        success = await service.test_fhir_connection(integration.config_json)
        return {"success": success}

    raise HTTPException(status_code=400, detail="Connection test not supported for this type")


@router.post(
    "/ingestion/{integration_id}/run",
    response_model=schemas.IngestionRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_ingestion(
    integration_id: int,
    db: AsyncSession = Depends(get_db),
):
    integration = await service.get_integration(db, integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    if integration.type != "fhir":
        raise HTTPException(status_code=400, detail="Use /snowflake endpoint for Snowflake")

    # Import here to avoid circular dependency
    from app.modules.transformation.engine import TransformationEngine

    engine = TransformationEngine()
    run = await service.run_fhir_ingestion(db, integration, engine)
    return run


@router.get("/ingestion/runs", response_model=list[schemas.IngestionRunResponse])
async def list_runs(
    integration_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await service.list_ingestion_runs(db, integration_id)


@router.get("/ingestion/runs/{run_id}", response_model=schemas.IngestionRunResponse)
async def get_run(run_id: int, db: AsyncSession = Depends(get_db)):
    run = await service.get_ingestion_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Ingestion run not found")
    return run


@router.get("/quarantine/", response_model=list[schemas.QuarantineResponse])
async def list_quarantine(
    run_id: int | None = None,
    resource_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await service.list_quarantine_records(db, run_id, resource_type, limit, offset)


@router.get("/quarantine/stats", response_model=schemas.QuarantineStatsResponse)
async def quarantine_stats(db: AsyncSession = Depends(get_db)):
    stats = await service.get_quarantine_stats(db)
    return stats
