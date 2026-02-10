import sys
sys.path.insert(0, '.')

try:
    print("Testing import of maintenance_plan module...")
    from app.api.v1 import maintenance_plan
    print("Import successful!")
    print(f"Router prefix: {maintenance_plan.router.prefix}")
    print(f"Number of routes: {len(maintenance_plan.router.routes)}")
except Exception as e:
    print(f"Import failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
