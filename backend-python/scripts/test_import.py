from app.api.v1 import maintenance_plan
print("Import successful")
print(f"Router prefix: {maintenance_plan.router.prefix}")
print(f"Routes: {[route.path for route in maintenance_plan.router.routes]}")
