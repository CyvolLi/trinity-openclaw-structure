#!/bin/bash
# Generate image using Alibaba DashScope API (wan2.6-image)
# Supports reference image + text prompt

set -e

REF_IMAGE="$1"
OUTPUT_FILE="$2"

# Base64 encode reference image with proper prefix
MIME_TYPE="image/jpeg"
IMG_B64_PREFIXED="data:${MIME_TYPE};base64,$(base64 -w0 "$REF_IMAGE")"

# Create JSON payload
# Using image editing mode (enable_interleave=false) for reference-image-based generation
cat > /tmp/draw_payload.json << JSONEOF
{
  "model": "wan2.6-image",
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "text": "参考照片中这个男孩的形象，画一张他7-10岁时的写实肖像：同样的脸型和气质（戴细框眼镜、穿棕色连帽外套、安静微笑的男孩），但面容更稚嫩、更孩子气。背景简单干净，纯色浅色背景。写实插画风格，温暖光线，面部细节清晰。"
          },
          {
            "image": "${IMG_B64_PREFIXED}"
          }
        ]
      }
    ]
  },
  "parameters": {
    "enable_interleave": false,
    "negative_prompt": "照片、真人照片、畸形的、扭曲、模糊、低质量、色差、噪点、双下巴、色块、过度光滑、过度锐化",
    "n": 1,
    "size": "1K",
    "watermark": false,
    "prompt_extend": true
  }
}
JSONEOF

echo "Sending API request to generate image..."
HTTP_CODE=$(curl -s -o /tmp/draw_response.json -w "%{http_code}" \
  -X POST "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/draw_payload.json)

echo "HTTP status: $HTTP_CODE"
echo "Response:"
cat /tmp/draw_response.json | python3 -m json.tool 2>/dev/null || cat /tmp/draw_response.json

if [ "$HTTP_CODE" != "200" ]; then
    echo "SUCCESS=false"
    echo "FAIL_REASON=API returned HTTP $HTTP_CODE"
    exit 1
fi

# Extract image URL from response
IMAGE_URL=$(python3 -c "
import json
with open('/tmp/draw_response.json') as f:
    data = json.load(f)
try:
    url = data['output']['choices'][0]['message']['content'][0]['image']
    print(url)
except (KeyError, IndexError, TypeError):
    print('')
" 2>/dev/null)

if [ -z "$IMAGE_URL" ]; then
    echo "SUCCESS=false"
    echo "FAIL_REASON=No image URL in response"
    exit 1
fi

echo "Downloading image from: $IMAGE_URL"
curl -s -L -o "$OUTPUT_FILE" "$IMAGE_URL"
FILE_SIZE=$(stat -c%s "$OUTPUT_FILE" 2>/dev/null || stat -f%z "$OUTPUT_FILE" 2>/dev/null)
echo "File size: $FILE_SIZE bytes"
echo "Saved to: $OUTPUT_FILE"
echo "SUCCESS=true"
