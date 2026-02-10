import sys
import os

print("Current directory:", os.getcwd())
sys.path.insert(0, os.getcwd())

print("Testing imports...")
try:
    print("1. Importing app.config...")
    from app.config import get_settings
    print("   Success")
    
    print("2. Importing app.database...")
    from app.database import get_db
    print("   Success")
    
    print("3. Importing app.schemas.maintenance_plan...")
    from app.schemas.maintenance_plan import MaintenancePlanCreate, MaintenancePlanUpdate, ApiResponse, PaginatedResponse
    print("   Success")
    
    print("4. Importing app.services.maintenance_plan...")
    from app.services.maintenance_plan import MaintenancePlanService
    print("   Success")
    
    print("5. Importing app.api.v1.maintenance_plan...")
    from app.api.v1 import maintenance_plan
    print("   Success")
    
    print(f"\nRouter prefix: {maintenance_plan.router.prefix}")
    print(f"Number of routes: {len(maintenance_plan.router.routes)}")
    
    for i, route in enumerate(maintenance_plan.router.routes[:5], 1):
        print(f"  Route {i}: {route.path} [{route.methods}]")
    
except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
