import httpx
import base64
import io
import json
import sys
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"
TEST_USERNAME = "测试管理员"
TEST_PASSWORD = "test1234"
TEST_PROJECT_ID = "TQ-2024-055A-SH"
TEST_PROJECT_NAME = "真如街道垃圾厢房智能化建设项目"

created_resources = {"spot_work_id": None, "temp_repair_id": None, "periodic_id": None, "photo_urls": []}


def create_test_image(size=(100, 100), color="red", fmt="JPEG"):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


def create_test_image_base64(size=(100, 100), color="red"):
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def get_auth_token(client):
    resp = client.post(f"{BASE_URL}/auth/login-json", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert resp.status_code == 200, f"登录失败: {resp.text}"
    data = resp.json()
    token = data.get("data", {}).get("access_token") or data.get("access_token")
    assert token, f"未获取到token: {resp.text}"
    return token


def test_health(client):
    resp = client.get(f"{BASE_URL.replace('/api/v1', '')}/api/v1/health")
    assert resp.status_code == 200, f"健康检查失败: {resp.status_code}"
    data = resp.json()
    print(f"  ✅ 健康检查通过，版本: {data.get('version', 'unknown')}")


def test_upload_image(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    img_buf = create_test_image(color="blue")
    resp = client.post(f"{BASE_URL}/upload", headers=headers, files={"file": ("test_photo.jpg", img_buf, "image/jpeg")})
    assert resp.status_code == 200, f"图片上传失败: {resp.text}"
    data = resp.json()
    url = data.get("data", {}).get("url") or data.get("data", {}).get("filename")
    assert url, f"未获取到上传URL: {resp.text}"
    print(f"  ✅ 图片上传成功: {url}")
    return url


def test_upload_base64(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    b64_data = create_test_image_base64(color="green")
    resp = client.post(f"{BASE_URL}/upload/base64", headers=headers, json={"data": b64_data, "filename": "test_b64.jpg"})
    assert resp.status_code == 200, f"Base64上传失败: {resp.text}"
    data = resp.json()
    url = data.get("data", {}).get("url") or data.get("data", {}).get("filename")
    assert url, f"未获取到上传URL: {resp.text}"
    print(f"  ✅ Base64上传成功: {url}")
    return url


def test_spot_work_photo_add_delete(client, token, photo_url1, photo_url2):
    headers = {"Authorization": f"Bearer {token}"}
    print("\n📋 测试现场施工(spot_work)图片添加和删除")

    resp = client.post(f"{BASE_URL}/spot-work", headers=headers, json={
        "project_id": TEST_PROJECT_ID,
        "project_name": TEST_PROJECT_NAME,
        "plan_start_date": "2026-05-15",
        "plan_end_date": "2026-05-16",
        "work_content": "测试图片上传删除功能",
        "photos": [photo_url1, photo_url2],
        "remarks": "自动化测试数据"
    })
    assert resp.status_code in (200, 201), f"创建现场施工失败: {resp.text}"
    data = resp.json()
    sw_id = data.get("data", {}).get("id")
    assert sw_id, f"未获取到工单ID: {resp.text}"
    created_resources["spot_work_id"] = sw_id
    print(f"  ✅ 创建工单成功 ID={sw_id}，含2张图片")

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    assert resp.status_code == 200, f"获取工单失败: {resp.text}"
    photos = resp.json().get("data", {}).get("photos", [])
    assert len(photos) == 2, f"图片数量应为2，实际为{len(photos)}"
    print(f"  ✅ 确认工单有2张图片: {photos}")

    resp = client.patch(f"{BASE_URL}/spot-work/{sw_id}", headers=headers, json={
        "photos": [photo_url1],
        "work_content": "测试图片上传删除功能",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"删除图片(patch)失败: {resp.text}"
    print(f"  ✅ patch删除1张图片成功")

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos", [])
    assert len(photos) == 1, f"删除后图片数量应为1，实际为{len(photos)}"
    assert photo_url1 in photos, f"剩余图片应为{photo_url1}，实际为{photos}"
    print(f"  ✅ 确认删除后只剩1张图片: {photos}")

    resp = client.patch(f"{BASE_URL}/spot-work/{sw_id}", headers=headers, json={
        "photos": [],
        "work_content": "测试图片上传删除功能",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"清空图片(patch)失败: {resp.text}"
    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos") or []
    assert len(photos) == 0, f"清空后图片数量应为0，实际为{len(photos)}"
    print(f"  ✅ 确认清空所有图片成功（空数组同步到后端）")

    resp = client.patch(f"{BASE_URL}/spot-work/{sw_id}", headers=headers, json={
        "photos": [photo_url1, photo_url2],
        "work_content": "测试图片上传删除功能",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"重新添加图片失败: {resp.text}"
    print(f"  ✅ 重新添加2张图片成功")


def test_temporary_repair_photo_add_delete(client, token, photo_url1, photo_url2):
    headers = {"Authorization": f"Bearer {token}"}
    print("\n📋 测试临时维修(temporary_repair)图片添加和删除")

    resp = client.post(f"{BASE_URL}/temporary-repair", headers=headers, json={
        "project_id": TEST_PROJECT_ID,
        "project_name": "测试项目-临时维修图片",
        "plan_start_date": "2026-05-15",
        "plan_end_date": "2026-05-16",
        "fault_description": "测试故障描述",
        "solution": "测试解决方案",
        "photos": [photo_url1, photo_url2],
        "remarks": "自动化测试数据"
    })
    assert resp.status_code in (200, 201), f"创建临时维修失败: {resp.text}"
    data = resp.json()
    tr_id = data.get("data", {}).get("id")
    assert tr_id, f"未获取到工单ID: {resp.text}"
    created_resources["temp_repair_id"] = tr_id
    print(f"  ✅ 创建工单成功 ID={tr_id}，含2张图片")

    resp = client.get(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos", [])
    assert len(photos) == 2, f"图片数量应为2，实际为{len(photos)}"
    print(f"  ✅ 确认工单有2张图片")

    resp = client.patch(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers, json={
        "photos": [photo_url1],
        "fault_description": "测试故障描述-已修改",
        "solution": "测试解决方案-已修改",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"删除图片(patch)失败: {resp.text}"
    print(f"  ✅ patch删除1张图片成功（含fault_description和solution字段）")

    resp = client.get(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers)
    data = resp.json().get("data", {})
    photos = data.get("photos", [])
    assert len(photos) == 1, f"删除后图片数量应为1，实际为{len(photos)}"
    fault_desc = data.get("fault_description", "")
    solution = data.get("solution", "")
    assert "已修改" in fault_desc, f"fault_description应包含'已修改'，实际为: {fault_desc}"
    assert "已修改" in solution, f"solution应包含'已修改'，实际为: {solution}"
    print(f"  ✅ 确认删除后只剩1张图片，且fault_description和solution字段正确保留")

    resp = client.patch(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers, json={
        "photos": [],
        "fault_description": "测试故障描述",
        "solution": "测试解决方案",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"清空图片失败: {resp.text}"
    resp = client.get(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos") or []
    assert len(photos) == 0, f"清空后图片数量应为0，实际为{len(photos)}"
    print(f"  ✅ 确认清空所有图片成功（空数组同步到后端）")


def test_admin_photo_delete(client, token, photo_url1, photo_url2):
    headers = {"Authorization": f"Bearer {token}"}
    print("\n📋 测试管理员编辑(admin-edit)照片添加和删除")

    sw_id = created_resources["spot_work_id"]
    if not sw_id:
        print("  ⚠️ 跳过：无现场施工工单ID")
        return

    resp = client.patch(f"{BASE_URL}/spot-work/{sw_id}", headers=headers, json={
        "photos": [photo_url1],
        "work_content": "测试图片上传删除功能",
        "remarks": "自动化测试数据"
    })
    assert resp.status_code == 200, f"设置初始图片失败: {resp.text}"

    resp = client.post(f"{BASE_URL}/admin-edit/photo/add", headers=headers, json={
        "work_order_type": "spot_work",
        "work_order_id": sw_id,
        "photo_url": photo_url2,
        "remark": "管理员添加测试图片"
    })
    assert resp.status_code == 200, f"管理员添加照片失败: {resp.text}"
    print(f"  ✅ 管理员添加照片成功")

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos", [])
    assert len(photos) == 2, f"添加后图片数量应为2，实际为{len(photos)}"
    print(f"  ✅ 确认添加后工单有2张图片")

    resp = client.post(f"{BASE_URL}/admin-edit/photo/delete", headers=headers, json={
        "work_order_type": "spot_work",
        "work_order_id": sw_id,
        "photo_url": photo_url2,
        "remark": "管理员删除测试图片"
    })
    assert resp.status_code == 200, f"管理员删除照片失败: {resp.text}"
    print(f"  ✅ 管理员删除照片成功")

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos", [])
    assert len(photos) == 1, f"删除后图片数量应为1，实际为{len(photos)}"
    assert photo_url1 in photos, f"剩余图片应为{photo_url1}，实际为{photos}"
    print(f"  ✅ 确认管理员删除后只剩1张图片")


def test_cleanup(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    print("\n🧹 清理测试数据")

    sw_id = created_resources["spot_work_id"]
    if sw_id:
        resp = client.delete(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
        status = "✅" if resp.status_code == 200 else "⚠️"
        print(f"  {status} 删除现场施工工单 ID={sw_id}")

    tr_id = created_resources["temp_repair_id"]
    if tr_id:
        resp = client.delete(f"{BASE_URL}/temporary-repair/{tr_id}", headers=headers)
        status = "✅" if resp.status_code == 200 else "⚠️"
        print(f"  {status} 删除临时维修工单 ID={tr_id}")

    pi_id = created_resources["periodic_id"]
    if pi_id:
        resp = client.delete(f"{BASE_URL}/periodic-inspection/{pi_id}", headers=headers)
        status = "✅" if resp.status_code == 200 else "⚠️"
        print(f"  {status} 删除定期巡检工单 ID={pi_id}")


def main():
    print("=" * 60)
    print("🧪 工单图片上传/删除端到端测试")
    print("=" * 60)

    client = httpx.Client(timeout=30)

    try:
        print("\n1️⃣ 健康检查")
        test_health(client)

        print("\n2️⃣ 登录获取Token")
        token = get_auth_token(client)
        print(f"  ✅ 登录成功，Token: {token[:20]}...")

        print("\n3️⃣ 图片上传测试")
        photo_url1 = test_upload_image(client, token)
        photo_url2 = test_upload_base64(client, token)
        created_resources["photo_urls"] = [photo_url1, photo_url2]

        print("\n4️⃣ 工单图片添加/删除测试")
        test_spot_work_photo_add_delete(client, token, photo_url1, photo_url2)
        test_temporary_repair_photo_add_delete(client, token, photo_url1, photo_url2)
        test_admin_photo_delete(client, token, photo_url1, photo_url2)

        print("\n5️⃣ 清理测试数据")
        test_admin_photo_delete_cleanup(client, token, photo_url1)

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            test_cleanup(client, token if 'token' in dir() else None)
        except:
            pass
        client.close()


def test_admin_photo_delete_cleanup(client, token, photo_url1):
    headers = {"Authorization": f"Bearer {token}"}
    sw_id = created_resources["spot_work_id"]
    if not sw_id:
        return

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos") or []

    if len(photos) > 1:
        for p in photos[1:]:
            resp = client.post(f"{BASE_URL}/admin-edit/photo/delete", headers=headers, json={
                "work_order_type": "spot_work",
                "work_order_id": sw_id,
                "photo_url": p,
                "remark": "测试清理"
            })
            if resp.status_code == 200:
                print(f"  ✅ 管理员删除照片成功: {p}")
            else:
                print(f"  ⚠️ 管理员删除照片失败: {resp.text}")

    resp = client.get(f"{BASE_URL}/spot-work/{sw_id}", headers=headers)
    photos = resp.json().get("data", {}).get("photos") or []
    assert len(photos) <= 1, f"管理员删除后应只剩0-1张图片，实际为{len(photos)}"
    print(f"  ✅ 管理员删除照片功能正常，剩余{len(photos)}张")


def test_cleanup(client, token):
    if not token:
        return
    headers = {"Authorization": f"Bearer {token}"}
    for key, endpoint in [("spot_work_id", "spot-work"), ("temp_repair_id", "temporary-repair"), ("periodic_id", "periodic-inspection")]:
        rid = created_resources.get(key)
        if rid:
            try:
                client.delete(f"{BASE_URL}/{endpoint}/{rid}", headers=headers)
                print(f"  🗑️ 清理{key}={rid}")
            except:
                pass


if __name__ == "__main__":
    sys.exit(main())
