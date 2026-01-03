# 算力侧API接口文档

## 基本信息

- **版本**: v1.0.31
- **基础URL**: 
  - 本地开发：`http://host.docker.internal:9000`
  - 生产环境（Nginx反向代理）: `http://host.docker.internal:8081`
- **认证方式**: 无（未来可考虑引入API认证）

---

## 接口概览

1. **POST /generate** - 提交任务
2. **GET /result/{prompt_id}** - 查询生成结果

---

## 1. 提交任务接口 `POST /generate`

### 功能描述

该接口用于提交生成任务。任务会被发送至 **ComfyUI API**，并返回一个唯一的 `prompt_id` 用于后续查询任务状态。

### 请求路径

POST /generate

### 请求参数

| 参数   | 类型   | 说明                                           |
|--------|--------|------------------------------------------------|
| prompt | string | 生成的提示词（Prompt）。这是生成内容的核心。 |

### 请求示例

{
  "prompt": "Generate an image of a sunset over the ocean."
}

### 相应参数

| 参数        | 类型     | 说明                 |
| --------- | ------ | ------------------ |
| msg       | string | 返回任务的提交状态信息。       |
| prompt_id | string | 任务的唯一标识符，用于查询任务结果。 |

### 响应示例

{
  "msg": "任务已提交",
  "prompt_id": "86fac369-2aa3-4c8d-b15b-2a8ef31768f8"
}

### 错误响应

| 状态码 | 说明     | 错误描述                   |
| --- | ------ | ---------------------- |
| 500 | 提交任务失败 | 例如 ComfyUI API 服务不可用等。 |

## 2. 查询任务结果接口 GET /result/{prompt_id}  
### 功能描述  
该接口用于查询生成任务的执行结果。通过 prompt_id 查询生成的图片文件和相关信息。  

### 请求路径  
GET /result/{prompt_id}  

### 请求参数  
| 参数        | 类型      | 说明                           |
| --------- | ------- | ---------------------------- |
| prompt_id | string  | 任务的唯一标识符，用于查询生成结果。           |
| b64       | integer | 是否返回图片的Base64编码（0 或 1），默认 0。 |

### 请求示例  
GET /result/86fac369-2aa3-4c8d-b15b-2a8ef31768f8

### 响应参数  
| 参数             | 类型     | 说明                                 |
| -------------- | ------ | ---------------------------------- |
| status         | string | 返回状态，成功为 `success`，未完成为 `pending`。 |
| prompt_id      | string | 与请求相同的 `prompt_id`。                |
| images         | array  | 生成的图像信息列表。                         |
| filename       | string | 生成图像的文件名。                          |
| url            | string | 生成图像的访问URL。                        |
| local_path     | string | 生成图像的本地存储路径。                       |
| archive_url    | string | 图片上传到 Cloudflare R2 的 URL（如果上传成功）。 |
| archive_status | string | 图片上传状态：`success` 或 `failed`。       |
| archive_error  | string | 上传失败时的错误信息。                        |
| base64         | string | （可选）图片的Base64编码字符串。                |

### 响应示例  
```
{  
  "status": "success",  
  "prompt_id": "86fac369-2aa3-4c8d-b15b-2a8ef31768f8",  
  "images": [  
    {  
      "filename": "86fac369-2aa3-4c8d-b15b-2a8ef31768f8_00001_.png",  
      "url": "https://aiimg.example.com/outputs/86fac369-2aa3-4c8d-b15b-2a8ef31768f8_00001_.png",  
      "local_path": "/data/outputs/86fac369-2aa3-4c8d-b15b-2a8ef31768f8_00001_.png",  
      "archive_url": "https://aiimgcdn.example.com/archive/2026/01/02/86fac369-2aa3-4c8d-b15b-2a8ef31768f8_00001_.png",  
      "archive_status": "success",  
      "archive_error": null  
    }  
  ]  
}  
```

### 错误响应  
| 状态码 | 说明    | 错误描述         |
| --- | ----- | ------------ |
| 404 | 未找到任务 | 查询的任务不存在。    |
| 500 | 服务器错误 | 任务查询过程中出现错误。 |


### 环境变量说明  
算力侧API依赖以下环境变量：  
| 变量名               | 类型     | 说明                                                     |
| ----------------- | ------ | ------------------------------------------------------ |
| `COMFY_API`       | string | ComfyUI API 的地址。默认值：`http://host.docker.internal:8188` |
| `OUTPUT_DIR`      | string | 生成图片的输出目录。默认值：`/data/outputs`                          |
| `PUBLIC_BASE_URL` | string | 公网访问生成图像的基础URL。默认值：`https://aiimg.example.com/outputs`  |  
这些环境变量可以通过 .env 文件配置，或者在 docker-compose.yml 中设置。

### 错误码总结  
| 错误码   | 说明                                 |
| ----- | ---------------------------------- |
| `500` | 内部错误，可能由于 ComfyUI API 不可用、网络问题等    |
| `404` | 未找到指定的任务，可能是 `prompt_id` 错误或任务尚未完成 |
| `502` | 请求 ComfyUI API 失败，可能是 API 服务不可达    |
| `503` | 系统过载，无法处理请求                        |


### 未来扩展  

认证与权限控制：可以引入OAuth2认证机制，限制某些功能的访问权限。  
任务排队与调度：为了处理大规模的并发任务，可能需要引入任务调度和排队机制，确保算力资源的有效利用。  
更多的存储后端支持：除了 Cloudflare R2，未来可以扩展支持其他云存储服务。  


注：接口文档中的接口功能、参数等内容基于当前系统设计，如有修改，接口文档也需要同步更新。