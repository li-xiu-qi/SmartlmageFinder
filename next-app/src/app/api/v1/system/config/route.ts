import { NextResponse } from 'next/server'
import { inferenceHealth } from '@/lib/inference'
import { getDb, countDistinctTags } from '@/lib/db'

// GET /api/v1/system/config —— 当前生效配置（对齐旧 FastAPI /system/config）
export async function GET() {
  try {
    const db = getDb()
    let tagCount = 0
    let imageCount = 0
    try {
      tagCount = countDistinctTags()
      imageCount = (db.prepare('SELECT COUNT(*) as cnt FROM images').get() as { cnt: number }).cnt
    } catch {
      // 表未就绪则记 0
    }

    const inferenceOk = await inferenceHealth()

    return NextResponse.json({
      code: 0,
      message: 'success',
      data: {
        vision_model: process.env.VISION_MODEL || 'glm-4.6v-flash',
        embedding_model: process.env.EMBEDDING_MODEL || 'jina-embeddings-v4',
        embedding_dimension: 2048,
        inference_service_url: process.env.INFERENCE_SERVICE_URL || 'http://192.168.1.170:8100',
        inference_service_status: inferenceOk ? 'ok' : 'unavailable',
        db_path: db.name,
        image_count: imageCount,
        tag_count: tagCount,
        backend: 'next.js',
      },
    })
  } catch (e: any) {
    return NextResponse.json(
      { code: 'INTERNAL_ERROR', message: e.message, data: null },
      { status: 500 }
    )
  }
}
