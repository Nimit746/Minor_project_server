from fastapi import APIRouter, File, Response, UploadFile, status

from app.api.deps import CurrentUser, Pagination, ResumeSvc
from app.schemas.resume_schema import ResumeRead

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_202_ACCEPTED)
async def upload_resume(user: CurrentUser, service: ResumeSvc, file: UploadFile = File(...)):
    """Accepts the file and queues processing. Poll GET /resumes/{uuid} until status == 'ready'."""
    return await service.create_from_upload(user, file)


@router.get("", response_model=list[ResumeRead])
async def list_resumes(user: CurrentUser, service: ResumeSvc, page: Pagination):
    return await service.list_for_user(user, page.skip, page.limit)


@router.get("/{resume_uuid}", response_model=ResumeRead)
async def get_resume(resume_uuid: str, user: CurrentUser, service: ResumeSvc):
    return await service.get_owned(user, resume_uuid)


@router.delete("/{resume_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_uuid: str, user: CurrentUser, service: ResumeSvc):
    await service.delete(user, resume_uuid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
