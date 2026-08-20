from fastapi import APIRouter

from app.api.v1.auth     import router as auth_router
from app.api.v1.users    import router as users_router
from app.api.v1.resumes  import router as resumes_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.ai       import router as ai_router
from app.api.v1.chat     import router as chat_router

router = APIRouter()
router.include_router(auth_router,     prefix="/auth",      tags=["Authentication"])
router.include_router(users_router,    prefix="/users",     tags=["Users"])
router.include_router(resumes_router,  prefix="/resumes",   tags=["Resumes"])
router.include_router(analysis_router, prefix="/analysis",  tags=["Analysis"])
router.include_router(ai_router,       prefix="/ai",        tags=["AI Features"])
router.include_router(chat_router,     prefix="/chat",      tags=["AI Chatbot"])
