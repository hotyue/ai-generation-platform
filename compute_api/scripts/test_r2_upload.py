from r2_uploader import upload_to_r2

# 请确保这个文件真实存在
test_file = r"D:\AI-Web\test.png"

# 上传到 R2 后的对象路径
object_key = "test/test.png"

url = upload_to_r2(test_file, object_key)

if url:
    print("UPLOAD OK:", url)
else:
    print("UPLOAD FAILED")
