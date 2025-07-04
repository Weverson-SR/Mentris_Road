from fastapi import FastAPI, Depends, HTTPException
from . import services, models, schemas
from .database import get_db, engine
from sqlalchemy.orm import Session

# iniciar a FASTAPI
app = FastAPI()

# Area responsavel pela criação dos modelos da fastapi da classe Motorista
@app.get("/motoristas/", response_model=list[schemas.Motorista])
async def get_all_motoristas(db: Session = Depends(get_db)):
    """
    Retorna todos os motoristas cadastrados.
    """
    return services.get_motoristas(db)

@app.get("/motoristas/{motorista_id}", response_model=schemas.Motorista)
async def get_motorista_by_id(motorista_id: int, db: Session = Depends(get_db)):
    """
    Retorna um motorista específico pelo ID.
    """
    motorista_queryset = services.get_motorista(db, motorista_id)
    if motorista_queryset:
         return motorista_queryset
    raise HTTPException(status_code=404, detail="Motorista não encontrado")

@app.post("/motoristas/", response_model=schemas.Motorista)
async def create_new_motorista(motorista: schemas.MotoristaCreate, db: Session = Depends(get_db)):
    """
    Cria um novo motorista.
    """
    return services.create_motorista(db, motorista)

@app.put("/motoristas/{motorista_id}", response_model=schemas.Motorista)
async def update_motorista(motorista_id: int, motorista: schemas.MotoristaCreate, db: Session = Depends(get_db)):
    """
    Atualiza um motorista existente.
    """
    db_updated_motorista = services.update_motorista(db, motorista, motorista_id)
    if not db_updated_motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    return db_updated_motorista

@app.delete("/motoristas/{motorista_id}", response_model=schemas.Motorista)
async def delete_motorista(motorista_id: int, db: Session = Depends(get_db)):
    """
    Deleta um motorista pelo ID.
    """
    motorista = services.get_motorista(db, motorista_id)
    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    # Verifica se o motorista possui veículos vinculados
    if motorista.veiculos and len(motorista.veiculos) > 0:
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir o motorista pois existem veículos vinculados a ele."
        )
    db_deleted_motorista = services.delete_motorista(db, motorista_id)
    return db_deleted_motorista
    

# Area responsavel pela criação dos modelos da fastapi da classe Veiculo
@app.get("/veiculos/", response_model=list[schemas.Veiculo])
async def get_all_veiculos(db: Session = Depends(get_db)):
    """
    Retorna todos os veículos cadastrados.
    """
    return services.get_veiculos(db)

@app.get("/veiculos/{veiculo_id}", response_model=schemas.Veiculo)
async def get_veiculo_by_id(veiculo_id: int, db: Session = Depends(get_db)):
    """
    Retorna um veículo específico pelo ID.
    """
    veiculo_queryset = services.get_veiculo(db, veiculo_id)
    if veiculo_queryset:
        return veiculo_queryset
    raise HTTPException(status_code=404, detail="Veículo não encontrado")

@app.post("/veiculos/", response_model=schemas.Veiculo)
async def create_new_veiculo(veiculo: schemas.VeiculoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo veículo.
    """
    # Verifica se o motorista já possui um veículo
    veiculo_exists = db.query(models.Veiculo).filter(models.Veiculo.motorista_id == veiculo.motorista_id).all()
    if veiculo_exists:
        raise HTTPException(status_code=400,detail="Este motorista já possui um veículo cadastrado.")
    return services.create_veiculo(db, veiculo)

@app.put("/veiculos/{veiculo_id}", response_model=schemas.Veiculo)
async def update_veiculo(veiculo_id: int, veiculo: schemas.VeiculoCreate, db: Session = Depends(get_db)):
    """
    Atualiza um veículo existente.
    """
    db_updated_veiculo = services.update_veiculo(db, veiculo, veiculo_id)
    if not db_updated_veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return db_updated_veiculo

@app.delete("/veiculos/{veiculo_id}", response_model=schemas.Veiculo)
async def delete_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    """
    Deleta um veículo pelo ID.
    """
    veiculo = services.get_veiculo(db, veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    # Armazena o objeto antes de deletar
    veiculo_delete = schemas.Veiculo.model_validate(veiculo)
    services.delete_veiculo(db, veiculo_id)
    return veiculo_delete
