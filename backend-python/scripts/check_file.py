with open('app/api/v1/maintenance_plan.py', 'rb') as f:
    content = f.read()
    print(f'File size: {len(content)} bytes')
    print(f'Contains null bytes: {b"\x00" in content}')
