import React from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { getImageUrl } from '@/utils/typeConverters'
import type { ImageCardModel } from '@/utils/typeConverters'

interface GalleryImageCardProps {
  image: ImageCardModel
  onClick?: (image: ImageCardModel) => void
  onTagClick?: (tag: string) => void
  showTags?: boolean
  showSimilarity?: boolean
  multiSelectMode?: boolean
  selected?: boolean
  onSelect?: (imageId: number, selected: boolean) => void
}

const processTags = (tags: unknown): string[] => {
  if (!tags) return []
  if (typeof tags === 'string') {
    try {
      return JSON.parse(tags)
    } catch {
      return []
    }
  }
  return Array.isArray(tags) ? tags : []
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/**
 * 画廊风图片卡片：图为主角，悬停浮层信息，相似度/多选态清晰
 */
const GalleryImageCard: React.FC<GalleryImageCardProps> = ({
  image,
  onClick,
  onTagClick,
  showTags = false,
  showSimilarity = false,
  multiSelectMode = false,
  selected = false,
  onSelect,
}) => {
  const isSearchResult = typeof image.score !== 'undefined'
  const tags = processTags(image.tags)
  const similarity = isSearchResult && showSimilarity ? Math.round((image.score || 0) * 100) : null

  const handleClick = () => {
    if (multiSelectMode && onSelect) {
      onSelect(image.id, !selected)
    } else if (onClick) {
      onClick(image)
    }
  }

  return (
    <figure
      onClick={handleClick}
      className={cn(
        'group relative cursor-pointer overflow-hidden rounded-lg border bg-card',
        'transition-all duration-200 ease-out',
        selected
          ? 'border-primary ring-2 ring-primary/40'
          : 'border-border hover:border-foreground/20 hover:shadow-lg hover:shadow-foreground/5'
      )}
    >
      {/* 图片区：aspect 固定，画廊感 */}
      <div className="relative aspect-[4/3] overflow-hidden bg-muted">
        <img
          src={getImageUrl(image as never)}
          alt={image.title || '图片'}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-300 ease-out group-hover:scale-[1.04]"
        />

        {/* 相似度徽章（搜索结果） */}
        {similarity !== null && (
          <span className="absolute left-2 top-2 rounded-full bg-foreground/85 px-2 py-0.5 text-[11px] font-medium text-background backdrop-blur-sm">
            相似度 {similarity}%
          </span>
        )}

        {/* 多选勾选 */}
        {multiSelectMode && (
          <span
            className={cn(
              'absolute right-2 top-2 flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all',
              selected
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-white/80 bg-black/20 text-transparent group-hover:bg-black/30'
            )}
          >
            <Check className="h-3.5 w-3.5" strokeWidth={3} />
          </span>
        )}

        {/* 悬停底部渐变 + 标题（画廊签名点） */}
        <figcaption
          className={cn(
            'pointer-events-none absolute inset-x-0 bottom-0 translate-y-1 bg-gradient-to-t from-black/70 via-black/30 to-transparent px-3 pb-2.5 pt-8',
            'opacity-0 transition-all duration-200 group-hover:translate-y-0 group-hover:opacity-100'
          )}
        >
          <p className="truncate text-sm font-medium text-white">
            {image.title || '未命名图片'}
          </p>
          <p className="text-[11px] text-white/70">{formatDate(image.created_at)}</p>
        </figcaption>
      </div>

      {/* 常驻信息区（仅在需要标签时显示，保持卡片干净） */}
      {showTags && tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 px-3 py-2">
          {tags.slice(0, 3).map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onTagClick?.(tag)
              }}
              className="rounded-full bg-secondary px-2 py-0.5 text-[11px] text-secondary-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              {tag}
            </button>
          ))}
          {tags.length > 3 && (
            <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
              +{tags.length - 3}
            </span>
          )}
        </div>
      )}
    </figure>
  )
}

export default GalleryImageCard
