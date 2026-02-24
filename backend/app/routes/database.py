"""
Database Testing and Health Check Routes
"""

from fastapi import APIRouter, HTTPException
from app.core.database import test_connection, connect_to_mongo, db
from app.core.config import Settings

router = APIRouter()
settings = Settings()

@router.get("/test-connection")
async def test_db_connection():
    """Test MongoDB connection and return detailed status"""
    try:
        connection_status = await test_connection()
        
        if connection_status["connected"]:
            return {
                "success": True,
                "message": "MongoDB connection is healthy",
                "details": connection_status
            }
        else:
            return {
                "success": False,
                "message": "MongoDB connection failed",
                "error": connection_status.get("error", "Unknown error")
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection test failed: {str(e)}"
        )

@router.get("/reconnect")
async def reconnect_database():
    """Attempt to reconnect to MongoDB"""
    try:
        success = await connect_to_mongo(settings)
        
        if success:
            return {
                "success": True,
                "message": "Successfully reconnected to MongoDB"
            }
        else:
            return {
                "success": False,
                "message": "Failed to reconnect to MongoDB"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database reconnection failed: {str(e)}"
        )

@router.get("/health")
async def database_health():
    """Quick health check for MongoDB"""
    try:
        if not db.client:
            return {
                "status": "disconnected",
                "message": "No database connection"
            }
        
        # Quick ping test
        await db.client.admin.command('ping')
        
        return {
            "status": "healthy",
            "message": "MongoDB is responding",
            "database": settings.MONGODB_DATABASE
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": f"MongoDB health check failed: {str(e)}"
        }